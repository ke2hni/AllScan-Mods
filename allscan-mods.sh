#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME=${0##*/}
ALLSCAN_DIR=/var/www/html/allscan

usage() {
    printf 'Usage: sudo ./%s [--allscan-dir PATH]\n' "$SCRIPT_NAME"
}

while (($#)); do
    case "$1" in
        --allscan-dir)
            (($# >= 2)) || { echo "ERROR: --allscan-dir requires a path." >&2; exit 2; }
            ALLSCAN_DIR=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if ((EUID != 0)); then
    echo "ERROR: Run this script with sudo." >&2
    exit 1
fi

INDEX_FILE=$ALLSCAN_DIR/index.php
VIEW_FILE=$ALLSCAN_DIR/include/viewUtils.php
JS_FILE=$ALLSCAN_DIR/js/main.js
CSS_FILE=$ALLSCAN_DIR/css/main.css
COMMON_FILE=$ALLSCAN_DIR/include/common.php

for required in "$INDEX_FILE" "$VIEW_FILE" "$JS_FILE" "$CSS_FILE" "$COMMON_FILE"; do
    [[ -f $required ]] || { echo "ERROR: Required AllScan file not found: $required" >&2; exit 1; }
done

grep -Eq '^\$AllScanVersion = "v1\.01";' "$COMMON_FILE" || {
    echo "ERROR: This installer supports David Gleason's AllScan v1.01 layout only." >&2
    echo "No files were changed." >&2
    exit 1
}

command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 is required." >&2; exit 1; }

work_dir=$(mktemp -d /tmp/allscan-mods.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT

stage_index=$work_dir/index.php
stage_view=$work_dir/viewUtils.php
stage_js=$work_dir/main.js
stage_css=$work_dir/main.css
cp -- "$INDEX_FILE" "$stage_index"
cp -- "$VIEW_FILE" "$stage_view"
cp -- "$JS_FILE" "$stage_js"
cp -- "$CSS_FILE" "$stage_css"

python3 - "$stage_index" "$stage_view" "$stage_js" "$stage_css" <<'PY'
from pathlib import Path
import re
import sys

index_path, view_path, js_path, css_path = map(Path, sys.argv[1:5])
index = index_path.read_text(encoding="utf-8")
view = view_path.read_text(encoding="utf-8")
js = js_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

def replace_once(text, old, new, description):
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"ERROR: Expected {description} exactly once, but found {count}. "
            "No live files were changed."
        )
    return text.replace(old, new, 1)

# Rx% / LCnt clickable headers.
old_header = "$hdrCols = ['#', 'Node', 'Name', 'Desc', 'Location', '<small>Rx%</small>', '<small>LCnt</small>'];"
new_header = "$hdrCols = ['#', 'Node', 'Name', 'Desc', 'Location', '<small><a href=\"#\" onclick=\"sortFavStats(5); return false;\">Rx%<span id=\"rxSortArrow\"></span></a></small>', '<small><a href=\"#\" onclick=\"sortFavStats(6); return false;\">LCnt<span id=\"lcntSortArrow\"></span></a></small>'];"
if new_header not in index:
    index = replace_once(index, old_header, new_header, "the stock Favorites header")

# Keep the friendly name available for the edit dialog without adding a visible table column.
old_fav_row = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP];"
new_fav_row = "$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];"
if new_fav_row not in index:
    index = replace_once(index, old_fav_row, new_fav_row, "the Favorites row builder")

new_row_output = '''foreach($favList as $f) {
	$favEditLabel = htmlspecialchars(array_pop($f), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
	$nodeNumAttr = ['1' => 'class="nodeNum" data-fav-label="' . $favEditLabel
		. '" onClick="selectFavorite(this)" onDblClick="connectNode(\\'connect\\')"'];'''
if new_row_output not in index:
    row_pattern = re.compile(
        r'''foreach\(\$favList as \$f\) \{\s*'''
        r'''\$nodeNumAttr = \['1' => 'class="nodeNum" onClick="setNodeBox\('\.\$f\[1\]\.\'\)" '\s*'''
        r'''\.\s*'onDblClick="connectNode\(\\'connect\\'\)"'\];'''
    )
    matches = list(row_pattern.finditer(index))
    if len(matches) != 1:
        raise SystemExit(
            f"ERROR: Expected the stock Favorites row output exactly once, but found {len(matches)}. "
            "No live files were changed."
        )
    index = row_pattern.sub(lambda match: new_row_output, index, count=1)

# Server-side Edit Favorite action.
edit_case_marker = '\tcase "Edit Favorite":'
edit_case = r'''	case "Edit Favorite":
		$originalNode = isset($parms['originalnode']) ? trim($parms['originalnode']) : '';
		$newLabel = isset($parms['editlabel']) ? trim($parms['editlabel']) : '';
		$msg[] = "Edit Favorite node $originalNode requested";
		if(!modifyOk()) {
			$msg[] = error("Modify permission is required.");
			break;
		}
		if(!isset($favsFile) || !$favsFile || !file_exists($favsFile)) {
			$msg[] = error("Favorites file does not exist.");
			break;
		}
		$allowedFavsFile = '';
		$allowedFavsFiles = findFavsFiles($allowedFavsFile);
		$requestedFavsFile = realpath($favsFile);
		if($requestedFavsFile === false || !in_array($requestedFavsFile, $allowedFavsFiles, true)) {
			$msg[] = error("Requested Favorites file is not allowed.");
			break;
		}
		$favsFile = $requestedFavsFile;
		if(!validDbID($originalNode) || strlen($originalNode) < 4 || strlen($originalNode) > 8 ||
			!validDbID($node) || strlen($node) < 4 || strlen($node) > 8) {
			$msg[] = error("Original and new node numbers must contain 4 to 8 digits.");
			break;
		}
		if($newLabel === '' || strlen($newLabel) > 120 || !checkAscii($newLabel) ||
			strpos($newLabel, '"') !== false || strpos($newLabel, "\r") !== false ||
			strpos($newLabel, "\n") !== false) {
			$msg[] = error("Friendly label must be 1 to 120 plain-text characters and cannot contain double quotes or line breaks.");
			break;
		}
		if(($favs = readFileLines($favsFile, $msg, false)) === false)
			break;
		$matchLine = null;
		$labelLine = null;
		$duplicate = false;
		$cmdPattern = '/^\\s*cmd\\[\\]\\s*=\\s*"rpt cmd %node% ilink 3 ([0-9]{4,8})"\\s*$/';
		foreach($favs as $i => $line) {
			if(preg_match($cmdPattern, $line, $matches) !== 1)
				continue;
			if($matches[1] === $node && $matches[1] !== $originalNode)
				$duplicate = true;
			if($matches[1] === $originalNode) {
				if($matchLine !== null) {
					$msg[] = error("Node $originalNode appears more than once; edit was not applied.");
					break 2;
				}
				$matchLine = $i;
				$labelLine = $i - 1;
			}
		}
		if($duplicate) {
			$msg[] = error("Node $node already exists in Favorites.");
			break;
		}
		if($matchLine === null || $labelLine < 0 ||
			preg_match('/^\\s*label\\[\\]\\s*=\\s*".*"\\s*$/', $favs[$labelLine]) !== 1) {
			$msg[] = error("Matching label/cmd pair for node $originalNode was not found.");
			break;
		}
		$backup = $favsFile . '.before-edit-' . date('Ymd-His');
		if(!copy($favsFile, $backup)) {
			$msg[] = error("Unable to create Favorites backup $backup.");
			break;
		}
		$favs[$labelLine] = 'label[] = "' . $newLabel . ' ' . $node . '"';
		$favs[$matchLine] = 'cmd[] = "rpt cmd %node% ilink 3 ' . $node . '"';
		if(!writeFileLines($favsFile, $favs, $msg)) {
			copy($backup, $favsFile);
			break;
		}
		if(parse_ini_file($favsFile, true) === false) {
			copy($backup, $favsFile);
			$msg[] = error("Edited Favorites file failed validation; the original was restored.");
			break;
		}
		$msg[] = "Favorite node $originalNode updated to node $node with label: $newLabel";
		$msg[] = "Backup saved as $backup";
		break;

'''
if edit_case_marker not in index:
    index = replace_once(index, '\tcase "Delete Favorite":', edit_case + '\tcase "Delete Favorite":', "Delete Favorite action")

# Final node-control layout and editor dialog.
final_view_marker = 'Save &amp; Close</button>'
if final_view_marker not in view:
    controls_pattern = re.compile(
        r'''<input type=hidden id="favsfile" name="favsfile".*?'''
        r'''<input type=button value="DTMF" onClick="dtmfCmd\(\);">''',
        re.DOTALL,
    )
    matches = list(controls_pattern.finditer(view))
    if len(matches) != 1:
        raise SystemExit(
            f"ERROR: Expected the AllScan node-control block exactly once, but found {len(matches)}. "
            "No live files were changed."
        )
    controls = '''<input type=hidden id="favsfile" name="favsfile" value="' . $favsFile .'">
<input type=hidden id="originalnode" name="originalnode" value="">
<input type=hidden id="editlabel" name="editlabel" value="">
<label for="node">Node#</label><input type="text" inputmode="tel" pattern="[0-9a-dA-D\\*#]*"
	id="node" name="node" maxlength="10" value="' . $remNode . '">
<input type=button value="Connect" onClick="connectNode(\\'connect\\');">
<input type=button value="Disconnect" onClick="disconnectNode();">
<input type=button value="Monitor" onClick="connectNode(\\'monitor\\');">
<br>
<input type=submit name="Submit" value="Add Favorite" class="small">
<input type=button value="Edit Favorite" class="small" onClick="openFavoriteEditor();">
<input type=submit name="Submit" value="Delete Favorite" class="small"
	onClick="return confirmFavAction(\\'Delete Favorite\\');">
<input type=button value="Local Mon" onClick="connectNode(\\'localmonitor\\');">
<input type=button value="DTMF" onClick="dtmfCmd();">'''
    view = controls_pattern.sub(lambda match: controls, view, count=1)
    modal = '''
<div id="favoriteEditModal" class="favEditModal" hidden onClick="favoriteEditorBackdrop(event);">
<div class="favEditPanel" role="dialog" aria-modal="true" aria-labelledby="favoriteEditTitle">
<h3 id="favoriteEditTitle">Edit Favorite</h3>
<label for="favoriteEditNode">Node Number</label>
<input type="text" inputmode="numeric" pattern="[0-9]*" id="favoriteEditNode" maxlength="8">
<label for="favoriteEditLabel">Friendly Name/Label</label>
<input type="text" id="favoriteEditLabel" maxlength="120">
<div class="favEditActions">
<button type="submit" name="Submit" value="Edit Favorite" class="small"
	onClick="return submitFavoriteEdit();">Save &amp; Close</button>
<input type="button" value="Cancel" class="small" onClick="closeFavoriteEditor();">
</div>
</div>
</div>'''
    view = replace_once(view, '</fieldset></form>', modal + '\n</fieldset></form>', "the node-control form closing tag")

sorter = r'''

// Local modification: client-side sorting for Favorites Rx% and LCnt columns.
var favStatsSortCol = -1;
var favStatsSortAsc = true;

function sortFavStats(col)
{
	var table = document.getElementById('favs');
	if(!table || !table.tBodies.length || table.tBodies[0].rows.length < 2 || (col !== 5 && col !== 6))
		return;
	if(favStatsSortCol === col)
		favStatsSortAsc = !favStatsSortAsc;
	else {
		favStatsSortCol = col;
		favStatsSortAsc = false;
	}
	var tbody = table.tBodies[0];
	var rows = Array.from(tbody.rows);
	var sortedRows = rows.map(function(row, index) {
		var text = row.cells[col] ? row.cells[col].textContent.trim() : '';
		var value = parseFloat(text);
		return {row:row, index:index, value:value, missing:isNaN(value)};
	});
	sortedRows.sort(function(a, b) {
		if(a.missing && b.missing) return a.index - b.index;
		if(a.missing) return 1;
		if(b.missing) return -1;
		if(a.value === b.value) return a.index - b.index;
		return favStatsSortAsc ? a.value - b.value : b.value - a.value;
	});
	sortedRows.forEach(function(item) { tbody.appendChild(item.row); });
	var rxArrow = document.getElementById('rxSortArrow');
	var lcntArrow = document.getElementById('lcntSortArrow');
	if(rxArrow) rxArrow.textContent = '';
	if(lcntArrow) lcntArrow.textContent = '';
	if(col === 5 && rxArrow) rxArrow.textContent = favStatsSortAsc ? '▲' : '▼';
	if(col === 6 && lcntArrow) lcntArrow.textContent = favStatsSortAsc ? '▲' : '▼';
}
'''
if len(re.findall(r'\bfunction\s+sortFavStats\s*\(', js)) == 0:
    js = js.rstrip() + sorter + '\n'

editor_marker = '// Local modification: AllScan-styled Favorites editor with Node and Friendly Label fields.'
editor_js = r'''

// Local modification: AllScan-styled Favorites editor with Node and Friendly Label fields.
function selectFavorite(cell) {
	if(!cell) return;
	var node = cell.textContent.trim();
	setNodeBox(node);
	rnode.dataset.favoriteNode = node;
	rnode.dataset.favoriteLabel = cell.getAttribute('data-fav-label') || '';
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
function openFavoriteEditor() {
	if(!findSelectedFavorite()) {
		alert('Select an existing favorite by clicking its node number before editing.');
		return;
	}
	var modal = document.getElementById('favoriteEditModal');
	var nodeInput = document.getElementById('favoriteEditNode');
	var labelInput = document.getElementById('favoriteEditLabel');
	nodeInput.value = rnode.dataset.favoriteNode || '';
	labelInput.value = rnode.dataset.favoriteLabel || '';
	modal.hidden = false;
	nodeInput.focus();
	nodeInput.select();
}
function closeFavoriteEditor() {
	var modal = document.getElementById('favoriteEditModal');
	if(modal) modal.hidden = true;
}
function favoriteEditorBackdrop(event) {
	if(event.target && event.target.id === 'favoriteEditModal') closeFavoriteEditor();
}
function submitFavoriteEdit() {
	var originalNode = rnode.dataset.favoriteNode || '';
	var newNode = document.getElementById('favoriteEditNode').value.trim();
	var newLabel = document.getElementById('favoriteEditLabel').value.trim();
	if(!/^[0-9]{4,8}$/.test(newNode)) {
		alert('Node number must contain 4 to 8 digits.');
		return false;
	}
	if(!newLabel || newLabel.length > 120 || /["\r\n]/.test(newLabel)) {
		alert('Friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');
		return false;
	}
	document.getElementById('originalnode').value = originalNode;
	document.getElementById('editlabel').value = newLabel;
	rnode.value = newNode;
	return true;
}
document.addEventListener('keydown', function(event) {
	var modal = document.getElementById('favoriteEditModal');
	if(event.key === 'Escape' && modal && !modal.hidden) closeFavoriteEditor();
});
'''
if editor_marker not in js:
    old_editor_marker = '// Local modification: select and safely edit an AllScan Favorite from the main page.'
    if old_editor_marker in js:
        js = js[:js.index(old_editor_marker)].rstrip()
    js = js.rstrip() + editor_js + '\n'

css_marker = '/* Local modification: AllScan Favorites editor dialog. */'
css_addition = r'''

/* Local modification: AllScan Favorites editor dialog. */
.favEditModal {position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:12px;background-color:rgba(0,0,0,0.72);}
.favEditModal[hidden] {display:none;}
.favEditPanel {box-sizing:border-box;width:min(420px,95vw);padding:12px 16px;border:3px solid rgb(51,51,119);border-radius:10px;background-color:hsl(240,25%,12%);box-shadow:0 8px 30px rgba(0,0,0,0.75);text-align:left;}
.favEditPanel h3 {margin:0 0 10px;text-align:center;font-size:16px;color:hsl(240,30%,70%);}
.favEditPanel label {display:block;margin-top:7px;color:#edc;}
.favEditPanel input[type=text] {box-sizing:border-box;width:100%;margin:2px 0 5px;padding:5px 7px;border:2px solid hsl(240,40%,60%);font-size:14px;}
.favEditActions {margin-top:10px;text-align:center;}
.favEditActions button {color:#fff;margin:2px 1px;background-color:#444;border-radius:3px;font:12px/1.25 Verdana,Arial,Helvetica,sans-serif;}
.favEditActions button:hover {background-color:#777;}
'''
if css_marker not in css:
    css = css.rstrip() + css_addition + '\n'

checks = {
    'Rx% header': 'onclick="sortFavStats(5); return false;"' in index,
    'LCnt header': 'onclick="sortFavStats(6); return false;"' in index,
    'Edit action': index.count(edit_case_marker) == 1,
    'row selection': 'onClick="selectFavorite(this)"' in index,
    'Save & Close dialog': final_view_marker in view,
    'sorter function': len(re.findall(r'\bfunction\s+sortFavStats\s*\(', js)) == 1,
    'editor function': len(re.findall(r'\bfunction\s+openFavoriteEditor\s*\(', js)) == 1,
    'editor CSS': css_marker in css,
    'Rx% live column': 'var busy = cells[5];' in js,
    'LCnt live column': 'var lcnt = cells[6];' in js,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('ERROR: Staged validation failed: ' + ', '.join(failed))

index_path.write_text(index, encoding="utf-8")
view_path.write_text(view, encoding="utf-8")
js_path.write_text(js, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
print('patch-ready')
PY

if cmp -s "$INDEX_FILE" "$stage_index" && cmp -s "$VIEW_FILE" "$stage_view" && \
   cmp -s "$JS_FILE" "$stage_js" && cmp -s "$CSS_FILE" "$stage_css"; then
    echo "AllScan Mods are already installed. No changes made."
    exit 0
fi

if command -v php >/dev/null 2>&1; then
    php -l "$stage_index" >/dev/null
    php -l "$stage_view" >/dev/null
else
    echo "WARNING: php was not found; PHP syntax validation was skipped."
fi
if command -v node >/dev/null 2>&1; then
    node --check "$stage_js"
else
    echo "NOTE: node was not found; JavaScript runtime syntax validation was skipped."
fi

timestamp=$(date +%Y%m%d-%H%M%S)
index_backup=$INDEX_FILE.before-allscan-mods-$timestamp
view_backup=$VIEW_FILE.before-allscan-mods-$timestamp
js_backup=$JS_FILE.before-allscan-mods-$timestamp
css_backup=$CSS_FILE.before-allscan-mods-$timestamp
cp -a -- "$INDEX_FILE" "$index_backup"
cp -a -- "$VIEW_FILE" "$view_backup"
cp -a -- "$JS_FILE" "$js_backup"
cp -a -- "$CSS_FILE" "$css_backup"

installed=false
rollback() {
    if [[ $installed != true ]]; then
        cp -a -- "$index_backup" "$INDEX_FILE" 2>/dev/null || true
        cp -a -- "$view_backup" "$VIEW_FILE" 2>/dev/null || true
        cp -a -- "$js_backup" "$JS_FILE" 2>/dev/null || true
        cp -a -- "$css_backup" "$CSS_FILE" 2>/dev/null || true
        echo "ERROR: Installation failed; the original files were restored." >&2
    fi
}
trap rollback ERR

cp -- "$stage_index" "$INDEX_FILE"
cp -- "$stage_view" "$VIEW_FILE"
cp -- "$stage_js" "$JS_FILE"
cp -- "$stage_css" "$CSS_FILE"

grep -Fq 'case "Edit Favorite":' "$INDEX_FILE"
grep -Fq 'Save &amp; Close</button>' "$VIEW_FILE"
[[ $(grep -Ec 'function[[:space:]]+sortFavStats[[:space:]]*\(' "$JS_FILE") -eq 1 ]]
[[ $(grep -Ec 'function[[:space:]]+openFavoriteEditor[[:space:]]*\(' "$JS_FILE") -eq 1 ]]

if command -v php >/dev/null 2>&1; then
    php -l "$INDEX_FILE" >/dev/null
    php -l "$VIEW_FILE" >/dev/null
fi
if command -v node >/dev/null 2>&1; then
    node --check "$JS_FILE"
fi

installed=true
trap - ERR

echo "AllScan Mods installed successfully."
echo "Backups:"
echo "  $index_backup"
echo "  $view_backup"
echo "  $js_backup"
echo "  $css_backup"
echo "Hard-refresh the AllScan page with Ctrl+F5."
