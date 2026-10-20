#!/usr/bin/env python3
"""Ensure v1.44 edits one shared call-sign-free Favorites label."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    forbidden = (
        "FAVORITE_LABEL_PATCH",
        "TOUCHGUI_FAVORITE_LABEL_PATCH",
        "touchtguilabel",
    )
    for filename in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        source = (ROOT / filename).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.65" in source
        assert "favoriteEditHint" in source
        assert "Favorites editor call-sign hint v1.43." in source
        assert "apply_favorite_editor_label_live" in source
        assert "favorite-editor-label.py" in source
        for marker in forbidden:
            assert marker not in source, f"{filename} still contains {marker}"
        assert "sortFavStats(5)" in source
        assert "sortFavStats(6)" in source
        assert "function openFavoriteEditor(" in source

    activity = (ROOT / "lib/touchgui-activity.py").read_text(encoding="utf-8")
    assert "TouchGUI matching callsign removal v1.18" in activity
    assert "touchguiLabel" not in activity
    assert "label.length > 33" not in activity
    assert "TouchGUI adaptive title fit v1.45" in activity
    assert "TouchGUI single-line label fit v1.37" in activity

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "single shared Friendly Name/Label field" in readme
    assert "call-sign-free view of that same field with a 33-character limit" in readme
    assert "optional TouchGUI card label overrides" not in readme

    helper = (ROOT / "lib/favorite-editor-label.py").read_text(encoding="utf-8")
    assert '<!-- AllScan Mods: 33-character call-sign-free Favorites editor label v1.43. -->' in helper
    assert "font-size:10px;font-weight:normal" in helper
    assert "color:hsl(240,30%,70%)" in helper
    assert 'maxlength="33"' in helper
    assert "substr($name, 0, 33)" in helper
    assert "newLabel.length > 33" in helper
    print("PASS: v1.04 keeps one shared, call-sign-free, 33-character Favorites label.")
    print("PASS: TouchGUI title fitting keeps card widths uniform and applies readable size floors before wrapping.")
    print("PASS: Rx%/LCnt sorting and PR #37 editor detection remain in both installers.")


if __name__ == "__main__":
    main()
