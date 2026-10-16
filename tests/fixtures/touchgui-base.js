var simple = {
	channels: [],
	channelByNode: {},
	baseUrl: '',
	channelsGrid: {querySelector: function() { return null; }},
	retryTmr: null
};
function simpleInit() {
	initEventSource();
}
function initEventSource() {}
function bindControls() {
	window.addEventListener('beforeunload', closeEventSource);
}
function closeEventSource() {}
function renderChannels() {
		btn.innerHTML = '<span class="channel-index">1</span>'
			+ '<span class="channel-label">Channel</span>'
			+ '<span class="channel-meta">' + escapeHtml(channelMeta(channel)) + '</span>';
		simple.channelByNode[channel.node] = channel;
}
function handleConnectionEvent(event) {}
