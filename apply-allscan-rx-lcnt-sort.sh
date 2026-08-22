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
JS_FILE=$ALLSCAN_DIR/js/main.js

for required in "$INDEX_FILE" "$JS_FILE"; do
    if [[ ! -f $required ]]; then
        echo "ERROR: Required AllScan file not found: $required" >&2
        exit 1
    fi
done

command -v python3 >/dev/null 2>&1 || {
    echo "ERROR: python3 is required." >&2
    exit 1
}

work_dir=$(mktemp -d /tmp/allscan-rx-lcnt-sort.XXXXXX)
trap 'rm -rf -- "$work_dir"' EXIT

stage_index=$work_dir/index.php
stage_js=$work_dir/main.js
cp -- "$INDEX_FILE" "$stage_index"
cp -- "$JS_FILE" "$stage_js"

python3 - "$stage_index" "$stage_js" <<'PY'
from pathlib import Path
import re
import sys

index_path = Path(sys.argv[1])
js_path = Path(sys.argv[2])
index = index_path.read_text(encoding="utf-8")
js = js_path.read_text(encoding="utf-8")

old_header = "$hdrCols = ['#', 'Node', 'Name', 'Desc', 'Location', '<small>Rx%</small>', '<small>LCnt</small>'];"
new_header = "$hdrCols = ['#', 'Node', 'Name', 'Desc', 'Location', '<small><a href=\"#\" onclick=\"sortFavStats(5); return false;\">Rx%<span id=\"rxSortArrow\"></span></a></small>', '<small><a href=\"#\" onclick=\"sortFavStats(6); return false;\">LCnt<span id=\"lcntSortArrow\"></span></a></small>'];"

header_installed = new_header in index
if not header_installed:
    count = index.count(old_header)
    if count != 1:
        raise SystemExit(
            "ERROR: Expected the stock Favorites header exactly once, but found "
            f"{count}. No files were changed; review this AllScan version before patching."
        )
    index = index.replace(old_header, new_header, 1)

sorter = r'''

// Local modification: client-side sorting for Favorites Rx% and LCnt columns.
var favStatsSortCol = -1;
var favStatsSortAsc = true;

function sortFavStats(col)
{
    var table = document.getElementById('favs');

    if(!table || !table.tBodies.length || table.tBodies[0].rows.length < 2)
        return;

    if(col !== 5 && col !== 6)
        return;

    if(favStatsSortCol === col) {
        favStatsSortAsc = !favStatsSortAsc;
    } else {
        favStatsSortCol = col;
        favStatsSortAsc = false;
    }

    var tbody = table.tBodies[0];
    var rows = Array.from(tbody.rows);
    var sortedRows = rows.map(function(row, index) {
        var text = row.cells[col] ? row.cells[col].textContent.trim() : '';
        var value = parseFloat(text);

        return {
            row: row,
            index: index,
            value: value,
            missing: isNaN(value)
        };
    });

    sortedRows.sort(function(a, b) {
        // Keep rows whose statistics have not arrived yet at the bottom.
        if(a.missing && b.missing)
            return a.index - b.index;
        if(a.missing)
            return 1;
        if(b.missing)
            return -1;
        if(a.value === b.value)
            return a.index - b.index;
        if(favStatsSortAsc)
            return a.value - b.value;
        return b.value - a.value;
    });

    sortedRows.forEach(function(item) {
        tbody.appendChild(item.row);
    });

    var rxArrow = document.getElementById('rxSortArrow');
    var lcntArrow = document.getElementById('lcntSortArrow');

    if(rxArrow)
        rxArrow.textContent = '';
    if(lcntArrow)
        lcntArrow.textContent = '';
    if(col === 5 && rxArrow)
        rxArrow.textContent = favStatsSortAsc ? '▲' : '▼';
    if(col === 6 && lcntArrow)
        lcntArrow.textContent = favStatsSortAsc ? '▲' : '▼';
}
'''

function_defs = len(re.findall(r"\bfunction\s+sortFavStats\s*\(", js))
if function_defs > 1:
    raise SystemExit("ERROR: main.js contains more than one sortFavStats function; no files were changed.")
if function_defs == 0:
    js = js.rstrip() + sorter + "\n"

if new_header not in index:
    raise SystemExit("ERROR: Failed to create the Rx%/LCnt header links.")
if len(re.findall(r"\bfunction\s+sortFavStats\s*\(", js)) != 1:
    raise SystemExit("ERROR: Failed to create exactly one sortFavStats function.")
if "var busy = cells[5];" not in js or "var lcnt = cells[6];" not in js:
    raise SystemExit("ERROR: This AllScan main.js does not use the expected Rx%/LCnt columns; no files were changed.")

index_path.write_text(index, encoding="utf-8")
js_path.write_text(js, encoding="utf-8")
print("already-installed" if header_installed and function_defs == 1 else "patch-ready")
PY

if cmp -s "$INDEX_FILE" "$stage_index" && cmp -s "$JS_FILE" "$stage_js"; then
    echo "AllScan Rx% / LCnt sorting is already installed. No changes made."
    exit 0
fi

if command -v php >/dev/null 2>&1; then
    php -l "$stage_index" >/dev/null
else
    echo "WARNING: php was not found; PHP syntax validation was skipped."
fi

if command -v node >/dev/null 2>&1; then
    node --check "$stage_js"
else
    echo "NOTE: node was not found; JavaScript runtime syntax validation was skipped."
fi

timestamp=$(date +%Y%m%d-%H%M%S)
index_backup=$INDEX_FILE.before-rx-lcnt-sort-$timestamp
js_backup=$JS_FILE.before-rx-lcnt-sort-$timestamp
cp -a -- "$INDEX_FILE" "$index_backup"
cp -a -- "$JS_FILE" "$js_backup"

installed=false
rollback() {
    if [[ $installed != true ]]; then
        cp -a -- "$index_backup" "$INDEX_FILE" 2>/dev/null || true
        cp -a -- "$js_backup" "$JS_FILE" 2>/dev/null || true
        echo "ERROR: Installation failed; the original files were restored." >&2
    fi
}
trap rollback ERR

# Copy over existing files so their ownership and modes remain unchanged.
cp -- "$stage_index" "$INDEX_FILE"
cp -- "$stage_js" "$JS_FILE"

grep -Fq 'onclick="sortFavStats(5); return false;"' "$INDEX_FILE"
grep -Fq 'onclick="sortFavStats(6); return false;"' "$INDEX_FILE"
[[ $(grep -Ec 'function[[:space:]]+sortFavStats[[:space:]]*\(' "$JS_FILE") -eq 1 ]]

if command -v php >/dev/null 2>&1; then
    php -l "$INDEX_FILE" >/dev/null
fi
if command -v node >/dev/null 2>&1; then
    node --check "$JS_FILE"
fi

installed=true
trap - ERR

echo "AllScan Rx% / LCnt sorting installed successfully."
echo "Backups:"
echo "  $index_backup"
echo "  $js_backup"
echo "Hard-refresh the AllScan page with Ctrl+F5."
