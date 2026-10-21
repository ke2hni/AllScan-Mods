<div align="center">

# AllScan Mods

### TouchGUI activity and statistics, Rx% / LCnt sorting, and safer monitoring for AllScan

![Platform](https://img.shields.io/badge/Platform-AllStarLink%203-0b7285?style=for-the-badge)
![Debian](https://img.shields.io/badge/Debian-12%20%7C%2013-a81d33?style=for-the-badge&logo=debian&logoColor=white)
![AllScan](https://img.shields.io/badge/AllScan-v1.01%20%7C%20v1.02%20%7C%20v1.03%20%7C%20v1.04-2f9e44?style=for-the-badge)
![Installer](https://img.shields.io/badge/Installer-Idempotent-6741d9?style=for-the-badge)

**AllScan Mods add TouchGUI activity colors and live `Rx%` / `LCnt` values, clickable sorting for those table columns on legacy releases, and an independent Disconnect before Monitor option. Choose the Mods-only installer or the combined AllScan updater.**

</div>

> [!NOTE]
> This is an unofficial modification. AllScan is created by **David Gleason, NR9V**. The official upstream project is [davidgsd/AllScan](https://github.com/davidgsd/AllScan) and remains the source of truth.

## Official AllScan integration (PR #37, v1.04)

On October 14, 2026, David merged the dashboard and TouchGUI enhancements into the official [AllScan pull request #37](https://github.com/davidgsd/AllScan/pull/37). New AllScan installations containing these features **do not need the legacy Mods patch**.

David released **AllScan v1.04 on 2026-10-14** with PR #37 integrated. Both installers recognize the integrated feature set. AllScan Mods keeps David’s one-field Favorites editor and adds a call-sign-free view of that same field with a 33-character limit and help text. The TouchGUI activity colors, statistics, and responsive card-title sizing are separate AllScan Mods enhancements tested against v1.04.

The installers check the **full set of PR #37 features** on AllScan v1.03 or v1.04. When found, they skip legacy dashboard modifications and check/apply the shared-label editor change plus independent TouchGUI activity, statistics, and text-layout enhancements. The v1.04 Favorites editor remains a single shared field; the Mods editor shows that label without the callsign, and the TouchGUI card derives its text from that same stored field. On v1.02 and pre-integration v1.03, the established legacy compatibility patches remain in use. AllScan v1.01 remains supported for existing Mods features but does not have TouchGUI. Unknown AllScan versions or unexpected v1.04 feature layouts are refused pending review.

Never restore an older `.before-allscan-mods-*` backup onto a newer upstream installation: those backups may remove David's integrated features or later fixes. Use the official AllScan updater to recover current upstream files. If the earlier Mods-only TouchGUI Favorites-label experiment is still installed, restore/reinstall the matching official AllScan files before installing v1.38; the installer detects that state and stops without changing files.

## Features

### Edit Favorites from the main page

- Keeps **Add Favorite**, **Edit Favorite**, and **Delete Favorite** together.
- Places **Connect**, **Disconnect**, and **Monitor** beside the Node# field.
- Leaves **Local Mon** and **DTMF** available in their established positions.
- Keeps **Permanent**, **Disconnect before Connect**, and **Disconnect before Monitor** together on one line.
- Click a favorite's node number, then click **Edit Favorite**.
- On AllScan v1.04, the editor keeps David’s single shared Friendly Name/Label field and favorite order field. AllScan adds the callsign for the main table; the editor omits it and allows up to 33 label characters.
- Existing favorites prefill the shared name without the automatically added callsign; new favorites use David’s normal default behavior. A clear, regular-weight note says the callsign is added automatically. Saving updates the one shared label used by both views.
- Edit the **favorite's order number** from the same dialog; moving a favorite inserts it at that position and shifts the other favorites automatically.
- Use **Save & Close** to apply the edit or **Cancel** to leave the file unchanged.
- Click outside the dialog or press Escape to close it.
- Rejects invalid node numbers, duplicate destinations, malformed labels, and unauthorized favorites-file paths.
- Creates a timestamped backup of the selected `favorites*.ini` before every edit.
- Validates the edited INI and restores its backup automatically if validation fails.
- Rejects zero, non-numeric, and out-of-range order values; no favorite is discarded when positions conflict.

AllScan’s Description and Location columns remain sourced from the AllStarLink database. The Favorites name field is shared by both views; TouchGUI removes a matching callsign from its displayed copy and fits the card title to the available space.

### Disconnect before Monitor

- Adds a third checkbox labeled **Disconnect before Monitor**.
- When selected, clicking **Monitor** disconnects all current links before monitoring the selected node.
- Waits briefly after disconnecting before starting Monitor so the commands occur in the intended order.
- Operates independently from **Disconnect before Connect**; either option can be enabled without enabling the other.
- Applies only to the **Monitor** button and does not change **Local Mon** behavior.
- If no nodes are connected, Monitor proceeds normally without issuing an unnecessary disconnect command.

### TouchGUI remote-node activity and statistics (testing)

- Uses AllScan's existing `stats.php` endpoint. `Rx%`, `LCnt`, and activity colors come from the same response, so displaying the added values does not create extra requests.
- Mirrors the Favorites table calculations: red Tx coloring uses the rolling percentage calculated from the difference in total Tx time across consecutive responses, with the same `>5%` threshold and red gradient; Rx uses the same green percentage gradient; LCnt uses the same blue count gradient; active and WebTransceiver states retain the table's green shades.
- Polls unique public favorites one at a time in the displayed Favorites order. The existing 2-second minimum between requests and 30-second minimum refresh interval per node are retained, limiting one TouchGUI page to at most 30 statistics requests per minute. A JSON-level 429 response retries the same node after 15 seconds.
- Places the favorite number at the upper left, with the Rx% and LCnt values stacked below it without labels to save card space. Rx values include the `%` sign. All three color fields have rounded corners. The Rx% and LCnt value text and badges are slightly larger, with compact line spacing. Card labels and metadata share a constrained, centered text column. The bold green node/callsign line aligns with the top of the # badge and is centered with the lower rows, with a visible gap before the aqua description and white note/location lines. Landscape cards give the line 1.5ch of extra width shifted left; portrait uses the matching balanced offset. Titles shrink within readable limits, then wrap inside the same card when needed; metadata keeps its existing single-line fit. Card sizing rules and the favorite-number badge size remain unchanged. Each item in that left strip uses the same color and threshold as its matching Favorites-table column: `#` for Tx/active state, green for Rx%, and blue for LCnt. Stats no longer recolor the full card; existing TouchGUI selected/connection styling remains.
- Preserves the existing TouchGUI connection border and footer layout. Other status messages remain unchanged.
- Each TouchGUI card shows the existing green node/callsign line and aqua ASTDB description, followed by a white favorite Name. If most of the Name text substantially matches the Description or Location, the card uses Location once; when the Name fits on one line, Location appears below it as an additional white row. A repeated country suffix such as `US` when Location is `USA` is removed from the aqua Description. This reuses existing favorite fields and adds no saved field. Description and note text fit responsively and can wrap within the card. For this test, the grid's minimum card width grows by `5ch` on desktop and narrow screens; the existing minimum card height is unchanged. The aqua description line sits 2px higher and shifts left by `0.5ch` to center it within the right column. Version 1.82 lowered the white note block 2px and added a small line gap; v1.83 adds 2px more space between white lines and lowers the block another 2px. Version 1.84 tests Arial on white card text only; green and aqua rows keep the existing Verdana-based font stack. Aqua descriptions retain their responsive sizing up to 18px and scale down to 13px. White note/location text retains its responsive sizing. The green-to-aqua gap is reduced by 3px. A small fit buffer and bounded horizontal scaling keep near-fit descriptions on one line; scaled text can paint beyond its unscaled clipping box, while longer text still wraps. The extra width flows into the right text column.
- The AllScan JavaScript keeps the matching-callsign cleanup and responsive card text fitting. Both shell installers show a standalone `v1.84` tag near the top. The connected banner shows the channel description followed by `(node# - callsign)` when a callsign is available; it keeps `(node#)` when it is not.
- TouchGUI card labels and their node/callsign metadata use responsive text sizing. Long card titles shrink no smaller than 14px on larger screens or 12px on narrow screens, then wrap within the existing card width. New editor labels are limited to 33 characters. In portrait orientation only, the node/callsign metadata may shrink to 10px to fit its single line; the existing landscape sizing remains unchanged.
- Applies to TouchGUI on AllScan v1.02, v1.03, and v1.04. AllScan v1.01 has no TouchGUI.
- On the integrated v1.03/v1.04 path, the installer creates dedicated timestamped TouchGUI backups; the legacy v1.02/pre-integration v1.03 path uses the installer's existing full-file backups.

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

On the AllStarLink node, choose the command for your situation. The commands below clone the repository for a new checkout. If it is already cloned, run the selected installer from `/home/asl/AllScan-Mods` instead; use the Upgrade section first if you need the latest Mods.

- **Install AllScan and Mods, or update AllScan before applying Mods:**

  ```bash
  cd /home/asl && git clone https://github.com/ke2hni/AllScan-Mods.git && cd AllScan-Mods && sudo ./install-allscan-n-mods.sh
  ```

  This runs David's official installer/updater, checks Apache PHP SQLite support, then applies the Mods. Review its prompts; accept the optional OS/package upgrade or DTMF-file replacement only if you want those actions.

- **AllScan is already installed; apply Mods without running David's updater:**

  ```bash
  cd /home/asl && git clone https://github.com/ke2hni/AllScan-Mods.git && cd AllScan-Mods && sudo ./allscan-mods.sh
  ```

  For a custom AllScan directory, add `--allscan-dir PATH`; AllScan must already be installed there.

The repository includes both scripts and the TouchGUI and Favorites editor helpers. After installation, open AllScan and press **Ctrl+F5** (or clear the browser cache on a phone) to reload the page, JavaScript, and CSS.

## Upgrade

To update the Mods repository on a node where it is already cloned, run this from its directory. It saves the current commit on a local backup branch, stashes local changes, and updates `main` from GitHub. It does not commit or push changes.

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
cd /home/asl/AllScan-Mods && sudo ./allscan-mods.sh --allscan-dir /your/allscan/path
```

HamVOIP example:

```bash
cd /home/asl/AllScan-Mods && sudo ./allscan-mods.sh --allscan-dir /srv/http/allscan
```

## Safety

The installer:

- Supports AllScan v1.01 through v1.04. TouchGUI activity colors apply to v1.02-v1.04; v1.01 has no TouchGUI.
- Applies the legacy Mods to clean v1.01-v1.03 layouts; v1.04 uses PR #37 feature detection and the independent TouchGUI enhancement.
- Upgrades an installation containing only the earlier Rx%/LCnt sorting modification.
- Upgrades the previous combined Favorites editor/sorting package.
- Recognizes installations containing the separately tested Disconnect before Monitor patch.
- Detects when the legacy Mods and TouchGUI activity, statistics, and text layout are already applied and avoids unnecessary changes or backups.
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
- On integrated PR #37 v1.03/v1.04, retains the single-field Favorites editor and adds its call-sign-free, 33-character label view. The independent TouchGUI activity, statistics, and text-layout enhancement applies to v1.02-v1.04.
- The TouchGUI enhancement helper is included at `lib/touchgui-activity.py`; keep it beside the installer directory when running either script.
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
index.php.before-favorite-editor-label-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
include/viewUtils.php.before-favorite-editor-label-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
js/main.js.before-favorite-editor-label-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
include/favsUtils.php.before-favorite-editor-label-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
css/simple.css.before-touchgui-activity-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
css/main.css.before-favorite-editor-label-YYYYMMDD-HHMMSS (integrated v1.03 and v1.04)
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
/var/www/html/allscan/include/favsUtils.php (integrated v1.03 and v1.04)
/var/www/html/allscan/include/viewUtils.php (integrated v1.03 and v1.04)
/var/www/html/allscan/js/main.js (integrated v1.03 and v1.04)
/var/www/html/allscan/css/main.css (integrated v1.03 and v1.04)
```

The main-page statistics polling is unchanged. TouchGUI requests one unique public node at a time in Favorites order, with at least 2 seconds between requests and at least 30 seconds between requests for the same node. This limits one TouchGUI page to at most 30 statistics requests per minute; larger favorite lists take longer than 30 seconds to complete a full pass. Multiple open AllScan clients still share the ASL statistics API's per-IP limit.

`favorites*.ini` changes only when an authorized user explicitly saves an edit.

## Verification

### Favorites editor

1. Click an existing favorite's node number.
2. Click **Edit Favorite**.
3. Confirm that Node Number, Order, and the single Friendly Name/Label field appear.
4. Confirm the single shared label field omits the callsign, shows the callsign-only guidance in clear bold text, prefills existing text without an ellipsis, and contains no stray internal marker text.
5. Change the shared name (test 33 characters and a 34th), node number, and/or order, then click **Save & Close**.
6. Confirm the favorite updates at the selected order and both views remain based on the same saved label; verify long TouchGUI titles stay legible within their cards.
7. Reopen the editor and confirm the shared name remains. Add a favorite and confirm David’s default add/edit behavior is unchanged.

### Rx% / LCnt sorting

1. Wait for live values to appear.
2. Click `Rx%` and confirm the highest value moves to the top with a `▼` arrow.
3. Click it again and confirm the order reverses with a `▲` arrow.
4. Repeat with `LCnt`.
5. Click and double-click nodes to confirm the original controls still work.

### TouchGUI activity, statistics, and footer

1. Confirm card numbers follow the displayed Favorites order and appear at upper left, with the Rx% (including `%`) and LCnt values beneath them and without text labels.
2. Confirm only the left stats strip is colored by activity: `#` follows the table's red/green/clear rules, higher `Rx%` produces a brighter green, and `LCnt` follows the blue gradient. Existing TouchGUI selected/connection styling should remain.
3. Confirm red Tx state responds to changes in total Tx time across successive stats responses, even when the raw keyed field is zero.
4. Check the layout on a laptop, tablet, and phone; card labels should remain legible within the existing card widths; metadata should not overlap the #/Rx/LCnt strip.
5. Check the status footer and confirm the TouchGUI controls and local-connection border still work.

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

Restore only files changed by that installation, using backups with its timestamp. For a legacy v1.01-v1.03 install, restore the five core files below. For v1.02 and pre-integration v1.03, also restore the four TouchGUI/Favorites files. Do not restore legacy backups onto a later upstream installation.

```bash
sudo cp -a /var/www/html/allscan/index.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/index.php && sudo cp -a /var/www/html/allscan/include/viewUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/include/viewUtils.php && sudo cp -a /var/www/html/allscan/js/main.js.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/js/main.js && sudo cp -a /var/www/html/allscan/css/main.css.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/css/main.css && sudo cp -a /var/www/html/allscan/astapi/connect.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/astapi/connect.php
```

Replace the timestamp, restore all five matching files, and press **Ctrl+F5**.

For v1.02 and pre-integration v1.03, also run these commands with the same timestamp:

```bash
sudo cp -a /var/www/html/allscan/include/favsUtils.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/include/favsUtils.php
sudo cp -a /var/www/html/allscan/css/simple.css.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/css/simple.css
sudo cp -a /var/www/html/allscan/simple/index.php.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/simple/index.php
sudo cp -a /var/www/html/allscan/js/simple.js.before-allscan-mods-YYYYMMDD-HHMMSS /var/www/html/allscan/js/simple.js
```

For integrated AllScan v1.03 or v1.04, the TouchGUI enhancement has its own JavaScript and CSS backups. Restore the matching pair printed by the installer:

```bash
sudo cp -a /var/www/html/allscan/js/simple.js.before-touchgui-activity-YYYYMMDD-HHMMSS /var/www/html/allscan/js/simple.js && sudo cp -a /var/www/html/allscan/css/simple.css.before-touchgui-activity-YYYYMMDD-HHMMSS /var/www/html/allscan/css/simple.css
```

Only restore these backups while the same AllScan version and files are still installed. If an official AllScan update has replaced these files or integrated the feature, do not restore the older backups; that could remove upstream changes. Reinstall or update AllScan through David's official installer instead.

To reverse an individual Favorite edit, copy its matching `.before-edit-YYYYMMDD-HHMMSS` backup over the active `favorites*.ini` file.

## Official AllScan updates

David's official updater may replace locally modified files. Before an installed v1.01 upgrade, the combined installer prints the path of a complete timestamped recovery copy. If you need to roll back, replace the timestamps below with the printed backup timestamp; this moves the updated AllScan directory aside and restores the pre-update copy without deleting either directory:

```bash
sudo mv /var/www/html/allscan /var/www/html/allscan.failed-YYYYMMDD-HHMMSS && sudo cp -a /var/www/html/allscan.before-update-v1.01-YYYYMMDD-HHMMSS /var/www/html/allscan
```

After an update, press **Ctrl+F5** and check the one-field Favorites editor, its 33-character limit, sorting, Monitor-disconnect option, and TouchGUI activity colors, statistics, responsive card-title fit, and footer. Run `allscan-mods.sh` again if you separately ran David's updater and only want to reapply Mods.

The installer safely reapplies the package on reviewed AllScan v1.01-v1.04 layouts. It recognizes the integrated PR #37 features on v1.03/v1.04, detects already-present TouchGUI activity and statistics features, and applies only missing independent enhancements. If the upstream version or required structure changes, it stops without modifying live files so compatibility can be reviewed first.

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
| Operating system | Debian 12 (Bookworm) and Debian 13 (Trixie) |
| AllScan | v1.01-v1.03 legacy patches; v1.04 integrated feature detection and TouchGUI patch |
| Default web root | `/var/www/html/allscan` |
| TouchGUI v1.11 | Upgrade test: `node446900`; fresh install: `pi4test`; other test-node installs pending |
| TouchGUI v1.12 | Installed and visually checked on `pi4test`; matched main-screen activity behavior reported by user |
| TouchGUI v1.13 | Workspace regression tests passed; test-node testing pending |
| TouchGUI v1.14 | User confirmed the value-only cards worked after AllStar stats requests recovered |
| TouchGUI v1.15 | Workspace regression tests passed; test-node testing pending |
| TouchGUI v1.16 | Workspace regression tests passed; test-node testing pending |
| TouchGUI v1.17 | Workspace regression tests passed; test-node testing pending |
| TouchGUI v1.18 | Workspace regression tests passed; test-node testing pending |
| AllScan Mods v1.19 | Installed on `pi4test`; editor still showed `&hellip;`, prompting the v1.20 fix |
| AllScan Mods v1.20 | Local regression tests and simulated v1.04 install/idempotence passed; `pi4test` testing pending |
| AllScan Mods v1.21 | Regression tests and simulated v1.20-to-v1.21 migration/idempotence passed; `pi4test` pending |
| AllScan Mods v1.22 | Previous dual-label experiment; removed in v1.36 to restore the v1.04 single-field editor |
| AllScan Mods v1.23 | Superseded before node testing; not installed |
| AllScan Mods v1.24 | User visual review approved the card text sizing; reported card-column gap and editor-help sizing issues |
| AllScan Mods v1.25 | Tighter TouchGUI card column spacing and smaller Favorites editor guidance; user reported node/callsign metadata became too small |
| AllScan Mods v1.26 | User test found the v1.25 metadata helper did not match the migration pattern; installer stopped safely without changes |
| AllScan Mods v1.27 | User confirmed install succeeded; node/callsign metadata still looked smaller than upstream 14px |
| AllScan Mods v1.28 | Desktop and landscape layout looked good; phone portrait showed node/callsign clipping, addressed in v1.29 |
| AllScan Mods v1.29 | Portrait-only node/callsign fitting; moved the 33-character reminder below its field and bolded the editor field titles |
| AllScan Mods v1.30 | Added a portrait-only horizontal fitting margin; landscape fit is unchanged |
| AllScan Mods v1.31 | Shifts the node/callsign line left by 1.5ch in portrait mode only |
| AllScan Mods v1.32 | Makes the portrait node/callsign line measurable so the existing fit routine can prevent clipping |
| AllScan Mods v1.33 | Adds portrait-only width compensation so shifting the node/callsign line left does not reduce space at its right edge; CSS max-width still capped the expansion |
| AllScan Mods v1.34 | Removes the portrait-only max-width cap so the extra 1.5ch line width can take effect; the final glyph remained clipped |
| AllScan Mods v1.35 | Allows portrait metadata glyphs to paint past their own text box while keeping the card boundary clipped |
| AllScan Mods v1.36 | Restores David’s stock single-field Favorites editor; keeps TouchGUI statistics, color mapping, responsive text sizing, and the confirmed portrait clipping fix |
| AllScan Mods v1.37 | Shows the shared label without the automatic callsign in the editor, limits it to 33 characters, and fits TouchGUI titles on one line without an ellipsis |
| AllScan Mods v1.38 | Hides the Favorites editor patch marker from the dialog and safely upgrades the v1.37 marker in place |
| AllScan Mods v1.39 | Removes the redundant length phrase and makes the callsign guidance larger, bold, and clearer |
| AllScan Mods v1.40 | Returns the callsign guidance to the form’s normal 12px font and weight, with higher contrast |
| AllScan Mods v1.41 | Matches the callsign guidance to the neighboring 11px form labels, with regular weight and higher contrast |
| AllScan Mods v1.42 | Makes the callsign guidance 10px in the Edit Favorite heading color and raises the field labels one size to 12px |
| AllScan Mods v1.43 | Tried giving long TouchGUI titles extra grid width; that made cards uneven and oversized |
| AllScan Mods v1.44 | Removes per-card grid expansion and lets long titles wrap within their normal card width |
| AllScan Mods v1.45 | Sets readable title-size floors of 14px on larger screens and 12px on narrow screens before wrapping long titles |
| AllScan Mods v1.46 | Shows the green node/callsign line above the white description on each TouchGUI card |
| AllScan Mods v1.47 | Aligns the green node/callsign line with the top of the # badge and adds spacing before the white description |
| AllScan Mods v1.48 | Makes only the green node/callsign line bold |
| AllScan Mods v1.49 | Shifts the bold node/callsign line left and gives it more width in landscape only; portrait is unchanged |
| AllScan Mods v1.50 | Reduces the landscape shift to 0.75ch while retaining 1.5ch of extra width, moving the bold line right without changing portrait |
| AllScan Mods v1.51 | Adds the callsign after the node number in the TouchGUI connected banner when one is available |
| AllScan Mods v1.52 | Adds aqua ASTDB descriptions and white favorite notes/location to TouchGUI cards, and widens the test cards by 5ch |
| AllScan Mods v1.53 | Moves the aqua row up 2px and fits each text row against the full available width before wrapping |
| AllScan Mods v1.54 | Reduces the aqua description text from 14px to 13px while preserving responsive fitting |
| AllScan Mods v1.55 | Centers the portrait node/callsign line and sizes aqua descriptions from 13px to 18px based on rendered width |
| AllScan Mods v1.56 | Adds a small width buffer to keep near-fit aqua descriptions on one line and adds separation before white notes |
| AllScan Mods v1.57 | Removes the extra aqua font shrink, keeps measured-fit descriptions on one line, and preserves the note gap |
| AllScan Mods v1.58 | Moves white notes toward the bottom of each card and keeps near-fit aqua descriptions on one line |
| AllScan Mods v1.59 | Fixes the installer migration for v1.57 TouchGUI wrapping code and upgrades v1.58 safely |
| AllScan Mods v1.60 | Prevents scaled aqua descriptions from clipping and raises white card notes |
| AllScan Mods v1.61 | Shifts aqua descriptions left by 0.5ch and raises white notes another 2px |
| AllScan Mods v1.62 | Prevents clipping of descenders in the white note row |
| AllScan Mods v1.63 | Uses Location when Name repeats the ASTDB description and shows Location beneath a one-line Name |
| AllScan Mods v1.64 | Uses a conservative similarity check to catch partial Name/Description overlap while retaining distinct user notes |
| AllScan Mods v1.65 | Avoids duplicated Name/Location text, removes repeated US/USA suffixes, centers the white row, and clears aqua descenders |
| AllScan Mods v1.66 | Removes repeated words shared by the aqua description and white location row, including HUB and US/USA |
| AllScan Mods v1.67 | Recognizes US/USA suffixes despite punctuation or surrounding Location text |
| AllScan Mods v1.68 | Fixes v1.67 card-helper detection so existing TouchGUI installs can upgrade safely |
| AllScan Mods v1.69 | Collapses equivalent `US` and `USA` favorite-name and Location rows to one white row |
| AllScan Mods v1.70 | Adds aqua description line-height clearance for descenders without increasing card height |
| AllScan Mods v1.71 | Applies descender clearance to both aqua descriptions and white note/location rows |
| AllScan Mods v1.72 | Always checks for missing incremental TouchGUI patches, even when the main feature set is already installed |
| AllScan Mods v1.73 | Lets card text descenders paint beyond the clipping card edge and restores the white note’s original line height |
| AllScan Mods v1.74 | Caps the aqua description text size at 14.3px for testing |
| AllScan Mods v1.75 | Sets white note/location text to a 14.3px base while retaining responsive shrinking |
| AllScan Mods v1.76 | Restores responsive aqua and white text sizing and adds a 2px visual gap between the white name and location lines |
| AllScan Mods v1.81 | Removes the unsuccessful v1.77-v1.80 white-text rendering experiments and keeps the last accepted card spacing |
| AllScan Mods v1.82 | Balances vertical spacing between card rows: reduces the callsign-to-description gap, moves white text down, and adds a small gap between white lines |
| AllScan Mods v1.83 | Adds another 2px between the white text lines and lowers the white text block another 2px |
| AllScan Mods v1.84 | Tests Arial bold font rendering on the white TouchGUI card text only |

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
<img width="1600" height="900" alt="Screenshot 2026-10-16 210859" src="https://github.com/user-attachments/assets/cb17c558-ef89-4a92-b19d-fe8c77addc8f" />

