#!/usr/bin/env python3
"""Keep the main Favorites editor on one call-sign-free, 33-character label."""
from pathlib import Path
import sys


def replace_once(text: str, old: str, new: str, description: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"ERROR: Expected {description} exactly once, found {count}. "
            "No staged files were written."
        )
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "Usage: favorite-editor-label.py INDEX_PHP VIEWUTILS_PHP MAIN_JS FAVSUTILS_PHP"
        )
    index_path, view_path, js_path, favs_path = map(Path, sys.argv[1:])
    index = index_path.read_text(encoding="utf-8")
    view = view_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")
    favs = favs_path.read_text(encoding="utf-8")

    marker = "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.38. -->"
    old_marker = "// AllScan Mods: 33-character call-sign-free Favorites editor label v1.37."
    fav_marker = "// AllScan Mods: Call-sign-free Favorites editor value v1.38."
    old_fav_marker = "// AllScan Mods: Call-sign-free Favorites editor value v1.37."
    if marker in view and fav_marker in favs:
        print("Favorites editor label changes are already applied.")
        return
    if old_marker in view and old_fav_marker in favs:
        view = view.replace(old_marker, marker, 1)
        favs = favs.replace(old_fav_marker, fav_marker, 1)
        view_path.write_text(view, encoding="utf-8")
        favs_path.write_text(favs, encoding="utf-8")
        print("Favorites editor marker updated without changing the label behavior.")
        return
    if marker in view or fav_marker in favs or old_marker in view or old_fav_marker in favs:
        raise SystemExit("ERROR: Existing Favorites editor label patch is incomplete; no files were written.")

    # The editor gets the cleaned favorite text before AllScan adds the callsign
    # for the main-table display and before its 33-character table truncation.
    insertion = "\t\t// Name is derived from favorites file text, but if that contained only redundant information to what\n"
    if favs.count(insertion) != 1:
        raise SystemExit("ERROR: Expected the v1.04 favorite-name cleanup block exactly once.")
    favs = favs.replace(
        insertion,
        insertion
        + "\t\t// AllScan Mods: Call-sign-free Favorites editor value v1.38.\n"
        + "\t\t$editName = substr($name, 0, 33);\n",
        1,
    )
    favs = replace_once(
        favs,
        "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];",
        "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];",
        "the v1.04 Favorites editor data value",
    )

    view = replace_once(
        view,
        '<input type="text" id="favoriteEditLabel" maxlength="120">',
        '<input type="text" id="favoriteEditLabel" maxlength="33">\n'
        '<small>Up to 33 characters. The callsign is added automatically.</small>',
        "the v1.04 Favorites editor label field",
    )
    view = view.replace(
        '<label for="favoriteEditLabel">Friendly Name/Label</label>',
        marker + "\n<label for=\"favoriteEditLabel\">Friendly Name/Label</label>",
        1,
    )

    old_validation = '''\tif(!newLabel || newLabel.length > 120 || /["\\r\\n]/.test(newLabel)) {
\t\talert('Friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');'''
    new_validation = '''\tif(newLabel.length > 33 || /["\\r\\n]/.test(newLabel)) {
\t\talert('Friendly label must be no more than 33 characters and cannot contain double quotes or line breaks.');'''
    js = replace_once(js, old_validation, new_validation, "the v1.04 editor validation")

    old_server_validation = '''\t\t\tif($newLabel === '' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||'''
    new_server_validation = '''\t\t\tif(strlen($newLabel) > 33 || !checkAscii($newLabel) ||'''
    index = replace_once(index, old_server_validation, new_server_validation, "the v1.04 server-side label validation")
    index = replace_once(
        index,
        'Friendly label must be 1 to 120 plain-text characters and ',
        'Friendly label must be no more than 33 plain-text characters and ',
        "the v1.04 label validation message",
    )

    # Write only after all four source structures have passed exact-match checks.
    favs_path.write_text(favs, encoding="utf-8")
    view_path.write_text(view, encoding="utf-8")
    js_path.write_text(js, encoding="utf-8")
    index_path.write_text(index, encoding="utf-8")
    print("Favorites editor label patch-ready.")


if __name__ == "__main__":
    main()
