from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEXICON = ROOT / "tools" / "style_lexicon.json"


CJK_RE = re.compile(r"[\u4e00-\u9fff]")
ASCII_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
SPEAKER_RE = re.compile(r"^\s*([^：:「『“”\"']{1,12})[：:]\s*(.*)$")
QUOTE_START_RE = re.compile(r"^\s*[「『“\"']")
KNOWN_SPEAKERS = {"我", "安达", "岛村", "樽见", "日野", "永藤", "小社", "妹妹", "母亲", "店长"}


@dataclass
class TermHit:
    term: str
    count: int


def load_lexicon(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path: Path) -> str:
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
    raise UnicodeDecodeError("text", data, 0, 1, f"unsupported text encoding: {path}")


def approx_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def count_words_for_context(text: str) -> int:
    cjk = len(CJK_RE.findall(text))
    ascii_tokens = len(ASCII_TOKEN_RE.findall(text))
    return cjk + ascii_tokens


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def is_dialogue_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("#", "-", "*", "`")):
        return False
    if QUOTE_START_RE.match(stripped):
        return True
    match = SPEAKER_RE.match(stripped)
    if not match:
        return False
    speaker = match.group(1).strip()
    content = match.group(2).strip()
    return bool(content) and speaker in KNOWN_SPEAKERS


def dialogue_content(line: str) -> str:
    stripped = line.strip()
    match = SPEAKER_RE.match(stripped)
    if match:
        stripped = match.group(2).strip()
    return stripped.strip("「」『』“”\"' ")


def speaker_name(line: str) -> str | None:
    match = SPEAKER_RE.match(line.strip())
    if not match:
        return None
    return match.group(1).strip()


def count_terms(text: str, terms: Iterable[str]) -> list[TermHit]:
    hits = []
    for term in terms:
        count = text.count(term)
        if count:
            hits.append(TermHit(term=term, count=count))
    return sorted(hits, key=lambda h: (-h.count, h.term))


def strip_negated_terms(text: str, terms: Iterable[str]) -> str:
    cleaned = text
    prefixes = ["不", "不要", "不能", "不可", "没有", "没", "并不", "并没有", "未"]
    for term in terms:
        for prefix in prefixes:
            cleaned = cleaned.replace(prefix + term, "")
    return cleaned


def strip_guarded_terms(text: str, terms: Iterable[str]) -> str:
    cleaned = strip_negated_terms(text, terms)
    guards = ["避免", "禁止", "不要使用", "不要写", "应避免"]
    term_list = list(terms)
    guarded_lines: list[str] = []
    for line in cleaned.splitlines():
        if any(guard in line for guard in guards) and any(term in line for term in term_list):
            for term in term_list:
                line = line.replace(term, "")
        guarded_lines.append(line)
    cleaned = "\n".join(guarded_lines)
    for term in term_list:
        for guard in guards:
            cleaned = re.sub(re.escape(guard) + r"[「『“\"']?" + re.escape(term), "", cleaned)
    return cleaned


def sum_hits(hits: Iterable[TermHit]) -> int:
    return sum(hit.count for hit in hits)


def per_1000(count: int, char_count: int) -> float:
    if char_count <= 0:
        return 0.0
    return count * 1000.0 / char_count


def status_line(status: str, label: str, detail: str) -> str:
    return f"- `{status}` **{label}**：{detail}"


def status_for_max(value: float, warn: float, risk: float) -> str:
    if value >= risk:
        return "RISK"
    if value >= warn:
        return "WARN"
    return "OK"


def status_for_min(value: float, warn: float, risk: float) -> str:
    if value < risk:
        return "RISK"
    if value < warn:
        return "WARN"
    return "OK"


def format_hits(hits: list[TermHit], limit: int = 8) -> str:
    if not hits:
        return "无"
    return "、".join(f"{hit.term}×{hit.count}" for hit in hits[:limit])


def hits_to_json(hits: list[TermHit]) -> list[dict[str, int | str]]:
    return [{"term": hit.term, "count": hit.count} for hit in hits]


def basic_metrics(text: str) -> dict:
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    dialogue_lines = [line for line in non_empty_lines if is_dialogue_line(line)]
    char_count = approx_chars(text)
    return {
        "char_count": char_count,
        "word_context_count": count_words_for_context(text),
        "paragraph_count": len(split_paragraphs(text)),
        "line_count": len(lines),
        "non_empty_line_count": len(non_empty_lines),
        "dialogue_line_count": len(dialogue_lines),
        "dialogue_ratio": (len(dialogue_lines) / len(non_empty_lines)) if non_empty_lines else 0.0,
        "dialogue_lines": dialogue_lines,
    }


def shimamura_dialogue_metrics(text: str, lexicon: dict) -> dict:
    explicit_lines: list[str] = []
    explanation_hits = 0
    for line in text.splitlines():
        speaker = speaker_name(line)
        if speaker and "岛村" in speaker:
            content = dialogue_content(line)
            explicit_lines.append(content)
            explanation_hits += sum(content.count(term) for term in lexicon["shimamura_explanation_markers"])

    avg_len = 0.0
    if explicit_lines:
        avg_len = sum(approx_chars(line) for line in explicit_lines) / len(explicit_lines)
    return {
        "explicit_count": len(explicit_lines),
        "avg_len": avg_len,
        "explanation_hits": explanation_hits,
    }


def dialogue_burst_metrics(dialogue_lines: list[str]) -> dict:
    lengths = [approx_chars(dialogue_content(line)) for line in dialogue_lines]
    if not lengths:
        return {
            "max_len": 0,
            "avg_len": 0.0,
            "count_ge_40": 0,
            "count_ge_80": 0,
            "count_ge_200": 0,
            "length_bins": {},
        }
    bins = dialogue_length_bins(lengths)
    return {
        "max_len": max(lengths),
        "avg_len": sum(lengths) / len(lengths),
        "count_ge_40": sum(length >= 40 for length in lengths),
        "count_ge_80": sum(length >= 80 for length in lengths),
        "count_ge_200": sum(length >= 200 for length in lengths),
        "length_bins": bins,
    }


def dialogue_length_bins(lengths: list[int]) -> dict[str, dict[str, float | int]]:
    ranges = [
        ("1-5", 1, 5),
        ("6-10", 6, 10),
        ("11-20", 11, 20),
        ("21-40", 21, 40),
        ("41-80", 41, 80),
        ("81-160", 81, 160),
        ("161-320", 161, 320),
        ("321+", 321, None),
    ]
    total = len(lengths)
    bins: dict[str, dict[str, float | int]] = {}
    for label, low, high in ranges:
        count = sum(length >= low and (high is None or length <= high) for length in lengths)
        bins[label] = {
            "count": count,
            "pct": (count * 100.0 / total) if total else 0.0,
        }
    return bins


def format_dialogue_bins(bins: dict[str, dict[str, float | int]]) -> str:
    if not bins:
        return "无"
    return "；".join(
        f"{label}: {values['count']} ({values['pct']:.1f}%)"
        for label, values in bins.items()
    )


def evaluate_prompt(text: str, source: Path, lexicon: dict) -> str:
    metrics = basic_metrics(text)
    thresholds = lexicon["thresholds"]
    unsafe_scope = strip_negated_terms(text, lexicon["prompt_unsafe_phrases"])
    unsafe_hits = count_terms(unsafe_scope, lexicon["prompt_unsafe_phrases"])
    boundary_hits = count_terms(text, lexicon["prompt_boundary_phrases"])
    anchor_hits = count_terms(text, lexicon["prompt_required_anchors"])
    closure_scope = strip_guarded_terms(text, lexicon["closure_terms"])
    closure_hits = count_terms(closure_scope, lexicon["closure_terms"])
    literary_scope = strip_guarded_terms(text, lexicon["literary_risk_terms"])
    literary_hits = count_terms(literary_scope, lexicon["literary_risk_terms"])

    lines = [
        "# 文本风格评估报告",
        "",
        f"- 模式：`prompt`",
        f"- 文件：`{source}`",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 基础指标",
        "",
        f"- 字符数：{metrics['char_count']}",
        f"- 段落数：{metrics['paragraph_count']}",
        "",
        "## 检查结果",
        "",
    ]

    unsafe_status = "RISK" if unsafe_hits else "OK"
    lines.append(status_line(unsafe_status, "指令风险", f"风险短语：{format_hits(unsafe_hits)}"))

    boundary_count = sum_hits(boundary_hits)
    boundary_status = status_for_min(
        boundary_count,
        thresholds["prompt_boundary_min"],
        max(1, thresholds["prompt_boundary_min"] - 2),
    )
    lines.append(status_line(boundary_status, "版权与风格边界", f"边界提示命中 {boundary_count} 次：{format_hits(boundary_hits)}"))

    anchor_count = len(anchor_hits)
    anchor_status = status_for_min(anchor_count, thresholds["prompt_required_anchor_min"], 2)
    lines.append(status_line(anchor_status, "任务锚点", f"锚点类别命中 {anchor_count} 个：{format_hits(anchor_hits)}"))

    closure_status = "WARN" if closure_hits else "OK"
    lines.append(status_line(closure_status, "结尾封闭化风险", f"解决/和解词：{format_hits(closure_hits)}"))

    literary_density = per_1000(sum_hits(literary_hits), metrics["char_count"])
    literary_status = status_for_max(literary_density, thresholds["literary_per_1000_warn"], thresholds["literary_per_1000_warn"] * 2)
    lines.append(status_line(literary_status, "过度文学化风险", f"密度 {literary_density:.2f}/千字；命中：{format_hits(literary_hits)}"))

    lines.extend([
        "",
        "## 解释",
        "",
        "- `OK` 表示当前指标没有明显风险。",
        "- `WARN` 表示建议人工复核。",
        "- `RISK` 表示该项可能影响生成约束或版权边界。",
    ])
    return "\n".join(lines) + "\n"


def evaluate_draft(text: str, source: Path, lexicon: dict) -> str:
    data = evaluate_draft_data(text, source, lexicon)
    return render_draft_markdown(data, source)


def render_draft_markdown(data: dict[str, Any], source: Path) -> str:
    metrics = data["metrics"]

    lines = [
        "# 文本风格评估报告",
        "",
        f"- 模式：`draft`",
        f"- 文件：`{source}`",
        f"- 生成时间：{data['generated_at']}",
        "",
        "## 基础指标",
        "",
        f"- 字符数：{metrics['char_count']}",
        f"- 段落数：{metrics['paragraph_count']}",
        f"- 非空行数：{metrics['non_empty_line_count']}",
        f"- 对话行数：{metrics['dialogue_line_count']}",
        f"- 对话占比：{metrics['dialogue_ratio']:.1%}",
        "",
        "## 检查结果",
        "",
    ]
    for check in data["checks"]:
        lines.append(status_line(check["status"], check["label"], check["detail"]))

    lines.extend([
        "",
        "## 解释",
        "",
        "- `OK` 表示当前指标没有明显风险。",
        "- `WARN` 表示建议人工复核。",
        "- `RISK` 表示该项可能破坏目标文本机制。",
        "- 本工具只做规则提示，不替代人工审稿。",
    ])
    return "\n".join(lines) + "\n"


def evaluate_draft_data(text: str, source: Path, lexicon: dict) -> dict[str, Any]:
    metrics = basic_metrics(text)
    thresholds = lexicon["thresholds"]
    char_count = metrics["char_count"]
    tail = text[-thresholds["tail_chars"] :] if text else ""

    direct_hits = count_terms(text, lexicon["direct_emotion_terms"])
    hedge_hits = count_terms(text, lexicon["hedge_terms"])
    negation_hits = count_terms(text, lexicon["negation_terms"])
    correction_hits = count_terms(text, lexicon["self_correction_terms"])
    mundane_hits = count_terms(text, lexicon["mundane_object_terms"])
    closure_tail_scope = strip_negated_terms(tail, lexicon["closure_terms"])
    closure_tail_hits = count_terms(closure_tail_scope, lexicon["closure_terms"])
    literary_hits = count_terms(text, lexicon["literary_risk_terms"])
    analysis_leak_hits = count_terms(text, lexicon["analysis_leak_terms"])
    receiver_hits = count_terms(text, lexicon["receiver_misalignment_terms"])
    shimamura = shimamura_dialogue_metrics(text, lexicon)
    burst = dialogue_burst_metrics(metrics["dialogue_lines"])

    direct_density = per_1000(sum_hits(direct_hits), char_count)
    ambiguity_count = sum_hits(hedge_hits) + sum_hits(negation_hits) + sum_hits(correction_hits)
    ambiguity_density = per_1000(ambiguity_count, char_count)
    mundane_density = per_1000(sum_hits(mundane_hits), char_count)
    literary_density = per_1000(sum_hits(literary_hits), char_count)
    checks: list[dict[str, Any]] = []

    def add_check(status: str, label: str, detail: str, values: dict[str, Any] | None = None) -> None:
        checks.append({
            "status": status,
            "label": label,
            "detail": detail,
            "values": values or {},
        })

    confidence_status = "OK" if char_count >= thresholds["min_chars_for_confident_draft"] else "WARN"
    add_check(
        confidence_status,
        "文本长度",
        f"{char_count} 字符；低于 {thresholds['min_chars_for_confident_draft']} 时只适合做初步提示",
        {"char_count": char_count, "min_chars_for_confident_draft": thresholds["min_chars_for_confident_draft"]},
    )

    direct_status = status_for_max(direct_density, thresholds["direct_emotion_per_1000_warn"], thresholds["direct_emotion_per_1000_risk"])
    add_check(
        direct_status,
        "情绪表达直白度",
        f"密度 {direct_density:.2f}/千字；命中：{format_hits(direct_hits)}",
        {"density_per_1000": round(direct_density, 4), "hits": hits_to_json(direct_hits)},
    )

    ambiguity_status = status_for_min(ambiguity_density, thresholds["ambiguity_per_1000_min"], thresholds["ambiguity_per_1000_low"])
    add_check(
        ambiguity_status,
        "含混与自我修正",
        f"密度 {ambiguity_density:.2f}/千字；含混：{format_hits(hedge_hits)}；否定/修正：{format_hits(negation_hits + correction_hits)}",
        {
            "density_per_1000": round(ambiguity_density, 4),
            "hedge_hits": hits_to_json(hedge_hits),
            "negation_correction_hits": hits_to_json(negation_hits + correction_hits),
        },
    )

    mundane_status = status_for_min(mundane_density, thresholds["mundane_object_per_1000_min"], 1)
    add_check(
        mundane_status,
        "日常物件承载",
        f"密度 {mundane_density:.2f}/千字；命中：{format_hits(mundane_hits)}",
        {"density_per_1000": round(mundane_density, 4), "hits": hits_to_json(mundane_hits)},
    )

    dialogue_status = status_for_max(metrics["dialogue_ratio"], thresholds["dialogue_ratio_warn"], thresholds["dialogue_ratio_risk"])
    add_check(
        dialogue_status,
        "对话占比",
        f"{metrics['dialogue_ratio']:.1%}；过高时容易变成解释性辩论",
        {"dialogue_ratio": metrics["dialogue_ratio"]},
    )

    burst_status = status_for_min(
        burst["max_len"],
        thresholds["burst_dialogue_chars_warn"],
        thresholds["burst_dialogue_chars_low"],
    )
    add_check(
        burst_status,
        "过载长台词",
        (
            f"最长台词 {burst['max_len']} 字符，平均 {burst['avg_len']:.1f} 字符；"
            f">=40：{burst['count_ge_40']} 行，>=80：{burst['count_ge_80']} 行，>=200：{burst['count_ge_200']} 行"
        ),
        burst,
    )
    add_check("INFO", "台词长度分布", format_dialogue_bins(burst["length_bins"]), {"length_bins": burst["length_bins"]})

    receiver_count = sum_hits(receiver_hits)
    receiver_status = status_for_min(
        receiver_count,
        thresholds["receiver_misalignment_min"],
        thresholds["receiver_misalignment_low"],
    )
    add_check(
        receiver_status,
        "接收端错位",
        f"命中 {receiver_count} 次：{format_hits(receiver_hits)}",
        {"count": receiver_count, "hits": hits_to_json(receiver_hits)},
    )

    analysis_leak_count = sum_hits(analysis_leak_hits)
    analysis_leak_status = status_for_max(
        analysis_leak_count,
        thresholds["analysis_leak_hits_warn"],
        thresholds["analysis_leak_hits_risk"],
    )
    add_check(
        analysis_leak_status,
        "分析概念泄漏",
        f"命中 {analysis_leak_count} 次：{format_hits(analysis_leak_hits)}",
        {"count": analysis_leak_count, "hits": hits_to_json(analysis_leak_hits)},
    )

    if shimamura["explicit_count"]:
        shimamura_status = status_for_max(
            shimamura["avg_len"],
            thresholds["shimamura_avg_dialogue_warn"],
            thresholds["shimamura_avg_dialogue_risk"],
        )
        shimamura_detail = (
            f"显式岛村台词 {shimamura['explicit_count']} 行，"
            f"平均 {shimamura['avg_len']:.1f} 字符，解释标记 {shimamura['explanation_hits']} 次"
        )
    else:
        shimamura_status = "WARN"
        shimamura_detail = "未检测到 `岛村：` 这类显式说话人标记，无法估算岛村回应长度"
    add_check(shimamura_status, "岛村回应解释化", shimamura_detail, shimamura)

    closure_status = "RISK" if sum_hits(closure_tail_hits) >= thresholds["closure_tail_warn"] else "OK"
    add_check(
        closure_status,
        "结尾封闭化",
        f"末尾 {thresholds['tail_chars']} 字命中：{format_hits(closure_tail_hits)}",
        {"tail_chars": thresholds["tail_chars"], "hits": hits_to_json(closure_tail_hits)},
    )

    literary_status = status_for_max(literary_density, thresholds["literary_per_1000_warn"], thresholds["literary_per_1000_warn"] * 2)
    add_check(
        literary_status,
        "过度文学化风险",
        f"密度 {literary_density:.2f}/千字；命中：{format_hits(literary_hits)}",
        {"density_per_1000": round(literary_density, 4), "hits": hits_to_json(literary_hits)},
    )

    public_metrics = {key: value for key, value in metrics.items() if key != "dialogue_lines"}
    public_metrics["dialogue_burst"] = burst
    return {
        "mode": "draft",
        "file": str(source),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "metrics": public_metrics,
        "checks": checks,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lightweight prompt/draft style evaluator.")
    parser.add_argument("path", type=Path, help="Prompt or draft file to evaluate.")
    parser.add_argument("--mode", choices=["prompt", "draft"], required=True, help="Evaluation mode.")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON, help="Lexicon JSON path.")
    parser.add_argument("--output", type=Path, help="Optional Markdown report output path.")
    parser.add_argument("--json-output", type=Path, help="Optional structured JSON report output path.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.path.exists():
        print(f"error: input file not found: {args.path}", file=sys.stderr)
        return 2
    if not args.lexicon.exists():
        print(f"error: lexicon file not found: {args.lexicon}", file=sys.stderr)
        return 2

    lexicon = load_lexicon(args.lexicon)
    text = read_text(args.path)
    if args.mode == "prompt":
        report = evaluate_prompt(text, args.path, lexicon)
        json_report = {
            "mode": "prompt",
            "file": str(args.path),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "metrics": {key: value for key, value in basic_metrics(text).items() if key != "dialogue_lines"},
            "checks": [],
        }
    else:
        json_report = evaluate_draft_data(text, args.path, lexicon)
        report = render_draft_markdown(json_report, args.path)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(json_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
