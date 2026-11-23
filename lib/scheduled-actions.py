#!/usr/bin/env python3
"""Patch staged AllScan v1.06 files for grouped and editable schedules.

AllScan Mods v1.97; created by KE2HNI; 2026-11-22T18:42:43-05:00.
Schedule layout update v1.98; updated by KE2HNI; 2026-11-22T20:35:36-05:00.
Both repository installers call this shared patch helper.
"""
from pathlib import Path
import sys

api_path, view_path, js_path, css_path = map(Path, sys.argv[1:5])
api, view, js, css = [p.read_text(encoding="utf-8") for p in (api_path, view_path, js_path, css_path)]

def replace_once(source, old, new, description):
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"ERROR: Expected one {description} section; found {count}.")
    return source.replace(old, new, 1)

api_marker = "// AllScan Mods: Editable grouped schedule actions v1.97."
api_edit = '''\tcase 'edit':
\t\t$id = isset($_POST['id']) ? trim($_POST['id']) : '';
\t\t$foundIndex = null;
\t\tforeach($entries as $i => $e) {
\t\t\tif(($e['id'] ?? '') === $id) { $foundIndex = $i; break; }
\t\t}
\t\tif($foundIndex === null)
\t\t\treply(false, 'Schedule entry not found');
\t\t$in = [];
\t\tforeach(['action2', 'node', 'time', 'days', 'perm', 'autodisc'] as $f)
\t\t\t$in[$f] = isset($_POST[$f]) ? trim(strip_tags($_POST[$f])) : '';
\t\t$in['action'] = $in['action2'];
\t\tif(($updated = schedValidate($in, $err)) === false)
\t\t\treply(false, $err);
\t\t$updated['id'] = $entries[$foundIndex]['id'];
\t\t$updated['enabled'] = !empty($entries[$foundIndex]['enabled']);
\t\t$entries[$foundIndex] = $updated;
\t\tif(!schedSave($entries, $err))
\t\t\treply(false, $err);
\t\tbreak;
'''
if api_marker not in api:
    api = replace_once(api, "<?php\n// Scheduled connect/disconnect management API. Returns JSON.\n", "<?php\n// Scheduled connect/disconnect management API. Returns JSON.\n" + api_marker + "\n", "schedule API header")
    api = replace_once(api, "\tcase 'delete':\n\tcase 'toggle':", api_edit + "\tcase 'delete':\n\tcase 'toggle':", "schedule edit API insertion point")

view_marker = "<!-- AllScan Mods: Group schedule actions by node v1.98. -->"
view_marker_old = "<!-- AllScan Mods: Group schedule actions by node v1.97. -->"
modal_anchor = '<div id="scheduleModal" class="favEditModal" hidden onClick="scheduleBackdrop(event);">'
if view_marker_old in view:
    view = replace_once(view, view_marker_old, view_marker, "previous schedule layout marker")
elif view_marker not in view:
    view = replace_once(view, modal_anchor, view_marker + '\n' + modal_anchor, "schedule dialog anchor")
if 'class="schedHelp"' not in view:
    view = replace_once(view, '<h3 id="scheduleTitle">Schedule Connect/Disconnect</h3>', '<h3 id="scheduleTitle">Schedule Connect/Disconnect</h3>\n<p class="schedHelp">Add multiple timed actions for a node. Actions for the same node are grouped below; edit any action to change its node, action, time, days, or options.</p>', "schedule dialog title")
if 'id="schedSubmit"' not in view:
    view = replace_once(view, '<input type="button" value="Add Schedule" class="small" onClick="addSchedule();">\n<input type="button" value="Close" class="small" onClick="closeScheduleDialog();">', '<input type="button" id="schedSubmit" value="Add Schedule" class="small" onClick="saveSchedule();">\n<input type="button" id="schedCancelEdit" value="Cancel Edit" class="small" hidden onClick="schedCancelEdit();">\n<input type="button" value="Close" class="small" onClick="closeScheduleDialog();">', "schedule dialog controls")
if '<thead><tr><th>Node</th><th>Scheduled actions</th></tr></thead>' not in view:
    view = replace_once(view, '<table id="schedList" class="favs"></table>', '<table id="schedList" class="favs"><thead><tr><th>Node</th><th>Scheduled actions</th></tr></thead><tbody></tbody></table>', "schedule action list")
if 'class="schedLayout"' not in view:
    view = replace_once(view, '<label for="schedAction">Action</label>', '<div class="schedLayout">\n<div class="schedForm">\n<label for="schedAction">Action</label>', "schedule grid start")
    view = replace_once(view, '\n<div id="schedMsg"></div>\n<table id="schedList"', '\n</div>\n<div class="schedListPane">\n<div id="schedMsg"></div>\n<table id="schedList"', "schedule list pane start")
    view = replace_once(view, "</table>\n</div>\n</div>\n';", "</table>\n</div>\n</div>\n</div>\n</div>\n';", "schedule grid closing tags")

js_marker = "// AllScan Mods: Edit and group scheduled actions by node v1.97."
if js_marker not in js:
    start = js.find("function schedRender(r) {")
    end = js.find("\nfunction openScheduleDialog()", start)
    if start < 0 or end < 0:
        raise SystemExit("ERROR: Expected the unmodified schedule-rendering block in main.js.")
    replacement = '''var schedEditingId = '';
function schedRender(r) {
\tvar msg = document.getElementById('schedMsg');
\tmsg.textContent = r.ok ? '' : r.msg;
\tif(!r.ok) return;
\tdocument.getElementById('schedWarn').hidden = r.runner;
\tdocument.getElementById('schedServerTime').textContent = 'server time ' + r.servertime;
\tvar t = document.querySelector('#schedList tbody');
\tt.textContent = '';
\tvar groups = {};
\tr.entries.forEach(function(e) { if(!groups[e.node]) groups[e.node] = []; groups[e.node].push(e); });
\tObject.keys(groups).forEach(function(node) {
\t\tgroups[node].sort(function(a, b) { return a.time.localeCompare(b.time); });
\t\tvar tr = t.insertRow();
\t\ttr.insertCell().textContent = node === '0' ? 'All nodes' : node;
\t\tvar actions = tr.insertCell();
\t\tgroups[node].forEach(function(e) {
\t\t\tvar rule = document.createElement('div');
\t\t\trule.className = 'schedRule';
\t\t\tvar description = document.createElement('span');
\t\t\tdescription.className = 'schedRuleText';
\t\t\tdescription.textContent = e.desc + (e.autodisc ? ' (disc first)' : '') + (e.enabled ? '' : ' [off]');
\t\t\trule.appendChild(description);
\t\t\t[['edit', 'Edit'], ['toggle', e.enabled ? 'Disable' : 'Enable'], ['delete', 'Delete']].forEach(function(a) {
\t\t\t\tvar b = document.createElement('input');
\t\t\t\tb.type = 'button'; b.className = 'small'; b.value = a[1];
\t\t\t\tb.onclick = function() { if(a[0] === 'edit') schedEdit(e); else schedPost('action=' + a[0] + '&id=' + encodeURIComponent(e.id), schedRender); };
\t\t\t\trule.appendChild(b);
\t\t\t});
\t\t\tactions.appendChild(rule);
\t\t});
\t});
}
function schedResetForm() {
\tschedEditingId = '';
\tdocument.getElementById('scheduleTitle').textContent = 'Schedule Connect/Disconnect';
\tdocument.getElementById('schedSubmit').value = 'Add Schedule';
\tdocument.getElementById('schedCancelEdit').hidden = true;
\tdocument.getElementById('schedAction').value = 'connect';
\tdocument.getElementById('schedTime').value = '08:00';
\tdocument.getElementById('schedPerm').checked = false;
\tdocument.getElementById('schedAutodisc').checked = false;
\tdocument.querySelectorAll('.schedDay').forEach(function(c) { c.checked = false; });
}
function schedEdit(e) {
\tschedEditingId = e.id;
\tdocument.getElementById('scheduleTitle').textContent = 'Edit Schedule';
\tdocument.getElementById('schedAction').value = e.action;
\tdocument.getElementById('schedNode').value = e.node;
\tdocument.getElementById('schedTime').value = e.time;
\tdocument.querySelectorAll('.schedDay').forEach(function(c) { c.checked = e.days.indexOf(parseInt(c.value, 10)) !== -1; });
\tdocument.getElementById('schedPerm').checked = !!e.perm;
\tdocument.getElementById('schedAutodisc').checked = !!e.autodisc;
\tdocument.getElementById('schedSubmit').value = 'Save Changes';
\tdocument.getElementById('schedCancelEdit').hidden = false;
\tdocument.getElementById('schedMsg').textContent = '';
}
'''
    js = js[:start] + js_marker + "\n" + replacement + js[end:]
    js = replace_once(js, "function openScheduleDialog() {\n\tdocument.getElementById('schedNode').value = rnode.value.trim();", "function openScheduleDialog() {\n\tschedResetForm();\n\tdocument.getElementById('schedNode').value = rnode.value.trim();", "schedule dialog open handler")
    js = replace_once(js, "function closeScheduleDialog() {\n\tdocument.getElementById('scheduleModal').hidden = true;\n}", "function closeScheduleDialog() {\n\tdocument.getElementById('scheduleModal').hidden = true;\n\tschedResetForm();\n}\nfunction schedCancelEdit() {\n\tschedResetForm();\n\tdocument.getElementById('schedNode').value = rnode.value.trim();\n\tdocument.getElementById('schedMsg').textContent = '';\n}", "schedule dialog close handler")
    old_add = '''function addSchedule() {
\tvar days = [];
\tdocument.querySelectorAll('.schedDay').forEach(function(c) { if(c.checked) days.push(c.value); });
\tvar node = document.getElementById('schedNode').value.trim();
\tif(!/^[0-9]{1,7}$/.test(node)) {
\t\talert('Enter a valid node number.');
\t\treturn;
\t}
\tschedPost('action=add&action2=' + document.getElementById('schedAction').value
\t\t+ '&node=' + node + '&time=' + document.getElementById('schedTime').value
\t\t+ '&days=' + days.join(',') + '&perm=' + document.getElementById('schedPerm').checked
\t\t+ '&autodisc=' + document.getElementById('schedAutodisc').checked, schedRender);
}'''
    new_add = '''function saveSchedule() {
\tvar days = [];
\tdocument.querySelectorAll('.schedDay').forEach(function(c) { if(c.checked) days.push(c.value); });
\tvar node = document.getElementById('schedNode').value.trim();
\tif(!/^[0-9]{1,7}$/.test(node)) { alert('Enter a valid node number.'); return; }
\tvar operation = schedEditingId ? 'edit' : 'add';
\tvar data = 'action=' + operation + '&action2=' + encodeURIComponent(document.getElementById('schedAction').value)
\t\t+ '&node=' + encodeURIComponent(node) + '&time=' + encodeURIComponent(document.getElementById('schedTime').value)
\t\t+ '&days=' + encodeURIComponent(days.join(',')) + '&perm=' + document.getElementById('schedPerm').checked
\t\t+ '&autodisc=' + document.getElementById('schedAutodisc').checked;
\tif(schedEditingId) data += '&id=' + encodeURIComponent(schedEditingId);
\tschedPost(data, function(r) { if(r.ok) schedResetForm(); schedRender(r); });
}'''
    js = replace_once(js, old_add, new_add, "schedule add handler")

css_marker = "/* AllScan Mods: Schedule form/list side-by-side layout v1.98. */"
css_marker_old = "/* AllScan Mods: Grouped schedule action rows v1.97. */"
css_old = css_marker_old + "\n.schedHelp {margin:0 0 8px;font-size:0.85em;color:#ddd;}\n#schedList {width:100%;}\n.schedRule {display:flex;flex-wrap:wrap;align-items:center;gap:2px 4px;padding:4px 0;}\n.schedRule + .schedRule {border-top:1px solid #555;}\n.schedRuleText {flex:1 1 100%;}\n.schedRule input {margin:0;}\n.schedWarn {margin-bottom:8px;"
css_rules = css_marker + "\n.schedHelp {margin:0 0 8px;font-size:0.85em;color:#ddd;}\n.schedLayout {display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start;}\n.schedForm,.schedListPane {min-width:0;}\n.schedListPane {max-height:65vh;overflow:auto;}\n#schedList {width:100%;margin:0;}\n#schedList thead th {position:sticky;top:0;z-index:1;}\n.schedRule {display:flex;flex-wrap:wrap;align-items:center;gap:2px 4px;padding:4px 0;}\n.schedRule + .schedRule {border-top:1px solid #555;}\n.schedRuleText {flex:1 1 100%;}\n.schedRule input {margin:0;}\n#scheduleModal .favEditPanel {width:min(820px,96vw);}\n@media (max-width:720px) {\n.schedLayout {grid-template-columns:1fr;gap:12px;}\n.schedListPane {max-height:35vh;}\n#scheduleModal .favEditPanel {width:min(500px,95vw);}\n}\n.schedWarn {margin-bottom:8px;"
if css_marker_old in css:
    css = replace_once(css, css_old, css_rules, "v1.97 schedule layout styles")
elif css_marker not in css:
    css = replace_once(css, ".schedWarn {margin-bottom:8px;", css_rules, "schedule CSS anchor")


for p, data in zip((api_path, view_path, js_path, css_path), (api, view, js, css)):
    p.write_text(data, encoding="utf-8")
