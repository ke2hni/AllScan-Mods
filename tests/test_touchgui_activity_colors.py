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
        assert "TouchGUI activity colors mod version: v1.18" in text, installer
        assert "apply_touchgui_activity_live" in text, installer
        assert "TOUCHGUI_ACTIVITY_PATCH" in text, installer
        assert "activity.rxPct" in text and "activity.linkCnt" in text, installer
        assert "rx.textContent = hasRx ? String(activity.rxPct) + '%' : '—';" in text, installer
        assert "border-radius:8px;" in text, installer
        assert "font-size:12px;" in text, installer
        assert "grep -A7 -F '.channel-stats {'" in text, installer
        assert "channel-side" in text, installer
        assert "simple.txTim[node] = now" in text, installer
        assert "responseData.retcode == 429" in text, installer
        assert "convertActivityRange(2 * rxPct, 10, 30)" in text, installer
        assert "button.style.backgroundColor = '';" in text, installer
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
        assert "TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.18." in patched_js
        assert "TouchGUI matching callsign removal v1.18" in patched_js
        assert "updateChannelActivity(stats)" in patched_js
        assert "function closeChannelStats()" in patched_js
        assert "function formatTouchguiStatusMessage(msg)" in patched_js
        assert "30000 / nodes.length" in patched_js
        assert "status === 429" in patched_js
        assert "responseData.retcode == 429" in patched_js
        assert "getChannelStatsNodes()" in patched_js
        assert "nodes.indexOf(node) < 0" in patched_js
        assert "Object.keys(nodeList)" not in patched_js
        assert "number < 3000000" in patched_js
        assert "simple.txTim[node] = now" in patched_js
        assert "convertActivityRange(2 * rxPct, 10, 30)" in patched_js
        assert "convertActivityRange(3 * linkCount, 15, 30)" in patched_js
        assert "channel-side" in patched_js and "channel-content" in patched_js
        assert patched_js.index('class="channel-side"') < patched_js.index('class="channel-content"')
        assert "active-wt" in patched_js
        assert "TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17." in patched_css
        assert "font-size:12px;\nfont-weight:normal;\nline-height:1;" in patched_css
        assert ".channel-stats { font-size:11px; }" in patched_css
        assert "flex:0 0 34px;\nborder-radius:8px;" in patched_css
        assert "padding:1px 4px;\nborder-radius:8px;" in patched_css
        assert "min-height:86px;\npadding:8px;" in patched_css
        assert "TouchGUI centered card text v1.17" in patched_css
        assert ".channel-label, .channel-meta {\nwidth:100%;\nmin-width:0;" in patched_css
        assert ".channel-label {\nfont-size:16px;\noverflow-wrap:anywhere;" in patched_css
        assert ".channel-btn { min-height:82px; padding:7px; }" in patched_css
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
        assert "button.style.backgroundColor = '';" in patched_js
        assert '.channel-btn[data-activity="active"]' not in patched_css
        assert "var keyed = activity.txAverage > 5" in patched_js
        assert "convertActivityRange(activity.txAverage, 15, 29)" in patched_js
        assert "simple.txAvg[node] = Math.round(simple.txAvg[node] / 2 + txPercent / 2)" in patched_js
        assert "simple.txTim[node] = now" in patched_js
        runtime_js = temp / "runtime.js"
        runtime_js.write_text(patched_js + r'''
function escapeRegExp(txt) {
	return String(txt).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
var nowSeconds = 100;
Date.now = function() { return nowSeconds * 1000; };
var index = {style: {}};
var rx = {textContent: '', style: {}};
var lcnt = {textContent: '', style: {}};
var button = {
	dataset: {},
	style: {},
	querySelector: function(selector) {
		if(selector === '.channel-index') return index;
		if(selector === '.channel-rx') return rx;
		if(selector === '.channel-lcnt') return lcnt;
		return null;
	}
};
var cardLabel = channelLabel({node: '512511', call: 'GB3CR', label: 'GB3CR North Wales UK 512511', name: 'GB3CR'});
if(cardLabel !== 'North Wales UK')
	throw new Error('TouchGUI did not remove the exact ASTDB callsign from the card title: ' + cardLabel);
cardLabel = channelLabel({node: '512511', call: 'GB3CR', label: 'GB3CR North Wales GB3CR UK 512511'});
if(cardLabel !== 'North Wales UK')
	throw new Error('TouchGUI did not remove each exact callsign token: ' + cardLabel);
cardLabel = channelLabel({node: '512511', call: 'GB3CR', label: 'XGB3CR North Wales 512511'});
if(cardLabel !== 'XGB3CR North Wales')
	throw new Error('TouchGUI removed a callsign embedded in a different token: ' + cardLabel);
cardLabel = channelLabel({node: '512511', call: 'GB3CR', label: 'GB3XX North Wales 512511'});
if(cardLabel !== 'GB3XX North Wales')
	throw new Error('TouchGUI removed a callsign that did not match AllScan data: ' + cardLabel);
cardLabel = channelLabel({node: '512511', call: 'GB3CR', label: 'GB3CR 512511', desc: 'GB3CR Backup Repeater'});
if(cardLabel !== 'Backup Repeater')
	throw new Error('TouchGUI did not fall back to description after removing a callsign-only label: ' + cardLabel);
cardLabel = channelLabel({node: '512511', call: 'GB3CR', label: 'GB3CR 12345678901234567890123456789012345 512511'});
if(cardLabel.length > 33 || cardLabel.charAt(cardLabel.length - 1) !== '…')
	throw new Error('TouchGUI card title did not fit within 33 characters: ' + cardLabel);
simple.channels = [
	{node: '30000'}, {node: '2000'}, {node: '30000'},
	{node: '1999'}, {node: '3000000'}, {node: '2001'}
];
if(JSON.stringify(getChannelStatsNodes()) !== JSON.stringify(['30000', '2000', '2001']))
	throw new Error('TouchGUI stats nodes did not preserve favorite order and uniqueness');
simple.channels = [{node: '2999999'}];
simple.channelByNode['2999999'] = simple.channels[0];
simple.channelsGrid = {querySelector: function() { return button; }};
updateChannelActivity({node: '2999999', keyups: 100, txtime: 1000, keyed: 0, active: 1, wt: 0, busyPct: 39, linkCnt: 153});
if(rx.textContent !== '39%' || lcnt.textContent !== '153')
	throw new Error('TouchGUI stats values were not rendered: rx=' + rx.textContent + ', lcnt=' + lcnt.textContent);
if(simple.txTim['2999999'] !== 100)
	throw new Error('TouchGUI did not store the current Tx time snapshot');
if(button.style.backgroundColor !== '' || index.style.backgroundColor !== 'hsl(150,50%,15%)' || rx.style.backgroundColor !== 'hsl(125,40%,26%)')
	throw new Error('Rx green did not use the main-page percentage gradient');
if(lcnt.style.backgroundColor !== 'hsl(240,40%,30%)')
	throw new Error('LCnt blue did not use the main-page count gradient');
applyChannelActivity(button, {active: 0, wt: 0, txAverage: 0, rxPct: 2, linkCnt: 2});
if(index.style.backgroundColor !== 'transparent' || rx.style.backgroundColor !== '' || lcnt.style.backgroundColor !== '')
	throw new Error('The #, Rx%, and LCnt backgrounds did not follow the table zero/inactive thresholds');
applyChannelActivity(button, {active: 1, wt: 0, txAverage: 0, rxPct: 10, linkCnt: 3});
var lowRxShade = rx.style.backgroundColor;
applyChannelActivity(button, {active: 1, wt: 0, txAverage: 0, rxPct: 39, linkCnt: 153});
if(lowRxShade !== 'hsl(125,40%,14%)' || rx.style.backgroundColor !== 'hsl(125,40%,26%)' || button.style.backgroundColor !== '')
	throw new Error('Higher Rx% did not produce a brighter green');
applyChannelActivity(button, {active: 1, wt: 1, txAverage: 0, rxPct: '-', linkCnt: '-'});
if(rx.textContent !== '—' || lcnt.textContent !== '-')
	throw new Error('Missing Rx% data was not shown as a dash');
if(button.style.backgroundColor !== '' || index.style.backgroundColor !== 'hsl(150,50%,20%)')
	throw new Error('The WebTransceiver active color did not match the table');
applyChannelActivity(button, {active: 1, wt: 0, txAverage: 100, rxPct: 39, linkCnt: 153});
if(button.style.backgroundColor !== '' || index.style.backgroundColor !== 'hsl(0,100%,29%)')
	throw new Error('Current keyed activity did not use the table red color');
applyChannelActivity(button, {active: 1, wt: 1, txAverage: 5, rxPct: '-', linkCnt: '-'});
if(index.style.backgroundColor !== 'hsl(150,50%,20%)')
	throw new Error('Tx color threshold changed at exactly 5%');
applyChannelActivity(button, {active: 1, wt: 1, txAverage: 6, rxPct: '-', linkCnt: '-'});
if(index.style.backgroundColor !== 'hsl(0,100%,16%)')
	throw new Error('Tx red did not start above the table 5% threshold');
nowSeconds = 130;
updateChannelActivity({node: '2999999', keyups: 101, txtime: 1005, keyed: 0, active: 1, wt: 0, busyPct: 39, linkCnt: 153});
if(simple.txAvg['2999999'] !== 9 || button.dataset.activity !== 'keyed' || index.style.backgroundColor !== 'hsl(0,100%,16%)' || button.style.backgroundColor !== '')
	throw new Error('Tx% was not calculated from consecutive total-Tx-time samples');
var scheduledDelay = null;
var originalSetTimeout = setTimeout;
global.setTimeout = function(callback, delay) { scheduledDelay = delay; return 1; };
function FakeXHR() {
	this.readyState = 0;
	this.status = 200;
	this.responseText = '{"data":{"retcode":429,"node":"2999999"}}';
}
FakeXHR.prototype.open = function() {};
FakeXHR.prototype.setRequestHeader = function() {};
FakeXHR.prototype.send = function() { this.readyState = 4; this.onreadystatechange(); };
FakeXHR.prototype.abort = function() {};
global.XMLHttpRequest = FakeXHR;
simple.statsIndex = 0;
getChannelStats();
global.setTimeout = originalSetTimeout;
if(simple.statsIndex !== 0 || scheduledDelay !== 15000)
	throw new Error('TouchGUI did not retry the same node after a JSON-level 429');
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

        prior_markers = (
            "TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.",
            "TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.10.",
            "TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
            "TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.08.",
            "TouchGUI activity colors, Rx%/LCnt, and complete status footer v1.07.",
            "TouchGUI activity colors, Rx%/LCnt, and mobile footer v1.06.",
            "TouchGUI activity colors and Rx%/LCnt v1.05.",
        )
        for prior_marker in prior_markers:
            older_js = temp / "older.js"
            older_css = temp / "older.css"
            old_marker = "TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11."
            js_text = (FIXTURES / "touchgui-installed-v1.11.js").read_text(encoding="utf-8")
            css_text = (FIXTURES / "touchgui-installed-v1.11.css").read_text(encoding="utf-8")
            older_js.write_text(js_text.replace(old_marker, prior_marker), encoding="utf-8")
            older_css.write_text(css_text.replace(old_marker, prior_marker), encoding="utf-8")
            subprocess.run(["python3", str(PATCHER), str(older_js), str(older_css)], check=True)
            subprocess.run(["node", "--check", str(older_js)], check=True)
            upgraded_js = older_js.read_text(encoding="utf-8")
            upgraded_css = older_css.read_text(encoding="utf-8")
            assert "rounded value badges v1.18" in upgraded_js
            assert "simple.txTim[node] = now" in upgraded_js
            assert "channel-side" in upgraded_js and ".channel-side" in upgraded_css
            assert '.channel-btn[data-activity="active"]' not in upgraded_css
            assert "join(' - ')" in upgraded_js
            assert ".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }" in upgraded_css
            upgraded = (older_js.read_bytes(), older_css.read_bytes())
            subprocess.run(["python3", str(PATCHER), str(older_js), str(older_css)], check=True)
            assert upgraded == (older_js.read_bytes(), older_css.read_bytes()), f"v1.12 was not idempotent after {prior_marker} upgrade"

        v112_js = temp / "v1.12.js"
        v112_css = temp / "v1.12.css"
        shutil.copy2(FIXTURES / "touchgui-installed-v1.12.js", v112_js)
        shutil.copy2(FIXTURES / "touchgui-installed-v1.12.css", v112_css)
        subprocess.run(["python3", str(PATCHER), str(v112_js), str(v112_css)], check=True)
        subprocess.run(["node", "--check", str(v112_js)], check=True)
        upgraded_js = v112_js.read_text(encoding="utf-8")
        upgraded_css = v112_css.read_text(encoding="utf-8")
        assert "rounded value badges v1.18" in upgraded_js
        assert "button.style.backgroundColor = '';" in upgraded_js
        assert '.channel-btn[data-activity="active"]' not in upgraded_css
        v112_upgraded = (v112_js.read_bytes(), v112_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(v112_js), str(v112_css)], check=True)
        assert v112_upgraded == (v112_js.read_bytes(), v112_css.read_bytes()), "v1.12 upgrade was not idempotent"

        v113_js = temp / "v1.13.js"
        v113_css = temp / "v1.13.css"
        shutil.copy2(FIXTURES / "touchgui-installed-v1.13.js", v113_js)
        shutil.copy2(FIXTURES / "touchgui-installed-v1.13.css", v113_css)
        subprocess.run(["python3", str(PATCHER), str(v113_js), str(v113_css)], check=True)
        subprocess.run(["node", "--check", str(v113_js)], check=True)
        upgraded_js = v113_js.read_text(encoding="utf-8")
        upgraded_css = v113_css.read_text(encoding="utf-8")
        assert "rounded value badges v1.18" in upgraded_js
        assert "rounded value badges v1.17" in upgraded_css
        assert "Rx% —" not in upgraded_js and "LCnt —" not in upgraded_js
        assert "rx.textContent = hasRx ? String(activity.rxPct) + '%' : '—';" in upgraded_js
        assert "links.textContent = activity.linkCnt === undefined" in upgraded_js
        v113_upgraded = (v113_js.read_bytes(), v113_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(v113_js), str(v113_css)], check=True)
        assert v113_upgraded == (v113_js.read_bytes(), v113_css.read_bytes()), "v1.13 upgrade was not idempotent"

        v114_js = temp / "v1.14.js"
        v114_css = temp / "v1.14.css"
        shutil.copy2(FIXTURES / "touchgui-installed-v1.14.js", v114_js)
        shutil.copy2(FIXTURES / "touchgui-installed-v1.14.css", v114_css)
        subprocess.run(["python3", str(PATCHER), str(v114_js), str(v114_css)], check=True)
        subprocess.run(["node", "--check", str(v114_js)], check=True)
        upgraded_js = v114_js.read_text(encoding="utf-8")
        upgraded_css = v114_css.read_text(encoding="utf-8")
        assert "rounded value badges v1.18" in upgraded_js
        assert "rounded value badges v1.17" in upgraded_css
        assert "String(activity.rxPct) + '%'" in upgraded_js
        assert "border-radius:8px;" in upgraded_css
        assert "min-height:86px;" in upgraded_css
        assert ".channel-btn { min-height:82px; padding:7px; }" in upgraded_css
        v114_upgraded = (v114_js.read_bytes(), v114_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(v114_js), str(v114_css)], check=True)
        assert v114_upgraded == (v114_js.read_bytes(), v114_css.read_bytes()), "v1.14 upgrade was not idempotent"

        v116_js = temp / "v1.16.js"
        v116_css = temp / "v1.16.css"
        shutil.copy2(FIXTURES / "touchgui-installed-v1.16.js", v116_js)
        shutil.copy2(FIXTURES / "touchgui-installed-v1.16.css", v116_css)
        subprocess.run(["python3", str(PATCHER), str(v116_js), str(v116_css)], check=True)
        subprocess.run(["node", "--check", str(v116_js)], check=True)
        upgraded_js = v116_js.read_text(encoding="utf-8")
        upgraded_css = v116_css.read_text(encoding="utf-8")
        assert "rounded value badges v1.18" in upgraded_js and "rounded value badges v1.17" in upgraded_css
        assert "TouchGUI centered card text v1.17" in upgraded_css
        assert "min-height:86px;\npadding:8px;" in upgraded_css
        assert ".channel-btn { min-height:82px; padding:7px; }" in upgraded_css
        v116_upgraded = (v116_js.read_bytes(), v116_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(v116_js), str(v116_css)], check=True)
        assert v116_upgraded == (v116_js.read_bytes(), v116_css.read_bytes()), "v1.16 upgrade was not idempotent"

        v115_js = temp / "v1.15.js"
        v115_css = temp / "v1.15.css"
        shutil.copy2(FIXTURES / "touchgui-installed-v1.15.js", v115_js)
        shutil.copy2(FIXTURES / "touchgui-installed-v1.15.css", v115_css)
        subprocess.run(["python3", str(PATCHER), str(v115_js), str(v115_css)], check=True)
        subprocess.run(["node", "--check", str(v115_js)], check=True)
        upgraded_js = v115_js.read_text(encoding="utf-8")
        upgraded_css = v115_css.read_text(encoding="utf-8")
        assert "rounded value badges v1.18" in upgraded_js and "rounded value badges v1.17" in upgraded_css
        assert "font-size:12px;\nfont-weight:normal;\nline-height:1;" in upgraded_css
        assert "padding:1px 4px;\nborder-radius:8px;" in upgraded_css
        assert ".channel-stats { font-size:11px; }" in upgraded_css
        assert "min-height:86px;\npadding:8px;" in upgraded_css
        assert ".channel-btn { min-height:82px; padding:7px; }" in upgraded_css
        v115_upgraded = (v115_js.read_bytes(), v115_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(v115_js), str(v115_css)], check=True)
        assert v115_upgraded == (v115_js.read_bytes(), v115_css.read_bytes()), "v1.15 upgrade was not idempotent"

        legacy_js = temp / "legacy.js"
        legacy_css = temp / "legacy.css"
        shutil.copy2(FIXTURES / "touchgui-legacy.js", legacy_js)
        shutil.copy2(FIXTURES / "touchgui-legacy.css", legacy_css)
        subprocess.run(["python3", str(PATCHER), str(legacy_js), str(legacy_css)], check=True)
        subprocess.run(["node", "--check", str(legacy_js)], check=True)
        upgraded_js = legacy_js.read_text(encoding="utf-8")
        assert "simple.txTim[node] = now" in upgraded_js
        assert "function convertActivityRange(value, min, max)" in upgraded_js
        assert "channel-side" in upgraded_js
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
        assert 'class="channel-rx">—</span>' in current_source and 'class="channel-lcnt">—</span>' in current_source
        assert "rounded value badges v1.18" in current_source
        assert "TouchGUI matching callsign removal v1.18" in current_source
        assert "border-radius:8px;" in current_style
        assert "activity.rxPct" in current_source and "activity.linkCnt" in current_source
        assert "grid-template-rows:auto;" in current_style
        assert "grid-template-rows:auto auto auto" not in current_style
        assert "@media (max-width:700px)" in current_style
        assert "@media (max-height:430px)" in current_style
        current = (current_js.read_bytes(), current_css.read_bytes())
        subprocess.run(["python3", str(PATCHER), str(current_js), str(current_css)], check=True)
        assert current == (current_js.read_bytes(), current_css.read_bytes()), "stats patch was not idempotent"

        v117_js = temp / "v1.17.js"
        v117_css = temp / "v1.17.css"
        shutil.copy2(FIXTURES / "touchgui-installed-v1.17.js", v117_js)
        shutil.copy2(FIXTURES / "touchgui-installed-v1.17.css", v117_css)
        subprocess.run(["python3", str(PATCHER), str(v117_js), str(v117_css)], check=True)
        subprocess.run(["node", "--check", str(v117_js)], check=True)
        upgraded_v117 = (v117_js.read_bytes(), v117_css.read_bytes())
        upgraded_v117_js = v117_js.read_text(encoding="utf-8")
        assert "rounded value badges v1.18" in upgraded_v117_js
        assert "TouchGUI matching callsign removal v1.18" in upgraded_v117_js
        subprocess.run(["python3", str(PATCHER), str(v117_js), str(v117_css)], check=True)
        assert upgraded_v117 == (v117_js.read_bytes(), v117_css.read_bytes()), "v1.17 upgrade was not idempotent"

    print("PASS: installers include the TouchGUI activity patch path.")
    print("PASS: ordered polling, Tx/Rx/LCnt colors, card layout, footer, compatibility upgrades, syntax, and repeat application.")


if __name__ == "__main__":
    main()
