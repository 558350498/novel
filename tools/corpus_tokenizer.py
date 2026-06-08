from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEXICON = ROOT / "tools" / "style_lexicon.json"
DEFAULT_TAXONOMY = ROOT / "tools" / "lexicon_taxonomy.json"
PUNCTUATION = set("，。！？；：、“”‘’（）《》〈〉「」『』…—,.!?;:\"'()[]{}<>- \t\r\n")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
ASCII_RE = re.compile(r"[A-Za-z0-9_]+")
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?]+")


class TokenizerError(ValueError):
    pass


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    if not path.exists():
        raise TokenizerError(f"file not found: {path}")
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    for encoding in ("utf-8", "gb18030", "utf-16"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise TokenizerError(f"unsupported text encoding: {path}")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_lexicon_terms(path: Path) -> list[str]:
    if not path.exists():
        return []
    lexicon = load_json(path)
    terms: set[str] = set()
    for value in lexicon.values():
        if isinstance(value, list):
            terms.update(term for term in value if isinstance(term, str))
    return sorted((term for term in terms if term), key=lambda item: (-len(item), item))


def load_taxonomy(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"categories": {}}
    return load_json(path)


def slice_lines(text: str, start_line: int | None, end_before_line: int | None) -> str:
    if start_line is None and end_before_line is None:
        return text
    if start_line is None or end_before_line is None:
        raise TokenizerError("start-line and end-before-line must be used together")
    if start_line < 1:
        raise TokenizerError("start-line must be >= 1")
    if end_before_line <= start_line:
        raise TokenizerError("end-before-line must be greater than start-line")
    lines = text.splitlines()
    return "\n".join(lines[start_line - 1 : end_before_line - 1])


def compact_chars(text: str) -> list[str]:
    return [ch for ch in text if CJK_RE.match(ch)]


def sentence_lengths(text: str) -> list[int]:
    lengths = []
    for sentence in SENTENCE_SPLIT_RE.split(text):
        compact = re.sub(r"\s+", "", sentence)
        if compact:
            lengths.append(len(compact))
    return lengths


def percentile(values: list[int], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return float(ordered[index])


def regex_tokens(text: str, protected_terms: list[str]) -> list[str]:
    tokens: list[str] = []
    term_by_first: dict[str, list[str]] = {}
    for term in protected_terms:
        if term:
            term_by_first.setdefault(term[0], []).append(term)

    index = 0
    while index < len(text):
        ch = text[index]
        if ch in PUNCTUATION or ch.isspace():
            index += 1
            continue

        matched = None
        for term in term_by_first.get(ch, []):
            if text.startswith(term, index):
                matched = term
                break
        if matched:
            tokens.append(matched)
            index += len(matched)
            continue

        ascii_match = ASCII_RE.match(text, index)
        if ascii_match:
            tokens.append(ascii_match.group(0))
            index = ascii_match.end()
            continue

        if CJK_RE.match(ch):
            tokens.append(ch)
        index += 1
    return tokens


def jieba_tokens(text: str, protected_terms: list[str]) -> list[str]:
    try:
        import jieba  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise TokenizerError("jieba is not installed; use --engine regex or install jieba") from exc

    for term in protected_terms:
        if len(term) >= 2:
            jieba.add_word(term)

    tokens = []
    for token in jieba.cut(text, cut_all=False):
        stripped = token.strip()
        if stripped and not all(ch in PUNCTUATION for ch in stripped):
            tokens.append(stripped)
    return tokens


def tiktoken_tokens(text: str, encoding_name: str) -> list[str]:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise TokenizerError("tiktoken is not installed; install tiktoken or use --engine regex") from exc

    try:
        encoding = tiktoken.get_encoding(encoding_name)
    except Exception as exc:  # pragma: no cover - depends on optional tiktoken registry.
        raise TokenizerError(f"unknown tiktoken encoding: {encoding_name}") from exc

    token_ids = encoding.encode(text)
    tokens: list[str] = []
    for token_id in token_ids:
        token_bytes = encoding.decode_single_token_bytes(token_id)
        token = token_bytes.decode("utf-8", errors="replace")
        if token and not token.isspace():
            tokens.append(token)
    return tokens


def hf_tokens(text: str, model_name: str, local_files_only: bool) -> list[str]:
    try:
        from transformers import AutoTokenizer  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise TokenizerError("transformers is not installed; install transformers/tokenizers or use --engine regex") from exc

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            local_files_only=local_files_only,
        )
    except Exception as exc:  # pragma: no cover - depends on optional model cache/network.
        mode = "local cache" if local_files_only else "Hugging Face"
        raise TokenizerError(f"failed to load tokenizer {model_name!r} from {mode}: {exc}") from exc

    token_ids = tokenizer.encode(text, add_special_tokens=False)
    tokens = [
        tokenizer.decode([token_id], clean_up_tokenization_spaces=False)
        for token_id in token_ids
    ]
    return [token for token in tokens if token and not token.isspace()]


def tokenize(
    text: str,
    engine: str,
    protected_terms: list[str],
    tiktoken_encoding: str,
    hf_model: str,
    hf_local_files_only: bool,
) -> list[str]:
    if engine == "regex":
        return regex_tokens(text, protected_terms)
    if engine == "jieba":
        return jieba_tokens(text, protected_terms)
    if engine == "tiktoken":
        return tiktoken_tokens(text, tiktoken_encoding)
    if engine == "hf":
        return hf_tokens(text, hf_model, hf_local_files_only)
    raise TokenizerError(f"unknown engine: {engine}")


def cjk_ngrams(text: str, n: int) -> Counter[str]:
    chars = compact_chars(text)
    return Counter("".join(chars[index : index + n]) for index in range(0, max(0, len(chars) - n + 1)))


def token_ngrams(tokens: list[str], n: int) -> Counter[str]:
    return Counter(" ".join(tokens[index : index + n]) for index in range(0, max(0, len(tokens) - n + 1)))


def top_items(counter: Counter[str], limit: int) -> list[dict[str, int | str]]:
    return [{"item": item, "count": count} for item, count in counter.most_common(limit)]


def count_terms(text: str, terms: Iterable[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for term in terms:
        count = text.count(term)
        if count:
            counts[term] = count
    return counts


def taxonomy_hits(text: str, lexicon: dict[str, Any], taxonomy: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for category_id, config in taxonomy.get("categories", {}).items():
        terms: list[str] = []
        for key in config.get("current_lexicon_keys", []):
            value = lexicon.get(key)
            if isinstance(value, list):
                terms.extend(term for term in value if isinstance(term, str))
        hits = count_terms(text, terms)
        rows.append({
            "id": category_id,
            "label": config.get("label", category_id),
            "count": sum(hits.values()),
            "matched_terms": top_items(hits, limit),
            "project_gate_labels": config.get("project_gate_labels", []),
        })
    return sorted(rows, key=lambda item: (-item["count"], item["id"]))


def filter_candidate_phrases(counter: Counter[str], *, min_count: int, limit: int) -> list[dict[str, int | str]]:
    candidates = []
    bad_chars = set("的一是在了不有和就也都而及与为着过吗呢啊吧")
    for item, count in counter.most_common():
        if count < min_count:
            break
        if len(item) < 2:
            continue
        if item[0] in bad_chars or item[-1] in bad_chars:
            continue
        if len(set(item)) == 1:
            continue
        candidates.append({"item": item, "count": count})
        if len(candidates) >= limit:
            break
    return candidates


def build_report(
    source_path: Path,
    text: str,
    tokens: list[str],
    engine: str,
    tiktoken_encoding: str | None,
    hf_model: str | None,
    start_line: int | None,
    end_before_line: int | None,
    topn: int,
    lexicon: dict[str, Any],
    taxonomy: dict[str, Any],
) -> dict[str, Any]:
    lengths = sentence_lengths(text)
    token_counts = Counter(tokens)
    cjk_bigram = cjk_ngrams(text, 2)
    cjk_trigram = cjk_ngrams(text, 3)
    cjk_quadgram = cjk_ngrams(text, 4)
    token_bigram = token_ngrams(tokens, 2)
    token_trigram = token_ngrams(tokens, 3)

    return {
        "source_path": display_path(source_path),
        "engine": engine,
        "tiktoken_encoding": tiktoken_encoding,
        "hf_model": hf_model,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "slice": {
            "start_line": start_line,
            "end_before_line": end_before_line,
        },
        "metrics": {
            "chars_no_ws": len(re.sub(r"\s+", "", text)),
            "cjk_chars": len(compact_chars(text)),
            "line_count": len(text.splitlines()),
            "token_count": len(tokens),
            "unique_tokens": len(token_counts),
            "sentence_count": len(lengths),
            "sentence_avg": round(sum(lengths) / len(lengths), 2) if lengths else 0.0,
            "sentence_median": round(statistics.median(lengths), 2) if lengths else 0.0,
            "sentence_p90": round(percentile(lengths, 0.9), 2),
        },
        "top_tokens": top_items(token_counts, topn),
        "top_token_bigrams": top_items(token_bigram, topn),
        "top_token_trigrams": top_items(token_trigram, topn),
        "top_cjk_bigrams": top_items(cjk_bigram, topn),
        "top_cjk_trigrams": top_items(cjk_trigram, topn),
        "top_cjk_quadgrams": top_items(cjk_quadgram, topn),
        "candidate_phrases": {
            "cjk_bigrams": filter_candidate_phrases(cjk_bigram, min_count=6, limit=topn),
            "cjk_trigrams": filter_candidate_phrases(cjk_trigram, min_count=4, limit=topn),
            "cjk_quadgrams": filter_candidate_phrases(cjk_quadgram, min_count=3, limit=topn),
        },
        "taxonomy_hits": taxonomy_hits(text, lexicon, taxonomy, topn),
        "notes": [
            "Tokenization is for lexicon discovery and diagnostics, not a literary quality score.",
            "The regex engine is deterministic and uses protected lexicon terms plus CJK characters.",
            "The jieba engine is used only when the optional open-source package is installed.",
            "The tiktoken engine is OpenAI model-tokenization oriented and should not be treated as linguistic word segmentation.",
            "The hf engine loads a Hugging Face tokenizer such as DeepSeek and should also be treated as model tokenization, not linguistic word segmentation.",
            "Taxonomy hits use general linguistic categories before mapping to project gate labels.",
        ],
    }


def render_section(title: str, items: Iterable[dict[str, int | str]], limit: int = 20) -> list[str]:
    lines = [f"## {title}", "", "| 项 | 次数 |", "|---|---:|"]
    for entry in list(items)[:limit]:
        lines.append(f"| `{entry['item']}` | {entry['count']} |")
    lines.append("")
    return lines


def render_taxonomy_hits(items: list[dict[str, Any]]) -> list[str]:
    lines = ["## Taxonomy Category Hits", "", "| 分类 | 次数 | 项目映射 | Top hits |", "|---|---:|---|---|"]
    for item in items:
        hits = "、".join(f"`{hit['item']}`×{hit['count']}" for hit in item["matched_terms"][:8]) or "无"
        gates = "、".join(item.get("project_gate_labels", [])) or "-"
        lines.append(f"| `{item['id']}` {item['label']} | {item['count']} | {gates} | {hits} |")
    lines.append("")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# 语料 Tokenization 报告",
        "",
        f"- 文件：`{report['source_path']}`",
        f"- 引擎：`{report['engine']}`",
        f"- tiktoken encoding：`{report['tiktoken_encoding'] or '-'}`",
        f"- HF model：`{report['hf_model'] or '-'}`",
        f"- 生成时间：{report['generated_at']}",
        "- 边界：用于词表发现和诊断，不作为质量评分。",
        "",
        "## 基础指标",
        "",
        f"- 非空白字符：{metrics['chars_no_ws']}",
        f"- CJK 字符：{metrics['cjk_chars']}",
        f"- 行数：{metrics['line_count']}",
        f"- token 数：{metrics['token_count']}",
        f"- unique token：{metrics['unique_tokens']}",
        f"- 句数：{metrics['sentence_count']}",
        f"- 平均/中位/P90 句长：{metrics['sentence_avg']} / {metrics['sentence_median']} / {metrics['sentence_p90']}",
        "",
    ]
    lines.extend(render_taxonomy_hits(report.get("taxonomy_hits", [])))
    lines.extend(render_section("Top Tokens", report["top_tokens"]))
    lines.extend(render_section("Top Token Bigrams", report["top_token_bigrams"]))
    lines.extend(render_section("Top CJK Trigrams", report["top_cjk_trigrams"]))
    lines.extend(render_section("Candidate Phrase Seeds", report["candidate_phrases"]["cjk_trigrams"]))
    lines.extend([
        "## 说明",
        "",
        "- `regex` 引擎不会假装完成真正中文分词；它主要给出稳定 token、字符 n-gram 和候选短语。",
        "- 如果安装 `jieba`，可用 `--engine jieba` 生成更接近中文词的 token 结果。",
        "- 如果安装 `tiktoken`，可用 `--engine tiktoken` 生成 OpenAI 模型侧 tokenization 对照；它不是语言学分词。",
        "- 如果安装 `transformers` 并具备模型 tokenizer 文件，可用 `--engine hf --hf-model deepseek-ai/DeepSeek-V3` 生成 DeepSeek tokenizer 对照；它同样不是语言学分词。",
        "- 后续词表迭代应结合用户 review，不应直接把高频词全部加入 gate。",
    ])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tokenize corpus slices for lexicon discovery.")
    parser.add_argument("--source", type=Path, required=True, help="Source text file.")
    parser.add_argument("--output-prefix", type=Path, required=True, help="Output path prefix without extension.")
    parser.add_argument("--engine", choices=["regex", "jieba", "tiktoken", "hf"], default="regex", help="Tokenization engine.")
    parser.add_argument("--tiktoken-encoding", default="o200k_base", help="Encoding name for --engine tiktoken.")
    parser.add_argument("--hf-model", default="deepseek-ai/DeepSeek-V3", help="Hugging Face tokenizer model for --engine hf.")
    parser.add_argument("--hf-local-files-only", action="store_true", help="Load Hugging Face tokenizer from local cache only.")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON, help="Protected term lexicon.")
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY, help="General lexicon taxonomy.")
    parser.add_argument("--start-line", type=int, help="Optional 1-based slice start line.")
    parser.add_argument("--end-before-line", type=int, help="Optional exclusive slice end line.")
    parser.add_argument("--topn", type=int, default=50, help="Number of top items to report.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    source_path = resolve_project_path(args.source)
    output_prefix = resolve_project_path(args.output_prefix)
    lexicon_path = resolve_project_path(args.lexicon)
    taxonomy_path = resolve_project_path(args.taxonomy)

    try:
        text = slice_lines(read_text(source_path), args.start_line, args.end_before_line)
        lexicon = load_json(lexicon_path) if lexicon_path.exists() else {}
        taxonomy = load_taxonomy(taxonomy_path)
        protected_terms = load_lexicon_terms(lexicon_path)
        tokens = tokenize(
            text,
            args.engine,
            protected_terms,
            args.tiktoken_encoding,
            args.hf_model,
            args.hf_local_files_only,
        )
        report = build_report(
            source_path,
            text,
            tokens,
            args.engine,
            args.tiktoken_encoding if args.engine == "tiktoken" else None,
            args.hf_model if args.engine == "hf" else None,
            args.start_line,
            args.end_before_line,
            args.topn,
            lexicon,
            taxonomy,
        )
    except (TokenizerError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    markdown_path = output_prefix.with_suffix(".md")
    tokens_path = output_prefix.with_suffix(".tokens.txt")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    tokens_path.write_text(" ".join(tokens) + "\n", encoding="utf-8")
    print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
