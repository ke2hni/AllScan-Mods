#!/usr/bin/env bash
# AllScan standalone uninstaller version: v2
set -Eeuo pipefail
umask 077

SCRIPT_NAME=${0##*/}
APP_PATH=''
BACKUP_DIR=/var/backups/allscan-uninstall
CHECK_ONLY=false
REMOVE_DB=false
ALLOW_CUSTOM_ROOT=false

usage() {
    cat <<EOF
Usage: sudo ./$SCRIPT_NAME [--check] [--path ALLSCAN_DIR] [--backup-dir DIR] [--remove-db] [--allow-custom-root]

  --check             Show the exact plan without changing files.
  --path ALLSCAN_DIR  Select one AllScan installation. If omitted, a single
                      conventional install is selected automatically.
  --backup-dir DIR    Recovery archive directory (default: $BACKUP_DIR).
  --remove-db         Also remove this instance's /etc/allscan/<folder>.db.
  --allow-custom-root Permit an explicit --path outside /var/www/html and /srv/http.
  -h, --help          Show this help.

The app directory is always archived before removal. Shared AllScan data and
system packages are preserved.
EOF
}

while (($#)); do
    case "$1" in
        --check) CHECK_ONLY=true; shift ;;
        --path)
            (($# >= 2)) || { echo "ERROR: --path requires a directory." >&2; exit 2; }
            APP_PATH=$2
            shift 2
            ;;
        --backup-dir)
            (($# >= 2)) || { echo "ERROR: --backup-dir requires a directory." >&2; exit 2; }
            BACKUP_DIR=$2
            shift 2
            ;;
        --remove-db) REMOVE_DB=true; shift ;;
        --allow-custom-root) ALLOW_CUSTOM_ROOT=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERROR: Unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
done

if ((EUID != 0)); then
    echo "ERROR: Run this script with sudo." >&2
    exit 1
fi

for command_name in realpath tar grep mktemp; do
    command -v "$command_name" >/dev/null 2>&1 || {
        echo "ERROR: Required command not found: $command_name" >&2
        exit 1
    }
done

if [[ -z $APP_PATH ]]; then
    candidates=()
    for candidate in /var/www/html/allscan /srv/http/allscan; do
        if [[ -d $candidate && -f $candidate/include/common.php ]]; then candidates+=("$candidate"); fi
    done
    if ((${#candidates[@]} == 0)); then
        echo "ERROR: No conventional AllScan installation found. Specify --path." >&2
        exit 1
    elif ((${#candidates[@]} > 1)); then
        echo "ERROR: Multiple conventional AllScan installations found; specify one with --path:" >&2
        printf '  %s\n' "${candidates[@]}" >&2
        exit 1
    fi
    APP_PATH=${candidates[0]}
fi

[[ $APP_PATH == /* ]] || { echo "ERROR: --path must be absolute." >&2; exit 1; }
[[ ! -L $APP_PATH ]] || { echo "ERROR: Refusing a symlinked AllScan path: $APP_PATH" >&2; exit 1; }
[[ -d $APP_PATH ]] || { echo "ERROR: AllScan directory not found: $APP_PATH" >&2; exit 1; }
APP_PATH=$(realpath -e -- "$APP_PATH")
APP_NAME=${APP_PATH##*/}
APP_PARENT=${APP_PATH%/*}
[[ -n $APP_NAME && $APP_PATH != / && $APP_PATH != /var/www/html && $APP_PATH != /srv/http ]] || {
    echo "ERROR: Refusing an unsafe target path: $APP_PATH" >&2
    exit 1
}
[[ -f $APP_PATH/include/common.php && -f $APP_PATH/index.php ]] || {
    echo "ERROR: The selected directory does not have the AllScan application structure." >&2
    exit 1
}
grep -Eq '^\$AllScanVersion = "v[0-9.]+";' "$APP_PATH/include/common.php" || {
    echo "ERROR: The selected directory has no recognized AllScan version marker." >&2
    exit 1
}
ALLSCAN_VERSION=$(sed -nE 's/^\$AllScanVersion = "(v[0-9.]+)";.*/\1/p' "$APP_PATH/include/common.php")

case "$APP_PARENT" in
    /var/www/html|/srv/http) ;;
    *)
        if [[ $ALLOW_CUSTOM_ROOT != true ]]; then
            echo "ERROR: The target is outside /var/www/html and /srv/http." >&2
            echo "For a confirmed custom web root, pass --allow-custom-root with --path." >&2
            exit 1
        fi
        ;;
esac

DB_FILE=/etc/allscan/$APP_NAME.db
SHARED_DB_INSTANCE=false
for other_root in /var/www/html /srv/http; do
    other_app=$other_root/$APP_NAME
    if [[ $other_app != "$APP_PATH" && -f $other_app/include/common.php ]]; then SHARED_DB_INSTANCE=true; fi
done
if [[ $REMOVE_DB == true && $SHARED_DB_INSTANCE == true ]]; then
    echo "ERROR: Another conventional AllScan instance named $APP_NAME uses the same database: $DB_FILE" >&2
    echo 'Remove neither database nor sibling instance with this run.' >&2
    exit 1
fi
if [[ $REMOVE_DB == true && ! -f $DB_FILE ]]; then
    echo "NOTE: The instance database does not exist: $DB_FILE"
fi

BACKUP_DIR=$(realpath -m -- "$BACKUP_DIR")
case "$BACKUP_DIR/" in
    "$APP_PATH/"*|"$APP_PARENT/"*) echo "ERROR: Backup directory must be outside the AllScan web root and installation." >&2; exit 1 ;;
esac

printf 'AllScan uninstaller v2\n'
printf 'Instance: %s (%s)\n' "$APP_PATH" "$ALLSCAN_VERSION"
printf 'Recovery archive directory: %s\n' "$BACKUP_DIR"
printf 'Instance database: %s\n' "$DB_FILE"
if [[ $REMOVE_DB == true ]]; then
    printf 'Database action: remove after backing it up\n'
else
    printf 'Database action: keep\n'
fi
printf 'Shared data action: keep /etc/allscan/asdb.txt, shared favorites files, and external favorites files\n'
printf 'System action: leave packages, services, web-server configuration, and optional DTMF files unchanged\n'

if [[ $CHECK_ONLY == true ]]; then
    echo 'CHECK ONLY: No files or system state changed.'
    exit 0
fi

printf 'Type "UNINSTALL %s" to archive and remove this AllScan instance: ' "$APP_NAME"
IFS= read -r confirmation || { echo; echo 'ERROR: No confirmation received; nothing changed.' >&2; exit 1; }
[[ $confirmation == "UNINSTALL $APP_NAME" ]] || { echo 'Canceled; nothing changed.'; exit 0; }

if [[ -e $BACKUP_DIR && ! -d $BACKUP_DIR ]]; then
    echo "ERROR: Backup path exists and is not a directory: $BACKUP_DIR" >&2
    exit 1
fi
mkdir -p -- "$BACKUP_DIR"
chmod 700 -- "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE=$BACKUP_DIR/allscan-$APP_NAME-before-uninstall-$TIMESTAMP.tar.gz
[[ ! -e $ARCHIVE ]] || { echo "ERROR: Recovery archive already exists: $ARCHIVE" >&2; exit 1; }

archive_paths=("${APP_PATH#/}")
if [[ $REMOVE_DB == true && -f $DB_FILE ]]; then archive_paths+=("${DB_FILE#/}"); fi
if ! tar -czf "$ARCHIVE" -C / --numeric-owner "${archive_paths[@]}"; then
    rm -f -- "$ARCHIVE"
    echo 'ERROR: Recovery archive creation failed; the AllScan installation was not removed.' >&2
    exit 1
fi
ARCHIVE_LIST=$(mktemp "$BACKUP_DIR/.allscan-archive-list.XXXXXX")
if ! tar -tzf "$ARCHIVE" > "$ARCHIVE_LIST" || \
   { ! grep -Fxq -- "${APP_PATH#/}/" "$ARCHIVE_LIST" && ! grep -Fxq -- "${APP_PATH#/}" "$ARCHIVE_LIST"; }; then
    rm -f -- "$ARCHIVE_LIST"
    rm -f -- "$ARCHIVE"
    echo 'ERROR: Recovery archive verification failed; the AllScan installation was not removed.' >&2
    exit 1
fi
rm -f -- "$ARCHIVE_LIST"
chmod 600 -- "$ARCHIVE"
echo "Verified recovery archive: $ARCHIVE"

if ! rm -rf -- "$APP_PATH"; then
    echo 'ERROR: Could not remove the AllScan directory. Restore from the archive if needed.' >&2
    exit 1
fi
if [[ $REMOVE_DB == true && -f $DB_FILE ]] && ! rm -f -- "$DB_FILE"; then
    echo 'ERROR: The app directory was removed but its database could not be removed.' >&2
    echo "The verified recovery archive contains the app and database: $ARCHIVE" >&2
    exit 1
fi

echo "PASS: AllScan $APP_NAME ($ALLSCAN_VERSION) was removed."
echo "Recovery archive: $ARCHIVE"
if [[ $REMOVE_DB != true ]]; then echo "Instance database retained: $DB_FILE"; fi
echo 'Shared AllScan data and system packages were retained.'
