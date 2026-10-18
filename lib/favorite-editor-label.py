#!/usr/bin/env python3
"""Pass the original favorite label to the main-page edit dialog."""

from pathlib import Path
import sys


MARKER = "// AllScan Mods: Use original favorite label in editor v1.20."
LEGACY_MARKER = "// AllScan Mods: Preserve full favorite name for editor v1.19."
EDITOR_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $f->label];"
LEGACY_ROW = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];"
UPSTREAM_ROW = EDITOR_ROW
TRUNCATION = "\t\tif(strlen($name) > 33)"
OLD_ROWS = (
    "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];",
    "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP];",
)


def patch(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    if MARKER in source:
        if source.count(MARKER) != 1 or source.count(EDITOR_ROW) != 1:
            raise SystemExit("ERROR: Favorite-label marker is inconsistent; file left unchanged.")
        return False

    if LEGACY_MARKER in source:
        if (source.count(LEGACY_MARKER) != 1 or source.count(LEGACY_ROW) != 1
                or source.count("$editName = $name;") != 1):
            raise SystemExit("ERROR: Existing v1.19 favorite-label patch is inconsistent; file left unchanged.")
        source = source.replace(LEGACY_MARKER, MARKER, 1)
        source = source.replace("$editName = $name;\n", "", 1)
        source = source.replace(LEGACY_ROW, EDITOR_ROW, 1)
        path.write_text(source, encoding="utf-8")
        return True
    if source.count(UPSTREAM_ROW) == 1:
        return False
    if source.count(LEGACY_MARKER) > 1 or source.count(LEGACY_ROW) > 1 or source.count(UPSTREAM_ROW) > 1:
        raise SystemExit("ERROR: Favorite-label row is duplicated; file left unchanged.")

    matches = [row for row in OLD_ROWS if source.count(row) == 1]
    if len(matches) != 1:
        raise SystemExit(
            "ERROR: Expected exactly one recognized Favorites row builder; file left unchanged."
        )

    if source.count(TRUNCATION) != 1:
        raise SystemExit("ERROR: Expected the name-shortening point exactly once; file left unchanged.")

    source = source.replace(
        TRUNCATION,
        MARKER + "\n" + TRUNCATION,
        1,
    )
    source = source.replace(matches[0], EDITOR_ROW, 1)
    path.write_text(source, encoding="utf-8")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: favorite-editor-label.py <staged-index-or-favsUtils.php>")
    try:
        changed = patch(Path(sys.argv[1]))
    except OSError as error:
        raise SystemExit(f"ERROR: Could not patch favorite label source: {error}") from error
    print("Favorite editor label patch-ready." if changed else "Favorite editor label already present.")
