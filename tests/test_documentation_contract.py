"""Host-side automated tests for multilingual documentation contracts."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import generate_docs  # noqa: E402


HEADER_PATTERNS = {
    "doc_id": re.compile(r"<!--\s*doc-id:\s*([^>]+?)\s*-->"),
    "language": re.compile(r"<!--\s*language:\s*([^>]+?)\s*-->"),
    "revision": re.compile(r"<!--\s*content-revision:\s*([^>]+?)\s*-->"),
}
SECTION_PATTERN = re.compile(r"<!--\s*section:\s*([^>]+?)\s*-->")


class DocumentationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata = json.loads(
            (ROOT / "docs" / "metadata.json").read_text(encoding="utf-8")
        )
        cls.hardware = json.loads(
            (ROOT / "config" / "hardware.json").read_text(encoding="utf-8")
        )
        cls.runtime = json.loads(
            (ROOT / "config" / "runtime.json").read_text(encoding="utf-8")
        )

    def test_three_languages_are_current(self) -> None:
        self.assertEqual(
            set(self.metadata["languages"]),
            {"EN", "PT", "ES"},
        )
        self.assertEqual(self.metadata["canonical_language"], "EN")

    def test_every_registered_document_satisfies_contract(self) -> None:
        for doc_id, spec in self.metadata["documents"].items():
            revision = str(spec["content_revision"])
            required = set(spec["required_sections"])
            for language in self.metadata["languages"]:
                with self.subTest(document=doc_id, language=language):
                    path = ROOT / spec["paths"][language]
                    text = path.read_text(encoding="utf-8")
                    self.assertEqual(
                        HEADER_PATTERNS["doc_id"].search(text).group(1).strip(),
                        doc_id,
                    )
                    self.assertEqual(
                        HEADER_PATTERNS["language"].search(text).group(1).strip(),
                        language,
                    )
                    self.assertEqual(
                        HEADER_PATTERNS["revision"].search(text).group(1).strip(),
                        revision,
                    )
                    sections = {
                        match.group(1).strip()
                        for match in SECTION_PATTERN.finditer(text)
                    }
                    self.assertTrue(required.issubset(sections))

    def test_generated_document_regions_are_exact(self) -> None:
        for relative, language, names in generate_docs.target_files():
            with self.subTest(path=relative, language=language):
                path = ROOT / relative
                actual = path.read_text(encoding="utf-8")
                expected = generate_docs.render_file(
                    path,
                    language,
                    names,
                    self.hardware,
                    self.runtime,
                )
                self.assertEqual(actual, expected)

    def test_generator_covers_every_maintained_language(self) -> None:
        targets = generate_docs.target_files()
        target_languages = {language for _, language, _ in targets}
        self.assertEqual(
            target_languages,
            set(self.metadata["languages"]),
        )


if __name__ == "__main__":
    unittest.main()
