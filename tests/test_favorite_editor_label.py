#!/usr/bin/env python3
"""Regression checks for the Favorites editor label and node suffix."""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "lib" / "favorite-editor-label.py"
MARKER = "Use complete favorite name in editor v1.21."
EDIT_NAME = "$editName = str_replace('&hellip;', '', $name);"
EDITOR_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];"
V119_MARKER = "// AllScan Mods: Preserve full favorite name for editor v1.19."
V119_ROW = EDITOR_ROW
V120_MARKER = "// AllScan Mods: Use original favorite label in editor v1.20."
V120_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $f->label];"
OLD_MOD_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];"


def run_patch(path: Path, success: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["python3", str(PATCHER), str(path)], text=True, capture_output=True)
    assert (result.returncode == 0) == success, result.stderr
    return result


def main() -> None:
    for installer in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        text = (ROOT / installer).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.22" in text
        assert "FAVORITE_LABEL_PATCH" in text
        assert "apply_favorite_label_live" in text
        assert MARKER in text
        assert "\\$editName = str_replace('&hellip;', '', \\$name);" in text
        assert EDITOR_ROW in text

    with tempfile.TemporaryDirectory(prefix="favorite-label-test-") as temp:
        temp = Path(temp)
        source = temp / "favsUtils.php"
        source.write_text(
            "<?php\n"
            "$name = str_replace([$f->node, $call, $desc, $loc], ' ', $f->label);\n"
            "\t\tif(strlen($name) > 33)\n"
            + OLD_MOD_ROW
            + "\n",
            encoding="utf-8",
        )
        run_patch(source)
        patched = source.read_text(encoding="utf-8")
        assert patched.count(MARKER) == 1
        assert patched.count(EDIT_NAME) == 1
        assert patched.count(EDITOR_ROW) == 1
        assert "\t\t" + EDIT_NAME + "\n\t\tif(strlen($name) > 33)" in patched
        assert "str_replace([$f->node, $call, $desc, $loc]" in patched
        assert "if(strlen($name) > 33)" in patched, "The visible table name shortening changed."
        first = source.read_bytes()
        run_patch(source)
        assert source.read_bytes() == first, "Reapplying the fix changed the file."

        v119 = temp / "v119.php"
        v119.write_text(
            "<?php\n" + V119_MARKER + "\n$editName = $name;\n"
            "\t\tif(strlen($name) > 33)\n" + V119_ROW + "\n",
            encoding="utf-8",
        )
        run_patch(v119)
        migrated_v119 = v119.read_text(encoding="utf-8")
        assert MARKER in migrated_v119 and EDIT_NAME in migrated_v119
        assert EDITOR_ROW in migrated_v119

        v120 = temp / "v120.php"
        v120.write_text(
            "<?php\n" + V120_MARKER + "\n\t\tif(strlen($name) > 33)\n"
            + V120_ROW + "\n",
            encoding="utf-8",
        )
        run_patch(v120)
        migrated_v120 = v120.read_text(encoding="utf-8")
        assert MARKER in migrated_v120 and EDIT_NAME in migrated_v120
        assert EDITOR_ROW in migrated_v120
        assert "\t\t" + EDIT_NAME + "\n\t\tif(strlen($name) > 33)" in migrated_v120
        assert V120_ROW not in migrated_v120

        upstream = temp / "upstream.php"
        upstream.write_text("<?php\n" + V120_ROW + "\n", encoding="utf-8")
        upstream_before = upstream.read_bytes()
        run_patch(upstream)
        assert upstream.read_bytes() == upstream_before, "An upstream implementation was rewritten."

        ambiguous = temp / "ambiguous.php"
        ambiguous.write_text("<?php\n" + OLD_MOD_ROW + "\n" + OLD_MOD_ROW + "\n", encoding="utf-8")
        before = ambiguous.read_bytes()
        run_patch(ambiguous, success=False)
        assert ambiguous.read_bytes() == before, "An unrecognized file was modified."

    print("PASS: editor uses the node-cleaned name without the display ellipsis; table shortening stays unchanged.")
    print("PASS: v1.19/v1.20 migration, upstream detection, idempotence, and ambiguity protection.")


if __name__ == "__main__":
    main()
