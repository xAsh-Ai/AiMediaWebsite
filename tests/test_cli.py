from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from engine_runtime.cli import main


class CliTests(unittest.TestCase):
    def test_list_sources(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["list-sources"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertTrue(any(item["id"] == "openai-api-changelog" for item in payload))

    def test_run_html(self) -> None:
        html = """
        <html>
          <head><title>OpenAI API changelog</title></head>
          <body>
            <h2>Responses API adds new output options</h2>
            <time datetime="2026-04-01T00:00:00Z">2026-04-01</time>
            <p>Developers can configure output handling for new workloads.</p>
          </body>
        </html>
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = Path(tmpdir) / "sample.html"
            out_dir = Path(tmpdir) / "out"
            html_path.write_text(html, encoding="utf-8")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "run-html",
                        "--source-id",
                        "openai-api-changelog",
                        "--html-file",
                        str(html_path),
                        "--output-dir",
                        str(out_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(buffer.getvalue())
            self.assertEqual(payload["runs"][0]["content_job"]["status"], "approved")
            self.assertTrue((out_dir / "pipeline-output.json").exists())


if __name__ == "__main__":
    unittest.main()
