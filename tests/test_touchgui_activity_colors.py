#!/usr/bin/env python3
"""Local regression checks for TouchGUI activity-color installer code."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
PATCHER = ROOT / "lib" / "touchgui-activity.py"


def main():
    for installer in ("allscan-mods.sh", "install-allscan-n-mods.sh"):
        text = (ROOT / installer).read_text(encoding="utf-8")
        assert "apply_touchgui_activity_live" in text, installer
        assert "TOUCHGUI_ACTIVITY_PATCH" in text, installer
        assert "activity.rxPct" in text and "activity.linkCnt" in text, installer
        assert "channel-stats" in text, installer
        assert "allscan_version == v1.02 || $allscan_version == v1.03" in text, installer
        assert "AllScan already includes the integrated enhancements (PR #37)" in text, installer

    with tempfile.TemporaryDirectory(prefix="touchgui-activity-test-") as temp:
        temp = Path(temp)
        js = temp / "simple.js"
        css = temp / "simple.css"
        shutil.copy2(FIXTURES / "touchgui-base.js", js)
        shutil.copy2(FIXTURES / "touchgui-base.css", css)
        subprocess.run(["python3", str(PATCHER), str(js), str(css)], check=True)
        subprocess.run(["node", "--check", str(js)], check=True)
        patched_js = js.read_text(encoding="utf-8")
        patched_css = css.read_text(encoding="utf-8")
        assert "getChannelStats()" in patched_js
        assert "TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11." in patched_js
        assert "updateChannelActivity(stats)" in patched_js
        assert "function closeChannelStats()" in patched_js
        assert "function formatTouchguiStatusMessage(msg)" in patched_js
        assert "30000 / nodes.length" in patched_js
        assert "status === 429" in patched_js
        assert "Object.keys(nodeList)" in patched_js
        assert "Number(channel.node) < 3000000" in patched_js
        assert "data-activity=\"active-wt\"" in patched_css
        assert "TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11." in patched_css
        assert "height:100vh;\nheight:100dvh" in patched_css
        assert "@media (max-height:430px) {\n.simple-footer { display:grid; }\n}" in patched_css
        assert ".simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }" in patched_css
        assert "white-space:normal; overflow:visible; overflow-wrap:anywhere; min-width:0;" in patched_css
        assert "grid-template-columns:1fr; gap:0;" in patched_css
        assert "@media (max-width:430px)" in patched_css
        assert "font-size:9px; line-height:1.15;" in patched_css
        assert "@media (max-width:380px)" in patched_css
        assert ".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }" in patched_css
        assert "hsl(150,50%,15%)" in patched_js
        assert "hsl(150,50%,20%)" in patched_js
        assert "hsl(0,100%," in patched_js
        assert "var keyed = activity.txAverage > 5" in patched_js
        assert "convertActivityRange(activity.txAverage, 15, 29)" in patched_js
        assert "simple.txAvg[node] = Math.round(simple.txAvg[node] / 2 + txPercent / 2)" in patched_js
        assert "simple.txTim[node] = now" not in patched_js
        runtime_js = temp / "runtime.js"
        runtime_js.write_text(patched_js + r'''
var rx = {textContent: ''};
var lcnt = {textContent: ''};
var button = {
	dataset: {},
	style: {},
	querySelector: function(selector) { return selector === '.channel-rx' ? rx : lcnt; }
};
simple.channels = [{node: '2999999'}];
simple.channelByNode['2999999'] = simple.channels[0];
simple.channelsGrid = {querySelector: function() { return button; }};
updateChannelActivity({node: '2999999', keyups: 1, txtime: 25, keyed: 1, active: 1, wt: 0, busyPct: 39, linkCnt: 153});
if(rx.textContent !== 'Rx% 39' || lcnt.textContent !== 'LCnt 153')
	throw new Error('TouchGUI stats values were not rendered');
if(button.dataset.activity !== 'keyed' || button.style.backgroundColor !== 'hsl(0,100%,29%)')
	throw new Error('Keyed activity color was not retained');
var footer = formatTouchguiStatusMessage('ASL Ver: 3.10.5, AllScan Ver: 1.04<br>\nRxAudioStats supported, Simpleusb driver<br>\nChannel driver settings:<br>\nRx Level currently set to 550<br>\nTx A Level currently set to 550<br>\nTx B Level currently set to 550');
if(footer !== 'ASL Ver: 3.10.5, AllScan Ver: 1.04 - RxAudioStats supported, Simpleusb driver<br>Channel settings: Rx 550 | Tx A 550 | Tx B 550')
	throw new Error('Footer driver settings were not condensed correctly: ' + footer);
if(formatTouchguiStatusMessage('TouchGUI connected') !== 'TouchGUI connected')
	throw new Error('Unrelated footer message was changed');
''', encoding="utf-8")
        subprocess.run(["node", str(runtime_js)], check=True)
        before = (js.read_bytes(), css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(js), str(css)], check=True)
        assert before == (js.read_bytes(), css.read_bytes()), "second application changed files"

        older_js = temp / "older.js"
        older_css = temp / "older.css"
        shutil.copy2(FIXTURES / "touchgui-base.js", older_js)
        shutil.copy2(FIXTURES / "touchgui-base.css", older_css)
        subprocess.run(["python3", str(PATCHER), str(older_js), str(older_css)], check=True)
        older_js.write_text(older_js.read_text(encoding="utf-8").replace("TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.", "TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.10."), encoding="utf-8")
        older_style = older_css.read_text(encoding="utf-8").replace("TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.", "TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.10.")
        older_style = older_style.replace(".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }\n", "")
        older_css.write_text(older_style, encoding="utf-8")
        subprocess.run(["python3", str(PATCHER), str(older_js), str(older_css)], check=True)
        upgraded_footer = older_js.read_text(encoding="utf-8")
        assert "centered status footer v1.11" in upgraded_footer
        assert "join(' - ')" in upgraded_footer
        assert ".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }" in older_css.read_text(encoding="utf-8")

        legacy_js = temp / "legacy.js"
        legacy_css = temp / "legacy.css"
        shutil.copy2(FIXTURES / "touchgui-legacy.js", legacy_js)
        shutil.copy2(FIXTURES / "touchgui-legacy.css", legacy_css)
        subprocess.run(["python3", str(PATCHER), str(legacy_js), str(legacy_css)], check=True)
        subprocess.run(["node", "--check", str(legacy_js)], check=True)
        upgraded_js = legacy_js.read_text(encoding="utf-8")
        assert "simple.txTim[node] = now" not in upgraded_js
        assert "function convertActivityRange(value, min, max)" in upgraded_js
        upgraded = (legacy_js.read_bytes(), legacy_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(legacy_js), str(legacy_css)], check=True)
        assert upgraded == (legacy_js.read_bytes(), legacy_css.read_bytes()), "upgraded patch was not idempotent"

        current_js = temp / "current.js"
        current_css = temp / "current.css"
        shutil.copy2(FIXTURES / "touchgui-colors-v3.js", current_js)
        shutil.copy2(FIXTURES / "touchgui-colors-v3.css", current_css)
        subprocess.run(["python3", str(PATCHER), str(current_js), str(current_css)], check=True)
        subprocess.run(["node", "--check", str(current_js)], check=True)
        current_source = current_js.read_text(encoding="utf-8")
        current_style = current_css.read_text(encoding="utf-8")
        assert "Rx% —" in current_source and "LCnt —" in current_source
        assert "activity.rxPct" in current_source and "activity.linkCnt" in current_source
        assert "grid-template-rows:auto auto auto" in current_style
        assert "@media (max-width:700px)" in current_style
        assert "@media (max-height:430px)" in current_style
        current = (current_js.read_bytes(), current_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(current_js), str(current_css)], check=True)
        assert current == (current_js.read_bytes(), current_css.read_bytes()), "stats patch was not idempotent"

    print("PASS: installers include the TouchGUI activity patch path.")
    print("PASS: TouchGUI stats poller, colors, Rx%/LCnt fields, mobile footer visibility, viewport sizing, upgrades, syntax, and repeat application.")


if __name__ == "__main__":
    main()
