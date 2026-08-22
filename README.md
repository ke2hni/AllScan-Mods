<div align="center">

# 📊 AllScan Rx% / LCnt Sort Modification

### Safe, one-command sorting enhancement for the AllScan Favorites table

![Platform](https://img.shields.io/badge/Platform-AllStarLink%203-0b7285?style=for-the-badge)
![Debian](https://img.shields.io/badge/Debian-12%20%7C%2013-a81d33?style=for-the-badge&logo=debian&logoColor=white)
![AllScan](https://img.shields.io/badge/AllScan-v1.01-2f9e44?style=for-the-badge)
![Installer](https://img.shields.io/badge/Installer-Idempotent-6741d9?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-f59f00?style=for-the-badge)

**Adds clickable sorting to the live `Rx%` and `LCnt` columns without replacing AllScan's original statistics or node-control logic.**

</div>

---

## ✨ Overview

AllScan normally provides server-side sorting for the first five Favorites columns:

| Column | Stock AllScan sorting |
|:--|:--:|
| `#` | ✅ |
| `Node` | ✅ |
| `Name` | ✅ |
| `Desc` | ✅ |
| `Location` | ✅ |
| `Rx%` | ❌ |
| `LCnt` | ❌ |

`Rx%` and `LCnt` cannot use the original PHP sorter because their values are not present when PHP initially builds the table. They are populated later in the browser from live AllStarLink statistics.

The included installer adds a small client-side sorter that works with those live values while preserving the original AllScan behavior.

> [!NOTE]
> This is an unofficial local modification for AllScan. AllScan itself is authored by **David Gleason, NR9V**, and is available from the [official AllScan repository](https://github.com/davidgsd/AllScan).

---

## 🚀 Features

- Click `Rx%` or `LCnt` to sort the Favorites table.
- First click sorts from highest to lowest.
- Second click reverses the order.
- Switching columns starts with highest-to-lowest sorting.
- Direction arrows show the active order: `▼` descending or `▲` ascending.
- Rows whose live statistics have not arrived remain at the bottom.
- Equal values retain their current relative order.
- Existing row elements are moved instead of recreated.
- Node click and double-click handlers remain attached.
- Live statistics and connected-node highlighting continue working.
- No additional AllStarLink statistics requests are made.
- No service restart or reboot is required.

---

## 🛡️ Safety First

The installer is intentionally conservative and production-oriented.

### Automatic backups

Before changing either live file, it creates timestamped copies similar to:

```text
/var/www/html/allscan/index.php.before-rx-lcnt-sort-YYYYMMDD-HHMMSS
/var/www/html/allscan/js/main.js.before-rx-lcnt-sort-YYYYMMDD-HHMMSS
```

### Compatibility checks

The script verifies that:

- Both required AllScan files exist.
- The expected stock Favorites header is present.
- AllScan still uses column `5` for `Rx%`.
- AllScan still uses column `6` for `LCnt`.
- Exactly one `sortFavStats()` function exists after patching.

If a future AllScan update changes the expected structure, the installer stops without modifying the live files.

### Automatic failure recovery

If an error occurs after backups are created, the installer automatically restores both original files.

### Safe repeated execution

The installer is idempotent. Running it again after a successful installation reports:

```text
AllScan Rx% / LCnt sorting is already installed. No changes made.
```

---

## 📁 Files Modified

Only these two AllScan files are changed:

```text
/var/www/html/allscan/index.php
/var/www/html/allscan/js/main.js
```

The modification does **not** change:

- `stats/stats.php`
- AllStarLink statistics request frequency
- AllScan's dynamic request-rate protection
- Asterisk communications
- Connect or disconnect behavior
- `favorites.ini`
- The AllScan database
- Existing PHP sorting for the first five columns

---

## 📥 Download

Download the following file to your computer:

```text
apply-allscan-rx-lcnt-sort.sh
```

Then transfer it to the `asl` user's home directory on the node.

### Option 1 — Windows SCP

From PowerShell in the folder containing the downloaded script, replace `node44690.local` if necessary:

```powershell
scp .\apply-allscan-rx-lcnt-sort.sh asl@node44690.local:/home/asl/
```

You may use the node's IP address instead:

```powershell
scp .\apply-allscan-rx-lcnt-sort.sh asl@192.168.1.100:/home/asl/
```

### Option 2 — File-transfer program

Use WinSCP, FileZilla, or another SFTP/SCP client:

| Setting | Value |
|:--|:--|
| Protocol | SFTP or SCP |
| User | `asl` |
| Destination | `/home/asl/` |
| File | `apply-allscan-rx-lcnt-sort.sh` |

---

## ⚙️ Installation

SSH into the node and run this single copy-and-paste command:

```bash
cd /home/asl && chmod 755 apply-allscan-rx-lcnt-sort.sh && sudo ./apply-allscan-rx-lcnt-sort.sh
```

This command:

1. Changes to `/home/asl`.
2. Applies executable permissions with `chmod 755`.
3. Runs the installer with the root permissions required to modify AllScan.

When installation succeeds, the script displays the two backup filenames and:

```text
AllScan Rx% / LCnt sorting installed successfully.
Hard-refresh the AllScan page with Ctrl+F5.
```

Afterward, open AllScan and press **Ctrl+F5** so the browser loads the updated JavaScript.

---

## 🧭 Custom AllScan Directory

The default AllScan directory is:

```text
/var/www/html/allscan
```

If your installation uses another directory, supply it explicitly:

```bash
cd /home/asl && chmod 755 apply-allscan-rx-lcnt-sort.sh && sudo ./apply-allscan-rx-lcnt-sort.sh --allscan-dir /your/allscan/path
```

For example, the common HamVOIP web-root location would be:

```bash
cd /home/asl && chmod 755 apply-allscan-rx-lcnt-sort.sh && sudo ./apply-allscan-rx-lcnt-sort.sh --allscan-dir /srv/http/allscan
```

---

## ✅ Verification

### Browser verification

1. Hard-refresh AllScan with **Ctrl+F5**.
2. Wait for live values to appear under `Rx%` and `LCnt`.
3. Click `Rx%` once and confirm the highest value moves to the top.
4. Confirm a `▼` arrow appears next to `Rx%`.
5. Click `Rx%` again and confirm the lowest value moves to the top with `▲`.
6. Repeat the same check with `LCnt`.
7. Click or double-click a node and confirm the normal AllScan controls still work.

### File verification

Use this single command to confirm that both header links and exactly one sorter function are installed:

```bash
sudo grep -F 'sortFavStats' /var/www/html/allscan/index.php && sudo grep -Ec 'function[[:space:]]+sortFavStats[[:space:]]*\(' /var/www/html/allscan/js/main.js
```

The final number should be:

```text
1
```

---

## ↩️ Manual Rollback

The successful installation output displays the exact backup filenames. Restore those two matching timestamped backups with:

```bash
sudo cp -a /var/www/html/allscan/index.php.before-rx-lcnt-sort-YYYYMMDD-HHMMSS /var/www/html/allscan/index.php && sudo cp -a /var/www/html/allscan/js/main.js.before-rx-lcnt-sort-YYYYMMDD-HHMMSS /var/www/html/allscan/js/main.js
```

Replace `YYYYMMDD-HHMMSS` with the timestamp shown by the installer, then hard-refresh the browser with **Ctrl+F5**.

> [!IMPORTANT]
> Always restore `index.php` and `main.js` backups bearing the same timestamp.

---

## 🔄 AllScan Updates

The official AllScan updater may replace `index.php` or `js/main.js`, removing this local modification.

After updating AllScan:

1. Hard-refresh the browser and check whether `Rx%` and `LCnt` remain clickable.
2. If the modification was removed, run the installer again.
3. If the updated AllScan structure remains compatible, the script safely reapplies the change.
4. If upstream changed the relevant code, the installer stops without modifying anything so the patch can be reviewed first.

---

## 🔧 Troubleshooting

### `Run this script with sudo`

Run the installer using the complete command from the Installation section.

### `Required AllScan file not found`

Confirm AllScan is installed under `/var/www/html/allscan`, or use `--allscan-dir` with the correct location.

### `Expected the stock Favorites header exactly once`

The file may already contain another modification, or a newer AllScan release may have changed the header. The installer intentionally leaves the node unchanged. Review the current files before attempting a manual patch.

### The headers do not appear clickable

Press **Ctrl+F5** or clear the browser cache. AllScan's previous JavaScript may still be cached.

### The table does not automatically move after every live update

This is intentional. Live values continue updating, but the table only sorts when a header is clicked. This prevents rows from jumping while the table is being used.

---

## 🧪 Tested Configuration

| Component | Tested configuration |
|:--|:--|
| Node | `node44690` |
| Platform | AllStarLink 3 |
| Operating system | Debian 13 |
| AllScan | v1.01-compatible source layout |
| Web root | `/var/www/html/allscan` |

The installer also supports an alternate directory through `--allscan-dir` and includes a documented HamVOIP path example.

---

## 🎯 Design Philosophy

- Preserve the official AllScan application.
- Make the smallest practical local changes.
- Never silently guess when upstream code is unexpected.
- Back up before modifying production files.
- Keep installation repeatable and easy to audit.
- Avoid extra network requests or background processes.
- Make rollback simple and transparent.

---

## 👤 Author

**KE2HNI**

Created as an enhancement for personal AllStarLink nodes running AllScan.

AllScan is a separate open-source project created by **David Gleason, NR9V**. This modification is not an official AllScan release and is not affiliated with or endorsed by the AllScan author.

---

## 📄 License

MIT License

Use at your own risk. Review the script before execution and keep current backups of important node configuration and application files.

Testing modifications on a non-production node first is recommended whenever possible.

---

<div align="center">

### Built for safer, cleaner AllStarLink node customization

**KE2HNI · AllScan Rx% / LCnt Sort Modification**

</div>
