#!/usr/bin/env python3
"""Regression checks for editable, node-associated TouchGUI card labels."""

from pathlib import Path
import subprocess
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / "lib" / "touchgui-favorite-labels.py"
ACTIVITY_PATCHER = ROOT / "lib" / "touchgui-activity.py"


def write(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")


def main() -> None:
    for installer in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        text = (ROOT / installer).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.32" in text
        assert "apply_touchgui_favorite_labels_live" in text
        assert "TOUCHGUI_FAVORITE_LABEL_PATCH" in text
        assert 'Favorites editor helper text v1.25.' in text
        assert 'Favorites editor field labels v1.29.' in text
        assert "before-touchgui-labels-" in text

    with tempfile.TemporaryDirectory(prefix="touchgui-favorite-labels-") as temp:
        root = Path(temp)
        index = root / "index.php"
        view = root / "viewUtils.php"
        main_js = root / "main.js"
        favs = root / "favsUtils.php"
        simple_index = root / "simple-index.php"
        simple_js = root / "simple.js"
        simple_css = root / "simple.css"
        main_css = root / "main.css"
        write(main_css, ".favEditPanel { width:min(420px,95vw); }\n")

        write(index, '''<?php
require_once('include/common.php');
require_once('astapi/nodeInfo.php');
foreach($favList as $f) {
\t\t$favEditLabel = htmlspecialchars(array_pop($f), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
\t\t$nodeNumAttr = ['1' => 'class="nodeNum" data-fav-label="' . $favEditLabel
\t\t\t. '" onClick="selectFavorite(this)" onDblClick="connectNode(\'connect\')"'];
}
function processForm($parms, &$msg) {
\t\tcase "Add Favorite":
\t\t\t$msg[] = "Add Node $node to Favorites requested";
\t\t\tif(!validDbID($node)) break;
\t\t\t$label = "label[] = \\"$call $desc, $loc $node\\"";
\t\t\t$cmd = "cmd[] = \\"rpt cmd %node% ilink 3 $node\\"";
\t\t\tarray_splice($favs, $insertLn, 0, [$label, $cmd, '']);
\t\t\tbreak;
\t\tcase "Edit Favorite":
\t\t\t$originalNode = isset($parms['originalnode']) ? trim($parms['originalnode']) : '';
\t\t\t$newLabel = isset($parms['editlabel']) ? trim($parms['editlabel']) : '';
\t\t\t$newOrder = isset($parms['editorder']) ? trim($parms['editorder']) : '';
\t\t\tif($newLabel === '' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||
\t\t\t\tstrpos($newLabel, '\"') !== false || strpos($newLabel, "\\r") !== false ||
\t\t\t\tstrpos($newLabel, "\\n") !== false) {
\t\t\t\t$msg[] = error("Friendly label must be 1 to 120 plain-text characters and cannot contain double quotes or line breaks.");
\t\t\t\tbreak;
\t\t\t}
\t\t\t$favs[$labelLine] = 'label[] = "' . $newLabel . ' ' . $node . '"';
\t\t\t$favs[$matchLine] = 'cmd[] = "rpt cmd %node% ilink 3 ' . $node . '"';
\t\t\tif(!writeFileLines($favsFile, $favs, $msg)) { copy($backup, $favsFile); break; }
\t\t\tbreak;
\t\tcase "Delete Favorite":
\t\t\tif(!writeFileLines($favsFile, $favs, $msg)) break;
\t\t\tbreak;
\t\tcase SET_NODE_INFO_CFGS:
\t\t\tbreak;
}
''')
        write(view, '''function showNodeCtrlForm() {
<input type=hidden id="editlabel" name="editlabel" value="">
<input type=hidden id="editorder" name="editorder" value="">
<input type=submit name="Submit" value="Add Favorite" class="small">
<div id="favoriteEditModal">
<h3 id="favoriteEditTitle">Edit Favorite</h3>
<label for="favoriteEditOrder">Order</label>
<input type="number" min="1" step="1" id="favoriteEditOrder">
<label for="favoriteEditLabel">Friendly Name/Label</label>
<input type="text" id="favoriteEditLabel" maxlength="120">
<button type="submit" name="Submit" value="Edit Favorite" class="small">Save &amp; Close</button>
</div>
''')
        write(main_js, '''// Local modification: AllScan-styled Favorites editor with Node, Order, and Friendly Label fields.
function openFavoriteEditor() {}
''')
        write(favs, '''<?php
\t$favsIni = parse_ini_file($favsFile, true);
\t$favs[$i] = (object)['node'=>$m[0], 'label'=>$label, 'cmd'=>$c];
''')
        write(simple_index, "\t\t'label' => $rawLabel,\n")
        shutil.copy2(ROOT / "tests" / "fixtures" / "touchgui-installed-v1.17.js", simple_js)
        shutil.copy2(ROOT / "tests" / "fixtures" / "touchgui-installed-v1.17.css", simple_css)

        subprocess.run(["python3", str(ACTIVITY_PATCHER), str(simple_js), str(simple_css)], check=True)
        args = [str(index), str(view), str(main_js), str(favs), str(simple_index), str(simple_js), str(main_css)]
        command = ["python3", str(PATCHER), *args]
        subprocess.run(command, check=True)
        subprocess.run(["node", "--check", str(main_js)], check=True)
        subprocess.run(["node", "--check", str(simple_js)], check=True)

        result = index.read_text(encoding="utf-8")
        assert "function allscanModsSetTouchguiLabel" in result
        assert "allscanModsSetTouchguiLabel($favs, '', $node, $touchguiLabel)" in result
        assert "allscanModsSetTouchguiLabel($favs, $originalNode, $node, $touchguiLabel)" in result
        assert "allscanModsSetTouchguiLabel($favs, $node, '', '')" in result
        assert "data-fav-touchgui-label" in result
        assert "TouchGUI favorite labels v1.22" in view.read_text(encoding="utf-8")
        view_text = view.read_text(encoding="utf-8")
        assert "favoriteEditTouchguiLabel" in view_text
        assert "maxlength=\"33\"" in view.read_text(encoding="utf-8")
        assert '<div class="favoriteEditHelp">AllScan adds the node callsign to this name.</div>' in view_text
        assert '<div class="favoriteEditHelp">Up to 33 characters. Callsign not needed.</div>' in view_text
        touchgui_input = '<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">'
        help_order_marker = '<!-- AllScan Mods: TouchGUI favorite-label help order v1.29. -->'
        assert view_text.index(touchgui_input) < view_text.index(help_order_marker) < view_text.index('Up to 33 characters. Callsign not needed.')
        assert "Favorites editor helper text v1.25" in main_css.read_text(encoding="utf-8")
        assert "font-size:11px;" in main_css.read_text(encoding="utf-8")
        assert ".favEditPanel label {\n\tfont-weight:bold;\n}" in main_css.read_text(encoding="utf-8")
        assert "openNewFavoriteEditor()" in main_js.read_text(encoding="utf-8")
        assert "touchguiLabel" in favs.read_text(encoding="utf-8")
        assert "touchguiLabel" in simple_index.read_text(encoding="utf-8")

        before = {path: path.read_bytes() for path in (index, view, main_js, favs, simple_index, simple_js, main_css)}
        subprocess.run(command, check=True)
        assert before == {path: path.read_bytes() for path in before}, "Reapplying changed the patched files."

        migration_root = root / "v128"
        migration_root.mkdir()
        migration_sources = (index, view, main_js, favs, simple_index, simple_js, main_css)
        migration_paths = tuple(migration_root / path.name for path in migration_sources)
        for source_path, dest_path in zip(migration_sources, migration_paths):
            shutil.copy2(source_path, dest_path)
        old_v128_help = '<div class="favoriteEditHelp">AllScan adds the node callsign to this name.</div>\n<label for="favoriteEditTouchguiLabel">TouchGUI Card Label</label>\n<div class="favoriteEditHelp">Up to 33 characters. Callsign not needed.</div>\n<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">'
        current_v129_help = '<div class="favoriteEditHelp">AllScan adds the node callsign to this name.</div>\n<label for="favoriteEditTouchguiLabel">TouchGUI Card Label</label>\n<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">\n<!-- AllScan Mods: TouchGUI favorite-label help order v1.29. -->\n<div class="favoriteEditHelp">Up to 33 characters. Callsign not needed.</div>'
        v128_view = migration_paths[1].read_text(encoding="utf-8")
        assert current_v129_help in v128_view
        migration_paths[1].write_text(v128_view.replace(current_v129_help, old_v128_help, 1), encoding="utf-8")
        v128_css = migration_paths[6].read_text(encoding="utf-8")
        v129_label_css = '''/* AllScan Mods: Favorites editor field labels v1.29. */\n.favEditPanel label {\n\tfont-weight:bold;\n}\n'''
        assert v129_label_css in v128_css
        migration_paths[6].write_text(v128_css.replace("\n\n" + v129_label_css, "\n", 1), encoding="utf-8")
        migration_command = ["python3", str(PATCHER), *map(str, migration_paths)]
        subprocess.run(migration_command, check=True)
        migrated_view = migration_paths[1].read_text(encoding="utf-8")
        assert migrated_view.index(touchgui_input) < migrated_view.index(help_order_marker) < migrated_view.index("Up to 33 characters. Callsign not needed.")
        assert "Favorites editor field labels v1.29." in migration_paths[6].read_text(encoding="utf-8")
        migrated_v128 = {path: path.read_bytes() for path in migration_paths}
        subprocess.run(migration_command, check=True)
        assert migrated_v128 == {path: path.read_bytes() for path in migration_paths}, "v1.28 Favorites editor migration was not idempotent"

        old_help_style = '''/* AllScan Mods: Favorites editor helper text v1.23. */
.favEditPanel .favoriteEditHelp {
	margin:0 0 8px;
	color:#d7dfea;
	font-size:13px;
	line-height:1.35;
}'''
        new_help_style = '''/* AllScan Mods: Favorites editor helper text v1.25. */
.favEditPanel .favoriteEditHelp {
	margin:0 0 6px;
	color:#aebacc;
	font-size:11px;
	line-height:1.25;
}'''
        main_css.write_text(old_help_style + "\n", encoding="utf-8")
        subprocess.run(command, check=True)
        assert main_css.read_text(encoding="utf-8") == new_help_style + "\n\n/* AllScan Mods: Favorites editor field labels v1.29. */\n.favEditPanel label {\n\tfont-weight:bold;\n}\n"
        migrated_css = main_css.read_bytes()
        subprocess.run(command, check=True)
        assert main_css.read_bytes() == migrated_css, "v1.23 editor guidance CSS migration was not idempotent"

        editor_runtime = root / "editor-runtime.js"
        editor_runtime.write_text(r'''
var editorElements = {};
['favoriteEditTitle', 'favoriteEditSave', 'favoriteEditOrderRow', 'favoriteEditNode',
 'favoriteEditLabel', 'favoriteEditTouchguiLabel', 'favoriteEditOrder', 'favoriteEditModal',
 'originalnode', 'editlabel', 'touchtguilabel', 'editorder'].forEach(function(id) {
    editorElements[id] = {id:id, value:'', hidden:true, focus:function(){}, select:function(){}, click:function(){}};
});
var document = {
    getElementById:function(id){ return editorElements[id]; },
    querySelectorAll:function(){ return []; },
    addEventListener:function(){}
};
''' + main_js.read_text(encoding="utf-8") + r'''
var rnode = {value:'12345', dataset:{favoriteNode:'12345', favoriteLabel:'Existing AllScan name', favoriteTouchguiLabel:'Existing card name'}};
openFavoriteEditor();
if(editorElements.favoriteEditLabel.value !== 'Existing AllScan name') throw new Error('Existing AllScan label did not populate');
if(editorElements.favoriteEditTouchguiLabel.value !== 'Existing card name') throw new Error('Existing TouchGUI label did not populate');
openNewFavoriteEditor();
if(editorElements.favoriteEditLabel.value !== '') throw new Error('New favorite AllScan label was not blank');
if(editorElements.favoriteEditTouchguiLabel.value !== '') throw new Error('New favorite TouchGUI label was not blank');
''', encoding="utf-8")
        subprocess.run(["node", str(editor_runtime)], check=True)

        runtime = root / "runtime.js"
        runtime.write_text("var window = {addEventListener:function(){}};\n" + simple_js.read_text(encoding="utf-8") + r'''
function escapeRegExp(txt) {
	return String(txt).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
var card = {node:'12345', call:'W1ABC', label:'W1ABC Default Name 12345', name:'W1ABC', desc:'Database description', loc:'Somewhere'};
if(channelLabel(card) !== 'Default Name') throw new Error('Automatic title changed unexpectedly');
card.touchguiLabel = 'My independent label';
if(channelLabel(card) !== 'My independent label') throw new Error('Saved TouchGUI label did not override the automatic title');
''', encoding="utf-8")
        subprocess.run(["node", str(runtime)], check=True)

    print("PASS: existing and new editor flows carry independent TouchGUI labels.")
    print("PASS: node-keyed metadata survives add/edit/delete code paths and helper reruns cleanly.")
    print("PASS: TouchGUI uses the saved label when present and keeps automatic naming otherwise.")


if __name__ == "__main__":
    main()
