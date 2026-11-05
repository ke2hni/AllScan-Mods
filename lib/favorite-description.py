#!/usr/bin/env python3
"""Add v1.93 editable per-favorite Description support without changing TouchGUI controls."""
from pathlib import Path
import re
import sys


MARKER = "AllScan Mods: Favorites Description editor v1.93."
INI_MARKER = "; AllScan Mods Favorite Description v1.93 "


def replace_once(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"ERROR: Expected {name} exactly once, found {count}; no staged files were written.")
    return text.replace(old, new, 1)


def patch_favs(source: str) -> str:
    if "Favorite Description override data v1.93." not in source:
        source = replace_once(
            source,
            "\t$favsIni = parse_ini_file($favsFile, true);",
            "\t$favsIni = parse_ini_file($favsFile, true);\n"
            "\t// AllScan Mods: Read Description overrides from INI comments without changing ASTDB.\n"
            "\t$favoriteDescriptionOverrides = [];\n"
            "\t$favoriteDescriptionLines = @file($favsFile, FILE_IGNORE_NEW_LINES);\n"
            "\tif(is_array($favoriteDescriptionLines)) {\n"
            "\t\tforeach($favoriteDescriptionLines as $favoriteDescriptionLine) {\n"
            "\t\t\tif(preg_match('/^; AllScan Mods Favorite Description v1\\.93 ([0-9]{4,8}) ([A-Za-z0-9+\\/=]*|-)$/', trim($favoriteDescriptionLine), $favoriteDescriptionMatch) === 1) {\n"
            "\t\t\t\t$favoriteDescription = $favoriteDescriptionMatch[2] === '-' ? '' : base64_decode($favoriteDescriptionMatch[2], true);\n"
            "\t\t\t\tif($favoriteDescription !== false)\n"
            "\t\t\t\t\t$favoriteDescriptionOverrides[$favoriteDescriptionMatch[1]] = $favoriteDescription;\n"
            "\t\t\t}\n\t\t}\n\t}\n",
            "Favorites INI load point",
        )
        source = replace_once(
            source,
            "$favs[$i] = (object)['node'=>$m[0], 'label'=>$label, 'cmd'=>$c];",
            "$favs[$i] = (object)['node'=>$m[0], 'label'=>$label, 'cmd'=>$c, 'descriptionOverride'=>$favoriteDescriptionOverrides[$m[0]] ?? null];",
            "favorite object builder",
        )
        row = "\t\t$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $editName];"
        if row not in source:
            row = "\t\t$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];"
        source = replace_once(
            source,
            row,
            "\t\t// AllScan Mods: Keep the database Description separate from its optional favorite override. Favorite Description override data v1.93.\n"
            "\t\t$f->databaseDescription = $desc;\n"
            "\t\tif($f->descriptionOverride !== null)\n"
            "\t\t\t$desc = $f->descriptionOverride;\n"
            + row,
            "Favorites row builder",
        )
    # The Name-to-Description fallback is suppressed only by v1.92; keep the v1.93 patch
    # independent so explicit Description edits can be introduced without changing v1.92 behavior.
    return source


def patch_index(source: str) -> str:
    if "$newDescription = isset($parms['editdesc'])" not in source:
        source = replace_once(
            source,
            "$newOrder = isset($parms['editorder']) ? trim($parms['editorder']) : '';",
            "$newOrder = isset($parms['editorder']) ? trim($parms['editorder']) : '';\n"
            "$newDescription = isset($parms['editdesc']) ? trim($parms['editdesc']) : '';\n"
            "$useDbDescription = isset($parms['editdescdb']) && $parms['editdescdb'] === '1';",
            "Favorites editor request fields",
        )
        validation = "\t\tif(!preg_match('/^[1-9][0-9]*$/', $newOrder)) {"
        source = replace_once(
            source,
            validation,
            "\t\t// AllScan Mods: Validate optional Description overrides as single-line plain text.\n"
            "\t\tif(!$useDbDescription && (strlen($newDescription) > 120 || !checkAscii($newDescription) ||\n"
            "\t\t\tstrpos($newDescription, '\"') !== false || strpos($newDescription, \"\\r\") !== false ||\n"
            "\t\t\tstrpos($newDescription, \"\\n\") !== false)) {\n"
            "\t\t\t$msg[] = error(\"Description must be 120 plain-text characters or fewer and cannot contain quotes or line breaks.\");\n"
            "\t\t\tbreak;\n\t\t}\n" + validation,
            "Favorites Description validation point",
        )
        write_point = "\t\tif(!writeFileLines($favsFile, $favs, $msg)) {"
        source = replace_once(
            source,
            write_point,
            "\t\t// AllScan Mods: Re-key this favorite's override when its node number changes.\n"
            "\t\t$favs = array_values(array_filter($favs, function($line) use ($originalNode, $node) {\n"
            "\t\t\tif(preg_match('/^; AllScan Mods Favorite Description v1\\.93 ([0-9]{4,8}) ([A-Za-z0-9+\\/=]*|-)$/', trim($line), $match) !== 1)\n"
            "\t\t\t\treturn true;\n"
            "\t\t\treturn $match[1] !== $originalNode && $match[1] !== $node;\n"
            "\t\t}));\n"
            "\t\t// Remove any existing override for this favorite before appending its current mode.\n"
            "\t\t$favs = array_values(array_filter($favs, function($line) use ($node) {\n"
            "\t\t\treturn preg_match('/^; AllScan Mods Favorite Description v1\\.93 ' . preg_quote((string)$node, '/') . ' (?:[A-Za-z0-9+\\/=]*|-)$/', trim($line)) !== 1;\n"
            "\t\t}));\n"
            "\t\tif(!$useDbDescription)\n"
            "\t\t\t$favs[] = '; AllScan Mods Favorite Description v1.93 ' . $node . ' ' . ($newDescription === '' ? '-' : base64_encode($newDescription));\n"
            "\t\telse\n"
            "\t\t\t$msg[] = \"Using AllStarLink database Description for node $node.\";\n"
            + write_point,
            "Favorites Description save point",
        )
        source = replace_once(source, '\t\tcase "Edit Favorite":', '\t\t// ' + MARKER + '\n\t\tcase "Edit Favorite":', "Edit Favorite action")
    elif MARKER not in source:
        # The legacy installer builds this action inline before running this helper.
        # Accept that complete implementation and mark it; reject incomplete fragments.
        required = (
            "isset($parms['editdescdb'])",
            "Description as a comment in favorites.ini",
            "base64_encode($newDescription)",
        )
        if not all(token in source for token in required):
            raise SystemExit("ERROR: Description editor action is partially installed; review the staged index.php.")
        source = replace_once(source, '\tcase "Edit Favorite":', '\t// ' + MARKER + '\n\tcase "Edit Favorite":', "Edit Favorite action")

    if "Favorite Description override cleanup v1.93." not in source:
        delete_case = '\t\tcase "Delete Favorite":'
        cleanup = "\t\t// AllScan Mods: Remove a favorite's private Description override when deleting that node. Favorite Description override cleanup v1.93.\n\t\tcase \"Delete Favorite\":"
        source = replace_once(source, delete_case, cleanup, "Delete Favorite action")
        read_point = "\t\t\tif(($favs = readFileLines($favsFile, $msg, true)) === false)\n\t\t\t\tbreak;"
        read_new = read_point + "\n\t\t\t$favs = array_values(array_filter($favs, function($line) use ($node) {\n\t\t\t\treturn preg_match('/^; AllScan Mods Favorite Description v1\\\\.93 ' . preg_quote((string)$node, '/') . ' (?:[A-Za-z0-9+\\\\/=]*|-)$/', trim($line)) !== 1;\n\t\t\t}));"
        source = replace_once(source, read_point, read_new, "Delete Favorite file read")

    # Add effective and database values to the existing selectable node cell.
    if 'data-fav-description=' not in source or "Favorite Description row data v1.93." not in source:
        row_start = "\t\t$favEditLabel = htmlspecialchars(array_pop($f), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');"
        attr_end = "\t\t\t. '\" onClick=\"selectFavorite(this)\" onDblClick=\"connectNode(\\'connect\\')\"'];"
        if source.count(row_start) != 1 or source.count(attr_end) != 1:
            raise SystemExit("ERROR: Favorites row renderer differs from the supported structure; no staged files were written.")
        data_values = "\n\t\t// AllScan Mods: Attach effective and database Descriptions to the row used by the editor. Favorite Description row data v1.93.\n"
        data_values += "\t\t$favEditDescription = htmlspecialchars((string)($f[3] ?? ''), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');\n"
        data_values += "\t\t$favEditData = $favsData['favs'][$f[0]] ?? null;\n"
        data_values += "\t\t$favDatabaseDescription = htmlspecialchars((string)($favEditData->databaseDescription ?? ''), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');\n"
        data_values += "\t\t$favDescriptionCustom = ($favEditData && $favEditData->descriptionOverride !== null) ? '1' : '0';"
        if 'data-fav-description=' in source:
            existing = re.compile(r"\n\t\t// AllScan Mods: .*?\n\t\t\$favEditDescription = .*?;\n\t\t\$favDescriptionCustom = .*?;", re.DOTALL)
            source, count = existing.subn(data_values, source, count=1)
            if count != 1:
                raise SystemExit("ERROR: Existing Favorites Description row data could not be upgraded safely.")
        else:
            source = source.replace(row_start, row_start + data_values, 1)
        old_attrs = "\t\t. '\" data-fav-description=\"' . $favEditDescription . '\" data-fav-database-description=\"' . $favEditDescription . '\" data-fav-description-custom=\"' . $favDescriptionCustom"
        new_attrs = "\t\t. '\" data-fav-description=\"' . $favEditDescription\n"
        new_attrs += "\t\t. '\" data-fav-database-description=\"' . $favDatabaseDescription\n"
        new_attrs += "\t\t. '\" data-fav-description-custom=\"' . $favDescriptionCustom"
        if old_attrs in source:
            source = replace_once(source, old_attrs, new_attrs, "existing Favorites Description data attributes")
        elif 'data-fav-description=' not in source:
            source = source.replace(attr_end, new_attrs + "\n" + attr_end, 1)
    return source


def patch_view(source: str) -> str:
    if 'id="favoriteEditDescription"' not in source:
        old_fields = (
            '<input type="text" id="favoriteEditLabel" maxlength="50">',
            '<input type="text" id="favoriteEditLabel" maxlength="33">',
            '<input type="text" id="favoriteEditLabel" maxlength="120">',
        )
        old_field = next((field for field in old_fields if field in source), None)
        if old_field is None:
            raise SystemExit("ERROR: Favorites editor label field was not found; no staged files were written.")
        source = replace_once(
            source,
            old_field,
            old_field + '\n'
            '<label for="favoriteEditDescription">Description</label>\n'
            '<textarea id="favoriteEditDescription" maxlength="120" rows="3"></textarea>\n'
            '<div class="favEditDescriptionSource"><label><input type="checkbox" id="favoriteEditUseDatabase" checked onchange="toggleFavoriteDescriptionSource();"> Use AllStarLink database Description</label></div>',
            "Favorites editor Description field",
        )
    if 'id="editdesc"' not in source:
        source = replace_once(
            source,
            '<input type=hidden id="editlabel" name="editlabel" value="">',
            '<input type=hidden id="editlabel" name="editlabel" value="">\n'
            '<input type=hidden id="editdesc" name="editdesc" value="">\n'
            '<input type=hidden id="editdescdb" name="editdescdb" value="1">',
            "Favorites editor Description request fields",
        )
    return source


def patch_js(source: str) -> str:
    if "favoriteDescriptionOverride v1.93" not in source:
        # Legacy-generated editor already contains the same behavior inline.
        legacy_requirements = (
            "favoriteEditDescription",
            "favoriteEditUseDatabase",
            "editdescdb",
            "toggleFavoriteDescriptionSource",
        )
        if all(token in source for token in legacy_requirements):
            source = replace_once(
                source,
                "function selectFavorite(cell) {",
                "// AllScan Mods: Shared Favorites Description editor v1.93.\nfunction selectFavorite(cell) {",
                "legacy Description editor marker",
            )
            return source
        source = replace_once(
            source,
            "\trnode.dataset.favoriteLabel = cell.getAttribute('data-fav-label') || '';",
            "\trnode.dataset.favoriteLabel = cell.getAttribute('data-fav-label') || '';\n"
            "\t// favoriteDescriptionOverride v1.93 keeps database and custom values distinct.\n"
            "\t// AllScan Mods: Load effective and database Description values for the shared editor.\n"
            "\trnode.dataset.favoriteDescription = cell.getAttribute('data-fav-description') || '';\n"
            "\trnode.dataset.favoriteDatabaseDescription = cell.getAttribute('data-fav-database-description') || '';\n"
            "\trnode.dataset.favoriteDescriptionCustom = cell.getAttribute('data-fav-description-custom') || '0';",
            "selected favorite Description data",
        )
        source = replace_once(source, "\tvar orderInput = document.getElementById('favoriteEditOrder');", "\tvar orderInput = document.getElementById('favoriteEditOrder');\n\tvar descriptionInput = document.getElementById('favoriteEditDescription');\n\tvar useDatabaseDescription = document.getElementById('favoriteEditUseDatabase');", "editor Description controls")
        source = replace_once(
            source,
            "\tlabelInput.value = rnode.dataset.favoriteLabel || '';",
            "\tlabelInput.value = rnode.dataset.favoriteLabel || '';\n"
            "\tdescriptionInput.dataset.effectiveValue = rnode.dataset.favoriteDescription || '';\n"
            "\tdescriptionInput.dataset.databaseValue = rnode.dataset.favoriteDatabaseDescription || '';\n"
            "\tdescriptionInput.dataset.customValue = descriptionInput.dataset.effectiveValue;\n"
            "\tuseDatabaseDescription.checked = rnode.dataset.favoriteDescriptionCustom !== '1';\n"
            "\tdescriptionInput.value = descriptionInput.dataset.effectiveValue;\n"
            "\ttoggleFavoriteDescriptionSource();",
            "editor Description prefill",
        )
        toggle = """\n// AllScan Mods: Toggle between live database Description and a saved favorite override.\nfunction toggleFavoriteDescriptionSource() {\n\tvar field = document.getElementById('favoriteEditDescription');\n\tvar useDatabase = document.getElementById('favoriteEditUseDatabase').checked;\n\tif(useDatabase) {\n\t\tif(!field.disabled) field.dataset.customValue = field.value;\n\t\tfield.value = field.dataset.databaseValue || '';\n\t\tfield.disabled = true;\n\t} else {\n\t\tfield.disabled = false;\n\t\tfield.value = field.dataset.customValue || field.dataset.effectiveValue || '';\n\t}\n}\n"""
        source = replace_once(source, "function closeFavoriteEditor() {", toggle + "\nfunction closeFavoriteEditor() {", "editor Description source toggle")
        source = replace_once(source, "\tvar newOrder = document.getElementById('favoriteEditOrder').value.trim();", "\tvar newOrder = document.getElementById('favoriteEditOrder').value.trim();\n\tvar newDescription = document.getElementById('favoriteEditDescription').value.trim();\n\tvar useDatabaseDescription = document.getElementById('favoriteEditUseDatabase').checked;", "submitted Description values")
        source = replace_once(source, "\tif(!/^[1-9][0-9]*$/.test(newOrder)) { alert('Order must be a positive number.'); return false; }", "\tif(!useDatabaseDescription && (newDescription.length > 120 || /[\\\"\\r\\n]/.test(newDescription) || /[^\\x20-\\x7e]/.test(newDescription))) { alert('Description must be 120 plain-text characters or fewer.'); return false; }\n\tif(!/^[1-9][0-9]*$/.test(newOrder)) { alert('Order must be a positive number.'); return false; }", "Description browser validation")
        source = replace_once(source, "\tdocument.getElementById('editlabel').value = newLabel;", "\tdocument.getElementById('editlabel').value = newLabel;\n\tdocument.getElementById('editdesc').value = newDescription;\n\tdocument.getElementById('editdescdb').value = useDatabaseDescription ? '1' : '0';", "Description request values")
    return source


def patch_css(source: str) -> str:
    if "Favorites Description editor styling v1.93." not in source:
        source = source.rstrip() + """\n\n/* AllScan Mods: Favorites Description editor styling v1.93. */\n.favEditPanel {max-height:95vh;overflow-y:auto;}\n.favEditPanel textarea {box-sizing:border-box;width:100%;min-height:64px;resize:vertical;margin:2px 0 5px;padding:5px 7px;border:2px solid hsl(240,40%,60%);font:14px/1.3 Verdana,Arial,Helvetica,sans-serif;}\n.favEditPanel .favEditDescriptionSource label {display:flex;align-items:center;gap:6px;margin:2px 0 5px;font-size:11px;}\n.favEditPanel .favEditDescriptionSource input {width:auto;margin:0;}\n"""
    return source


def main() -> None:
    if len(sys.argv) != 6:
        raise SystemExit("Usage: favorite-description.py INDEX_PHP VIEWUTILS_PHP MAIN_JS FAVSUTILS_PHP MAIN_CSS")
    index_path, view_path, js_path, favs_path, css_path = map(Path, sys.argv[1:])
    # Prepare every changed file in memory first, so a mismatch never partially edits staged inputs.
    changed = {
        index_path: patch_index(index_path.read_text(encoding="utf-8")),
        view_path: patch_view(view_path.read_text(encoding="utf-8")),
        js_path: patch_js(js_path.read_text(encoding="utf-8")),
        favs_path: patch_favs(favs_path.read_text(encoding="utf-8")),
        css_path: patch_css(css_path.read_text(encoding="utf-8")),
    }
    for path, content in changed.items():
        path.write_text(content, encoding="utf-8")
    print("Favorites Description editor and shared TouchGUI Description data are patch-ready.")


if __name__ == "__main__":
    main()
