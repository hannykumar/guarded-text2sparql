"""Inline the demo data into the page, so the result is one file that needs no server."""
from pathlib import Path

data = Path("docs/demo_data.json").read_text()
page = Path("docs/demo.html").read_text()
# a literal </script> inside the JSON would close the tag early
out = Path("docs/demo_built.html")
out.write_text(page.replace("__DEMO_DATA__", data.replace("</", "<\\/")))
print(f"{out} ({round(len(out.read_text()) / 1024)} KB)")
