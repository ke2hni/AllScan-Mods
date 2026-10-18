#!/usr/bin/env python3
"""Keep the shared Favorites editor label call-sign-free and easy to read."""
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
    if len(sys.argv) != 6:
        raise SystemExit(
            "Usage: favorite-editor-label.py INDEX_PHP VIEWUTILS_PHP MAIN_JS FAVSUTILS_PHP MAIN_CSS"
        )
    index_path, view_path, js_path, favs_path, css_path = map(Path, sys.argv[1:])
    index = index_path.read_text(encoding="utf-8")
    view = view_path.read_text(encoding="utf-8")
    js = js_path.read_text(encoding="utf-8")
    favs = favs_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")

    view_marker = "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.40. -->"
    view_markers_old = (
        "// AllScan Mods: 33-character call-sign-free Favorites editor label v1.37.",
        "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.38. -->",
        "<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.39. -->",
    )
    fav_marker = "// AllScan Mods: Call-sign-free Favorites editor value v1.40."
    fav_markers_old = (
        "// AllScan Mods: Call-sign-free Favorites editor value v1.37.",
        "// AllScan Mods: Call-sign-free Favorites editor value v1.38.",
        "// AllScan Mods: Call-sign-free Favorites editor value v1.39.",
    )
    css_marker = "/* AllScan Mods: Favorites editor call-sign hint v1.40. */"
    old_css_marker = "/* AllScan Mods: Favorites editor call-sign hint v1.39. */"
    hint_markup = '<div class="favoriteEditHint">The callsign is added automatically.</div>'
    hint_style = (
        ".favEditPanel .favoriteEditHint {margin:2px 0 6px;color:#fff;"
        "font:12px/1.25 Verdana,Arial,Helvetica,sans-serif;font-weight:normal;}"
    )

    if (view_marker in view and fav_marker in favs and css_marker in css
            and hint_markup in view and hint_style in css):
        print("Favorites editor label and guidance are already applied.")
        return

    # Keep the call-sign-free editor value on the pre-callsign name and before
    # AllScan's existing 33-character table truncation.
    insertion = "\t\t// Name is derived from favorites file text, but if that contained only redundant information to what\n"
    value_marker_present = any(marker in favs for marker in fav_markers_old) or fav_marker in favs
    if not value_marker_present:
        if favs.count(insertion) != 1:
            raise SystemExit("ERROR: Expected the v1.04 favorite-name cleanup block exactly once.")
        favs = favs.replace(
            insertion,
            insertion + "\t\t" + fav_marker + "\n\t\t$editName = substr($name, 0, 33);\n",
            1,
        )
    else:
        for old in fav_markers_old:
            if old in favs:
                favs = replace_once(favs, old, fav_marker, "the previous editor value marker")
    old_fav_row = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];"
    new_fav_row = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];"
    if old_fav_row in favs:
        favs = replace_once(favs, old_fav_row, new_fav_row, "the v1.04 Favorites editor data value")
    elif new_fav_row not in favs:
        raise SystemExit("ERROR: Existing Favorites editor data structure is unexpected.")

    # Replace stock field/help markup or migrate the earlier v1.37/v1.38 help.
    old_field = '<input type="text" id="favoriteEditLabel" maxlength="120">'
    if old_field in view:
        view = replace_once(view, old_field,
                            '<input type="text" id="favoriteEditLabel" maxlength="33">',
                            "the v1.04 Favorites editor label field")
    elif '<input type="text" id="favoriteEditLabel" maxlength="33">' not in view:
        raise SystemExit("ERROR: Existing Favorites editor label field is unexpected.")
    old_help = '<small>Up to 33 characters. The callsign is added automatically.</small>'
    if old_help in view:
        view = replace_once(view, old_help, hint_markup, "the previous Favorites editor guidance")
    elif '<small>The callsign is added automatically.</small>' in view:
        view = replace_once(view, '<small>The callsign is added automatically.</small>', hint_markup,
                            "the previous Favorites editor guidance")
    elif hint_markup not in view:
        view = replace_once(
            view,
            '<input type="text" id="favoriteEditLabel" maxlength="33">',
            '<input type="text" id="favoriteEditLabel" maxlength="33">\n' + hint_markup,
            "the v1.04 Favorites editor guidance insertion point",
        )

    label_marker_old = next((marker for marker in view_markers_old if marker in view), None)
    if view_marker not in view:
        if label_marker_old:
            view = replace_once(view, label_marker_old, view_marker, "the previous editor marker")
        else:
            view = replace_once(view,
                                '<label for="favoriteEditLabel">Friendly Name/Label</label>',
                                view_marker + "\n<label for=\"favoriteEditLabel\">Friendly Name/Label</label>",
                                "the v1.04 Favorites editor label")

    old_validation = '''\tif(!newLabel || newLabel.length > 120 || /["\\r\\n]/.test(newLabel)) {
\t\talert('Friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');'''
    new_validation = '''\tif(newLabel.length > 33 || /["\\r\\n]/.test(newLabel)) {
\t\talert('Friendly label must be no more than 33 characters and cannot contain double quotes or line breaks.');'''
    if old_validation in js:
        js = replace_once(js, old_validation, new_validation, "the v1.04 editor validation")
    elif "newLabel.length > 33" not in js:
        raise SystemExit("ERROR: Existing browser-side Favorites validation is unexpected.")

    old_server_validation = '''\t\t\tif($newLabel === '' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||'''
    new_server_validation = '''\t\t\tif(strlen($newLabel) > 33 || !checkAscii($newLabel) ||'''
    if old_server_validation in index:
        index = replace_once(index, old_server_validation, new_server_validation,
                             "the v1.04 server-side label validation")
    elif "strlen($newLabel) > 33" not in index:
        raise SystemExit("ERROR: Existing server-side Favorites validation is unexpected.")
    old_message = 'Friendly label must be 1 to 120 plain-text characters and '
    new_message = 'Friendly label must be no more than 33 plain-text characters and '
    if old_message in index:
        index = replace_once(index, old_message, new_message, "the v1.04 label validation message")

    if css_marker not in css:
        old_hint_style = (
            ".favEditPanel .favoriteEditHint {margin:2px 0 6px;color:#edc;"
            "font-size:13px;font-weight:bold;line-height:1.25;}"
        )
        if old_css_marker in css:
            css = replace_once(css, old_css_marker, css_marker, "the v1.39 guidance style marker")
            css = replace_once(css, old_hint_style, hint_style, "the v1.39 bold guidance style")
        elif ".favEditPanel .favoriteEditHint" in css:
            raise SystemExit("ERROR: Existing Favorites guidance style is unexpected.")
        else:
            css = css.rstrip() + "\n\n" + css_marker + "\n" + hint_style + "\n"
    elif hint_style not in css:
        raise SystemExit("ERROR: Existing v1.40 Favorites guidance style is incomplete.")

    # Only write after each upstream structure has been recognized.
    favs_path.write_text(favs, encoding="utf-8")
    view_path.write_text(view, encoding="utf-8")
    js_path.write_text(js, encoding="utf-8")
    index_path.write_text(index, encoding="utf-8")
    css_path.write_text(css, encoding="utf-8")
    print("Favorites editor label and readable guidance are patch-ready.")


if __name__ == "__main__":
    main()
