#!/usr/bin/env python3
"""Check v1.93 Description editing, per-favorite storage, and TouchGUI data reuse."""
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT.parent.parent / "upstream" / "AllScan-main"


def patch_fixture(source_dir: Path) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="favs-description-v193-") as folder:
        target = Path(folder)
        paths = {
            "index.php": target / "index.php",
            "viewUtils.php": target / "viewUtils.php",
            "main.js": target / "main.js",
            "favsUtils.php": target / "favsUtils.php",
            "main.css": target / "main.css",
        }
        for name, path in paths.items():
            source = source_dir / name if name in ("index.php",) else source_dir / "include" / name
            if name == "main.js":
                source = source_dir / "js" / name
            elif name == "main.css":
                source = source_dir / "css" / name
            shutil.copy(source, path)
        args = ["python3", str(ROOT / "lib/favorite-description.py"), *(str(p) for p in paths.values())]
        subprocess.run(args, check=True, capture_output=True, text=True)
        # A second pass must leave supported v1.93 files unchanged.
        before = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
        subprocess.run(args, check=True, capture_output=True, text=True)
        after = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
        assert before == after
        return after


def main() -> None:
    integrated = ROOT.parent.parent / "integration" / "allscan"
    legacy = ROOT.parent.parent / "upstream" / "AllScan-main"
    modified = patch_fixture(integrated)
    legacy_modified = patch_fixture(legacy)
    assert 'id="favoriteEditDescription"' in modified["viewUtils.php"]
    assert 'id="favoriteEditUseDatabase" checked' in modified["viewUtils.php"]
    assert "data-fav-database-description" in modified["index.php"]
    assert "editdescdb" in modified["index.php"]
    assert "Favorite Description override cleanup v1.93." in modified["index.php"]
    assert "databaseDescription" in modified["favsUtils.php"]
    assert "descriptionOverride" in modified["favsUtils.php"]
    assert "channelDescription(channel)" in (UPSTREAM / "js/simple.js").read_text(encoding="utf-8")
    # The patch helper does not touch simple/ TouchGUI buttons or their request code.
    assert "autodiscBtn" not in modified["main.js"]
    # The v1.02/v1.03 installer-generated editor includes the same field and server action.
    assert "favoriteEditDescription" in legacy_modified["viewUtils.php"]
    assert "Description must be 120 plain-text characters" in legacy_modified["index.php"]

    for filename in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        installer = (ROOT / filename).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.93" in installer
        assert "apply_favorite_description_live" in installer
        assert '"$FAVORITE_DESCRIPTION_PATCH" "$stage_index" "$stage_view" "$stage_js" "$stage_favs_utils" "$stage_css"' in installer
    print("PASS: Description override editor patches idempotently and leaves TouchGUI button code untouched.")
    print("PASS: database Description remains the default; override metadata flows through the shared Favorites row.")


if __name__ == "__main__":
    main()
