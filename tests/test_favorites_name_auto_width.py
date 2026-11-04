#!/usr/bin/env python3
"""Regression checks for the Favorites Name display fix, file version v1.90."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    installer = (ROOT / "allscan-mods.sh").read_text(encoding="utf-8")
    wrapper = (ROOT / "install-allscan-n-mods.sh").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Both separate install paths must patch AllScan v1.03-v1.05 integrated releases.
    for source in (installer, wrapper):
        assert "apply_favorites_name_auto_width_live" in source
        assert "apply_favorite_editor_label_live\n    apply_favorites_name_auto_width_live" in source
        assert "before-favorites-name-v1.90-" in source
        assert "Keep the complete callsign-prefixed Favorites Name visible v1.90." in source
        assert "visible v1.89." in source
        assert "determine its column width v1.90." in source
        assert "column width v1.89." in source
        assert "table.favs th:nth-child(3), table.favs td:nth-child(3)" in source
        assert "width:max-content;" in source
        assert "max-width:none;" in source
        assert "white-space:nowrap;" in source
        assert "TouchGUI activity colors mod version: v1.90" in source
    assert "AllScan Mods v1.90" in readme
    print("PASS: full Favorites Names remain visible and the Name column sizes to its content.")


if __name__ == "__main__":
    main()
