#!/usr/bin/env python3
"""Apply the AllScan Mods TouchGUI activity-color enhancement."""

from pathlib import Path
import sys


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: touchgui-activity.py SIMPLE_JS SIMPLE_CSS")
    js_path, css_path = map(Path, sys.argv[1:])
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")

    marker = "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09."
    previous_markers = (
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and complete status footer v1.07.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.08.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and mobile footer v1.06.",
        "// AllScan Mods: TouchGUI activity colors and Rx%/LCnt v1.05.",
        "// AllScan Mods: TouchGUI remote-node activity colors.",
    )
    patch_marker = marker if marker in js else next(
        (item for item in previous_markers if item in js), previous_markers[0]
    )
    patch_present = patch_marker in js
    if (patch_present and marker in js
            and "compact status footer v1.09" in css
            and "function formatTouchguiStatusMessage(msg)" in js
            and "function convertActivityRange(value, min, max)" in js
            and "simple.txTim[node] = now" not in js
            and "channel-stats" in js and ".channel-stats" in css
            and "activity.rxPct" in js and "activity.linkCnt" in js
            and "Number(channel.node) < 3000000" in js
            and "height:100dvh" in css
            and ".simple-footer { display:grid; }" in css
            and ".simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }" in css
            and "white-space:normal; overflow:visible; overflow-wrap:anywhere; min-width:0;" in css):
        print("TouchGUI activity colors and compact status footer are already applied.")
        return

    state_marker = "\tretryTmr: null\n};"
    state_new = "\tstatsTmr: null,\n\tstatsReq: null,\n\tstatsIndex: 0,\n\ttxCnt: {},\n\ttxTim: {},\n\ttxTT: {},\n\ttxAvg: {},\n" + state_marker
    if patch_present:
        old_state = "\tstatsTmr: null,\n\tstatsReq: null,\n\tstatsIndex: 0,\n\ttxKeyups: {},\n\ttxTimes: {},\n\ttxUpdated: {},\n\ttxAverage: {},\n"
        new_state = state_new.removesuffix(state_marker)
        if js.count(old_state) == 1:
            js = js.replace(old_state, new_state, 1)
        elif all(field in js for field in ("\ttxCnt: {},", "\ttxTim: {},", "\ttxTT: {},", "\ttxAvg: {},")):
            pass
        else:
            raise SystemExit("ERROR: Existing TouchGUI activity patch has an unexpected state block; no files changed.")
    else:
        if js.count(state_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI state marker exactly once; no files changed.")
        js = js.replace(state_marker, state_new, 1)

    init_marker = "\tinitEventSource();\n}"
    init_new = "\tinitEventSource();\n\tgetChannelStats();\n}"
    if not patch_present:
        if js.count(init_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI initialization marker exactly once; no files changed.")
        js = js.replace(init_marker, init_new, 1)

    render_marker = "\t\tsimple.channelByNode[channel.node] = channel;"
    render_new = render_marker + "\n\t\tif(channel.activity)\n\t\t\tapplyChannelActivity(btn, channel.activity);"
    if not patch_present:
        if js.count(render_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI channel-render marker exactly once; no files changed.")
        js = js.replace(render_marker, render_new, 1)

    stats_markup = "\t\t\t+ '<span class=\"channel-meta\">' + escapeHtml(channelMeta(channel)) + '</span>';"
    stats_markup_new = stats_markup[:-1] + "\n\t\t\t+ '<span class=\"channel-stats\"><span class=\"channel-rx\">Rx% —</span><span class=\"channel-lcnt\">LCnt —</span></span>';"
    if "channel-stats" not in js:
        if js.count(stats_markup) != 1:
            raise SystemExit("ERROR: Expected TouchGUI channel metadata markup exactly once; no files changed.")
        js = js.replace(stats_markup, stats_markup_new, 1)

    unload_marker = "\twindow.addEventListener('beforeunload', closeEventSource);"
    if not patch_present:
        if js.count(unload_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI unload marker exactly once; no files changed.")
        js = js.replace(unload_marker, unload_marker + "\n\twindow.addEventListener('beforeunload', closeChannelStats);", 1)

    handler_marker = "function handleConnectionEvent(event) {"
    handler = r'''// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.
function getChannelStats() {
	var nodeList = {};
	simple.channels.forEach(function(channel) {
		if(Number(channel.node) >= 2000 && Number(channel.node) < 3000000)
			nodeList[String(channel.node)] = true;
	});
	var nodes = Object.keys(nodeList);
	if(!nodes.length)
		return;
	if(simple.statsIndex >= nodes.length)
		simple.statsIndex = 0;
	var node = nodes[simple.statsIndex++];
	simple.statsReq = new XMLHttpRequest();
	simple.statsReq.onreadystatechange = function() {
		if(simple.statsReq.readyState !== 4)
			return;
		var delay = Math.max(2000, Math.ceil(30000 / nodes.length));
		if(simple.statsReq.status === 200) {
			try {
				var response = JSON.parse(simple.statsReq.responseText);
				var stats = response.data && response.data.stats;
				if(stats && String(stats.node) === node)
					updateChannelActivity(stats);
			} catch(e) {}
		} else if(simple.statsReq.status === 429) {
			simple.statsIndex = Math.max(0, simple.statsIndex - 1);
			delay = 15000;
		} else if(simple.statsReq.status !== 0) {
			delay = 15000;
		}
		simple.statsTmr = setTimeout(getChannelStats, delay);
	};
	simple.statsReq.open('POST', simple.baseUrl + '/stats/stats.php', true);
	simple.statsReq.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	simple.statsReq.send('node=' + encodeURIComponent(node));
}

function closeChannelStats() {
	if(simple.statsTmr !== null)
		clearTimeout(simple.statsTmr);
	if(simple.statsReq)
		simple.statsReq.abort();
}

function updateChannelActivity(stats) {
	var node = String(stats.node);
	var now = Math.floor(Date.now() / 1000);
	if(!simple.txCnt[node] || stats.keyups < simple.txCnt[node] || stats.txtime < simple.txTT[node]) {
		simple.txCnt[node] = stats.keyups;
		simple.txTim[node] = 0;
		simple.txTT[node] = stats.txtime;
		simple.txAvg[node] = 0;
	}
	var keyupDelta = stats.keyups - simple.txCnt[node];
	var txDelta = stats.txtime - simple.txTT[node];
	var elapsed = now - simple.txTim[node];
	if(txDelta > 2 * elapsed || keyupDelta > elapsed / 3)
		keyupDelta = txDelta = 0;
	var txPercent = elapsed ? Math.min(100, Math.round(100 * txDelta / elapsed)) : 0;
	if(stats.keyed == 1)
		simple.txAvg[node] = 100;
	else if(simple.txAvg[node] + txPercent > 2)
		simple.txAvg[node] = Math.round(simple.txAvg[node] / 2 + txPercent / 2);
	else
		simple.txAvg[node] = 0;
	simple.txCnt[node] = stats.keyups;
	simple.txTT[node] = stats.txtime;
	var channel = simple.channelByNode[node];
	if(!channel)
		return;
	channel.activity = {active: stats.active == 1, wt: stats.wt == 1, txAverage: simple.txAvg[node], rxPct: stats.busyPct, linkCnt: stats.linkCnt};
	var button = simple.channelsGrid.querySelector('[data-node="' + node + '"]');
	if(button)
		applyChannelActivity(button, channel.activity);
}

function applyChannelActivity(button, activity) {
	var keyed = activity.txAverage > 5;
	var shade = convertActivityRange(activity.txAverage, 15, 29);
	var rx = button.querySelector('.channel-rx');
	var links = button.querySelector('.channel-lcnt');
	if(rx)
		rx.textContent = 'Rx% ' + (activity.rxPct === undefined ? '—' : activity.rxPct);
	if(links)
		links.textContent = 'LCnt ' + (activity.linkCnt === undefined ? '—' : activity.linkCnt);
	button.dataset.activity = keyed ? 'keyed' : (activity.active ? (activity.wt ? 'active-wt' : 'active') : 'idle');
	button.style.backgroundColor = keyed
		? 'hsl(0,100%,' + shade + '%)'
		: (activity.active ? (activity.wt ? 'hsl(150,50%,20%)' : 'hsl(150,50%,15%)') : '');
}

function convertActivityRange(value, min, max) {
	if(value > 100)
		value = 100;
	else if(value < 0)
		value = 0;
	return Math.round(value * (max - min) / 100 + min);
}

'''
    if patch_present:
        start = js.find(patch_marker)
        end = js.find(handler_marker, start)
        if start < 0 or end < 0 or js.find(patch_marker, start + len(patch_marker)) >= 0:
            raise SystemExit("ERROR: Existing TouchGUI activity handler is ambiguous; no files changed.")
        js = js[:start] + handler + js[end:]
    else:
        if js.count(handler_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI event-handler marker exactly once; no files changed.")
        js = js.replace(handler_marker, handler + handler_marker, 1)

    formatter = r'''function formatTouchguiStatusMessage(msg) {
	if(typeof msg !== 'string' || msg.indexOf('ASL Ver:') !== 0)
		return msg;
	var lines = msg.split(/<br\s*\/?\s*>/i);
	lines = lines.map(function(line) { return line.trim(); });
	if(lines.length < 3)
		return msg;
	var settingsIndex = lines.indexOf('Channel driver settings:');
	if(settingsIndex < 0 || settingsIndex === lines.length - 1)
		return msg;
	var settings = lines.slice(settingsIndex + 1).filter(function(line) { return line !== ''; }).map(function(line) {
		return line.replace(/ Level currently set to /, ' ');
	});
	if(!settings.length)
		return msg;
	return lines.slice(0, settingsIndex).join('<br>') + '<br>Channel settings: ' + settings.join(' | ');
}

'''
    format_func = "function formatTouchguiStatusMessage(msg) {"
    statmsg_func = "function statMsg(msg) {"
    statmsg_marker = "\tsimple.statmsg.innerHTML = msg;"
    formatted_marker = "\tsimple.statmsg.innerHTML = formatTouchguiStatusMessage(msg);"
    if js.count(format_func) == 1:
        start = js.index(format_func)
        end = js.find(statmsg_func, start)
        if end < 0:
            raise SystemExit("ERROR: Existing TouchGUI status formatter is incomplete; no files changed.")
        js = js[:start] + formatter + js[end:]
    elif format_func not in js:
        if statmsg_marker in js:
            if js.count(statmsg_marker) != 1 or js.count(statmsg_func) != 1:
                raise SystemExit("ERROR: Expected TouchGUI status-message markers exactly once; no files changed.")
            js = js.replace(statmsg_marker, formatted_marker, 1)
            js = js.replace(statmsg_func, formatter + statmsg_func, 1)
    else:
        raise SystemExit("ERROR: TouchGUI status formatter is ambiguous; no files changed.")
    if format_func in js and statmsg_marker in js:
        if js.count(statmsg_marker) != 1:
            raise SystemExit("ERROR: TouchGUI status-message marker is ambiguous; no files changed.")
        js = js.replace(statmsg_marker, formatted_marker, 1)

    css_marker = ".channel-btn.active {"
    css_rules = '''.channel-btn[data-activity="active"] {
background-color:hsl(150,50%,15%);
}
.channel-btn[data-activity="active-wt"] {
background-color:hsl(150,50%,20%);
}
.channel-btn[data-activity="keyed"] {
color:#fff;
}
'''
    stats_css = '''/* AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09. */
.channel-stats {
grid-column:2;
display:flex;
justify-content:space-between;
gap:4px;
min-width:0;
font-size:11px;
font-weight:normal;
line-height:1.15;
color:#c8d8e5;
white-space:nowrap;
}
.channel-btn {
grid-template-rows:auto auto auto;
min-height:120px;
}
.channel-index {
grid-row:1 / span 3;
}
@media (max-width:700px) {
.channel-btn { min-height:112px; }
.channel-stats { font-size:10px; gap:3px; }
}
@media (max-height:430px) {
.channel-btn { min-height:108px; }
.channel-label { font-size:15px; }
.channel-meta { font-size:12px; }
.channel-stats { font-size:10px; }
}
'''
    if not patch_present:
        if css.count(css_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI active-channel CSS marker exactly once; no files changed.")
        css = css.replace(css_marker, css_rules + css_marker, 1)
    elif '.channel-btn[data-activity="active"]' not in css:
        raise SystemExit("ERROR: Existing TouchGUI CSS patch is incomplete; no files changed.")
    if ".channel-stats" not in css:
        css = css.rstrip() + "\n" + stats_css
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors and Rx%/LCnt v1.05.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and mobile footer v1.06.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and complete status footer v1.07.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.08.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
    )
    if "compact status footer v1.09" not in css:
        css = css.rstrip() + "\n/* AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09. */\n"
    if ".simple-app {\nheight:100vh;\nheight:100dvh;\n}" not in css:
        css = css.rstrip() + "\n.simple-app {\nheight:100vh;\nheight:100dvh;\n}\n"
    if "@media (max-height:430px) {\n.simple-footer { display:grid; }\n}" not in css:
        css = css.rstrip() + "\n@media (max-height:430px) {\n.simple-footer { display:grid; }\n}\n"
    footer_css = '''.simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }
.simple-footer #scanmsg,
.simple-footer #statmsg { white-space:normal; overflow:visible; overflow-wrap:anywhere; min-width:0; }
@media (max-width:700px) {
.simple-footer { grid-template-columns:1fr; gap:0; }
.simple-footer #scanmsg,
.simple-footer #statmsg { font-size:11px; line-height:1.2; }
}
'''
    if ".simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }" not in css:
        css = css.rstrip() + "\n" + footer_css

    if "simple.statsTmr = setTimeout(getChannelStats" not in js or 'data-activity="active-wt"' not in css:
        raise SystemExit("ERROR: TouchGUI activity patch validation failed; no files changed.")
    js_path.write_text(js, encoding="utf-8")
    css_path.write_text(css, encoding="utf-8")
    print("TouchGUI activity colors are patch-ready.")


if __name__ == "__main__":
    main()
