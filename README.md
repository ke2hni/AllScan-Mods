<div align="center">

# AllScan Mods

### Favorites editing, live Rx% / LCnt sorting, and safer monitoring for AllScan

![Platform](https://img.shields.io/badge/Platform-AllStarLink%203-0b7285?style=for-the-badge)
![Debian](https://img.shields.io/badge/Debian-12%20%7C%2013-a81d33?style=for-the-badge&logo=debian&logoColor=white)
![AllScan](https://img.shields.io/badge/AllScan-v1.01-2f9e44?style=for-the-badge)
![Installer](https://img.shields.io/badge/Installer-Idempotent-6741d9?style=for-the-badge)

**One safe installer adds a main-page Favorites editor, clickable sorting for AllScan's live `Rx%` and `LCnt` columns, and an independent Disconnect before Monitor option.**

</div>

> [!NOTE]
> This is an unofficial modification. AllScan is created by **David Gleason, NR9V**. The official upstream project is [davidgsd/AllScan](https://github.com/davidgsd/AllScan) and remains the source of truth.

## Features

### Edit Favorites from the main page

- Keeps **Add Favorite**, **Edit Favorite**, and **Delete Favorite** together.
- Places **Connect**, **Disconnect**, and **Monitor** beside the Node# field.
- Leaves **Local Mon** and **DTMF** available in their established positions.
- Keeps **Permanent**, **Disconnect before Connect**, and **Disconnect before Monitor** together on one line.
- Click a favorite's node number, then click **Edit Favorite**.
- Edit the node number and friendly name/label together in an AllScan-styled dialog.
- Use **Save & Close** to apply the edit or **Cancel** to leave the file unchanged.
- Click outside the dialog or press Escape to close it.
- Rejects invalid node numbers, duplicate destinations, malformed labels, and unauthorized favorites-file paths.
- Creates a timestamped backup of the selected `favorites*.ini` before every edit.
- Validates the edited INI and restores its backup automatically if validation fails.

AllScan's Description and Location columns remain sourced from the AllStarLink database. The editor changes only the favorite's node number and friendly label.

### Disconnect before Monitor

- Adds a third checkbox labeled **Disconnect before Monitor**.
- When selected, clicking **Monitor** disconnects all current links before monitoring the selected node.
- Waits briefly after disconnecting before starting Monitor so the commands occur in the intended order.
- Operates independently from **Disconnect before Connect**; either option can be enabled without enabling the other.
- Applies only to the **Monitor** button and does not change **Local Mon** behavior.
- If no nodes are connected, Monitor proceeds normally without issuing an unnecessary disconnect command.

### Sort Rx% and LCnt

- Click `Rx%` or `LCnt` to sort the Favorites table.
- First click sorts highest to lowest; the next click reverses the order.
- Direction arrows indicate ascending or descending order.
- Rows without live statistics remain at the bottom.
- Equal values retain their relative order.
- Existing node click/double-click actions remain attached.
- No additional AllStarLink statistics requests are made.
- Live values continue updating without automatically moving rows after every update.

## Installation

Repository: [github.com/ke2hni/AllScan-Mods](https://github.com/ke2hni/AllScan-Mods)

### Git

New download and installation:

```bash
cd /home/asl && git clone https://github.com/ke2hni/AllScan-Mods.git && cd AllScan-Mods && chmod 755 allscan-mods.sh && sudo ./allscan-mods.sh
```

Update an existing clone and run the latest installer:

```bash
cd /home/asl/AllScan-Mods && git pull --ff-only && chmod 755 allscan-mods.sh && sudo ./allscan-mods.sh
```

### Wget

```bash
cd /home/asl && wget -O allscan-mods.sh https://raw.githubusercontent.com/ke2hni/AllScan-Mods/refs/heads/main/allscan-mods.sh && chmod 755 allscan-mods.sh && sudo ./allscan-mods.sh
```

### Curl

```bash
cd /home/asl && curl -fL https://raw.githubusercontent.com/ke2hni/AllScan-Mods/refs/heads/main/allscan-mods.sh -o allscan-mods.sh && chmod 755 allscan-mods.sh && sudo ./allscan-mods.sh
```

Use only one method. Every terminal example is one copy-and-paste command.

After installation, open AllScan and press **Ctrl+F5** to reload the page, JavaScript, and CSS.

## Custom AllScan directory

The default directory is `/var/www/html/allscan`.

```bash
cd /home/asl && chmod 755 allscan-mods.sh && sudo ./allscan-mods.sh --allscan-dir /your/allscan/path
```

HamVOIP example:

```bash
cd /home/asl && chmod 755 allscan-mods.sh && sudo ./allscan-mods.sh --allscan-dir /srv/http/allscan
```

## Safety

The installer:

- Supports David Gleason's AllScan v1.01-compatible source layout.
- Works on a clean AllScan v1.01 installation.
- Upgrades an installation containing only the earlier Rx%/LCnt sorting modification.
- Upgrades the previous combined Favorites editor/sorting package.
- Recognizes installations containing the separately tested Disconnect before Monitor patch.
- Recognizes the fully installed package and exits without making changes.
- Stages every change before touching live files.
- Stops if required upstream structures are missing or ambiguous.
- Runs PHP syntax validation when PHP is installed.
- Runs JavaScript syntax validation when Node.js is installed.
- Preserves existing file ownership and permissions.
- Automatically restores all code files if installation fails after backups are created.
- Does not restart Asterisk, the web server, or the node.

It creates matching timestamped backups:

```text
index.php.before-allscan-mods-YYYYMMDD-HHMMSS
include/viewUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS
js/main.js.before-allscan-mods-YYYYMMDD-HHMMSS
css/main.css.before-allscan-mods-YYYYMMDD-HHMMSS
astapi/connect.php.before-allscan-mods-YYYYMMDD-HHMMSS
```

Each successful Favorite edit separately creates:

```text
favorites.ini.before-edit-YYYYMMDD-HHMMSS
```

The actual name matches whichever `favorites*.ini` file is selected in AllScan.

## Files modified

```text
/var/www/html/allscan/index.php
/var/www/html/allscan/include/viewUtils.php
/var/www/html/allscan/js/main.js
/var/www/html/allscan/css/main.css
/var/www/html/allscan/astapi/connect.php
```

The package does not modify AllScan's statistics request frequency, request-rate protection, Asterisk configuration, database, or the existing PHP sorter for the first five columns.

`favorites*.ini` changes only when an authorized user explicitly saves an edit.

## Verification

### Favorites editor

1. Click an existing favorite's node number.
2. Click **Edit Favorite**.
3. Confirm that Node Number and Friendly Name/Label appear together.
4. Change the friendly label and click **Save & Close**.
5. Confirm that the updated name appears in the table.
6. Reopen the editor and confirm the saved value is loaded.

### Rx% / LCnt sorting

1. Wait for live values to appear.
2. Click `Rx%` and confirm the highest value moves to the top with a `▼` arrow.
3. Click it again and confirm the order reverses with a `▲` arrow.
4. Repeat with `LCnt`.
5. Click and double-click nodes to confirm the original controls still work.

### Disconnect before Monitor

1. Connect to a node normally.
2. Select a different favorite.
3. Check **Disconnect before Monitor**.
4. Click **Monitor**.
5. Confirm the existing connection disconnects before monitoring begins.
6. Uncheck **Disconnect before Monitor** and confirm Monitor retains its normal behavior.
7. Confirm **Local Mon** is unaffected by this checkbox.

### File check

```bash
sudo grep -F 'case "Edit Favorite":' /var/www/html/allscan/index.php && sudo grep -Ec 'function[[:space:]]+sortFavStats[[:space:]]*\(' /var/www/html/allscan/js/main.js && sudo grep -Ec 'function[[:space:]]+openFavoriteEditor[[:space:]]*\(' /var/www/html/allscan/js/main.js && sudo grep -Fc 'id="automondisc"' /var/www/html/allscan/include/viewUtils.php && sudo grep -Fc 'if($automondisc)' /var/www/html/allscan/astapi/connect.php
```

All four final counts should be `1`.

## Rollback

Restore the five files bearing the same timestamp printed by the installer:

```bash
sudo cp -a /var/www/html/allscan/index.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/index.php && sudo cp -a /var/www/html/allscan/include/viewUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/include/viewUtils.php && sudo cp -a /var/www/html/allscan/js/main.js.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/js/main.js && sudo cp -a /var/www/html/allscan/css/main.css.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/css/main.css && sudo cp -a /var/www/html/allscan/astapi/connect.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/astapi/connect.php
```

Replace the timestamp, restore all five matching files, and press **Ctrl+F5**.

To reverse an individual Favorite edit, copy its matching `.before-edit-YYYYMMDD-HHMMSS` backup over the active `favorites*.ini` file.

## Official AllScan updates

David's official updater may replace locally modified files. After an update, press **Ctrl+F5** and check the editor, sorting, and Monitor-disconnect option. Run `allscan-mods.sh` again if needed.

If the reviewed v1.01-compatible structure is unchanged, the installer safely reapplies the package. If the upstream version or structure changes, it stops without modifying live files so compatibility can be reviewed first.

## Troubleshooting

### `Run this script with sudo`

Run the complete command from the Installation section.

### `Required AllScan file not found`

Confirm AllScan is under `/var/www/html/allscan`, or use `--allscan-dir`.

### `supports ... AllScan v1.01 layout only`

The installed AllScan version differs from the reviewed version. Review David's newer source before updating this package.

### Compatibility or expected-structure error

The installer found an unexpected local or upstream modification and intentionally left live files unchanged.

### Changes do not appear

Press **Ctrl+F5** or clear the browser cache.

### Matching label/cmd pair was not found

The selected entry is not a standard adjacent `label[]` and `cmd[] = "rpt cmd %node% ilink 3 ..."` pair, so it is intentionally left unchanged.

## Tested configuration

| Component | Tested configuration |
|:--|:--|
| Platform | AllStarLink 3 |
| Operating system | Debian 13 |
| AllScan | v1.01-compatible source layout |
| Default web root | `/var/www/html/allscan` |
| Nodes | `node44690` and a separate test node |

The editor, layout, Save & Close workflow, validation, backups, Add/Delete controls, connection controls, Rx%/LCnt sorting, and Disconnect before Monitor behavior were browser-tested before consolidation.

## Design principles

- Preserve David's official AllScan application and attribution.
- Make the smallest practical local changes.
- Never guess when upstream code is unexpected.
- Validate and back up before modifying live files.
- Keep installation repeatable and rollback transparent.
- Add no services, background processes, or statistics requests.

## Author

**KE2HNI**

AllScan is a separate open-source project created by **David Gleason, NR9V**. This package is not an official AllScan release and is not affiliated with or endorsed by the AllScan author.

## License

MIT License. Use at your own risk and keep current backups.

<div align="center">

**KE2HNI · AllScan Mods**

</div>
