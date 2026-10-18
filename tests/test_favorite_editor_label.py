#!/usr/bin/env python3
"""Regression checks for the original favorite label used by the edit dialog."""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "lib" / "favorite-editor-label.py"
MARKER = "Use original favorite label in editor v1.20."
EDITOR_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $f->label];"
UPSTREAM_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $f->label];"
OLD_MOD_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];"
V119_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];"


def run_patch(path: Path, success: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["python3", str(PATCHER), str(path)], text=True, capture_output=True)
    assert (result.returncode == 0) == success, result.stderr
    return result


def main() -> None:
    for installer in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        text = (ROOT / installer).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.20" in text
        assert "FAVORITE_LABEL_PATCH" in text
        assert "apply_favorite_label_live" in text
        assert "Use original favorite label in editor v1.20." in text
        assert "NBSP, NBSP, $f->label];' \"$favorite_label_stage\"" in text

    with tempfile.TemporaryDirectory(prefix="favorite-label-test-") as temp:
        temp = Path(temp)
        source = temp / "favsUtils.php"
        source.write_text(
            "<?php\n"
            "$name = substr($name, 0, 33) . '&hellip;';\n"
            "\t\tif(strlen($name) > 33)\n"
            "$tableName = $name;\n"
            + OLD_MOD_ROW
            + "\n",
            encoding="utf-8",
        )
        original_display = "$name = substr($name, 0, 33) . '&hellip;';"
        run_patch(source)
        patched = source.read_text(encoding="utf-8")
        assert original_display in patched, "The main-table truncation behavior changed."
        assert patched.count(MARKER) == 1
        assert patched.count(EDITOR_ROW) == 1
        assert "$editName = $name;" not in patched
        assert "$tableName = $name;" in patched, "The visible table name source changed."
        first = source.read_bytes()
        run_patch(source)
        assert source.read_bytes() == first, "Reapplying the fix changed the file."

        v119 = temp / "v119.php"
        v119.write_text(
            "<?php\n"
            "// AllScan Mods: Preserve full favorite name for editor v1.19.\n"
            "$editName = $name;\n"
            "\t\tif(strlen($name) > 33)\n"
            + V119_ROW
            + "\n",
            encoding="utf-8",
        )
        run_patch(v119)
        migrated = v119.read_text(encoding="utf-8")
        assert MARKER in migrated
        assert EDITOR_ROW in migrated
        assert "$editName" not in migrated

        stock = temp / "stock.php"
        stock.write_text("<?php\n\t\tif(strlen($name) > 33)\n$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP];\n", encoding="utf-8")
        run_patch(stock)
        assert EDITOR_ROW in stock.read_text(encoding="utf-8")

        upstream = temp / "upstream.php"
        upstream.write_text("<?php\n" + UPSTREAM_ROW + "\n", encoding="utf-8")
        upstream_before = upstream.read_bytes()
        run_patch(upstream)
        assert upstream.read_bytes() == upstream_before, "An upstream implementation was rewritten."

        ambiguous = temp / "ambiguous.php"
        ambiguous.write_text("<?php\n" + OLD_MOD_ROW + "\n" + OLD_MOD_ROW + "\n", encoding="utf-8")
        before = ambiguous.read_bytes()
        run_patch(ambiguous, success=False)
        assert ambiguous.read_bytes() == before, "An unrecognized file was modified."

    print("PASS: main-table truncation stays intact while the editor receives the original label.")
    print("PASS: v1.19 migration, stock row, upstream detection, idempotence, and ambiguity protection.")


if __name__ == "__main__":
    main()
