var simple = {
	channels: [],
	channelByNode: {},
	baseUrl: '',
	channelsGrid: {querySelector: function() { return null; }},
	statsTmr: null,
	statsReq: null,
	statsIndex: 0,
	txCnt: {},
	txTim: {},
	txTT: {},
	txAvg: {},
	retryTmr: null
};
function simpleInit() {
	initEventSource();
	getChannelStats();
}
function initEventSource() {}
function bindControls() {
	window.addEventListener('beforeunload', closeEventSource);
	window.addEventListener('beforeunload', closeChannelStats);
}
function closeEventSource() {}
function formatTouchguiStatusMessage(msg) {
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

function statMsg(msg) {
	if(!simple.statmsg || !msg)
		return;
	simple.statmsg.innerHTML = formatTouchguiStatusMessage(msg);
}
function renderChannels() {
		btn.innerHTML = '<span class="channel-side"><span class="channel-index">' + (i + 1) + '</span>'
			+ '<span class="channel-stats"><span class="channel-rx">—</span><span class="channel-lcnt">—</span></span></span>'
			+ '<span class="channel-content"><span class="channel-label">' + escapeHtml(channelLabel(channel)) + '</span>'
			+ '<span class="channel-meta">' + escapeHtml(channelMeta(channel)) + '</span></span>';
		simple.channelByNode[channel.node] = channel;
		if(channel.activity)
			applyChannelActivity(btn, channel.activity);
}
// AllScan Mods: TouchGUI activity colors, Rx%/LCnt, main-table color mapping and rounded value badges v1.15.
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

function handleConnectionEvent(event) {}
