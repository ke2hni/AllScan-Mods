#!/usr/bin/env python3
"""Check the shared Favorites label, regular-weight hint, and prior-version migrations."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "lib/favorite-editor-label.py"

INDEX = '''<?php
\t\t\tif($newLabel === '' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||
\t\t\t\tstrpos($newLabel, '"') !== false) {
\t\t\t\t$msg[] = error("Friendly label must be 1 to 120 plain-text characters and "
\t\t\t\t\t. "cannot contain double quotes or line breaks.");
}
'''
VIEW = '''<label for="favoriteEditLabel">Friendly Name/Label</label>
<input type="text" id="favoriteEditLabel" maxlength="120">
'''
JS = '''function submitFavoriteEdit() {
    var newLabel = document.getElementById('favoriteEditLabel').value.trim();
\tif(!newLabel || newLabel.length > 120 || /["\\r\\n]/.test(newLabel)) {
\t\talert('Friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');
        return false;
    }
}
'''
FAVS = '''<?php
function buildFavList($favs) {
    $name = 'Coast Repeater';
    // Fix common misspellings
    foreach(['name', 'desc'] as $var)
        $$var = str_replace(['mhz', 'MHZ', 'hz'], ['MHz', 'MHz', 'Hz'], $$var);
\t\t// Name is derived from favorites file text, but if that contained only redundant information to what
    // was in astdb and is thus now blank, use the call sign
    if(!$name)
        $name = $call;
    elseif(strpos($name, $call) === false && $call !== '-')
        $name = $call . ' ' . $name;
    if(strlen($name) > 33)
        $name = substr($name, 0, 33) . '&hellip;';
    $favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];
}
'''
CSS = '''body, textarea, input, select { font:12px/1.25 Verdana,Arial,Helvetica,sans-serif; }
'''


def write_files(temp: Path, content: dict[str, str]) -> None:
    for name, text in content.items():
        (temp / name).write_text(text, encoding="utf-8")


def run_patcher(temp: Path) -> None:
    args = [str(temp / name) for name in
            ("index.php", "viewUtils.php", "main.js", "favsUtils.php", "main.css")]
    subprocess.run(["python3", str(PATCHER), *args], check=True)


def main() -> None:
    base = {"index.php": INDEX, "viewUtils.php": VIEW, "main.js": JS,
            "favsUtils.php": FAVS, "main.css": CSS}
    with tempfile.TemporaryDirectory(prefix="favorite-editor-v140-") as folder:
        temp = Path(folder)
        write_files(temp, base)
        run_patcher(temp)
        current = {name: (temp / name).read_text(encoding="utf-8") for name in base}
        first_bytes = {name: (temp / name).read_bytes() for name in base}
        run_patcher(temp)
        assert first_bytes == {name: (temp / name).read_bytes() for name in base}, "patch is not idempotent"

        view = current["viewUtils.php"]
        assert 'maxlength="33"' in view and 'class="favoriteEditHint">The callsign is added automatically.' in view
        assert "Up to 33 characters." not in view
        assert "// AllScan Mods: 33-character" not in view
        assert "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.40. -->" in view
        assert "font:12px/1.25 Verdana,Arial,Helvetica,sans-serif;font-weight:normal" in current["main.css"]
        assert "font-size:13px" not in current["main.css"]
        assert "font-weight:bold" not in current["main.css"]
        assert "strlen($newLabel) > 33" in current["index.php"] and "$newLabel === ''" not in current["index.php"]
        assert "newLabel.length > 33" in current["main.js"] and "!newLabel" not in current["main.js"]
        assert "$editName = substr($name, 0, 33);" in current["favsUtils.php"]
        assert "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];" in current["favsUtils.php"]

        # Upgrade previous marker/help combinations without altering label behavior.
        for old_version, old_marker, old_help in (
            ("1.37", "// AllScan Mods: 33-character call-sign-free Favorites editor label v1.37.",
             "<small>Up to 33 characters. The callsign is added automatically.</small>"),
            ("1.38", "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.38. -->",
             "<small>Up to 33 characters. The callsign is added automatically.</small>"),
            ("1.39", "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.39. -->",
             '<div class="favoriteEditHint">The callsign is added automatically.</div>'),
        ):
            legacy = dict(current)
            legacy["viewUtils.php"] = view.replace(
                "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.39. -->",
                old_marker, 1).replace(
                '<div class="favoriteEditHint">The callsign is added automatically.</div>',
                old_help, 1)
            legacy["favsUtils.php"] = current["favsUtils.php"].replace(
                "Call-sign-free Favorites editor value v1.39.",
                f"Call-sign-free Favorites editor value v{old_version}.", 1)
            legacy_css = CSS
            if old_version == "1.39":
                legacy_css += (
                    "\n/* AllScan Mods: Favorites editor call-sign hint v1.39. */\n"
                    ".favEditPanel .favoriteEditHint {margin:2px 0 6px;color:#edc;"
                    "font-size:13px;font-weight:bold;line-height:1.25;}\n"
                )
            legacy["main.css"] = legacy_css
            write_files(temp, legacy)
            before = {name: (temp / name).read_bytes() for name in ("index.php", "main.js")}
            run_patcher(temp)
            migrated_view = (temp / "viewUtils.php").read_text(encoding="utf-8")
            assert "// AllScan Mods: 33-character" not in migrated_view
            if old_version != "1.39":
                assert old_help not in migrated_view
            assert "Up to 33 characters." not in migrated_view
            assert '<div class="favoriteEditHint">The callsign is added automatically.</div>' in migrated_view
            assert "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.40. -->" in migrated_view
            migrated_css = (temp / "main.css").read_text(encoding="utf-8")
            assert "font:12px/1.25 Verdana,Arial,Helvetica,sans-serif;font-weight:normal" in migrated_css
            assert "font-size:13px" not in migrated_css and "font-weight:bold" not in migrated_css
            assert (temp / "index.php").read_bytes() == before["index.php"]
            assert (temp / "main.js").read_bytes() == before["main.js"]

    print("PASS: one shared call-sign-free label is capped at 33 characters.")
    print("PASS: the hint uses the normal 12px font and weight, with increased contrast and no length phrase.")
    print("PASS: clean install, repeat install, and v1.37-v1.39 editor migrations.")


if __name__ == "__main__":
    main()
