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
		simple.channelByNode[channel.node] = channel;
}
function handleConnectionEvent(event) {}
