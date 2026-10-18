#!/usr/bin/env python3
"""Ensure the v1.04 shared Favorites label remains unmodified by Mods."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    forbidden = (
        "favorite-editor-label.py",
        "touchgui-favorite-labels.py",
        "FAVORITE_LABEL_PATCH",
        "TOUCHGUI_FAVORITE_LABEL_PATCH",
        "apply_favorite_label_live",
        "apply_touchgui_favorite_labels_live",
        "touchtguilabel",
    )
    for filename in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        source = (ROOT / filename).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.36" in source
        for marker in forbidden:
            assert marker not in source, f"{filename} still contains {marker}"
        assert "sortFavStats(5)" in source
        assert "sortFavStats(6)" in source
        assert "function openFavoriteEditor(" in source
        assert source.count("favoriteEditTouchguiLabel") == 1
        assert source.index("favoriteEditTouchguiLabel") < source.index("touchgui_activity_present()")

    activity = (ROOT / "lib/touchgui-activity.py").read_text(encoding="utf-8")
    assert "TouchGUI matching callsign removal v1.18" in activity
    assert "touchguiLabel" not in activity
    assert "label.slice(0, 32)" in activity

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "one shared Friendly Name/Label field" in readme
    assert "optional TouchGUI card label overrides" not in readme

    print("PASS: v1.04 keeps the standard single-field Favorites editor.")
    print("PASS: TouchGUI card title cleanup and text-fit behavior remain in the activity feature.")
    print("PASS: Rx%/LCnt sorting and PR #37 editor detection remain in both installers.")


if __name__ == "__main__":
    main()
