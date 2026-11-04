# AllScan standalone uninstaller v2

Built against the supplied AllScan source archive at commit `db1800c53515f9fddd079d1ec6968e686136d82b`, whose `include/common.php` identifies AllScan v1.05. The source archive has no branch metadata.

## What it removes

The script removes one selected AllScan web application directory after creating and verifying a timestamped recovery archive under `/var/backups/allscan-uninstall/`.

By default, it keeps that instance's database at `/etc/allscan/<web-folder-name>.db`. Pass `--remove-db` to remove that database after it has been included in the recovery archive. In either mode, the archive contains the AllScan web directory.

It preserves `/etc/allscan/asdb.txt`, favorites files outside the selected web directory, other AllScan instances, optional DTMF files that may be shared with Asterisk, system packages, services, and web-server configuration. It does not restart Apache or Asterisk.

## Test on a node

First copy the script to the node and run **check only**. This command inspects the selected installation and makes no changes:

```bash
sudo ./uninstall-allscan-v1.sh --check --path /var/www/html/allscan
```

For HamVOIP, use `/srv/http/allscan`. If both conventional locations contain AllScan, `--path` is required. Custom web roots require the explicit `--allow-custom-root` option.

Review the check output before proceeding. To uninstall, run the same command without `--check`; the script asks you to type `UNINSTALL allscan` before it changes anything. Use `--remove-db` only if you also intend to remove that instance's database.

## Restore

The script prints the verified archive path. The archive stores paths relative to `/`, so restoring it is:

```bash
sudo tar -xzf /var/backups/allscan-uninstall/allscan-allscan-before-uninstall-YYYYMMDD-HHMMSS.tar.gz -C /
```

Replace the example archive name with the exact path printed by the script. Restore the database from the archive only if it was removed.

## Version

- `uninstall-allscan-v1.sh`: v2
- `README-uninstall-allscan-v1.md`: v2
