#!/usr/bin/env python3
"""Regression checks for the Favorites Name display fix, file version v1.89."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    installer = (ROOT / "allscan-mods.sh").read_text(encoding="utf-8")
    wrapper = (ROOT / "install-allscan-n-mods.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # The main installer must patch the files used by integrated AllScan v1.04/v1.05.
    assert "apply_favorites_name_auto_width_live" in installer
    assert 'apply_favorites_name_auto_width_live\n    if [[ $allscan_version == v1.05 ]]' in installer
    assert "before-favorites-name-v1.89-" in installer
    assert "Keep the complete callsign-prefixed Favorites Name visible v1.89." in installer
    assert "determine its column width v1.89." in installer
    assert "table.favs th:nth-child(3), table.favs td:nth-child(3)" in installer
    assert "width:max-content;" in installer
    assert "max-width:none;" in installer
    assert "white-space:nowrap;" in installer
    assert "AllScan Mods v1.89" in readme
    assert "TouchGUI activity colors mod version: v1.89" in installer
    assert "TouchGUI activity colors mod version: v1.89" in wrapper
    print("PASS: full Favorites Names remain visible and the Name column sizes to its content.")


if __name__ == "__main__":
    main()
