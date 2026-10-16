var simple = {
	channels: [],
	channelByNode: {},
	baseUrl: '',
	channelsGrid: {querySelector: function() { return null; }},
	statsTmr: null,
	statsReq: null,
	statsIndex: 0,
	txKeyups: {},
	txTimes: {},
	txUpdated: {},
	txAverage: {},
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
function renderChannels() {
		btn.innerHTML = '<span class="channel-index">1</span>'
			+ '<span class="channel-label">Channel</span>'
			+ '<span class="channel-meta">' + escapeHtml(channelMeta(channel)) + '</span>';
		simple.channelByNode[channel.node] = channel;
		if(channel.activity)
			applyChannelActivity(btn, channel.activity);
}
// AllScan Mods: TouchGUI remote-node activity colors.
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

function handleConnectionEvent(event) {}
