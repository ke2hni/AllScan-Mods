#!/usr/bin/env python3
"""Regression checks for v1.92 Favorites Name display and column sizing."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_FALLBACK = """\t\t// Many nodes in astdb have descriptive text in the name field but then a blank description. In this
\t\t// case, to make the table look more consistent and clean move any text from the name (except for the
\t\t// call sign) to the description column
\t\tif(empty($desc) && strlen($name) > strlen($call) && strlen($call) > 2) {
\t\t\tif(strpos($name, $call) === 0) {
\t\t\t\t$desc = trim(substr($name, strlen($call)), $trimchars);
\t\t\t\t$name = $call;
\t\t\t}
\t\t}"""


def main() -> None:
    for filename in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        source = (ROOT / filename).read_text(encoding="utf-8")
        assert "apply_favorites_name_auto_width_live" in source
        assert "apply_favorite_editor_label_live\n    apply_favorites_name_auto_width_live" in source
        assert "before-favorites-name-v1.92-" in source
        assert "Keep the complete callsign-prefixed Favorites Name visible v1.90." in source
        assert "determine its column width v1.90." in source
        assert "Keep custom Favorites Names in the Name column v1.92." in source
        assert "Description remains sourced from AllStarLink database data." in source
        assert "TouchGUI activity colors mod version: v1.92" in source

        # Execute the same embedded patcher used by each installer on the upstream fallback.
        match = re.search(r"python3 - \"\$work_dir/favsUtils\.php\" \"\$work_dir/main\.css\" <<'PY'\n(.*?)\nPY", source, re.S)
        assert match, f"Favorites Name patcher missing from {filename}"
        with tempfile.TemporaryDirectory(prefix="favs-name-v192-") as folder:
            temp = Path(folder)
            favs = temp / "favsUtils.php"
            css = temp / "main.css"
            favs.write_text("\t\t// Shorten long names\n\t\tif(strlen($name) > 33)\n\t\t\t$name = substr($name, 0, 33) . '&hellip;';\n" + UPSTREAM_FALLBACK + "\n", encoding="utf-8")
            css.write_text("td {\nmax-width:32em;\n}\n", encoding="utf-8")
            patcher = "import sys\n" + match.group(1)
            subprocess.run(["python3", "-c", patcher, str(favs), str(css)], check=True)
            updated = favs.read_text(encoding="utf-8")
            assert "Keep custom Favorites Names in the Name column v1.92." in updated
            assert "if(empty($desc) && strlen($name)" not in updated
            assert "$desc = trim(substr($name" not in updated
            assert "substr($name, 0, 33)" not in updated
            assert "Description remains sourced from AllStarLink database data." in updated
            subprocess.run(["python3", "-c", patcher, str(favs), str(css)], check=True)

    assert "AllScan Mods v1.92" in (ROOT / "README.md").read_text(encoding="utf-8")
    print("PASS: both installers keep a custom favorite label in Name and leave Description database-sourced.")
    print("PASS: full Favorites Names remain visible, Name auto-width remains enabled, and repeat patching is safe.")


if __name__ == "__main__":
    main()
