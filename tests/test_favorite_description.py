#!/usr/bin/env python3
"""Check v1.93 Description editing, per-favorite storage, and TouchGUI data reuse."""
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT.parent.parent / "upstream" / "AllScan-main"


def patch_fixture(source_dir: Path, migrate_120_limit: bool = False) -> dict[str, str]:
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
        files = [str(p) for p in paths.values()]
        label_args = ["python3", str(ROOT / "lib/favorite-editor-label.py"), *files]
        subprocess.run(label_args, check=True, capture_output=True, text=True)
        args = ["python3", str(ROOT / "lib/favorite-description.py"), *files]
        subprocess.run(args, check=True, capture_output=True, text=True)
        if migrate_120_limit:
            for filename in ("index.php", "main.js"):
                path = paths[filename]
                content = path.read_text(encoding="utf-8")
                content = content.replace("$newDescription) > 20", "$newDescription) > 120")
                content = content.replace("newDescription.length > 20", "newDescription.length > 120")
                content = content.replace("Description must be 20 plain-text characters", "Description must be 120 plain-text characters")
                path.write_text(content, encoding="utf-8")
            view = paths["viewUtils.php"]
            content = view.read_text(encoding="utf-8").replace('maxlength="20"', 'maxlength="120"').replace('20 characters max.', '120 characters max.')
            view.write_text(content, encoding="utf-8")
            subprocess.run(args, check=True, capture_output=True, text=True)
            assert 'maxlength="20"' in view.read_text(encoding="utf-8")
            assert '20 characters max.' in view.read_text(encoding="utf-8")
        # A second pass must leave supported v1.93 files unchanged.
        before = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
        subprocess.run(args, check=True, capture_output=True, text=True)
        after = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
        assert before == after
        return after


def main() -> None:
    integrated = ROOT.parent.parent / "integration" / "allscan"
    legacy = ROOT.parent.parent / "upstream" / "AllScan-main"
    modified = patch_fixture(integrated, migrate_120_limit=True)
    legacy_modified = patch_fixture(legacy)
    assert 'id="favoriteEditDescription"' in modified["viewUtils.php"]
    assert 'rows="2"' in modified["viewUtils.php"]
    assert '20 characters max.' in modified["viewUtils.php"]
    assert 'The callsign is added automatically. 50 characters max.' in modified["viewUtils.php"]
    assert modified["viewUtils.php"].index('id="favoriteEditLabel"') < modified["viewUtils.php"].index('class="favoriteEditHint"') < modified["viewUtils.php"].index('id="favoriteEditDescription"')
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
    assert "20 characters max." in legacy_modified["viewUtils.php"]
    assert legacy_modified["viewUtils.php"].index('id="favoriteEditLabel"') < legacy_modified["viewUtils.php"].index('class="favoriteEditHint"') < legacy_modified["viewUtils.php"].index('id="favoriteEditDescription"')
    assert "Description must be 20 plain-text characters" in legacy_modified["index.php"]

    for filename in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        installer = (ROOT / filename).read_text(encoding="utf-8")
        assert "TouchGUI activity colors mod version: v1.93" in installer
        assert 'The callsign is added automatically. 50 characters max.' in installer
        assert 'favoriteEditDescriptionHint">20 characters max.' in installer
        assert 'id="favoriteEditLabel" maxlength="50"' in installer
        assert 'favoriteEditDescription" maxlength="20" rows="2"' in installer
        assert 'newLabel.length > 50' in installer
        assert "apply_favorite_description_live" in installer
        assert '"$FAVORITE_DESCRIPTION_PATCH" "$stage_index" "$stage_view" "$stage_js" "$stage_favs_utils" "$stage_css"' in installer
    print("PASS: Description override editor patches idempotently and leaves TouchGUI button code untouched.")
    print("PASS: database Description remains the default; override metadata flows through the shared Favorites row.")


if __name__ == "__main__":
    main()
