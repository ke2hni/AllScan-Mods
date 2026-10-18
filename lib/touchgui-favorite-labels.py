#!/usr/bin/env python3
"""Add an optional, per-favorite TouchGUI card label to AllScan."""

from pathlib import Path
import re
import sys


MARKER = "TouchGUI favorite card label v1.22"
HELP_STYLE_MARKER = "/* AllScan Mods: Favorites editor helper text v1.25. */"
FIELD_LABEL_STYLE_MARKER = "/* AllScan Mods: Favorites editor field labels v1.29. */"
OLD_HELP_STYLE = '''/* AllScan Mods: Favorites editor helper text v1.23. */
.favEditPanel .favoriteEditHelp {
	margin:0 0 8px;
	color:#d7dfea;
	font-size:13px;
	line-height:1.35;
}'''
NEW_HELP_STYLE = '''/* AllScan Mods: Favorites editor helper text v1.25. */
.favEditPanel .favoriteEditHelp {
	margin:0 0 6px;
	color:#aebacc;
	font-size:11px;
	line-height:1.25;
}'''
FIELD_LABEL_STYLE = '''/* AllScan Mods: Favorites editor field labels v1.29. */
.favEditPanel label {
	font-weight:bold;
}'''


def replace_once(text: str, old: str, new: str, what: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"ERROR: Expected {what} exactly once, found {count}; files left unchanged.")
    return text.replace(old, new, 1)


def patch_favs_utils(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// AllScan Mods: Read TouchGUI favorite labels v1.22."
    if marker not in source:
        source = replace_once(
            source,
            "\t$favsIni = parse_ini_file($favsFile, true);",
            "\t$favsIni = parse_ini_file($favsFile, true);\n"
            "\t" + marker + "\n"
            "\t$touchguiLabels = [];\n"
            "\t$touchguiLines = @file($favsFile, FILE_IGNORE_NEW_LINES);\n"
            "\tif(is_array($touchguiLines)) {\n"
            "\t\tforeach($touchguiLines as $touchguiLine) {\n"
            "\t\t\tif(preg_match('/^; AllScan Mods TouchGUI Label ([0-9]{4,8}) ([A-Za-z0-9+\\/]+=*)$/', trim($touchguiLine), $touchguiMatch) === 1) {\n"
            "\t\t\t\t$touchguiValue = base64_decode($touchguiMatch[2], true);\n"
            "\t\t\t\tif($touchguiValue !== false)\n"
            "\t\t\t\t\t$touchguiLabels[$touchguiMatch[1]] = $touchguiValue;\n"
            "\t\t\t}\n"
            "\t\t}\n"
            "\t}\n",
            "Favorites INI load point",
        )
    if "'touchguiLabel'=>$touchguiLabels[$m[0]] ?? ''" not in source:
        source = replace_once(
            source,
            "$favs[$i] = (object)['node'=>$m[0], 'label'=>$label, 'cmd'=>$c];",
            "$favs[$i] = (object)['node'=>$m[0], 'label'=>$label, 'cmd'=>$c, 'touchguiLabel'=>$touchguiLabels[$m[0]] ?? ''];",
            "favorite object builder",
        )
    path.write_text(source, encoding="utf-8")


def patch_index(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// AllScan Mods: TouchGUI favorite labels v1.22."
    if marker not in source:
        helper = r'''
// AllScan Mods: TouchGUI favorite labels v1.22.
function allscanModsSetTouchguiLabel(&$lines, $oldNode, $newNode, $label = null) {
	$storedLabel = null;
	$prefix = '; AllScan Mods TouchGUI Label ';
	foreach($lines as $lineNo => $line) {
		if(preg_match('/^; AllScan Mods TouchGUI Label ([0-9]{4,8}) ([A-Za-z0-9+\/]+=*)$/', trim($line), $match) === 1) {
			if((string)$match[1] === (string)$oldNode)
				$storedLabel = base64_decode($match[2], true);
			if((string)$match[1] === (string)$oldNode || (string)$match[1] === (string)$newNode)
				unset($lines[$lineNo]);
		}
	}
	$lines = array_values($lines);
	if($label === null)
		$label = $storedLabel;
	if($label !== null && $label !== '' && validDbID($newNode))
		$lines[] = $prefix . $newNode . ' ' . base64_encode($label);
}
'''
        source = replace_once(
            source,
            "require_once('astapi/nodeInfo.php');",
            "require_once('astapi/nodeInfo.php');\n" + helper,
            "main-page include insertion point",
        )

    add_pattern = re.compile(r'\t\tcase "Add Favorite":.*?(?=\t\tcase "Edit Favorite":)', re.S)
    add_match = add_pattern.search(source)
    if not add_match:
        raise SystemExit("ERROR: Add Favorite action not found; files left unchanged.")
    add_case = add_match.group(0)
    if "allscanModsSetTouchguiLabel($favs, '', $node, $touchguiLabel);" not in add_case:
        add_case = add_case.replace(
            '\t\t\t$msg[] = "Add Node $node to Favorites requested";',
            '\t\t\t$msg[] = "Add Node $node to Favorites requested";\n'
            "\t\t\t$newLabel = isset($parms['editlabel']) ? trim($parms['editlabel']) : '';\n"
            "\t\t\t$touchguiLabel = isset($parms['touchtguilabel']) ? trim($parms['touchtguilabel']) : '';\n"
            "\t\t\tif(($newLabel !== '' && (strlen($newLabel) > 120 || !checkAscii($newLabel) || strpos($newLabel, '\"') !== false || strpos($newLabel, \"\\n\") !== false || strpos($newLabel, \"\\r\") !== false)) || strlen($touchguiLabel) > 33 || !checkAscii($touchguiLabel) || strpos($touchguiLabel, \"\\n\") !== false || strpos($touchguiLabel, \"\\r\") !== false) {\n"
            '\t\t\t\t$msg[] = error("Favorite labels are too long or contain unsupported characters.");\n'
            "\t\t\t\tbreak;\n"
            "\t\t\t}\n",
            1,
        )
        add_case = add_case.replace(
            '\t\t\t$label = "label[] = \\"$call $desc, $loc $node\\"";',
            '\t\t\t$mainLabel = $newLabel !== \'\' ? $newLabel : "$call $desc, $loc";\n'
            '\t\t\t$label = "label[] = \\"$mainLabel $node\\"";',
            1,
        )
        add_case = add_case.replace(
            '\t\t\tarray_splice($favs, $insertLn, 0, [$label, $cmd, \'\']);',
            '\t\t\tarray_splice($favs, $insertLn, 0, [$label, $cmd, \'\']);\n'
            "\t\t\tallscanModsSetTouchguiLabel($favs, '', $node, $touchguiLabel);",
            1,
        )
        if "allscanModsSetTouchguiLabel($favs, '', $node, $touchguiLabel);" not in add_case:
            raise SystemExit("ERROR: Add Favorite action shape is unsupported; files left unchanged.")
        source = source[:add_match.start()] + add_case + source[add_match.end():]

    edit_pattern = re.compile(r'\t\tcase "Edit Favorite":.*?(?=\t\tcase "Delete Favorite":)', re.S)
    edit_match = edit_pattern.search(source)
    if not edit_match:
        raise SystemExit("ERROR: Edit Favorite action not found; files left unchanged.")
    edit_case = edit_match.group(0)
    if "allscanModsSetTouchguiLabel($favs, $originalNode, $node" not in edit_case:
        edit_case = edit_case.replace(
            '\t\t\t$newOrder = isset($parms[\'editorder\']) ? trim($parms[\'editorder\']) : \'\';',
            '\t\t\t$newOrder = isset($parms[\'editorder\']) ? trim($parms[\'editorder\']) : \'\';\n'
            "\t\t\t$touchguiLabel = isset($parms['touchtguilabel']) ? trim($parms['touchtguilabel']) : null;",
            1,
        )
        edit_case = edit_case.replace(
            '\t\t\tif(($newLabel === \'\' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||\n',
            '\t\t\tif(($newLabel === \'\' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||\n',
            1,
        )
        validation_pattern = re.compile(r"(\t\t\tif\(\$newLabel === ''[\s\S]*?\t\t\t\tbreak;\n\t\t\t\}\n)")
        edit_case, validation_count = validation_pattern.subn(
            lambda match: match.group(1) + '\t\t\tif($touchguiLabel !== null && (strlen($touchguiLabel) > 33 || !checkAscii($touchguiLabel) || strpos($touchguiLabel, "\\n") !== false || strpos($touchguiLabel, "\\r") !== false)) {\n\t\t\t\t$msg[] = error("TouchGUI label must be 33 characters or fewer and contain plain text only.");\n\t\t\t\tbreak;\n\t\t\t}\n',
            edit_case,
            count=1,
        )
        if validation_count != 1:
            raise SystemExit("ERROR: Edit Favorite label validation is unsupported; file left unchanged.")
        edit_case = replace_once(
            edit_case,
            '\t\t\tif(!writeFileLines($favsFile, $favs, $msg)) {',
            '\t\t\tif(array_key_exists(\'touchtguilabel\', $parms))\n'
            '\t\t\t\tallscanModsSetTouchguiLabel($favs, $originalNode, $node, $touchguiLabel);\n'
            '\t\t\telse if($originalNode !== $node)\n'
            '\t\t\t\tallscanModsSetTouchguiLabel($favs, $originalNode, $node, null);\n'
            '\t\t\tif(!writeFileLines($favsFile, $favs, $msg)) {',
            "Edit Favorite write point",
        )
        source = source[:edit_match.start()] + edit_case + source[edit_match.end():]

    delete_pattern = re.compile(r'\t\tcase "Delete Favorite":.*?(?=\t\tcase SET_NODE_INFO_CFGS:)', re.S)
    delete_match = delete_pattern.search(source)
    if not delete_match:
        raise SystemExit("ERROR: Delete Favorite action not found; files left unchanged.")
    delete_case = delete_match.group(0)
    if "allscanModsSetTouchguiLabel($favs, $node, '', '');" not in delete_case:
        delete_case = replace_once(
            delete_case,
            '\t\t\tif(!writeFileLines($favsFile, $favs, $msg))',
            "\t\t\tallscanModsSetTouchguiLabel($favs, $node, '', '');\n\t\t\tif(!writeFileLines($favsFile, $favs, $msg))",
            "Delete Favorite metadata cleanup",
        )
        source = source[:delete_match.start()] + delete_case + source[delete_match.end():]

    if marker not in source:
        raise SystemExit("ERROR: TouchGUI label server marker missing after patching.")
    path.write_text(source, encoding="utf-8")


def patch_view(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// AllScan Mods: TouchGUI favorite labels v1.22."
    if marker not in source:
        source = replace_once(
            source,
            "function showNodeCtrlForm() {",
            "function showNodeCtrlForm() {\n\t" + marker,
            "Favorites editor version marker",
        )
    add_old = '<input type=submit name="Submit" value="Add Favorite" class="small">'
    add_new = '<input type=button value="Add Favorite" class="small" onClick="openNewFavoriteEditor();">'
    if add_new not in source:
        source = replace_once(source, add_old, add_new, "Add Favorite control")
    if 'id="touchtguilabel"' not in source:
        source = replace_once(
            source,
            '<input type=hidden id="editlabel" name="editlabel" value="">',
            '<input type=hidden id="editlabel" name="editlabel" value="">\n<input type=hidden id="touchtguilabel" name="touchtguilabel" value="">',
            "Favorites editor hidden fields",
        )
    if 'id="favoriteEditTouchguiLabel"' not in source:
        source = replace_once(
            source,
            '<label for="favoriteEditOrder">Order</label>\n<input type="number" min="1" step="1" id="favoriteEditOrder">',
            '<div id="favoriteEditOrderRow"><label for="favoriteEditOrder">Order</label>\n<input type="number" min="1" step="1" id="favoriteEditOrder"></div>',
            "Favorites editor order field",
        )
        source = replace_once(
            source,
            '<label for="favoriteEditLabel">Friendly Name/Label</label>\n<input type="text" id="favoriteEditLabel" maxlength="120">',
            '<label for="favoriteEditLabel">AllScan Friendly Name/Label</label>\n<input type="text" id="favoriteEditLabel" maxlength="120">\n<small>AllScan adds the node callsign to this name.</small>\n<label for="favoriteEditTouchguiLabel">TouchGUI Card Label <small>(up to 33 characters; callsign not needed)</small></label>\n<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">',
            "Favorites editor label fields",
        )
        source = replace_once(
            source,
            '<button type="submit" name="Submit" value="Edit Favorite" class="small"',
            '<button type="submit" id="favoriteEditSave" name="Submit" value="Edit Favorite" class="small"',
            "Favorites editor save button",
        )
    if 'id="favoriteEditTitle">Edit Favorite' in source:
        source = source.replace('id="favoriteEditTitle">Edit Favorite', 'id="favoriteEditTitle">Edit Favorite', 1)
    new_help = '<div class="favoriteEditHelp">AllScan adds the node callsign to this name.</div>\n<label for="favoriteEditTouchguiLabel">TouchGUI Card Label</label>\n<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">\n<!-- AllScan Mods: TouchGUI favorite-label help order v1.29. -->\n<div class="favoriteEditHelp">Up to 33 characters. Callsign not needed.</div>'
    old_help_v128 = '<div class="favoriteEditHelp">AllScan adds the node callsign to this name.</div>\n<label for="favoriteEditTouchguiLabel">TouchGUI Card Label</label>\n<div class="favoriteEditHelp">Up to 33 characters. Callsign not needed.</div>\n<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">'
    old_help_v125 = '<small>AllScan adds the node callsign to this name.</small>\n<label for="favoriteEditTouchguiLabel">TouchGUI Card Label <small>(up to 33 characters; callsign not needed)</small></label>\n<input type="text" id="favoriteEditTouchguiLabel" maxlength="33">'
    if new_help not in source:
        if old_help_v128 in source:
            source = replace_once(source, old_help_v128, new_help, "v1.28 Favorites editor helper placement")
        else:
            source = replace_once(source, old_help_v125, new_help, "Favorites editor helper text")
    path.write_text(source, encoding="utf-8")


def patch_main_css(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    if HELP_STYLE_MARKER not in source:
        if source.count(OLD_HELP_STYLE) == 1:
            source = source.replace(OLD_HELP_STYLE, NEW_HELP_STYLE, 1)
        elif "Favorites editor helper text v1.23." not in source:
            source = source.rstrip() + "\n\n" + NEW_HELP_STYLE + "\n"
        else:
            raise SystemExit("ERROR: Existing Favorites editor guidance CSS is unexpected; files left unchanged.")
    if FIELD_LABEL_STYLE_MARKER not in source:
        source = source.rstrip() + "\n\n" + FIELD_LABEL_STYLE + "\n"
    path.write_text(source, encoding="utf-8")


def patch_main_js(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// Local modification: TouchGUI favorite card label editor v1.22."
    if marker in source:
        return
    start_markers = (
        "// Local modification: AllScan-styled Favorites editor with Node, Order, and Friendly Label fields.",
        "// Local modification: AllScan-styled Favorites editor with Node and Friendly Label fields.",
        "// Local modification: select and safely edit an AllScan Favorite from the main page.",
    )
    positions = [source.find(item) for item in start_markers if item in source]
    if len(positions) != 1:
        raise SystemExit("ERROR: Favorites editor JavaScript block is missing or ambiguous; file left unchanged.")
    prefix = source[:min(positions)].rstrip()
    editor = r'''

// Local modification: TouchGUI favorite card label editor v1.22.
var favoriteEditorMode = 'edit';
function selectFavorite(cell) {
	if(!cell) return;
	var node = cell.textContent.trim();
	setNodeBox(node);
	rnode.dataset.favoriteNode = node;
	rnode.dataset.favoriteLabel = cell.getAttribute('data-fav-label') || '';
	rnode.dataset.favoriteTouchguiLabel = cell.getAttribute('data-fav-touchgui-label') || '';
}
function findSelectedFavorite() {
	var currentNode = rnode.value.trim();
	var selectedNode = rnode.dataset.favoriteNode || '';
	if(currentNode && selectedNode === currentNode) return true;
	var cells = document.querySelectorAll('#favs td.nodeNum');
	for(var i = 0; i < cells.length; i++) {
		if(cells[i].textContent.trim() === currentNode) {
			selectFavorite(cells[i]);
			return true;
		}
	}
	return false;
}
function setFavoriteEditorMode(mode) {
	favoriteEditorMode = mode;
	var isAdd = mode === 'add';
	document.getElementById('favoriteEditTitle').textContent = isAdd ? 'Add Favorite' : 'Edit Favorite';
	document.getElementById('favoriteEditSave').value = isAdd ? 'Add Favorite' : 'Edit Favorite';
	document.getElementById('favoriteEditSave').textContent = isAdd ? 'Add Favorite' : 'Save & Close';
	document.getElementById('favoriteEditOrderRow').hidden = isAdd;
}
function openFavoriteEditor() {
	if(!findSelectedFavorite()) {
		alert('Select an existing favorite by clicking its node number before editing.');
		return;
	}
	setFavoriteEditorMode('edit');
	var nodeInput = document.getElementById('favoriteEditNode');
	document.getElementById('favoriteEditLabel').value = rnode.dataset.favoriteLabel || '';
	document.getElementById('favoriteEditTouchguiLabel').value = rnode.dataset.favoriteTouchguiLabel || '';
	var orderInput = document.getElementById('favoriteEditOrder');
	nodeInput.value = rnode.dataset.favoriteNode || '';
	var favCells = document.querySelectorAll('#favs td.nodeNum');
	for(var oi = 0; oi < favCells.length; oi++) if(favCells[oi].textContent.trim() === (rnode.dataset.favoriteNode || '')) { orderInput.value = oi + 1; break; }
	var modal = document.getElementById('favoriteEditModal');
	modal.hidden = false;
	nodeInput.focus();
	nodeInput.select();
}
function openNewFavoriteEditor() {
	setFavoriteEditorMode('add');
	document.getElementById('favoriteEditNode').value = rnode.value.trim();
	document.getElementById('favoriteEditOrder').value = '';
	document.getElementById('favoriteEditLabel').value = '';
	document.getElementById('favoriteEditTouchguiLabel').value = '';
	document.getElementById('favoriteEditModal').hidden = false;
	document.getElementById('favoriteEditNode').focus();
}
document.addEventListener('DOMContentLoaded', function() {
	var nodeBox = document.getElementById('node');
	if(nodeBox) nodeBox.addEventListener('keydown', function(event) {
		if(event.key === 'Enter') {
			event.preventDefault();
			openNewFavoriteEditor();
		}
	});
});
function closeFavoriteEditor() {
	var modal = document.getElementById('favoriteEditModal');
	if(modal) modal.hidden = true;
}
function favoriteEditorBackdrop(event) {
	if(event.target && event.target.id === 'favoriteEditModal') closeFavoriteEditor();
}
function submitFavoriteEdit() {
	var isAdd = favoriteEditorMode === 'add';
	var originalNode = rnode.dataset.favoriteNode || '';
	var newNode = document.getElementById('favoriteEditNode').value.trim();
	var newLabel = document.getElementById('favoriteEditLabel').value.trim();
	var touchguiLabel = document.getElementById('favoriteEditTouchguiLabel').value.trim();
	var newOrder = document.getElementById('favoriteEditOrder').value.trim();
	if(!/^[0-9]{4,8}$/.test(newNode)) {
		alert('Node number must contain 4 to 8 digits.');
		return false;
	}
	if((!isAdd && !newLabel) || newLabel.length > 120 || /["\r\n]/.test(newLabel)) {
		alert('AllScan friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');
		return false;
	}
	if(touchguiLabel.length > 33 || /[\r\n]/.test(touchguiLabel)) {
		alert('TouchGUI label must be 33 characters or fewer and contain no line breaks.');
		return false;
	}
	if(!isAdd && !/^[1-9][0-9]*$/.test(newOrder)) { alert('Order must be a positive number.'); return false; }
	document.getElementById('originalnode').value = isAdd ? '' : originalNode;
	document.getElementById('editlabel').value = newLabel;
	document.getElementById('touchtguilabel').value = touchguiLabel;
	document.getElementById('editorder').value = newOrder;
	rnode.value = newNode;
	return true;
}
document.addEventListener('keydown', function(event) {
	var modal = document.getElementById('favoriteEditModal');
	if(event.key === 'Escape' && modal && !modal.hidden) closeFavoriteEditor();
	if(event.key === 'Enter' && modal && !modal.hidden && modal.contains(event.target)) {
		event.preventDefault();
		document.getElementById('favoriteEditSave').click();
	}
});
'''
    path.write_text(prefix + editor, encoding="utf-8")


def patch_simple_index(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// AllScan Mods: TouchGUI favorite card label JSON v1.22."
    if marker in source:
        return
    source = replace_once(
        source,
        "\t\t'label' => $rawLabel,",
        "\t\t'label' => $rawLabel,\n"
        "\t\t" + marker + "\n"
        "\t\t'touchguiLabel' => $favsData['favs'][$f[0]]->touchguiLabel ?? '',",
        "TouchGUI channel JSON fields",
    )
    path.write_text(source, encoding="utf-8")


def patch_simple_js(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// AllScan Mods: TouchGUI card label override v1.22."
    if marker in source:
        return
    source = replace_once(
        source,
        "function channelLabel(channel) {\n\tvar callsign = channel.call ? String(channel.call).trim() : '';",
        "function channelLabel(channel) {\n"
        "\t" + marker + "\n"
        "\tif(channel.touchguiLabel && String(channel.touchguiLabel).trim())\n"
        "\t\treturn String(channel.touchguiLabel).trim();\n"
        "\tvar callsign = channel.call ? String(channel.call).trim() : '';",
        "TouchGUI channel label function",
    )
    path.write_text(source, encoding="utf-8")


def patch_index_row(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    marker = "// AllScan Mods: TouchGUI favorite label row data v1.22."
    if marker in source:
        return
    row_start_marker = "\t\t$favEditLabel = htmlspecialchars(array_pop($f), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');"
    if source.count(row_start_marker) != 1:
        raise SystemExit("ERROR: Favorites table row renderer is unsupported; file left unchanged.")
    row_start = source.index(row_start_marker)
    attr_start = source.index("\n\t\t$nodeNumAttr = ", row_start) + 1
    row_end = source.index("];", attr_start) + 2
    attr_source = source[attr_start:row_end]
    old_attr = 'data-fav-label="\' . $favEditLabel'
    new_attr = 'data-fav-label="\' . $favEditLabel . \'" data-fav-touchgui-label="\' . $favTouchguiLabel'
    if attr_source.count(old_attr) != 1 or "onDblClick=\"connectNode(" not in attr_source:
        raise SystemExit("ERROR: Favorites node attributes are unsupported; file left unchanged.")
    row = r'''\t\t$favEditLabel = htmlspecialchars(array_pop($f), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
		$favTouchguiLabel = $favs[$f[0]]->touchguiLabel ?? '';
		if($favTouchguiLabel === '') {
			$touchguiRaw = $favs[$f[0]]->label ?? $f[2];
			$touchguiRaw = preg_replace('/(^|[\s,;:-]+)' . preg_quote((string)$f[1], '/') . '([\s,;:-]*$|(?=[\s,;:-]+))/', '$1', $touchguiRaw);
			$touchguiCall = isset($astdb[$f[1]][1]) ? trim($astdb[$f[1]][1]) : '';
			if($touchguiCall !== '')
				$touchguiRaw = preg_replace('/(^|[\s,;:.()]+)' . preg_quote($touchguiCall, '/') . '(?=$|[\s,;:.()]+)/i', '$1', $touchguiRaw);
			$touchguiRaw = trim(trim(preg_replace('/\s{2,}/', ' ', $touchguiRaw)), " ,;:.()");
			if($touchguiRaw === '') $touchguiRaw = trim($f[3]) ?: trim($f[4]) ?: (string)$f[1];
			if(strlen($touchguiRaw) > 33) $touchguiRaw = substr($touchguiRaw, 0, 32) . '…';
			$favTouchguiLabel = $touchguiRaw;
		}
		$favTouchguiLabel = htmlspecialchars($favTouchguiLabel, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
		// AllScan Mods: TouchGUI favorite label row data v1.22.'''.replace(r'\t', '\t')
    source = source[:row_start] + row + "\n" + attr_source.replace(old_attr, new_attr, 1) + source[row_end:]
    path.write_text(source, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 8:
        raise SystemExit("Usage: touchgui-favorite-labels.py INDEX.PHP VIEWUTILS.PHP MAIN.JS FAVSUTILS.PHP SIMPLE-INDEX.PHP SIMPLE.JS MAIN.CSS")
    index, view, main_js, favs_utils, simple_index, simple_js, main_css = map(Path, sys.argv[1:])
    original = {path: path.read_bytes() for path in (index, view, main_js, favs_utils, simple_index, simple_js, main_css)}
    try:
        patch_favs_utils(favs_utils)
        patch_index(index)
        patch_view(view)
        patch_main_js(main_js)
        patch_index_row(index)
        patch_simple_index(simple_index)
        patch_simple_js(simple_js)
        patch_main_css(main_css)
    except Exception:
        for path, content in original.items():
            path.write_bytes(content)
        raise
    print("TouchGUI favorite card labels patch-ready.")


if __name__ == "__main__":
    main()
