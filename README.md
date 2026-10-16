<div align="center">

# AllScan Mods

### Favorites editing, live Rx% / LCnt sorting, and safer monitoring for AllScan

![Platform](https://img.shields.io/badge/Platform-AllStarLink%203-0b7285?style=for-the-badge)
![Debian](https://img.shields.io/badge/Debian-12%20%7C%2013-a81d33?style=for-the-badge&logo=debian&logoColor=white)
![AllScan](https://img.shields.io/badge/AllScan-v1.01%20%7C%20v1.02%20%7C%20v1.03%20%7C%20v1.04-2f9e44?style=for-the-badge)
![Installer](https://img.shields.io/badge/Installer-Idempotent-6741d9?style=for-the-badge)

**AllScan Mods add a main-page Favorites editor, clickable sorting for the live `Rx%` and `LCnt` columns, and an independent Disconnect before Monitor option. Choose the Mods-only installer or the combined AllScan updater.**

</div>

> [!NOTE]
> This is an unofficial modification. AllScan is created by **David Gleason, NR9V**. The official upstream project is [davidgsd/AllScan](https://github.com/davidgsd/AllScan) and remains the source of truth.

## Official AllScan integration (PR #37, v1.04)

On October 14, 2026, David merged the dashboard and TouchGUI enhancements into the official [AllScan pull request #37](https://github.com/davidgsd/AllScan/pull/37). New AllScan installations containing these features **do not need the legacy Mods patch**.

David released **AllScan v1.04 on 2026-10-14** with PR #37 integrated. Both installers recognize the integrated feature set and leave those changes intact. The TouchGUI remote-node activity colors are a separate AllScan Mods enhancement being tested against v1.04.

The installers check the **full set of PR #37 features** on AllScan v1.03 or v1.04. When found, they skip the legacy dashboard modifications and only check/apply the independent TouchGUI activity-color enhancement. On v1.02 and pre-integration v1.03, the established legacy patch workflow remains in use and the TouchGUI enhancement is applied to its staged files. AllScan v1.01 remains supported for existing Mods features but does not have TouchGUI, so it does not receive this enhancement. Unknown AllScan versions or unexpected v1.04 feature layouts are refused pending review.

Never restore an older `.before-allscan-mods-*` backup onto a newer upstream installation: those backups may remove David's integrated features or later fixes. Use the official AllScan updater to recover current upstream files.

## Features

### Edit Favorites from the main page

- Keeps **Add Favorite**, **Edit Favorite**, and **Delete Favorite** together.
- Places **Connect**, **Disconnect**, and **Monitor** beside the Node# field.
- Leaves **Local Mon** and **DTMF** available in their established positions.
- Keeps **Permanent**, **Disconnect before Connect**, and **Disconnect before Monitor** together on one line.
- Click a favorite's node number, then click **Edit Favorite**.
- Edit the node number and friendly name/label together in an AllScan-styled dialog.
- Edit the **favorite's order number** from the same dialog; moving a favorite inserts it at that position and shifts the other favorites automatically.
- Use **Save & Close** to apply the edit or **Cancel** to leave the file unchanged.
- Click outside the dialog or press Escape to close it.
- Rejects invalid node numbers, duplicate destinations, malformed labels, and unauthorized favorites-file paths.
- Creates a timestamped backup of the selected `favorites*.ini` before every edit.
- Validates the edited INI and restores its backup automatically if validation fails.
- Rejects zero, non-numeric, and out-of-range order values; no favorite is discarded when positions conflict.

AllScan's Description and Location columns remain sourced from the AllStarLink database. The editor changes only the favorite's node number and friendly label.

### Disconnect before Monitor

- Adds a third checkbox labeled **Disconnect before Monitor**.
- When selected, clicking **Monitor** disconnects all current links before monitoring the selected node.
- Waits briefly after disconnecting before starting Monitor so the commands occur in the intended order.
- Operates independently from **Disconnect before Connect**; either option can be enabled without enabling the other.
- Applies only to the **Monitor** button and does not change **Local Mon** behavior.
- If no nodes are connected, Monitor proceeds normally without issuing an unnecessary disconnect command.

### TouchGUI remote-node activity and statistics (testing)

- Uses AllScan's existing `stats.php` endpoint to color each configured TouchGUI channel by remote-node activity.
- Uses the same red keyed/recently keyed activity shading and the same dark/medium green active states as the main Favorites table.
- Replaces the previous Mods TouchGUI activity patch with the corrected calculation and creates fresh timestamped backups when upgrading it.
- Shows each channel's `Rx%` and `LCnt` values in a compact footer beneath its node/callsign line. The values use fields from the same stats response already used for activity colors; they do not add API requests.
- The two AllScan files modified by this TouchGUI feature are tagged `v1.08` in their JavaScript and CSS comments. The footer preserves the AllScan and ASL versions, RxAudioStats driver information, and all Rx/Tx level values while combining the channel levels into one compact line. Other status messages are unchanged.
- Keeps the channel name, node/callsign line, and TouchGUI controls intact. Cards grow slightly to fit the extra row; phone-width and short-screen CSS rules keep the values compact and readable.
- Keeps TouchGUI's existing local connection border and status behavior.
- Scans unique public node numbers one at a time. The interval is based on the channel count and keeps one TouchGUI page at or below 30 statistics requests per minute.
- Applies to TouchGUI on AllScan v1.02, v1.03, and v1.04. AllScan v1.01 has no TouchGUI.
- This feature is under testing. The integrated v1.03/v1.04 path creates dedicated timestamped TouchGUI backups; the legacy v1.02/pre-integration v1.03 path uses the installer's existing full-file backups.

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

This package contains two installers:

- `allscan-mods.sh` is the original installer for nodes where AllScan is already installed. It only applies the AllScan Mods changes and does not install AllScan or its packages.
- `install-allscan-n-mods.sh` is the combined installer. At the default AllScan location, it runs David's current official installer/updater first, then verifies PHP SQLite support for Apache and applies AllScan Mods. It installs AllScan on a new node and offers to upgrade an older release to the current release. If an update is declined and v1.01 remains, it stops without applying Mods. For a custom AllScan path, the official updater is skipped and AllScan must already be installed there.

Use `install-allscan-n-mods.sh` for a new node or to check/update the default AllScan installation before applying Mods. David's updater asks for confirmation before installing/updating. Decline its optional OS/package upgrade and optional DTMF support-file replacement unless you specifically want those actions. Use `allscan-mods.sh` when AllScan is already at a supported version and you only want to apply the Mods.

Both scripts are stored in Git with executable permissions, which Git preserves when you clone the repository. Files downloaded directly with Wget or Curl need `chmod +x`; the commands below include that step.

### Git

New node: install AllScan and AllScan Mods:

```bash
cd /home/asl && git clone https://github.com/ke2hni/AllScan-Mods.git && cd AllScan-Mods && sudo ./install-allscan-n-mods.sh
```

For a node that already has AllScan installed, first use the **Upgrade** section below to update this repository, then run `sudo ./allscan-mods.sh`.

### Wget

```bash
cd /home/asl && mkdir -p lib && wget -O install-allscan-n-mods.sh https://raw.githubusercontent.com/ke2hni/AllScan-Mods/refs/heads/main/install-allscan-n-mods.sh && wget -O lib/touchgui-activity.py https://raw.githubusercontent.com/ke2hni/AllScan-Mods/refs/heads/main/lib/touchgui-activity.py && chmod +x install-allscan-n-mods.sh && sudo ./install-allscan-n-mods.sh
```

### Curl

```bash
cd /home/asl && mkdir -p lib && curl -fL https://raw.githubusercontent.com/ke2hni/AllScan-Mods/refs/heads/main/install-allscan-n-mods.sh -o install-allscan-n-mods.sh && curl -fL https://raw.githubusercontent.com/ke2hni/AllScan-Mods/refs/heads/main/lib/touchgui-activity.py -o lib/touchgui-activity.py && chmod +x install-allscan-n-mods.sh && sudo ./install-allscan-n-mods.sh
```

The Wget and Curl examples use the combined installer. For an existing AllScan installation where you only want the Mods and do not want to run David's updater, download `allscan-mods.sh` and `lib/touchgui-activity.py` to the same `/home/asl` and `/home/asl/lib` locations, then run `sudo ./allscan-mods.sh`. Use only one method. Every terminal example is one copy-and-paste command.

After installation, open AllScan and press **Ctrl+F5** to reload the page, JavaScript, and CSS.

## Upgrade

This updates the AllScan Mods repository on a node where it is already cloned. It saves the current commit on a local backup branch, stashes any local changes, and updates `main` from GitHub. The command does not commit or push your changes.

```bash
cd /home/asl/AllScan-Mods && git fetch origin && backup="pre-update-$(date +%Y%m%d-%H%M%S)-$$" && git branch "$backup" HEAD && git stash push -u -m "Pre-update $backup" && git switch -C main origin/main
```

Then choose **one** installer:

- Apply or reapply the Mods to the currently installed AllScan version: `sudo ./allscan-mods.sh`
- Run David's official AllScan installer/updater first, then apply the Mods: `sudo ./install-allscan-n-mods.sh`

The combined installer can update AllScan itself and may prompt you to confirm that update. The Mods-only installer does not update AllScan. After either installer completes, hard-refresh the AllScan page with **Ctrl+F5**.

## Custom AllScan directory

The default directory is `/var/www/html/allscan`.

```bash
cd /home/asl && sudo ./allscan-mods.sh --allscan-dir /your/allscan/path
```

HamVOIP example:

```bash
cd /home/asl && sudo ./allscan-mods.sh --allscan-dir /srv/http/allscan
```

## Safety

The installer:

- Supports AllScan v1.01 through v1.04. TouchGUI activity colors apply to v1.02-v1.04; v1.01 has no TouchGUI.
- Works on clean AllScan v1.01, v1.02, and v1.03 installations.
- Upgrades an installation containing only the earlier Rx%/LCnt sorting modification.
- Upgrades the previous combined Favorites editor/sorting package.
- Recognizes installations containing the separately tested Disconnect before Monitor patch.
- Detects when the legacy Mods and TouchGUI activity colors are already applied and avoids unnecessary changes or backups.
- Stages and validates changes before touching live files, then creates timestamped backups before applying them.
- Stops if required upstream structures are missing or ambiguous.
- Runs PHP syntax validation when PHP is installed.
- Runs JavaScript syntax validation when Node.js is installed.
- At the default path, the combined installer runs David's current official installer/updater before applying Mods; it prompts before installing or updating AllScan and stops if an old v1.01 installation remains.
- The combined installer installs `php-sqlite3` when needed, enables `pdo_sqlite` and `sqlite3` for Apache PHP, restarts Apache when required, and verifies both extensions before modifying AllScan.
- At completion, both installers report whether Apache PHP has `pdo_sqlite` and `sqlite3` enabled. AllScan requires both. The Mods-only installer reports status without changing PHP settings; use the combined installer if they need to be enabled.
- Before upgrading an installed v1.01, the combined installer creates a full timestamped recovery copy named `allscan.before-update-v1.01-YYYYMMDD-HHMMSS`. If an existing `allscan.bak.v1.01` is present, it also preserves that backup with a timestamped suffix before David's updater can replace it.
- The combined installer preserves the official installer filename so AllScan's self-update check works correctly.
- Preserves existing file ownership and permissions.
- Automatically restores the backed-up files if applying the Mods fails after backups are created.
- On v1.02 and v1.03, also backs up and patches `include/favsUtils.php`, where upstream builds Favorites rows.
- On v1.02 and v1.03, also patches `css/simple.css` so the AllScan link remains visible in TouchGUI portrait mode; v1.01 is unchanged.
- On v1.02-v1.04, applies the independent TouchGUI activity-color enhancement without removing or replacing upstream functionality.
- The TouchGUI enhancement helper is included in the repository. Direct Wget/Curl installation downloads the helper to `lib/touchgui-activity.py` beside the installer.
- Preserves v1.03's TouchGUI selected-favorites-file link behavior and its duplicate-favorite handling in upstream code.
- At phone widths, including portrait mode, stacks the TouchGUI status and extra-connection panels so text and controls do not overlap or overflow.
- On v1.02 and v1.03, adds a TouchGUI Disconnect before Connect toggle synchronized with the regular-page checkbox. Its selection persists across reloads and tabs in the same browser, keyed to the local node; the configured AllScan default seeds first use. v1.01 has no TouchGUI and retains the regular-page behavior.
- The Mods-only installer does not restart Asterisk, Apache, or the node. The combined installer may restart Apache if needed to activate PHP SQLite support; it does not restart Asterisk or reboot the node.

It creates matching timestamped backups:

```text
index.php.before-allscan-mods-YYYYMMDD-HHMMSS
include/viewUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS
js/main.js.before-allscan-mods-YYYYMMDD-HHMMSS
css/main.css.before-allscan-mods-YYYYMMDD-HHMMSS
astapi/connect.php.before-allscan-mods-YYYYMMDD-HHMMSS
include/favsUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS (v1.02 and v1.03)
css/simple.css.before-allscan-mods-YYYYMMDD-HHMMSS (v1.02 and v1.03)
js/simple.js.before-touchgui-activity-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
css/simple.css.before-touchgui-activity-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
simple/index.php.before-allscan-mods-YYYYMMDD-HHMMSS (v1.02 and v1.03)
js/simple.js.before-allscan-mods-YYYYMMDD-HHMMSS (v1.02 and v1.03)
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
/var/www/html/allscan/include/favsUtils.php (v1.02 and v1.03)
/var/www/html/allscan/css/simple.css (v1.02-v1.04)
/var/www/html/allscan/simple/index.php (v1.02 and v1.03)
/var/www/html/allscan/js/simple.js (v1.02-v1.04)
```

The main-page statistics polling is unchanged. TouchGUI requests one unique public node at a time and adjusts its delay to keep its own request rate at or below 30 per minute. Multiple open AllScan clients share the ASL statistics API's per-IP limit.

`favorites*.ini` changes only when an authorized user explicitly saves an edit.

## Verification

### Favorites editor

1. Click an existing favorite's node number.
2. Click **Edit Favorite**.
3. Confirm that Node Number, Order, and Friendly Name/Label appear together.
4. Change the order and/or friendly label and click **Save & Close**.
5. Confirm that the selected favorite moves to the requested position and the other rows shift without loss.
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

Restore the five core files bearing the same timestamp printed by the installer. On v1.02 and v1.03, also restore the four TouchGUI/Favorites files listed below:

```bash
sudo cp -a /var/www/html/allscan/index.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/index.php && sudo cp -a /var/www/html/allscan/include/viewUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/include/viewUtils.php && sudo cp -a /var/www/html/allscan/js/main.js.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/js/main.js && sudo cp -a /var/www/html/allscan/css/main.css.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/css/main.css && sudo cp -a /var/www/html/allscan/astapi/connect.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/astapi/connect.php
```

Replace the timestamp, restore all five matching files, and press **Ctrl+F5**.

For v1.02 and v1.03, also run these commands with the same timestamp:

```bash
sudo cp -a /var/www/html/allscan/include/favsUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/include/favsUtils.php
sudo cp -a /var/www/html/allscan/css/simple.css.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/css/simple.css
sudo cp -a /var/www/html/allscan/simple/index.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/simple/index.php
sudo cp -a /var/www/html/allscan/js/simple.js.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/js/simple.js
```

To reverse an individual Favorite edit, copy its matching `.before-edit-YYYYMMDD-HHMMSS` backup over the active `favorites*.ini` file.

## Official AllScan updates

David's official updater may replace locally modified files. Before an installed v1.01 upgrade, the combined installer prints the path of a complete timestamped recovery copy. If you need to roll back, replace the timestamps below with the printed backup timestamp; this moves the updated AllScan directory aside and restores the pre-update copy without deleting either directory:

```bash
sudo mv /var/www/html/allscan /var/www/html/allscan.failed-YYYYMMDD-HHMMSS && sudo cp -a /var/www/html/allscan.before-update-v1.01-YYYYMMDD-HHMMSS /var/www/html/allscan
```

After an update, press **Ctrl+F5** and check the editor, sorting, and Monitor-disconnect option. Run `allscan-mods.sh` again if you separately ran David's updater and only want to reapply Mods.

The installer safely reapplies the package on reviewed v1.01, v1.02, and v1.03 layouts. If the upstream version or required structure changes, it stops without modifying live files so compatibility can be reviewed first.

## Troubleshooting

### `Run this script with sudo`

Run the complete command from the Installation section.

### `Required AllScan file not found`

Confirm AllScan is under `/var/www/html/allscan`, or use `--allscan-dir`.

### Unsupported AllScan version or layout

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
| AllScan | v1.01-v1.03 legacy patches; v1.04 integrated feature detection and safe skip |
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

This project is licensed under GPL-3.0-only. See [LICENSE](LICENSE).

AllScan is a separate GPL-3.0-licensed project created by David Gleason, NR9V. This repository contains unofficial modifications and is not affiliated with or endorsed by the AllScan author.

<div align="center">

**KE2HNI · AllScan Mods**

</div>
<img width="1600" height="852" alt="Screenshot 2026-09-22 185554" src="https://github.com/user-attachments/assets/a7f32979-f989-4c7d-98d4-c9d5d4922d65" />
<img width="1600" height="852" alt="Screenshot 2026-09-22 185608" src="https://github.com/user-attachments/assets/bd629410-6efe-4439-af79-aab5379923ba" />
<img width="1600" height="900" alt="Screenshot 2026-10-11 143018" src="https://github.com/user-attachments/assets/9ef2f29f-57d6-4d10-8c68-4323dc2837d7" />

