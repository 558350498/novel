from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import project_doctor  # noqa: E402


class ProjectDoctorTests(unittest.TestCase):
    def test_data_raw_links_are_optional_local_corpus_refs(self) -> None:
        self.assertTrue(
            project_doctor.target_exists(
                Path("INDEX.md"),
                "data/raw/vol05_第五卷_岛村之刃.txt",
            )
        )


if __name__ == "__main__":
    unittest.main()
