#!/usr/bin/env python3
"""Check the shared, call-sign-free 33-character editor patch and migration."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "lib/favorite-editor-label.py"

INDEX = '''<?php
			if($newLabel === '' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||
				strpos($newLabel, '"') !== false) {
				$msg[] = error("Friendly label must be 1 to 120 plain-text characters and "
					. "cannot contain double quotes or line breaks.");
}
'''
VIEW = '''<label for="favoriteEditLabel">Friendly Name/Label</label>
<input type="text" id="favoriteEditLabel" maxlength="120">
'''
JS = '''function submitFavoriteEdit() {
    var newLabel = document.getElementById('favoriteEditLabel').value.trim();
	if(!newLabel || newLabel.length > 120 || /["\\r\\n]/.test(newLabel)) {
		alert('Friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');
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
		// Name is derived from favorites file text, but if that contained only redundant information to what
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


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="favorite-editor-v137-") as folder:
        temp = Path(folder)
        files = {
            "index.php": INDEX,
            "viewUtils.php": VIEW,
            "main.js": JS,
            "favsUtils.php": FAVS,
        }
        for name, text in files.items():
            (temp / name).write_text(text, encoding="utf-8")
        args = [str(temp / name) for name in files]
        subprocess.run(["python3", str(PATCHER), *args], check=True)
        after_first = {name: (temp / name).read_bytes() for name in files}
        subprocess.run(["python3", str(PATCHER), *args], check=True)
        assert after_first == {name: (temp / name).read_bytes() for name in files}, "patch is not idempotent"

        index = (temp / "index.php").read_text(encoding="utf-8")
        view = (temp / "viewUtils.php").read_text(encoding="utf-8")
        js = (temp / "main.js").read_text(encoding="utf-8")
        favs = (temp / "favsUtils.php").read_text(encoding="utf-8")
        assert "strlen($newLabel) > 33" in index and "$newLabel === ''" not in index
        assert 'maxlength="33"' in view and "Up to 33 characters" in view
        assert "newLabel.length > 33" in js and "!newLabel" not in js
        assert "$editName = substr($name, 0, 33);" in favs
        assert "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];" in favs
        assert "&hellip;" not in after_first["viewUtils.php"].decode()
    print("PASS: editor patch uses one shared, callsign-free label capped at 33 characters.")
    print("PASS: empty labels remain valid for callsign-only favorites; server and browser enforce the same maximum.")
    print("PASS: helper is idempotent and preserves the existing main-table name field.")


if __name__ == "__main__":
    main()
