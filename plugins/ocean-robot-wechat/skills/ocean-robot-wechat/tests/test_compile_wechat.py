from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "compile_wechat.py"
SPEC = importlib.util.spec_from_file_location("compile_wechat", MODULE_PATH)
assert SPEC and SPEC.loader
compile_wechat = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compile_wechat)


class CompileWechatTests(unittest.TestCase):
    def test_swipe_is_script_free_and_shows_next_edge(self) -> None:
        block = {
            "type": "swipe_gallery",
            "component": "layout.swipe-gallery",
            "images": [
                {"src": "a.jpg", "alt": "A"},
                {"src": "b.jpg", "alt": "B"},
            ],
        }
        result = compile_wechat.render_block(block)
        self.assertIn("overflow-x:auto", result)
        self.assertIn("width:84%", result)
        self.assertNotIn("<script", result)

    def test_deep_blue_is_rejected(self) -> None:
        errors = compile_wechat.validate(
            '<section data-component="x" style="color:#0054A7;overflow-x:auto"></section>' * 6,
            {"blocks": []},
            Path("/tmp/article.json"),
        )
        self.assertTrue(any("deep blue" in item for item in errors))

    def test_complete_minimal_article_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "x.jpg").write_bytes(b"x")
            spec = {
                "blocks": [
                    {"type": "heading", "component": f"layout.h{i}", "number": "01", "title": "标题"}
                    for i in range(5)
                ]
                + [{"type": "swipe_gallery", "component": "layout.swipe-gallery", "images": [{"src": "x.jpg", "alt": "图"}]}]
            }
            inner = compile_wechat.compile_article(spec)
            self.assertEqual([], compile_wechat.validate(inner, spec, root / "article.json"))


if __name__ == "__main__":
    unittest.main()
