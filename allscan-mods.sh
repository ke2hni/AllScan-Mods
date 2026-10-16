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
CONNECT_FILE=$ALLSCAN_DIR/astapi/connect.php
COMMON_FILE=$ALLSCAN_DIR/include/common.php
FAVS_UTILS_FILE=$ALLSCAN_DIR/include/favsUtils.php
SIMPLE_CSS_FILE=$ALLSCAN_DIR/css/simple.css
SIMPLE_INDEX_FILE=$ALLSCAN_DIR/simple/index.php
SIMPLE_JS_FILE=$ALLSCAN_DIR/js/simple.js

for required in "$INDEX_FILE" "$VIEW_FILE" "$JS_FILE" "$CSS_FILE" "$CONNECT_FILE" "$COMMON_FILE"; do
    [[ -f $required ]] || { echo "ERROR: Required AllScan file not found: $required" >&2; exit 1; }
done

allscan_version=$(sed -nE 's/^\$AllScanVersion = "(v[0-9.]+)";.*/\1/p' "$COMMON_FILE")
case "$allscan_version" in
    v1.01) favs_source=$INDEX_FILE ;;
    v1.02|v1.03|v1.04)
        [[ -f $SIMPLE_INDEX_FILE && -f $SIMPLE_JS_FILE ]] || { echo "ERROR: Required TouchGUI files are missing. No files changed." >&2; exit 1; }
        [[ -f $FAVS_UTILS_FILE ]] || { echo "ERROR: Required AllScan file not found: $FAVS_UTILS_FILE" >&2; exit 1; }
        [[ -f $SIMPLE_CSS_FILE ]] || { echo "ERROR: Required AllScan file not found: $SIMPLE_CSS_FILE" >&2; exit 1; }
        favs_source=$FAVS_UTILS_FILE
        ;;
    *) echo "ERROR: Supports AllScan v1.01-v1.04; found ${allscan_version:-unknown}. No files changed." >&2; exit 1 ;;
esac

# PR #37 upstream integration guard. Check the complete feature set rather than
# trusting a version string alone: v1.03 may be either pre- or post-merge;
# v1.04 is the official release incorporating those features.
# A match is read-only and must not create backups or rewrite upstream files.
MODS_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
TOUCHGUI_ACTIVITY_PATCH=$MODS_DIR/lib/touchgui-activity.py

touchgui_activity_present() {
    grep -Fq 'AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.' "$SIMPLE_JS_FILE" &&
    grep -Fq 'AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.' "$SIMPLE_CSS_FILE" &&
    grep -Fq 'function formatTouchguiStatusMessage(msg)' "$SIMPLE_JS_FILE" &&
    grep -Fq 'function getChannelStats()' "$SIMPLE_JS_FILE" &&
    grep -Fq 'function updateChannelActivity(stats)' "$SIMPLE_JS_FILE" &&
    grep -Fq 'function convertActivityRange(value, min, max)' "$SIMPLE_JS_FILE" &&
    grep -Fq 'activity.rxPct' "$SIMPLE_JS_FILE" &&
    grep -Fq 'activity.linkCnt' "$SIMPLE_JS_FILE" &&
    grep -Fq 'channel-stats' "$SIMPLE_JS_FILE" &&
    grep -Fq 'Number(channel.node) < 3000000' "$SIMPLE_JS_FILE" &&
    ! grep -Fq 'simple.txTim[node] = now' "$SIMPLE_JS_FILE" &&
    grep -Fq '.channel-stats' "$SIMPLE_CSS_FILE" &&
    grep -Fq '.channel-btn[data-activity="active"]' "$SIMPLE_CSS_FILE" &&
    grep -Fq 'height:100dvh' "$SIMPLE_CSS_FILE" &&
    grep -Fq '.simple-footer { display:grid; }' "$SIMPLE_CSS_FILE" &&
    grep -Fq '.simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }' "$SIMPLE_CSS_FILE" &&
    grep -Fq '@media (max-width:430px)' "$SIMPLE_CSS_FILE" &&
    grep -Fq '@media (max-width:380px)' "$SIMPLE_CSS_FILE" &&
    grep -Fq 'font-size:9px; line-height:1.15;' "$SIMPLE_CSS_FILE" &&
    grep -Fq '.simple-footer #statmsg { grid-column:1 / -1; text-align:center; }' "$SIMPLE_CSS_FILE" &&
    grep -Fq 'white-space:normal; overflow:visible; overflow-wrap:anywhere; min-width:0;' "$SIMPLE_CSS_FILE"
}

apply_touchgui_activity_live() {
    if touchgui_activity_present; then
        echo "TouchGUI activity colors are already present. No changes made."
        return 0
    fi
    local work_dir stage_js stage_css timestamp js_backup css_backup
    work_dir=$(mktemp -d /tmp/allscan-touchgui-activity.XXXXXX)
    stage_js=$work_dir/simple.js
    stage_css=$work_dir/simple.css
    cp -- "$SIMPLE_JS_FILE" "$stage_js"
    cp -- "$SIMPLE_CSS_FILE" "$stage_css"
    python3 "$TOUCHGUI_ACTIVITY_PATCH" "$stage_js" "$stage_css"
    if command -v node >/dev/null 2>&1; then node --check "$stage_js"; fi
    if cmp -s "$SIMPLE_JS_FILE" "$stage_js" && cmp -s "$SIMPLE_CSS_FILE" "$stage_css"; then
        rm -rf -- "$work_dir"
        echo "TouchGUI activity colors already installed. No changes made."
        return 0
    fi
    timestamp=$(date +%Y%m%d-%H%M%S)
    js_backup=$SIMPLE_JS_FILE.before-touchgui-activity-$timestamp
    css_backup=$SIMPLE_CSS_FILE.before-touchgui-activity-$timestamp
    [[ ! -e $js_backup && ! -e $css_backup ]] || {
        rm -rf -- "$work_dir"
        echo "ERROR: TouchGUI backup path already exists; no files changed." >&2
        return 1
    }
    cp -a -- "$SIMPLE_JS_FILE" "$js_backup"
    cp -a -- "$SIMPLE_CSS_FILE" "$css_backup"
    if ! cp -- "$stage_js" "$SIMPLE_JS_FILE" || ! cp -- "$stage_css" "$SIMPLE_CSS_FILE"; then
        cp -a -- "$js_backup" "$SIMPLE_JS_FILE"
        cp -a -- "$css_backup" "$SIMPLE_CSS_FILE"
        rm -rf -- "$work_dir"
        echo "ERROR: TouchGUI activity installation failed; original files were restored." >&2
        return 1
    fi
    rm -rf -- "$work_dir"
    echo "TouchGUI activity colors installed. Backups: $js_backup and $css_backup"
}

upstream_features_present() {
    [[ $allscan_version == v1.03 || $allscan_version == v1.04 ]] || return 1
    grep -Fq 'case "Edit Favorite":' "$INDEX_FILE" &&
    grep -Fq 'sortFavStats(5)' "$INDEX_FILE" &&
    grep -Fq 'sortFavStats(6)' "$INDEX_FILE" &&
    grep -Fq 'Save &amp; Close</button>' "$VIEW_FILE" &&
    grep -Fq 'id="automondisc"' "$VIEW_FILE" &&
    grep -Fq 'function sortFavStats(' "$JS_FILE" &&
    grep -Fq 'function openFavoriteEditor(' "$JS_FILE" &&
    grep -Fq 'if($automondisc)' "$CONNECT_FILE" &&
    grep -Fq 'Local modification: AllScan Favorites editor dialog.' "$CSS_FILE" &&
    grep -Fq 'function toggleAutodiscPreference()' "$SIMPLE_JS_FILE" &&
    grep -Fq 'id="autodiscBtn"' "$SIMPLE_INDEX_FILE" &&
    grep -Fq 'grid-template-columns:auto 1fr auto;' "$SIMPLE_CSS_FILE" &&
    grep -Fq '$favList[] = [$n, $f->node, $name, $desc, $loc, NBSP, NBSP, $name];' "$FAVS_UTILS_FILE"
}
# v1.04 includes PR #37 upstream. Never run legacy patch transformations on
# v1.04 even if feature markers change; stop until compatibility is reviewed.
if [[ $allscan_version == v1.04 ]] && ! upstream_features_present; then
    echo "ERROR: AllScan v1.04 did not match the reviewed PR #37 feature layout. No Mods patches or backups made. Review the upstream files before proceeding." >&2
    exit 1
fi
if upstream_features_present; then
    echo "AllScan already includes the integrated enhancements (PR #37). Applying/checking the independent TouchGUI activity-color feature."
    apply_touchgui_activity_live
    exit 0
fi

command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 is required." >&2; exit 1; }

report_apache_sqlite_status() {
    local apache_ini sqlite_ok=false
    shopt -s nullglob
    local apache_inis=(/etc/php/*/apache2/php.ini)
    shopt -u nullglob

    if command -v php >/dev/null 2>&1 && ((${#apache_inis[@]} > 0)); then
        for apache_ini in "${apache_inis[@]}"; do
            if php -c "$apache_ini" -m 2>/dev/null | grep -qx 'pdo_sqlite' && \
               php -c "$apache_ini" -m 2>/dev/null | grep -qx 'sqlite3'; then
                sqlite_ok=true
                break
            fi
        done
    fi

    if [[ $sqlite_ok == true ]]; then
        echo "PHP SQLite status: pdo_sqlite and sqlite3 are enabled. AllScan requires both."
    else
        echo "PHP SQLite status: pdo_sqlite and/or sqlite3 are not enabled for Apache, or could not be verified. AllScan requires both; run the combined installer to enable and verify them."
    fi
}

work_dir=$(mktemp -d /tmp/allscan-mods.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT

stage_index=$work_dir/index.php
stage_view=$work_dir/viewUtils.php
stage_js=$work_dir/main.js
stage_css=$work_dir/main.css
stage_connect=$work_dir/connect.php
stage_favs_utils=$work_dir/favsUtils.php
stage_simple_css=$work_dir/simple.css
stage_simple_index=$work_dir/simple-index.php
stage_simple_js=$work_dir/simple.js
cp -- "$INDEX_FILE" "$stage_index"
cp -- "$VIEW_FILE" "$stage_view"
cp -- "$JS_FILE" "$stage_js"
cp -- "$CSS_FILE" "$stage_css"
cp -- "$CONNECT_FILE" "$stage_connect"
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -- "$FAVS_UTILS_FILE" "$stage_favs_utils"; fi
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -- "$SIMPLE_CSS_FILE" "$stage_simple_css"; cp -- "$SIMPLE_INDEX_FILE" "$stage_simple_index"; cp -- "$SIMPLE_JS_FILE" "$stage_simple_js"; fi

python3 - "$stage_index" "$stage_view" "$stage_js" "$stage_css" "$stage_connect" "$stage_favs_utils" "$stage_simple_css" "$stage_simple_index" "$stage_simple_js" "$allscan_version" <<'PY'
from pathlib import Path
import re
import sys

index_path, view_path, js_path, css_path, connect_path = map(Path, sys.argv[1:6])
favs_utils_path = Path(sys.argv[6])
simple_css_path = Path(sys.argv[7])
simple_index_path = Path(sys.argv[8])
simple_js_path = Path(sys.argv[9])
allscan_version = sys.argv[10]
index = index_path.read_text(encoding="utf-8")
view = view_path.read_text(encoding="utf-8")
js = js_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
connect = connect_path.read_text(encoding="utf-8")
has_v102_layout = allscan_version in ("v1.02", "v1.03")
simple_css = simple_css_path.read_text(encoding="utf-8") if has_v102_layout else ""
simple_index = simple_index_path.read_text(encoding="utf-8") if has_v102_layout else ""
simple_js = simple_js_path.read_text(encoding="utf-8") if has_v102_layout else ""

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
favs_utils = favs_utils_path.read_text(encoding="utf-8") if has_v102_layout else ""
if has_v102_layout:
    if old_fav_row in favs_utils:
        favs_utils = replace_once(favs_utils, old_fav_row, new_fav_row, "the v1.02 Favorites row builder")
    elif new_fav_row not in favs_utils:
        raise SystemExit("ERROR: Expected the v1.02 Favorites row builder. No live files were changed.")
elif new_fav_row not in index:
    index = replace_once(index, old_fav_row, new_fav_row, "the Favorites row builder")

new_row_output = '''foreach($favList as $f) {
	$favEditLabel = htmlspecialchars(array_pop($f), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
	$nodeNumAttr = ['1' => 'class="nodeNum" data-fav-label="' . $favEditLabel
		. '" onClick="selectFavorite(this)" onDblClick="connectNode(\\'connect\\')"'];'''
if has_v102_layout:
    old_v102_row_output = '''foreach($favList as $f) {
	$favEditLabel = htmlspecialchars($f[7], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
	$nodeNumAttr = ['1' => 'class="nodeNum" data-fav-label="' . $favEditLabel
		. '" onClick="selectFavorite(this)" onDblClick="connectNode(\\'connect\\')"'];'''
    if old_v102_row_output in index:
        index = replace_once(index, old_v102_row_output, new_row_output, "the previous v1.02 Favorites row renderer")
if new_row_output not in index:
    row_pattern = re.compile(
        r'''foreach\(\$favList as \$f\) \{\s*'''
        r'''\$nodeNumAttr = \['1' => 'class="nodeNum" onClick="setNodeBox\('\.\$f\[1\]\.\'\)" '\s*'''
        r'''\.\s*'onDblClick="connectNode\(\\'connect\\'\)"'\];'''
    )
    if has_v102_layout:
        row_pattern = re.compile(r'''foreach\(\$favList as \$f\) \{\s*\$nodeNumAttr = \['1' => 'class="nodeNum" onClick="setNodeBox\('\.\$f\[1\]\.\'\)" '\s*\.\s*'onDblClick="connectNode\(\\'connect\\'\)"'\];''')
    matches = list(row_pattern.finditer(index))
    if len(matches) != 1:
        raise SystemExit(
            f"ERROR: Expected the stock Favorites row output exactly once, but found {len(matches)}. "
            "No live files were changed."
        )
    index = row_pattern.sub(lambda match: new_row_output, index, count=1)



# Keep the AllScan link visible in the v1.02 TouchGUI portrait header.
old_touch_header = ".topbar {\ngrid-template-columns:1fr auto;\nheight:44px;\n}\n.brand {\ndisplay:none;\n}\n.node-title {\nfont-size:15px;\n}"
new_touch_header = ".topbar {\ngrid-template-columns:auto 1fr auto;\ngap:8px;\npadding:6px 10px;\nheight:44px;\n}\n.brand {\ndisplay:block;\nwhite-space:nowrap;\n}\n.node-title {\ndisplay:none;\nfont-size:15px;\n}\n.node-number {\nfont-size:14px;\n}"
stock_touch_header = ".topbar {\ngrid-template-columns:auto 1fr auto;\ngap:8px;\npadding:6px 10px;\nheight:44px;\n}\n.brand {\ndisplay:block;\nwhite-space:nowrap;\n}\n.node-title {\ndisplay:none;\nfont-size:15px;\n}"
if has_v102_layout and new_touch_header not in simple_css:
    if old_touch_header in simple_css:
        simple_css = replace_once(simple_css, old_touch_header, new_touch_header, "the v1.02 TouchGUI portrait header")
    elif stock_touch_header in simple_css:
        simple_css = replace_once(simple_css, stock_touch_header, new_touch_header, "the v1.02 TouchGUI portrait header")
    else:
        raise SystemExit("ERROR: Expected the stock or previously tested v1.02 TouchGUI portrait header. No live files were changed.")

# Share Disconnect before Connect across the regular page and TouchGUI.
old_checkbox_line = """<input type=checkbox id=\"autodisc\"' . ($gCfg[autodisc_def] ? ' checked' : '') . '><label"""
new_checkbox_line = """<input type=checkbox id=\"autodisc\"' . ($gCfg[autodisc_def] ? ' checked' : '') . ' data-autodisc-default=\"' . ($gCfg[autodisc_def] ? 'true' : 'false') . '\"><label"""
old_checkbox_line_oldmods = """<input type=checkbox id=\"autodisc\"' . ($gCfg[autodisc_def] ? ' checked' : '') . ' data-autodisc-default=\"' . ($gCfg[autodisc_def] ? 'true' : 'false') . '"><label"""
if new_checkbox_line not in view:
    if old_checkbox_line_oldmods in view:
        view = replace_once(view, old_checkbox_line_oldmods, new_checkbox_line, "previous Mods Disconnect before Connect checkbox default")
    elif 'data-autodisc-default=' in view and 'for="autodisc">Disconnect before Connect</label>' in view:
        malformed = "' data-autodisc-default=\"' . ($gCfg[autodisc_def] ? 'true' : 'false') . '><label"
        if malformed not in view:
            raise SystemExit("ERROR: Previous Mods checkbox default could not be upgraded safely. No live files were changed.")
        view = replace_once(view, malformed, "' data-autodisc-default=\"' . ($gCfg[autodisc_def] ? 'true' : 'false') . '\"><label", "previous Mods Disconnect before Connect checkbox default")
    else:
        view = replace_once(view, old_checkbox_line, new_checkbox_line, "Disconnect before Connect checkbox default")

storage_sync = r'''function initAutodiscPreference() {
	var checkbox = document.getElementById('autodisc');
	if(!checkbox)
		return;
	var key = 'allscan.autodisc.' + (document.getElementById('localnode') || {}).value;
	function save(value) {
		try { localStorage.setItem(key, value ? 'true' : 'false'); } catch(e) {}
	}
	function load() {
		try {
			var value = localStorage.getItem(key);
			if(value === 'true' || value === 'false')
				checkbox.checked = value === 'true';
			else {
				checkbox.checked = checkbox.dataset.autodiscDefault === 'true';
				save(checkbox.checked);
			}
		} catch(e) {}
	}
	load();
	checkbox.addEventListener('change', function() { save(checkbox.checked); });
	window.addEventListener('storage', function(event) {
		if(event.key === key && (event.newValue === 'true' || event.newValue === 'false'))
			checkbox.checked = event.newValue === 'true';
	});
}

if(document.readyState === 'loading')
	document.addEventListener('DOMContentLoaded', initAutodiscPreference);
else
	initAutodiscPreference();
'''
if 'function initAutodiscPreference()' not in js:
    js = js.rstrip() + '\n\n' + storage_sync
if 'initAutodiscPreference();' not in js:
    js = js.replace('\t// Handle offline/online events', '\tinitAutodiscPreference();\n\t// Handle offline/online events', 1)

simple_index_marker = """\t\t\t<button id=\"disconnectBtn\" class=\"disconnect-btn\" type=\"button\" disabled>Disconnect</button>"""
simple_index_control = """\t\t\t<div class=\"status-actions\">
\t\t\t\t<button id=\"autodiscBtn\" class=\"autodisc-btn\" type=\"button\" aria-pressed=\"true\">Disconnect before Connect: ON</button>
\t\t\t\t<button id=\"disconnectBtn\" class=\"disconnect-btn\" type=\"button\" disabled>Disconnect</button>
\t\t\t</div>"""
if has_v102_layout and simple_index_control not in simple_index:
    simple_index = replace_once(simple_index, simple_index_marker, simple_index_control, "TouchGUI disconnect preference button")
simple_index_cfg_marker = """\tcanModify: <?php echo $canModify ? 'true' : 'false'; ?>,"""
simple_index_cfg_new = """\tcanModify: <?php echo $canModify ? 'true' : 'false'; ?>,
\tautodiscDefault: <?php echo $gCfg[autodisc_def] ? 'true' : 'false'; ?>,"""
if has_v102_layout and simple_index_cfg_new not in simple_index:
    simple_index = replace_once(simple_index, simple_index_cfg_marker, simple_index_cfg_new, "TouchGUI server disconnect preference default")

simple_js_obj_marker = """\tcanModify: false,
\tbaseUrl: '',"""
simple_js_obj_new = """\tcanModify: false,
\tautodiscDefault: true,
\tautodisc: true,
\tautodiscBtn: null,
\tautodiscStorageKey: '',
\tbaseUrl: '',"""
if has_v102_layout and simple_js_obj_new not in simple_js:
    simple_js = replace_once(simple_js, simple_js_obj_marker, simple_js_obj_new, "TouchGUI preference state")
simple_js_init_marker = """\tsimple.canModify = !!cfg.canModify;
\tsimple.baseUrl = cfg.baseUrl || '';"""
simple_js_init_new = """\tsimple.canModify = !!cfg.canModify;
\tsimple.autodiscDefault = cfg.autodiscDefault !== false;
\tsimple.baseUrl = cfg.baseUrl || '';"""
if has_v102_layout and simple_js_init_new not in simple_js:
    simple_js = replace_once(simple_js, simple_js_init_marker, simple_js_init_new, "TouchGUI preference initialization")
simple_js_element_marker = """\tsimple.disconnectBtn = document.getElementById('disconnectBtn');"""
simple_js_element_new = """\tsimple.disconnectBtn = document.getElementById('disconnectBtn');
\tsimple.autodiscBtn = document.getElementById('autodiscBtn');
\tsimple.autodiscStorageKey = 'allscan.autodisc.' + simple.localNode;
\tinitAutodiscPreference();"""
if has_v102_layout and 'simple.autodiscBtn = document.getElementById' not in simple_js:
    simple_js = replace_once(simple_js, simple_js_element_marker, simple_js_element_new, "TouchGUI preference button setup")
simple_js_bind_marker = """\tsimple.disconnectBtn.addEventListener('click', function() {"""
simple_js_bind_new = """\tsimple.autodiscBtn.addEventListener('click', toggleAutodiscPreference);
\twindow.addEventListener('storage', handleAutodiscStorage);
\tsimple.disconnectBtn.addEventListener('click', function() {"""
if has_v102_layout and 'simple.autodiscBtn.addEventListener' not in simple_js:
    simple_js = replace_once(simple_js, simple_js_bind_marker, simple_js_bind_new, "TouchGUI preference button event")
simple_js_connect_old = """\t\t+ '&autodisc=true');"""
simple_js_connect_new = """\t\t+ '&autodisc=' + simple.autodisc);"""
if has_v102_layout and simple_js_connect_new not in simple_js:
    simple_js = replace_once(simple_js, simple_js_connect_old, simple_js_connect_new, "TouchGUI connect request disconnect setting")
simple_js_pref_funcs = r'''
function initAutodiscPreference() {
	try {
		var value = localStorage.getItem(simple.autodiscStorageKey);
		if(value === 'true' || value === 'false')
			simple.autodisc = value === 'true';
		else {
			simple.autodisc = simple.autodiscDefault;
			localStorage.setItem(simple.autodiscStorageKey, simple.autodisc ? 'true' : 'false');
		}
	} catch(e) {
		simple.autodisc = simple.autodiscDefault;
	}
	updateAutodiscButton();
}

function saveAutodiscPreference() {
	try { localStorage.setItem(simple.autodiscStorageKey, simple.autodisc ? 'true' : 'false'); } catch(e) {}
	updateAutodiscButton();
}

function toggleAutodiscPreference() {
	simple.autodisc = !simple.autodisc;
	saveAutodiscPreference();
}

function updateAutodiscButton() {
	if(!simple.autodiscBtn)
		return;
	simple.autodiscBtn.textContent = 'Disconnect before Connect: ' + (simple.autodisc ? 'ON' : 'OFF');
	simple.autodiscBtn.setAttribute('aria-pressed', simple.autodisc ? 'true' : 'false');
}

function handleAutodiscStorage(event) {
	if(event.key === simple.autodiscStorageKey && (event.newValue === 'true' || event.newValue === 'false')) {
		simple.autodisc = event.newValue === 'true';
		updateAutodiscButton();
	}
}
'''
if has_v102_layout and 'function toggleAutodiscPreference()' not in simple_js:
    simple_js = simple_js.rstrip() + '\n' + simple_js_pref_funcs

simple_css_marker = '.status-panel,\n.warning-panel,\n.readonly-panel {'
simple_css_addition = r'''
.status-actions {
display:flex;
justify-content:flex-end;
align-items:center;
gap:8px;
min-width:0;
}
.autodisc-btn {
min-height:44px;
max-width:100%;
padding:6px 10px;
border:2px solid #526a7d;
border-radius:6px;
color:#edf4fa;
background:#263646;
font-size:14px;
font-weight:bold;
}
.autodisc-btn[aria-pressed="true"] {
border-color:#b88732;
background:#493715;
}
.autodisc-btn[aria-pressed="false"] {
border-color:#36865a;
background:#173b29;
}
'''
if '.status-actions {' not in simple_css:
    simple_css = simple_css.replace(simple_css_marker, simple_css_addition + '\n' + simple_css_marker, 1)
simple_css = simple_css.replace('''grid-template-columns:1fr auto;
align-items:center;''','''grid-template-columns:minmax(0, 1fr) auto;
align-items:center;''',1)
mobile_marker = '''.disconnect-btn,
.disconnect-all-btn,
.login-btn {
min-width:120px;
min-height:50px;
font-size:15px;
}'''
mobile_new = '''.disconnect-btn,
.disconnect-all-btn,
.login-btn {
min-width:120px;
min-height:50px;
font-size:15px;
}
.status-panel {
grid-template-columns:minmax(0, 1fr);
}
.status-actions {
width:100%;
justify-content:flex-start;
gap:6px;
}
.status-actions .autodisc-btn {
flex:1 1 auto;
min-width:0;
min-height:42px;
padding:5px 7px;
font-size:12px;
}
.status-actions .disconnect-btn {
flex:0 0 auto;
min-width:92px;
min-height:42px;
padding:5px 8px;
font-size:14px;
}
.warning-panel,
.readonly-panel {
grid-template-columns:minmax(0, 1fr);
}
.warning-panel {
gap:6px;
}
.disconnect-all-btn {
width:100%;
min-width:0;
min-height:44px;
padding:4px 7px;
font-size:14px;
}'''
if has_v102_layout and mobile_new not in simple_css:
    simple_css = replace_once(simple_css, mobile_marker, mobile_new, "TouchGUI compact status controls")




# Server-side Edit Favorite action.
edit_case_marker = '\tcase "Edit Favorite":'
edit_case = r'''	case "Edit Favorite":
		$originalNode = isset($parms['originalnode']) ? trim($parms['originalnode']) : '';
		$newLabel = isset($parms['editlabel']) ? trim($parms['editlabel']) : '';
		$newOrder = isset($parms['editorder']) ? trim($parms['editorder']) : '';
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
		if(!preg_match('/^[1-9][0-9]*$/', $newOrder)) {
			$msg[] = error("Order must be a positive number.");
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
		$favoritePairs = [];
		foreach($favs as $i => $line) {
			if(preg_match('/^\\s*label\\[\\]\\s*=\\s*".*"\\s*$/', $line) && isset($favs[$i + 1]) && preg_match($cmdPattern, $favs[$i + 1]))
				$favoritePairs[] = [$i, $i + 1];
		}
		$currentOrder = null;
		foreach($favoritePairs as $pos => $pair) if($pair[0] === $labelLine) $currentOrder = $pos + 1;
		if($currentOrder === null || (int)$newOrder > count($favoritePairs)) {
			$msg[] = error("Order must be between 1 and " . count($favoritePairs) . ".");
			break;
		}
		$backup = $favsFile . '.before-edit-' . date('Ymd-His');
		if(!copy($favsFile, $backup)) {
			$msg[] = error("Unable to create Favorites backup $backup.");
			break;
		}
		$favs[$labelLine] = 'label[] = "' . $newLabel . ' ' . $node . '"';
		$favs[$matchLine] = 'cmd[] = "rpt cmd %node% ilink 3 ' . $node . '"';
		if((int)$newOrder !== $currentOrder) {
			$pair = [$favs[$labelLine], $favs[$matchLine]];
			$remaining = [];
			foreach($favoritePairs as $p) if($p[0] !== $labelLine) $remaining[] = [$favs[$p[0]], $favs[$p[1]]];
			array_splice($remaining, (int)$newOrder - 1, 0, [$pair]);
			foreach($favoritePairs as $k => $p) { $favs[$p[0]] = $remaining[$k][0]; $favs[$p[1]] = $remaining[$k][1]; }
		}
		if(!writeFileLines($favsFile, $favs, $msg)) {
			copy($backup, $favsFile);
			break;
		}
		if(parse_ini_file($favsFile, true) === false) {
			copy($backup, $favsFile);
			$msg[] = error("Edited Favorites file failed validation; the original was restored.");
			break;
		}
		$msg[] = "Favorite node $originalNode updated to node $node with label: $newLabel and order: $newOrder";
		$msg[] = "Backup saved as $backup";
		break;

'''
if edit_case_marker not in index:
    index = replace_once(index, '\tcase "Delete Favorite":', edit_case + '\tcase "Delete Favorite":', "Delete Favorite action")
else:
    index, replaced = re.subn(r'\tcase "Edit Favorite":.*?(?=\tcase "Delete Favorite":)', lambda match: edit_case, index, count=1, flags=re.DOTALL)
    if replaced != 1:
        raise SystemExit("ERROR: Existing Edit Favorite action could not be upgraded safely. No live files were changed.")

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
<input type=hidden id="editorder" name="editorder" value="">
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
<label for="favoriteEditOrder">Order</label>
<input type="number" min="1" step="1" id="favoriteEditOrder">
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

# Upgrade an already-installed editor dialog that predates the Order field.
if 'id="editorder"' not in view:
    view = replace_once(view, '<input type=hidden id="editlabel" name="editlabel" value="">', '<input type=hidden id="editlabel" name="editlabel" value="">\n<input type=hidden id="editorder" name="editorder" value="">', "the existing edit hidden fields")
if 'id="favoriteEditOrder"' not in view:
    view = replace_once(view, '<label for="favoriteEditLabel">Friendly Name/Label</label>', '<label for="favoriteEditOrder">Order</label>\n<input type="number" min="1" step="1" id="favoriteEditOrder">\n<label for="favoriteEditLabel">Friendly Name/Label</label>', "the existing Favorites editor fields")

# Independent Disconnect before Monitor option. Keep all three checkboxes together.
monitor_checkbox = '''<input type=checkbox id="automondisc"><label
\tfor="automondisc">Disconnect before Monitor</label>'''
permanent_checkbox = '''<input type=checkbox id="permanent"><label for="permanent">Permanent</label>&nbsp;'''
autodisc_checkbox = '''<input type=checkbox id="autodisc"' . ($gCfg[autodisc_def] ? ' checked' : '') . ' data-autodisc-default="' . ($gCfg[autodisc_def] ? 'true' : 'false') . '"><label
\tfor="autodisc">Disconnect before Connect</label>'''
base_checkbox_row = permanent_checkbox + '\n' + autodisc_checkbox
old_two_line_row = base_checkbox_row + '\n<br>\n' + monitor_checkbox
unwrapped_checkbox_row = base_checkbox_row + '&nbsp;\n' + monitor_checkbox
final_checkbox_row = '<span style="white-space:nowrap">' + unwrapped_checkbox_row + '</span>'
if final_checkbox_row in view:
    pass
elif old_two_line_row in view:
    view = replace_once(view, old_two_line_row, final_checkbox_row, "two-line Monitor checkbox layout")
elif unwrapped_checkbox_row in view:
    view = replace_once(view, unwrapped_checkbox_row, final_checkbox_row, "unwrapped Monitor checkbox layout")
elif monitor_checkbox not in view:
    view = replace_once(view, base_checkbox_row, final_checkbox_row, "existing checkbox row")

old_connect_js = '''\t// Disconnect before Connect checkbox. Only applies if conncnt > 0
\tvar autodisc = document.getElementById('autodisc').checked;
\tif(conncnt.value < 1)
\t\tautodisc = false;
\tparms = 'remotenode='+remoteNode + '&perm='+perm + '&button='+button + '&localnode='+localNode + '&autodisc='+autodisc;'''
new_connect_js = '''\t// Independent disconnect-before actions. They apply only when links are connected.
\tvar autodisc = document.getElementById('autodisc').checked;
\tvar automondisc = (button === 'monitor') && document.getElementById('automondisc').checked;
\tif(conncnt.value < 1) {
\t\tautodisc = false;
\t\tautomondisc = false;
\t}
\tparms = 'remotenode='+remoteNode + '&perm='+perm + '&button='+button + '&localnode='+localNode
\t\t+ '&autodisc='+autodisc + '&automondisc='+automondisc;'''
if new_connect_js not in js:
    js = replace_once(js, old_connect_js, new_connect_js, "connectNode disconnect options")

old_connect_fields = "$fields = ['remotenode', 'button', 'localnode', 'perm', 'autodisc'];"
new_connect_fields = "$fields = ['remotenode', 'button', 'localnode', 'perm', 'autodisc', 'automondisc'];"
if new_connect_fields not in connect:
    connect = replace_once(connect, old_connect_fields, new_connect_fields, "connect.php request-field list")

old_connect_bool = "$autodisc = ($autodisc === 'true');"
new_connect_bool = "$autodisc = ($autodisc === 'true');\n$automondisc = ($automondisc === 'true');"
if new_connect_bool not in connect:
    connect = replace_once(connect, old_connect_bool, new_connect_bool, "autodisc boolean conversion")

old_monitor_action = '''\tcase 'monitor':
\t\tif($perm) {'''
new_monitor_action = '''\tcase 'monitor':
\t\tif($automondisc) {
\t\t\techo "Disconnect all nodes from $localnode before Monitor...";
\t\t\t$resp = $ami->command($fp, "rpt cmd $localnode ilink 6 0");
\t\t\techo $resp . BR;
\t\t\tusleep(500000);
\t\t}
\t\tif($perm) {'''
if new_monitor_action not in connect:
    connect = replace_once(connect, old_monitor_action, new_monitor_action, "Monitor action")

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

editor_marker = '// Local modification: AllScan-styled Favorites editor with Node, Order, and Friendly Label fields.'
editor_js = r'''

// Local modification: AllScan-styled Favorites editor with Node, Order, and Friendly Label fields.
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
	var orderInput = document.getElementById('favoriteEditOrder');
	nodeInput.value = rnode.dataset.favoriteNode || '';
	labelInput.value = rnode.dataset.favoriteLabel || '';
	var favCells = document.querySelectorAll('#favs td.nodeNum');
	for(var oi = 0; oi < favCells.length; oi++) if(favCells[oi].textContent.trim() === (rnode.dataset.favoriteNode || '')) { orderInput.value = oi + 1; break; }
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
	var newOrder = document.getElementById('favoriteEditOrder').value.trim();
	if(!/^[0-9]{4,8}$/.test(newNode)) {
		alert('Node number must contain 4 to 8 digits.');
		return false;
	}
	if(!newLabel || newLabel.length > 120 || /["\r\n]/.test(newLabel)) {
		alert('Friendly label must be 1 to 120 characters and cannot contain double quotes or line breaks.');
		return false;
	}
	if(!/^[1-9][0-9]*$/.test(newOrder)) { alert('Order must be a positive number.'); return false; }
	document.getElementById('originalnode').value = originalNode;
	document.getElementById('editlabel').value = newLabel;
	document.getElementById('editorder').value = newOrder;
	rnode.value = newNode;
	return true;
}
document.addEventListener('keydown', function(event) {
	var modal = document.getElementById('favoriteEditModal');
	if(event.key === 'Escape' && modal && !modal.hidden) closeFavoriteEditor();
});
'''
if editor_marker not in js:
    old_editor_markers = [
        '// Local modification: AllScan-styled Favorites editor with Node and Friendly Label fields.',
        '// Local modification: select and safely edit an AllScan Favorite from the main page.',
    ]
    old_positions = [js.index(marker) for marker in old_editor_markers if marker in js]
    if old_positions:
        js = js[:min(old_positions)].rstrip()
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
    'friendly label does not render as extra cell': 'htmlspecialchars(array_pop($f)' in index,
    'Save & Close dialog': final_view_marker in view,
    'sorter function': len(re.findall(r'\bfunction\s+sortFavStats\s*\(', js)) == 1,
    'editor function': len(re.findall(r'\bfunction\s+openFavoriteEditor\s*\(', js)) == 1,
    'editor CSS': css_marker in css,
    'Rx% live column': 'var busy = cells[5];' in js,
    'LCnt live column': 'var lcnt = cells[6];' in js,
    'Favorites label source': not has_v102_layout or new_fav_row in favs_utils,
    'TouchGUI portrait header': not has_v102_layout or new_touch_header in simple_css,
    'TouchGUI disconnect toggle': (not has_v102_layout) or ('id="autodiscBtn"' in simple_index and 'function toggleAutodiscPreference()' in simple_js and "+ '&autodisc=' + simple.autodisc)" in simple_js),
    'Monitor checkbox': view.count('id="automondisc"') == 1,
    'one-line checkbox row': final_checkbox_row in view,
    'Monitor JavaScript flag': js.count("var automondisc = (button === 'monitor')") == 1,
    'Monitor request parameter': js.count("'&automondisc='+automondisc") == 1,
    'Monitor API field': connect.count("'automondisc'") == 1,
    'Monitor API boolean': connect.count("$automondisc = ($automondisc === 'true');") == 1,
    'Monitor disconnect action': connect.count('if($automondisc)') == 1,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('ERROR: Staged validation failed: ' + ', '.join(failed))

index_path.write_text(index, encoding="utf-8")
view_path.write_text(view, encoding="utf-8")
js_path.write_text(js, encoding="utf-8")
css_path.write_text(css, encoding="utf-8")
connect_path.write_text(connect, encoding="utf-8")
if has_v102_layout: favs_utils_path.write_text(favs_utils, encoding="utf-8")
if has_v102_layout: simple_css_path.write_text(simple_css, encoding="utf-8")
if has_v102_layout: simple_index_path.write_text(simple_index, encoding="utf-8")
if has_v102_layout: simple_js_path.write_text(simple_js, encoding="utf-8")
print('patch-ready')
PY

if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then
    python3 "$TOUCHGUI_ACTIVITY_PATCH" "$stage_simple_js" "$stage_simple_css"
fi

if cmp -s "$INDEX_FILE" "$stage_index" && cmp -s "$VIEW_FILE" "$stage_view" && \
   cmp -s "$JS_FILE" "$stage_js" && cmp -s "$CSS_FILE" "$stage_css" && \
   cmp -s "$CONNECT_FILE" "$stage_connect" && \
   { [[ $allscan_version != v1.02 && $allscan_version != v1.03 ]] || { cmp -s "$FAVS_UTILS_FILE" "$stage_favs_utils" && cmp -s "$SIMPLE_CSS_FILE" "$stage_simple_css" && cmp -s "$SIMPLE_INDEX_FILE" "$stage_simple_index" && cmp -s "$SIMPLE_JS_FILE" "$stage_simple_js"; }; }; then
    echo "AllScan Mods are already installed. No changes made."
    report_apache_sqlite_status
    exit 0
fi

if command -v php >/dev/null 2>&1; then
    php -l "$stage_index" >/dev/null
    php -l "$stage_view" >/dev/null
    php -l "$stage_connect" >/dev/null
    if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then php -l "$stage_favs_utils" >/dev/null; php -l "$stage_simple_index" >/dev/null; fi
else
    echo "WARNING: php was not found; PHP syntax validation was skipped."
fi
if command -v node >/dev/null 2>&1; then
    node --check "$stage_js"
    if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then node --check "$stage_simple_js"; fi
else
    echo "NOTE: node was not found; JavaScript runtime syntax validation was skipped."
fi

timestamp=$(date +%Y%m%d-%H%M%S)
index_backup=$INDEX_FILE.before-allscan-mods-$timestamp
view_backup=$VIEW_FILE.before-allscan-mods-$timestamp
js_backup=$JS_FILE.before-allscan-mods-$timestamp
css_backup=$CSS_FILE.before-allscan-mods-$timestamp
connect_backup=$CONNECT_FILE.before-allscan-mods-$timestamp
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then favs_utils_backup=$FAVS_UTILS_FILE.before-allscan-mods-$timestamp; fi
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then simple_css_backup=$SIMPLE_CSS_FILE.before-allscan-mods-$timestamp; simple_index_backup=$SIMPLE_INDEX_FILE.before-allscan-mods-$timestamp; simple_js_backup=$SIMPLE_JS_FILE.before-allscan-mods-$timestamp; fi
cp -a -- "$INDEX_FILE" "$index_backup"
cp -a -- "$VIEW_FILE" "$view_backup"
cp -a -- "$JS_FILE" "$js_backup"
cp -a -- "$CSS_FILE" "$css_backup"
cp -a -- "$CONNECT_FILE" "$connect_backup"
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -a -- "$FAVS_UTILS_FILE" "$favs_utils_backup"; fi
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -a -- "$SIMPLE_CSS_FILE" "$simple_css_backup"; cp -a -- "$SIMPLE_INDEX_FILE" "$simple_index_backup"; cp -a -- "$SIMPLE_JS_FILE" "$simple_js_backup"; fi

installed=false
rollback() {
    if [[ $installed != true ]]; then
        cp -a -- "$index_backup" "$INDEX_FILE" 2>/dev/null || true
        cp -a -- "$view_backup" "$VIEW_FILE" 2>/dev/null || true
        cp -a -- "$js_backup" "$JS_FILE" 2>/dev/null || true
        cp -a -- "$css_backup" "$CSS_FILE" 2>/dev/null || true
        cp -a -- "$connect_backup" "$CONNECT_FILE" 2>/dev/null || true
        if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -a -- "$favs_utils_backup" "$FAVS_UTILS_FILE" 2>/dev/null || true; fi
        if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -a -- "$simple_css_backup" "$SIMPLE_CSS_FILE" 2>/dev/null || true; cp -a -- "$simple_index_backup" "$SIMPLE_INDEX_FILE" 2>/dev/null || true; cp -a -- "$simple_js_backup" "$SIMPLE_JS_FILE" 2>/dev/null || true; fi
        echo "ERROR: Installation failed; the original files were restored." >&2
    fi
}
trap rollback ERR

cp -- "$stage_index" "$INDEX_FILE"
cp -- "$stage_view" "$VIEW_FILE"
cp -- "$stage_js" "$JS_FILE"
cp -- "$stage_css" "$CSS_FILE"
cp -- "$stage_connect" "$CONNECT_FILE"
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -- "$stage_favs_utils" "$FAVS_UTILS_FILE"; fi
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then cp -- "$stage_simple_css" "$SIMPLE_CSS_FILE"; cp -- "$stage_simple_index" "$SIMPLE_INDEX_FILE"; cp -- "$stage_simple_js" "$SIMPLE_JS_FILE"; fi

grep -Fq 'case "Edit Favorite":' "$INDEX_FILE"
grep -Fq 'Save &amp; Close</button>' "$VIEW_FILE"
grep -Fq 'Disconnect before Monitor</label>' "$VIEW_FILE"
grep -Fq 'if($automondisc)' "$CONNECT_FILE"
[[ $(grep -Ec 'function[[:space:]]+sortFavStats[[:space:]]*\(' "$JS_FILE") -eq 1 ]]
[[ $(grep -Ec 'function[[:space:]]+openFavoriteEditor[[:space:]]*\(' "$JS_FILE") -eq 1 ]]

if command -v php >/dev/null 2>&1; then
    php -l "$INDEX_FILE" >/dev/null
    php -l "$VIEW_FILE" >/dev/null
php -l "$CONNECT_FILE" >/dev/null
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then php -l "$FAVS_UTILS_FILE" >/dev/null; php -l "$SIMPLE_INDEX_FILE" >/dev/null; fi
fi
if command -v node >/dev/null 2>&1; then
    node --check "$JS_FILE"
    if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then node --check "$SIMPLE_JS_FILE"; fi
fi

installed=true
trap - ERR

echo "AllScan Mods installed successfully."
report_apache_sqlite_status
echo "Backups:"
echo "  $index_backup"
echo "  $view_backup"
echo "  $js_backup"
echo "  $css_backup"
echo "  $connect_backup"
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then echo "  $favs_utils_backup"; fi
if [[ $allscan_version == v1.02 || $allscan_version == v1.03 ]]; then echo "  $simple_css_backup"; echo "  $simple_index_backup"; echo "  $simple_js_backup"; fi
echo "Hard-refresh the AllScan page with Ctrl+F5."
