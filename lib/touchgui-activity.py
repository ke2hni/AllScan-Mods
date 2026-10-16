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

    marker = "// AllScan Mods: TouchGUI remote-node activity colors."
    if marker in js:
        if "button.dataset.activity = keyed" in js and ".channel-btn[data-activity=\"active\"]" in css:
            print("TouchGUI activity colors are already applied.")
            return
        raise SystemExit("ERROR: Partial TouchGUI activity patch detected; no files changed.")

    state_marker = "\tretryTmr: null\n};"
    state_new = "\tstatsTmr: null,\n\tstatsReq: null,\n\tstatsIndex: 0,\n\ttxKeyups: {},\n\ttxTimes: {},\n\ttxUpdated: {},\n\ttxAverage: {},\n" + state_marker
    if js.count(state_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI state marker exactly once; no files changed.")
    js = js.replace(state_marker, state_new, 1)

    init_marker = "\tinitEventSource();\n}"
    init_new = "\tinitEventSource();\n\tgetChannelStats();\n}"
    if js.count(init_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI initialization marker exactly once; no files changed.")
    js = js.replace(init_marker, init_new, 1)

    render_marker = "\t\tsimple.channelByNode[channel.node] = channel;"
    render_new = render_marker + "\n\t\tif(channel.activity)\n\t\t\tapplyChannelActivity(btn, channel.activity);"
    if js.count(render_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI channel-render marker exactly once; no files changed.")
    js = js.replace(render_marker, render_new, 1)

    unload_marker = "\twindow.addEventListener('beforeunload', closeEventSource);"
    if js.count(unload_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI unload marker exactly once; no files changed.")
    js = js.replace(unload_marker, unload_marker + "\n\twindow.addEventListener('beforeunload', closeChannelStats);", 1)

    handler_marker = "function handleConnectionEvent(event) {"
    handler = r'''// AllScan Mods: TouchGUI remote-node activity colors.
function getChannelStats() {
	var nodeList = {};
	simple.channels.forEach(function(channel) {
		if(Number(channel.node) >= 2000 && Number(channel.node) < 2000000)
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
	if(simple.txKeyups[node] === undefined || stats.keyups < simple.txKeyups[node] || stats.txtime < simple.txTimes[node]) {
		simple.txKeyups[node] = stats.keyups;
		simple.txTimes[node] = stats.txtime;
		simple.txUpdated[node] = now;
		simple.txAverage[node] = 0;
	}
	var keyupDelta = stats.keyups - simple.txKeyups[node];
	var txDelta = stats.txtime - simple.txTimes[node];
	var elapsed = now - simple.txUpdated[node];
	if(txDelta > 2 * elapsed || keyupDelta > elapsed / 3)
		keyupDelta = txDelta = 0;
	var txPercent = elapsed ? Math.min(100, Math.round(100 * txDelta / elapsed)) : 0;
	if(stats.keyed == 1)
		simple.txAverage[node] = 100;
	else if(simple.txAverage[node] + txPercent > 2)
		simple.txAverage[node] = Math.round(simple.txAverage[node] / 2 + txPercent / 2);
	else
		simple.txAverage[node] = 0;
	simple.txKeyups[node] = stats.keyups;
	simple.txTimes[node] = stats.txtime;
	simple.txUpdated[node] = now;
	var channel = simple.channelByNode[node];
	if(!channel)
		return;
	channel.activity = {active: stats.active == 1, wt: stats.wt == 1, txAverage: simple.txAverage[node]};
	var button = simple.channelsGrid.querySelector('[data-node="' + node + '"]');
	if(button)
		applyChannelActivity(button, channel.activity);
}

function applyChannelActivity(button, activity) {
	var keyed = activity.txAverage > 5;
	var shade = Math.round(Math.max(0, Math.min(100, activity.txAverage)) * 14 / 100 + 15);
	button.dataset.activity = keyed ? 'keyed' : (activity.active ? (activity.wt ? 'active-wt' : 'active') : 'idle');
	button.style.backgroundColor = keyed
		? 'hsl(0,100%,' + shade + '%)'
		: (activity.active ? (activity.wt ? 'hsl(150,50%,20%)' : 'hsl(150,50%,15%)') : '');
}

'''
    if js.count(handler_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI event-handler marker exactly once; no files changed.")
    js = js.replace(handler_marker, handler + handler_marker, 1)

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
    if css.count(css_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI active-channel CSS marker exactly once; no files changed.")
    css = css.replace(css_marker, css_rules + css_marker, 1)

    if "simple.statsTmr = setTimeout(getChannelStats" not in js or 'data-activity="active-wt"' not in css:
        raise SystemExit("ERROR: TouchGUI activity patch validation failed; no files changed.")
    js_path.write_text(js, encoding="utf-8")
    css_path.write_text(css, encoding="utf-8")
    print("TouchGUI activity colors are patch-ready.")


if __name__ == "__main__":
    main()
