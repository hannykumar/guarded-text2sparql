"""Inline the demo data into the page, so the result is one file that needs no server.

The payload is written as pure ASCII (\\uXXXX escapes) and the page itself avoids
non-ASCII characters, so the file renders correctly no matter what character set the
server claims. A plain `python -m http.server` sends none, and accented names in the
data were arriving as mojibake.
"""
import json
from pathlib import Path

data = json.loads(Path("docs/demo_data.json").read_text())
payload = json.dumps(data, separators=(",", ":"), ensure_ascii=True).replace("</", "<\\/")
page = Path("docs/demo.html").read_text()
out = Path("docs/demo_built.html")
out.write_text(page.replace("__DEMO_DATA__", payload), encoding="ascii", errors="xmlcharrefreplace")
print(f"{out} ({round(len(out.read_text()) / 1024)} KB)")
