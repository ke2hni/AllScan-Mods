#!/usr/bin/env python3
"""Apply the AllScan Mods TouchGUI activity-color enhancement."""

from pathlib import Path
import re
import sys


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: touchgui-activity.py SIMPLE_JS SIMPLE_CSS")
    js_path, css_path = map(Path, sys.argv[1:])
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")

    marker = "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.18."
    previous_markers = (
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.16.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.15.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and value-only statistics v1.14.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping v1.13.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, row-matched colors and order v1.12.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.10.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
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
            and "main-table color mapping and rounded value badges v1.17" in css
            and ".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }" in css
            and "function convertActivityRange(value, min, max)" in js
            and "simple.txTim[node] = now" in js
            and "getChannelStatsNodes()" in js
            and "channel-side" in js and ".channel-side" in css
            and "activity.rxPct" in js and "activity.linkCnt" in js
            and "rx.textContent = hasRx ? String(activity.rxPct) + '%' : '—';" in js
            and "links.textContent = activity.linkCnt === undefined" in js
            and "border-radius:8px;" in css
            and "button.style.backgroundColor = '';" in js
            and '.channel-btn[data-activity="active"]' not in css
            and "number < 3000000" in js
            and "height:100dvh" in css
            and ".simple-footer { display:grid; }" in css
            and ".simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }" in css
            and "@media (max-width:430px)" in css
            and "@media (max-width:380px)" in css
            and "white-space:normal; overflow:visible; overflow-wrap:anywhere; min-width:0;" in css
            and "TouchGUI centered card text v1.17" in css
            and "Responsive TouchGUI label auto-fit v1.37" in css
            and "TouchGUI single-line label fit v1.37" in css
            and "TouchGUI adaptive title fit v1.45" in js
            and "TouchGUI callsign-first card content v1.46" in js
            and "TouchGUI top-aligned callsign with description gap v1.47" in css
            and "TouchGUI bold node/callsign line v1.48" in css
            and "TouchGUI landscape callsign fit v1.50" in css
            and "TouchGUI connected banner callsign v1.51" in js
            and "TouchGUI three-row card data v1.52" in js
            and "function channelNote(channel)" in js
            and "TouchGUI three-row card styling v1.52" in css
            and "TouchGUI row text width fit v1.53" in js
            and "TouchGUI aqua row spacing v1.53" in css
            and "TouchGUI aqua description font size v1.54" in css
            and "TouchGUI responsive description sizing v1.55" in js
            and "TouchGUI centered node line v1.55" in css
            and "TouchGUI aqua fit safety margin v1.56" in js
            and "TouchGUI note separation v1.56" in css
            and "function fitChannelLabel(button)" in js
            and "@media (orientation: portrait)" in css
            and "display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-1.5ch; overflow:visible;" in css
            and "left:-1.5ch;" in css
            and "function fitChannelMeta(button)" in js
            and "function fitChannelLabel(button)" in js
            and "function fitTouchguiCardText()" in js
            and "window.matchMedia('(orientation: portrait)')" in js
            and "var scaleFactor = isPortrait ? 0.90 : 0.96;" in js
            and "TouchGUI matching callsign removal v1.18" in js):
        print("TouchGUI activity, statistics, and card layout are already applied.")
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

    channel_markup = r'''(?m)^[ \t]*btn\.innerHTML = [\s\S]*?;'''
    channel_markup_new = '''\t\t// AllScan Mods: TouchGUI callsign-first card content v1.46.
\t\t// AllScan Mods: TouchGUI three-row card data v1.52.
\t\tbtn.innerHTML = '<span class="channel-side"><span class="channel-index">' + (i + 1) + '</span>'
\t\t\t+ '<span class="channel-stats"><span class="channel-rx">—</span><span class="channel-lcnt">—</span></span></span>'
\t\t\t+ '<span class="channel-content"><span class="channel-meta">' + escapeHtml(channelMeta(channel)) + '</span>'
\t\t\t+ '<span class="channel-description">' + escapeHtml(channelDescription(channel)) + '</span>'
\t\t\t+ '<span class="channel-note">' + escapeHtml(channelNote(channel)) + '</span></span>';
'''.replace("\\t", "\t")
    updated_js, markup_count = re.subn(channel_markup, lambda _: channel_markup_new, js, count=1)
    if markup_count != 1 or "channel-index" not in updated_js or "channel-description" not in updated_js or "channel-note" not in updated_js:
        raise SystemExit("ERROR: Expected one TouchGUI card markup block; no files changed.")
    js = updated_js
    render_fit_pattern = re.compile(
        r"(?ms)^[ \t]*requestAnimationFrame\(function\(\) \{[^{}]*fitChannelMeta\(btn\);[^{}]*\}\);"
    )
    js = render_fit_pattern.sub("", js)
    render_end = "\t\t\t+ '<span class=\"channel-note\">' + escapeHtml(channelNote(channel)) + '</span></span>';"
    if js.count(render_end) != 1:
        raise SystemExit("ERROR: Expected one TouchGUI card render insertion point; no files changed.")
    render_fit_call = "\t\trequestAnimationFrame(function() {\n\t\t\tfitChannelMeta(btn);\n\t\t\tfitChannelDescription(btn);\n\t\t\tfitChannelLabel(btn);\n\t\t});"
    js = js.replace(render_end, render_end + "\n" + render_fit_call, 1)

    unload_marker = "\twindow.addEventListener('beforeunload', closeEventSource);"
    if not patch_present:
        if js.count(unload_marker) != 1:
            raise SystemExit("ERROR: Expected TouchGUI unload marker exactly once; no files changed.")
        js = js.replace(unload_marker, unload_marker + "\n\twindow.addEventListener('beforeunload', closeChannelStats);", 1)

    handler_marker = "function handleConnectionEvent(event) {"
    handler = r'''// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.18.
function getChannelStatsNodes() {
	var nodes = [];
	simple.channels.forEach(function(channel) {
		var node = String(channel.node);
		var number = Number(node);
		if(number >= 2000 && number < 3000000 && nodes.indexOf(node) < 0)
			nodes.push(node);
	});
	return nodes;
}

function getChannelStats() {
	var nodes = getChannelStatsNodes();
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
		var responseData = null;
		if(simple.statsReq.status === 200) {
			try {
				var response = JSON.parse(simple.statsReq.responseText);
				responseData = response.data || null;
			} catch(e) {}
		}
		if(simple.statsReq.status === 429 || (responseData && responseData.retcode == 429)) {
			simple.statsIndex = Math.max(0, simple.statsIndex - 1);
			delay = 15000;
		} else if(responseData && responseData.stats && String(responseData.stats.node) === node) {
			updateChannelActivity(responseData.stats);
		} else if(simple.statsReq.status !== 200 && simple.statsReq.status !== 0) {
			delay = 15000;
		} else if(responseData && responseData.retcode != 404) {
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
	simple.txTim[node] = now;
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
	var txColor = 'hsl(0,100%,' + convertActivityRange(activity.txAverage, 15, 29) + '%)';
	var activeColor = activity.wt ? 'hsl(150,50%,20%)' : 'hsl(150,50%,15%)';
	var rxPct = Number(activity.rxPct);
	var linkCount = Number(activity.linkCnt);
	var hasRx = activity.rxPct !== undefined && activity.rxPct !== null && activity.rxPct !== '-' && isFinite(rxPct);
	var hasLinks = activity.linkCnt !== undefined && activity.linkCnt !== null && activity.linkCnt !== '-' && isFinite(linkCount);
	var rxColor = hasRx && rxPct > 2 ? 'hsl(125,40%,' + convertActivityRange(2 * rxPct, 10, 30) + '%)' : '';
	var linkColor = hasLinks && linkCount > 2 ? 'hsl(240,40%,' + convertActivityRange(3 * linkCount, 15, 30) + '%)' : '';
	var index = button.querySelector('.channel-index');
	var rx = button.querySelector('.channel-rx');
	var links = button.querySelector('.channel-lcnt');
	if(index)
		index.style.backgroundColor = keyed ? txColor : (activity.active ? activeColor : 'transparent');
	if(rx)
		rx.textContent = hasRx ? String(activity.rxPct) + '%' : '—';
	if(rx)
		rx.style.backgroundColor = rxColor;
	if(links)
		links.textContent = activity.linkCnt === undefined || activity.linkCnt === null ? '—' : String(activity.linkCnt);
	if(links)
		links.style.backgroundColor = linkColor;
	button.dataset.activity = keyed ? 'keyed' : (activity.active ? (activity.wt ? 'active-wt' : 'active') : 'idle');
	button.style.backgroundColor = '';
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

    channel_title = r'''// AllScan Mods: TouchGUI connected banner callsign v1.51.
function channelTitle(node) {
	var channel = simple.channelByNode[node];
	if(!channel)
		return 'Node ' + node;
	var nodeCall = String(node);
	if(channel.call)
		nodeCall += ' - ' + String(channel.call).trim();
	return channelLabel(channel) + ' (' + nodeCall + ')';
}'''
    channel_title_pattern = re.compile(r"(?m)^function channelTitle\(node\) \{.*?^\}", re.DOTALL)
    title_matches = list(channel_title_pattern.finditer(js))
    if len(title_matches) == 1:
        js = channel_title_pattern.sub(lambda _: channel_title, js, count=1)
    elif not title_matches:
        if js.count(handler_marker) != 1:
            raise SystemExit("ERROR: Expected one TouchGUI connected-title insertion point; no files changed.")
        js = js.replace(handler_marker, channel_title + "\n\n" + handler_marker, 1)
    else:
        raise SystemExit("ERROR: Expected the TouchGUI channel-title function exactly once; no files changed.")

    channel_label_pattern = re.compile(r"(?m)^function channelLabel\(channel\) \{.*?^\}", re.DOTALL)
    channel_label = r'''// AllScan Mods: TouchGUI matching callsign removal v1.18.
function channelLabel(channel) {
	var callsign = channel.call ? String(channel.call).trim() : '';
	function cleanLabel(text) {
		text = String(text || '');
		if(channel.node) {
			var nodePat = new RegExp('(^|[\\s,;:-]+)' + escapeRegExp(channel.node) + '([\\s,;:-]*$|(?=[\\s,;:-]+))', 'g');
			text = text.replace(nodePat, function(match, prefix) {
				return prefix && prefix.trim() ? prefix : '';
			});
		}
		if(callsign) {
			var callPat = new RegExp('(^|[\\s,;:.()]+)' + escapeRegExp(callsign) + '(?=$|[\\s,;:.()]+)', 'gi');
			text = text.replace(callPat, function(match, prefix) {
				return prefix && prefix.trim() ? prefix : '';
			});
		}
		return text.replace(/\s{2,}/g, ' ').replace(/^[\s,;:.()]+|[\s,;:.()]+$/g, '').trim();
	}
	var label = cleanLabel(channel.label || channel.name || '');
	if(!label)
		label = cleanLabel(channel.desc);
	if(!label)
		label = cleanLabel(channel.loc);
	return label || channel.node || '';
}'''
    matches = list(channel_label_pattern.finditer(js))
    if len(matches) == 1:
        js = channel_label_pattern.sub(lambda _: channel_label, js, count=1)
    elif not matches:
        if js.count(handler_marker) != 1:
            raise SystemExit("ERROR: Expected one TouchGUI channel-label insertion point; no files changed.")
        js = js.replace(handler_marker, channel_label + "\n\n" + handler_marker, 1)
    else:
        raise SystemExit("ERROR: Expected the TouchGUI channel-label function exactly once; no files changed.")

    card_field_funcs = r'''function channelDescription(channel) {
	return String(channel.desc || '').trim();
}
function channelNote(channel) {
	var text = String(channel.label || '');
	var fields = [channel.node, channel.call, channel.desc, channel.loc]
		.filter(function(value) { return value !== undefined && value !== null && String(value).trim() && String(value).trim() !== '-'; })
		.map(function(value) { return String(value).trim(); })
		.sort(function(a, b) { return b.length - a.length; });
	fields.forEach(function(value) {
		var fieldPat = new RegExp('(^|[\\s,;:-]+)' + escapeRegExp(value) + '(?=$|[\\s,;:-]+)', 'gi');
		text = text.replace(fieldPat, function(match, prefix) {
			return prefix && prefix.trim() ? prefix : '';
		});
	});
	text = text.replace(/\s{2,}/g, ' ').replace(/^[\s,;:.()]+|[\s,;:.()]+$/g, '').trim();
	return text || String(channel.loc || '').trim();
}'''
    if "function channelNote(channel)" not in js:
        label_functions = list(channel_label_pattern.finditer(js))
        if len(label_functions) != 1:
            raise SystemExit("ERROR: Existing TouchGUI label helper is incomplete; no files changed.")
        label_end = label_functions[0].end()
        js = js[:label_end] + "\n" + card_field_funcs + js[label_end:]

    card_text_fit_funcs = r'''function fitChannelMeta(button) {
	var meta = button.querySelector('.channel-meta');
	if(!meta || !meta.clientWidth)
		return;
	meta.style.fontSize = '';
	meta.style.transform = '';
	var textWidth = meta.scrollWidth;
	if(textWidth > meta.clientWidth) {
		var fontSize = parseFloat(window.getComputedStyle(meta).fontSize);
		var isPortrait = window.matchMedia && window.matchMedia('(orientation: portrait)').matches;
		var minFontSize = isPortrait ? 10 : Math.max(12, fontSize * 0.9);
		meta.style.fontSize = Math.max(minFontSize, fontSize * meta.clientWidth / textWidth) + 'px';
		textWidth = meta.scrollWidth;
		if(textWidth > meta.clientWidth) {
			var scaleFactor = isPortrait ? 0.90 : 0.96;
			meta.style.transform = 'scaleX(' + (meta.clientWidth / textWidth * scaleFactor) + ')';
		}
	}
}

// AllScan Mods: TouchGUI responsive description sizing v1.55.
function fitChannelText(element, maxFontSize, minFontSize) {
	var label = element;
	if(!label || !label.clientWidth)
		return;
	label.style.fontSize = '';
	label.style.transform = '';
	label.style.whiteSpace = '';
	label.style.overflowWrap = '';
	label.style.display = '';
	label.style.maxHeight = '';
	label.style.overflow = '';
	label.style.whiteSpace = 'nowrap';
	var fontSize = parseFloat(window.getComputedStyle(label).fontSize);
	var targetFontSize = maxFontSize ? Math.max(fontSize, maxFontSize) : fontSize;
	if(maxFontSize)
		label.style.fontSize = targetFontSize + 'px';
	var textWidth = label.scrollWidth;
	if(textWidth > label.clientWidth) {
		var isSmallScreen = window.matchMedia && window.matchMedia('(max-width:700px)').matches;
		// v1.54 kept the aqua row from growing past its base; v1.55 bounds its new auto-fit range.
		var minSize = minFontSize || Math.min(isSmallScreen ? 12 : 14, fontSize);
		// AllScan Mods: TouchGUI aqua fit safety margin v1.56.
		var fitMargin = maxFontSize ? 0.94 : 1;
		label.style.fontSize = Math.max(minSize, targetFontSize * label.clientWidth / textWidth * fitMargin) + 'px';
		if(label.scrollWidth > label.clientWidth) {
			if(maxFontSize && label.scrollWidth <= label.clientWidth * 1.04) {
				label.style.transform = 'scaleX(' + (label.clientWidth / label.scrollWidth * 0.98) + ')';
			} else {
				label.style.whiteSpace = 'normal';
				label.style.overflowWrap = 'anywhere';
				label.style.display = 'block';
			}
		}
	} else {
		label.style.whiteSpace = '';
	}
}
function fitChannelDescription(button) {
	fitChannelText(button.querySelector('.channel-description'), 18, 13);
}
// AllScan Mods: TouchGUI adaptive title fit v1.45.
function fitChannelLabel(button) {
	fitChannelText(button.querySelector('.channel-note'));
}
function fitTouchguiCardText() {
	document.querySelectorAll('.channel-btn').forEach(function(button) {
		fitChannelMeta(button);
		fitChannelDescription(button);
		fitChannelLabel(button);
	});
}
window.addEventListener('resize', fitTouchguiCardText);'''
    if "function fitChannelMeta(button)" not in js:
        js = channel_label_pattern.sub(lambda match: match.group(0) + "\n" + card_text_fit_funcs, js, count=1)
    elif "function fitChannelLabel(button)" not in js:
        old_text_fit_pattern = re.compile(
            r"(?s)function fitChannelMeta\(button\) \{.*?"
            r"window\.addEventListener\('resize', [A-Za-z0-9_]+\);"
        )
        old_text_fit_matches = list(old_text_fit_pattern.finditer(js))
        if (len(old_text_fit_matches) != 1
                or "meta.scrollWidth" not in old_text_fit_matches[0].group(0)
                or "meta.clientWidth" not in old_text_fit_matches[0].group(0)
                or "meta.style.fontSize" not in old_text_fit_matches[0].group(0)):
            raise SystemExit("ERROR: Existing TouchGUI card sizing helper is unexpected; no files changed.")
        js = old_text_fit_pattern.sub(lambda _: card_text_fit_funcs, js, count=1)
    elif js.count("function fitChannelLabel(button)") != 1 or "function fitTouchguiCardText()" not in js:
        raise SystemExit("ERROR: TouchGUI card title sizing helper is ambiguous; no files changed.")
    if "TouchGUI row text width fit v1.53" not in js:
        fit_block_pattern = re.compile(
            r"(?s)function fitChannelMeta\(button\) \{.*?window\.addEventListener\('resize', fitTouchguiCardText\);"
        )
        fit_blocks = list(fit_block_pattern.finditer(js))
        if len(fit_blocks) != 1:
            raise SystemExit("ERROR: Existing TouchGUI text fitting block is unexpected; no files changed.")
        js = fit_block_pattern.sub(lambda _: "// AllScan Mods: TouchGUI row text width fit v1.53.\n" + card_text_fit_funcs, js, count=1)
    if "TouchGUI adaptive title fit v1.45" not in js:
        title_fit_pattern = re.compile(
            r"(?ms)^(?:// AllScan Mods: TouchGUI (?:horizontal title fit v1\.37|readable long-title fit v1\.43|uniform-card title fit v1\.44)\.\n)?"
            r"function fitChannelLabel\(button(?:, expanded)?\) \{.*?^}"
        )
        title_fits = list(title_fit_pattern.finditer(js))
        if len(title_fits) != 1:
            raise SystemExit("ERROR: Existing TouchGUI title fitting function is ambiguous; no files changed.")
        title_function = "function fitChannelLabel(button)" + card_text_fit_funcs.split("function fitChannelLabel(button)", 1)[1].split("function fitTouchguiCardText()", 1)[0]
        js = title_fit_pattern.sub(
            lambda _: "// AllScan Mods: TouchGUI adaptive title fit v1.45.\n" + title_function,
            js,
            count=1,
        )

    if "var scaleFactor = isPortrait ? 0.90 : 0.96;" not in js:
        fit_pattern = re.compile(r"(?ms)^function fitChannelMeta\(button\) \{.*?^}")
        fits = list(fit_pattern.finditer(js))
        if (len(fits) != 1 or "meta.scrollWidth" not in fits[0].group(0)
                or "meta.clientWidth" not in fits[0].group(0)
                or not any(item in fits[0].group(0) for item in (
                    "var minFontSize = isPortrait ? 10 : Math.max(12, fontSize * 0.9);",
                    "var minFontSize = Math.max(12, fontSize * 0.9);",
                    "var minFontSize = Math.max(10, fontSize * 0.9);",
                ))):
            raise SystemExit("ERROR: Existing TouchGUI metadata sizing helper is unexpected; no files changed.")
        new_meta = card_text_fit_funcs.split("function fitChannelLabel(button)", 1)[0].rstrip()
        js = js[:fits[0].start()] + new_meta + js[fits[0].end():]

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
	return lines.slice(0, settingsIndex).join(' - ') + '<br>Channel settings: ' + settings.join(' | ');
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
    old_activity_css = '''.channel-btn[data-activity="active"] {
background-color:hsl(150,50%,15%);
}
.channel-btn[data-activity="active-wt"] {
background-color:hsl(150,50%,20%);
}
.channel-btn[data-activity="keyed"] {
color:#fff;
}
'''
    if css.count(old_activity_css) > 1:
        raise SystemExit("ERROR: TouchGUI activity color CSS is duplicated; no files changed.")
    css = css.replace(old_activity_css, "", 1)
    stats_css = '''/* AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17. */
.channel-btn {
grid-template-rows:auto;
min-height:86px;
padding:8px;
align-items:stretch;
}
.channel-side {
grid-column:1;
grid-row:1;
display:flex;
flex-direction:column;
align-items:flex-start;
justify-content:flex-start;
gap:4px;
min-width:52px;
}
.channel-index {
grid-row:auto;
flex:0 0 34px;
border-radius:8px;
}
.channel-stats {
display:flex;
flex-direction:column;
align-items:flex-start;
gap:2px;
min-width:0;
font-size:12px;
font-weight:normal;
line-height:1;
color:#c8d8e5;
white-space:nowrap;
}
.channel-stats span {
padding:1px 4px;
border-radius:8px;
}
.channel-content {
grid-column:2;
grid-row:1;
display:flex;
flex-direction:column;
justify-content:center;
align-items:center;
min-width:0;
}
.channel-meta {
grid-column:auto;
max-width:100%;
}
@media (max-width:700px) {
.channel-btn { min-height:82px; padding:7px; }
.channel-side { min-width:48px; }
.channel-index { flex-basis:30px; width:30px; height:30px; }
.channel-stats { font-size:11px; }
}
@media (max-height:430px) {
.channel-btn { min-height:78px; }
}
'''
    if not patch_present and css.count(css_marker) != 1:
        raise SystemExit("ERROR: Expected TouchGUI active-channel CSS marker exactly once; no files changed.")
    previous_stats_css_body = '''.channel-stats {
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
    previous_stats_css_markers = (
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and value-only statistics v1.14.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping v1.13.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, row-matched colors and order v1.12.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.10.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and complete status footer v1.07.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.08.",
        "// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and mobile footer v1.06.",
        "// AllScan Mods: TouchGUI activity colors and Rx%/LCnt v1.05.",
    )
    previous_block = next((
        "/* " + item[3:] + " */\n" + previous_stats_css_body
        for item in previous_stats_css_markers
        if "/* " + item[3:] + " */\n" + previous_stats_css_body in css
    ), None)
    previous_mapping_css = stats_css.replace(
        "font-size:12px;\nfont-weight:normal;\nline-height:1;",
        "font-size:11px;\nfont-weight:normal;\nline-height:1.1;",
    ).replace(
        "padding:1px 4px;\nborder-radius:8px;",
        "padding:1px 3px;\nborder-radius:8px;",
    ).replace(
        ".channel-stats { font-size:11px; }",
        ".channel-stats { font-size:10px; }",
    ).replace(
        "flex:0 0 34px;\nborder-radius:8px;", "flex:0 0 34px;"
    ).replace(
        "padding:1px 3px;\nborder-radius:8px;", "padding:1px 3px;\nborder-radius:3px;"
    )
    v116_stats_css = stats_css.replace(
        "main-table color mapping and rounded value badges v1.17",
        "main-table color mapping and rounded value badges v1.16",
    )
    v115_stats_css = stats_css.replace(
        "font-size:12px;\nfont-weight:normal;\nline-height:1;",
        "font-size:11px;\nfont-weight:normal;\nline-height:1.1;",
    ).replace(
        "padding:1px 4px;\nborder-radius:8px;",
        "padding:1px 3px;\nborder-radius:8px;",
    ).replace(
        ".channel-stats { font-size:11px; }",
        ".channel-stats { font-size:10px; }",
    ).replace(
        "main-table color mapping and rounded value badges v1.17",
        "main-table color mapping and rounded value badges v1.15",
    )
    v114_stats_css = previous_mapping_css.replace(
        "main-table color mapping and rounded value badges v1.17",
        "main-table color mapping and value-only statistics v1.14",
    )
    v113_stats_css = previous_mapping_css.replace(
        "main-table color mapping and rounded value badges v1.17",
        "main-table color mapping v1.13",
    )
    v112_stats_css = previous_mapping_css.replace(
        "main-table color mapping and rounded value badges v1.17",
        "row-matched colors and order v1.12",
    )
    if previous_block:
        css = css.replace(previous_block, stats_css, 1)
    elif stats_css in css:
        pass
    elif v116_stats_css in css:
        css = css.replace(v116_stats_css, stats_css, 1)
    elif v115_stats_css in css:
        css = css.replace(v115_stats_css, stats_css, 1)
    elif v114_stats_css in css:
        css = css.replace(v114_stats_css, stats_css, 1)
    elif v113_stats_css in css:
        css = css.replace(v113_stats_css, stats_css, 1)
    elif v112_stats_css in css:
        css = css.replace(v112_stats_css, stats_css, 1)
    elif "main-table color mapping v1.13" in css:
        css = css.replace(
            "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping v1.13.",
            "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
        )
    elif ".channel-stats {" in css:
        raise SystemExit("ERROR: Existing TouchGUI card CSS is not a recognized Mods version; no files changed.")
    else:
        css = css.rstrip() + "\n" + stats_css
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, row-matched colors and order v1.12.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and centered status footer v1.11.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors and Rx%/LCnt v1.05.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and mobile footer v1.06.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and complete status footer v1.07.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.08.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.09.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    css = css.replace(
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, and compact status footer v1.10.",
        "AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17.",
    )
    if "main-table color mapping and rounded value badges v1.17" not in css:
        css = css.rstrip() + "\n/* AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.17. */\n"
    if ".simple-app {\nheight:100vh;\nheight:100dvh;\n}" not in css:
        css = css.rstrip() + "\n.simple-app {\nheight:100vh;\nheight:100dvh;\n}\n"
    if "@media (max-height:430px) {\n.simple-footer { display:grid; }\n}" not in css:
        css = css.rstrip() + "\n@media (max-height:430px) {\n.simple-footer { display:grid; }\n}\n"
    card_text_css = '''/* AllScan Mods: TouchGUI centered card text v1.17. */
.channel-content {
width:100%;
box-sizing:border-box;
}
.channel-label, .channel-meta {
width:100%;
min-width:0;
box-sizing:border-box;
text-align:center;
}
.channel-label {
font-size:16px;
overflow-wrap:anywhere;
}
'''
    if "TouchGUI centered card text v1.17" not in css:
        css = css.rstrip() + "\n" + card_text_css

    single_line_css = '''/* AllScan Mods: TouchGUI single-line label fit v1.37. */
.channel-content { overflow:visible; }
.channel-label {
 display:block;
 white-space:nowrap;
 overflow:visible;
 overflow-wrap:normal;
 text-overflow:clip;
 transform-origin:center;
}
'''
    if "TouchGUI single-line label fit v1.37" not in css:
        css = css.rstrip() + "\n" + single_line_css

    callsign_first_spacing_css = '''/* AllScan Mods: TouchGUI top-aligned callsign with description gap v1.47. */
.channel-content {
justify-content:flex-start;
}
.channel-meta {
margin-bottom:6px;
}
'''
    if "TouchGUI top-aligned callsign with description gap v1.47" not in css:
        css = css.rstrip() + "\n" + callsign_first_spacing_css

    bold_callsign_css = '''/* AllScan Mods: TouchGUI bold node/callsign line v1.48. */
.channel-meta {
font-weight:bold;
}
'''
    if "TouchGUI bold node/callsign line v1.48" not in css:
        css = css.rstrip() + "\n" + bold_callsign_css

    landscape_callsign_css = '''/* AllScan Mods: TouchGUI landscape callsign fit v1.50. */
@media (orientation: landscape) {
.channel-meta { display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-0.75ch; overflow:visible; }
}
'''
    previous_landscape_callsign_css = '''/* AllScan Mods: TouchGUI landscape callsign fit v1.49. */
@media (orientation: landscape) {
.channel-meta { display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-1.5ch; overflow:visible; }
}
'''
    if previous_landscape_callsign_css in css:
        css = css.replace(previous_landscape_callsign_css, landscape_callsign_css, 1)
    elif "TouchGUI landscape callsign fit v1.50" not in css:
        css = css.rstrip() + "\n" + landscape_callsign_css

    footer_css = '''.simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }
.simple-footer #scanmsg,
.simple-footer #statmsg { white-space:normal; overflow:visible; overflow-wrap:anywhere; min-width:0; }
@media (max-width:700px) {
.simple-footer { grid-template-columns:1fr; gap:0; }
.simple-footer #scanmsg,
.simple-footer #statmsg { font-size:11px; line-height:1.2; }
}
@media (max-width:430px) {
.simple-footer #statmsg { font-size:9px; line-height:1.15; }
}
@media (max-width:380px) {
.simple-footer #statmsg { font-size:8px; }
}
'''
    if ".simple-footer { height:auto; min-height:30px; flex:0 0 auto; overflow:visible; }" not in css:
        css = css.rstrip() + "\n" + footer_css
    footer_scale_css = '''@media (max-width:430px) {
.simple-footer #statmsg { font-size:9px; line-height:1.15; }
}
'''
    if "@media (max-width:430px)" not in css:
        css = css.rstrip() + "\n" + footer_scale_css
    narrow_footer_css = '''@media (max-width:380px) {
.simple-footer #statmsg { font-size:8px; }
}
'''
    if "@media (max-width:380px)" not in css:
        css = css.rstrip() + "\n" + narrow_footer_css
    center_footer_css = ".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }\n"
    if ".simple-footer #statmsg { grid-column:1 / -1; text-align:center; }" not in css:
        css = css.rstrip() + "\n" + center_footer_css

    responsive_card_css = '''/* AllScan Mods: Responsive TouchGUI label auto-fit v1.37. */
.channel-btn {
column-gap:4px;
}
.channel-content {
container-type:inline-size;
}
.channel-label {
font-size:18px;
line-height:1.12;
}
.channel-meta {
font-size:14px;
line-height:1.1;
white-space:nowrap;
overflow:hidden;
text-overflow:clip;
transform-origin:center;
}
@media (max-width:700px) {
.channel-label { font-size:16px; }
}
@media (max-height:430px) {
.channel-label { font-size:15px; }
.channel-meta { font-size:12px; }
}
@media (orientation: portrait) {
.channel-meta { display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-1.5ch; overflow:visible; }
}
'''
    old_responsive_card_css_v134 = responsive_card_css.replace('v1.35', 'v1.34', 1).replace(' overflow:visible;', '')
    old_responsive_card_css_v133 = responsive_card_css.replace('v1.35', 'v1.33', 1).replace(' overflow:visible;', '').replace('max-width:none; ', '')
    old_responsive_card_css_v132 = responsive_card_css.replace('v1.35', 'v1.32', 1).replace(' overflow:visible;', '').replace('max-width:none; ', '').replace('width:calc(100% + 1.5ch); ', 'width:100%; ')
    old_responsive_card_css_v131 = responsive_card_css.replace('v1.35', 'v1.31', 1).replace('display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; ', '').replace(' overflow:visible;', '')
    old_responsive_card_css_v130 = responsive_card_css.replace('v1.35', 'v1.30', 1).replace('''@media (orientation: portrait) {\n.channel-meta { display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-1.5ch; overflow:visible; }\n}\n''', '')
    old_responsive_card_css_v129 = responsive_card_css.replace('v1.35', 'v1.29', 1).replace('''@media (orientation: portrait) {\n.channel-meta { display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-1.5ch; overflow:visible; }\n}\n''', '')
    old_responsive_card_css_v128 = '''/* AllScan Mods: Responsive TouchGUI label auto-fit v1.28. */
.channel-btn {
column-gap:4px;
}
.channel-content {
container-type:inline-size;
}
.channel-label {
font-size:18px;
line-height:1.12;
}
.channel-meta {
font-size:14px;
line-height:1.1;
white-space:nowrap;
overflow:hidden;
text-overflow:clip;
transform-origin:center;
}
@media (max-width:700px) {
.channel-label { font-size:16px; }
}
@media (max-height:430px) {
.channel-label { font-size:15px; }
.channel-meta { font-size:12px; }
}
'''
    old_responsive_card_css_v127 = '''/* AllScan Mods: Responsive TouchGUI metadata readability v1.27. */
.channel-btn {
column-gap:4px;
}
.channel-content {
container-type:inline-size;
}
.channel-label {
font-size:clamp(12px, 12cqi, 16px);
}
.channel-meta {
font-size:clamp(10px, 10cqi, 12px);
line-height:1.1;
white-space:nowrap;
overflow:hidden;
text-overflow:clip;
transform-origin:center;
}
'''
    old_responsive_card_css_v125 = '''/* AllScan Mods: Responsive TouchGUI card spacing v1.25. */
.channel-btn {
column-gap:4px;
}
.channel-side {
min-width:48px;
}
.channel-content {
container-type:inline-size;
}
.channel-label {
font-size:clamp(12px, 12cqi, 16px);
}
.channel-meta {
font-size:clamp(8px, 8cqi, 12px);
line-height:1.1;
white-space:nowrap;
overflow:hidden;
text-overflow:clip;
}
'''
    old_responsive_card_css = '''/* AllScan Mods: Responsive TouchGUI card labels and metadata v1.23. */
.channel-content {
container-type:inline-size;
}
.channel-label {
font-size:clamp(12px, 12cqi, 16px);
}
.channel-meta {
font-size:clamp(10px, 10cqi, 12px);
line-height:1.1;
white-space:normal;
overflow:visible;
text-overflow:clip;
}
'''
    old_responsive_card_css_v124 = '''/* AllScan Mods: Responsive TouchGUI card labels and fitted one-line metadata v1.24. */
.channel-content {
container-type:inline-size;
}
.channel-label {
font-size:clamp(12px, 12cqi, 16px);
}
.channel-meta {
font-size:clamp(8px, 8cqi, 12px);
line-height:1.1;
white-space:nowrap;
overflow:hidden;
text-overflow:clip;
}
'''
    if "Responsive TouchGUI label auto-fit v1.35" in css:
        css = css.replace("Responsive TouchGUI label auto-fit v1.35", "Responsive TouchGUI label auto-fit v1.37", 1)
    if "Responsive TouchGUI label auto-fit v1.37" not in css:
        if css.count(old_responsive_card_css_v134) == 1:
            css = css.replace(old_responsive_card_css_v134, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v133) == 1:
            css = css.replace(old_responsive_card_css_v133, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v132) == 1:
            css = css.replace(old_responsive_card_css_v132, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v131) == 1:
            css = css.replace(old_responsive_card_css_v131, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v130) == 1:
            css = css.replace(old_responsive_card_css_v130, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v129) == 1:
            css = css.replace(old_responsive_card_css_v129, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v128) == 1:
            css = css.replace(old_responsive_card_css_v128, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v127) == 1:
            css = css.replace(old_responsive_card_css_v127, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v125) == 1:
            css = css.replace(old_responsive_card_css_v125, responsive_card_css, 1)
        elif css.count(old_responsive_card_css_v124) == 1:
            css = css.replace(old_responsive_card_css_v124, responsive_card_css, 1)
        elif css.count(old_responsive_card_css) == 1:
            css = css.replace(old_responsive_card_css, responsive_card_css, 1)
        elif "Responsive TouchGUI card labels and metadata v1.23" not in css and "Responsive TouchGUI card labels and fitted one-line metadata v1.24" not in css:
            css = css.rstrip() + "\n" + responsive_card_css
        else:
            raise SystemExit("ERROR: Existing responsive TouchGUI CSS is unexpected; no files changed.")

    three_row_css = '''/* AllScan Mods: TouchGUI three-row card styling v1.52. */
.channels-grid {
grid-template-columns:repeat(auto-fit, minmax(calc(180px + 5ch), 1fr));
}
.channel-description,
.channel-note {
display:block;
width:100%;
min-width:0;
box-sizing:border-box;
text-align:center;
font-size:14px;
font-weight:bold;
line-height:1.05;
overflow:hidden;
overflow-wrap:anywhere;
}
.channel-description { color:#00f5f5; }
.channel-note { color:#f8fbff; }
.channel-description:empty,
.channel-note:empty { display:none; }
@media (max-width:700px) {
.channels-grid { grid-template-columns:repeat(auto-fit, minmax(calc(145px + 5ch), 1fr)); }
}
'''
    if "TouchGUI three-row card styling v1.52" not in css:
        css = css.rstrip() + "\n" + three_row_css

    row_spacing_css = '''/* AllScan Mods: TouchGUI aqua row spacing v1.53. */
.channel-description {
position:relative;
top:-2px;
}
'''
    if "TouchGUI aqua row spacing v1.53" not in css:
        css = css.rstrip() + "\n" + row_spacing_css

    aqua_font_css = '''/* AllScan Mods: TouchGUI aqua description font size v1.54. */
.channel-description { font-size:13px; }
'''
    if "TouchGUI aqua description font size v1.54" not in css:
        css = css.rstrip() + "\n" + aqua_font_css

    centered_node_css = '''/* AllScan Mods: TouchGUI centered node line v1.55. */
@media (orientation: portrait) {
.channel-meta { left:-0.75ch; }
}
'''
    if "TouchGUI centered node line v1.55" not in css:
        css = css.rstrip() + "\n" + centered_node_css

    aqua_fit_margin_js = "// AllScan Mods: TouchGUI aqua fit safety margin v1.56."
    if aqua_fit_margin_js not in js:
        fit_line = "\t\tlabel.style.fontSize = Math.max(minSize, targetFontSize * label.clientWidth / textWidth) + 'px';"
        if js.count(fit_line) != 1:
            raise SystemExit("ERROR: Existing TouchGUI responsive fitting line is unexpected; no files changed.")
        js = js.replace(
            fit_line,
            "\t\t// AllScan Mods: TouchGUI aqua fit safety margin v1.56.\n"
            "\t\tvar fitMargin = maxFontSize ? 0.94 : 1;\n"
            "\t\tlabel.style.fontSize = Math.max(minSize, targetFontSize * label.clientWidth / textWidth * fitMargin) + 'px';",
            1,
        )

    if "label.scrollWidth <= label.clientWidth * 1.04" not in js:
        old_wrap = "\t\tif(label.scrollWidth > label.clientWidth) {\n\t\t\tlabel.style.whiteSpace = 'normal';\n\t\t\tlabel.style.overflowWrap = 'anywhere';\n\t\t\tlabel.style.display = 'block';\n\t\t}"
        new_wrap = "\t\tif(label.scrollWidth > label.clientWidth) {\n\t\t\tif(maxFontSize && label.scrollWidth <= label.clientWidth * 1.04) {\n\t\t\t\tlabel.style.transform = 'scaleX(' + (label.clientWidth / label.scrollWidth * 0.98) + ')';\n\t\t\t} else {\n\t\t\t\tlabel.style.whiteSpace = 'normal';\n\t\t\t\tlabel.style.overflowWrap = 'anywhere';\n\t\t\t\tlabel.style.display = 'block';\n\t\t\t}\n\t\t}"
        if js.count(old_wrap) != 1:
            raise SystemExit("ERROR: Existing TouchGUI text wrapping block is unexpected; no files changed.")
        js = js.replace(old_wrap, new_wrap, 1)

    note_spacing_css = '''/* AllScan Mods: TouchGUI note separation v1.56. */
.channel-note { margin-top:3px; }
'''
    if "TouchGUI note separation v1.56" not in css:
        css = css.rstrip() + "\n" + note_spacing_css

    if "TouchGUI responsive description sizing v1.55" not in js:
        fit_function = re.compile(r"(?ms)^function fitChannelText\(element\) \{.*?^}")
        fit_matches = list(fit_function.finditer(js))
        helper_definition = re.search(
            r"(?ms)^// AllScan Mods: TouchGUI responsive description sizing v1\.55\.\nfunction fitChannelText\(element, maxFontSize, minFontSize\) \{.*?^}",
            card_text_fit_funcs,
        )
        if len(fit_matches) != 1 or helper_definition is None:
            raise SystemExit("ERROR: Existing TouchGUI row text sizing floor is unexpected; no files changed.")
        updated_fit = helper_definition.group(0)
        js = js[:fit_matches[0].start()] + updated_fit + js[fit_matches[0].end():]
        description_function = re.compile(r"(?ms)^function fitChannelDescription\(button\) \{.*?^}")
        description_matches = list(description_function.finditer(js))
        if len(description_matches) != 1:
            raise SystemExit("ERROR: Existing TouchGUI description sizing function is unexpected; no files changed.")
        updated_description = "function fitChannelDescription(button) {\n\tfitChannelText(button.querySelector('.channel-description'), 18, 13);\n}"
        js = js[:description_matches[0].start()] + updated_description + js[description_matches[0].end():]

    if ("simple.statsTmr = setTimeout(getChannelStats" not in js
            or "active-wt" not in js
            or "simple.txTim[node] = now" not in js
            or "getChannelStatsNodes()" not in js
            or "button.style.backgroundColor = '';" not in js
            or "main-table color mapping and rounded value badges v1.17" not in css
            or "TouchGUI matching callsign removal v1.18" not in js
            or '.channel-btn[data-activity="active"]' in css
            or "channel-side" not in js
            or ".channel-side" not in css
            or "TouchGUI centered card text v1.17" not in css
            or "Responsive TouchGUI label auto-fit v1.37" not in css
            or "TouchGUI single-line label fit v1.37" not in css
            or "TouchGUI adaptive title fit v1.45" not in js
            or "TouchGUI three-row card data v1.52" not in js
            or "function channelDescription(channel)" not in js
            or "function channelNote(channel)" not in js
            or "TouchGUI three-row card styling v1.52" not in css
            or "TouchGUI row text width fit v1.53" not in js
            or "TouchGUI aqua row spacing v1.53" not in css
            or "TouchGUI aqua description font size v1.54" not in css
            or ".channel-description { font-size:13px; }" not in css
            or "TouchGUI responsive description sizing v1.55" not in js
            or "TouchGUI centered node line v1.55" not in css
            or "TouchGUI aqua fit safety margin v1.56" not in js
            or "var fitMargin = maxFontSize ? 0.94 : 1;" not in js
            or "label.scrollWidth <= label.clientWidth * 1.04" not in js
            or "TouchGUI note separation v1.56" not in css
            or ".channel-note { margin-top:3px; }" not in css
            or "calc(180px + 5ch)" not in css
            or "color:#00f5f5;" not in css
            or "@media (orientation: portrait)" not in css
            or "display:block; width:calc(100% + 1.5ch); max-width:none; min-width:0; position:relative; left:-1.5ch; overflow:visible;" not in css
            or ".channel-meta { left:-0.75ch; }" not in css
            or "left:-1.5ch;" not in css):
        raise SystemExit("ERROR: TouchGUI activity patch validation failed; no files changed.")
    js_path.write_text(js, encoding="utf-8")
    css_path.write_text(css, encoding="utf-8")
    print("TouchGUI activity, statistics, and card layout are patch-ready.")


if __name__ == "__main__":
    main()
