# update_crm_workflow.py
# Adds get_inbox, get_sent, client_message, create_ticket, get_tickets
# to the Hiraya — CRM workflow (G4l053ovnCmHW7nA)

import json, urllib.request, urllib.error, sys

with open('.mcp.json') as f:
    cfg = json.load(f)

API_KEY  = cfg['mcpServers']['n8n-mcp']['env']['N8N_API_KEY']
BASE     = 'https://n8n.srv1326251.hstgr.cloud/api/v1'
WF_ID    = 'G4l053ovnCmHW7nA'
DOC_ID   = '1U8g4vVOh5zaPIvnFNg60cl24I2HLJcxtfZBuTZPP3vY'
MSGS_GID = 1605329457
GS_CRED  = 'EH6hrB4uQNUUb6Qv'

def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
          headers={'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print('HTTP ERROR', e.code, e.read().decode())
        sys.exit(1)

# Fetch current workflow
wf = api('GET', f'/workflows/{WF_ID}')
nodes  = wf['nodes']
conns  = wf['connections']

# ── Helpers ──────────────────────────────────────────

def gs_read(name, sheet_gid, sheet_name, pos):
    return {
        "id": name.lower().replace(' ','_'),
        "name": name,
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": pos,
        "credentials": {"googleSheetsOAuth2Api": {"id": GS_CRED, "name": "Google Sheets account 5"}},
        "parameters": {
            "operation": "read",
            "documentId": {"__rl": True, "mode": "id", "value": DOC_ID},
            "sheetName":  {"__rl": True, "value": sheet_gid, "mode": "list",
                          "cachedResultName": sheet_name,
                          "cachedResultUrl": f"https://docs.google.com/spreadsheets/d/{DOC_ID}/edit#gid={sheet_gid}"},
            "options": {}
        }
    }

def gs_append(name, sheet_gid, sheet_name, pos, columns_value):
    return {
        "id": name.lower().replace(' ','_'),
        "name": name,
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": pos,
        "credentials": {"googleSheetsOAuth2Api": {"id": GS_CRED, "name": "Google Sheets account 5"}},
        "parameters": {
            "operation": "append",
            "documentId": {"__rl": True, "mode": "id", "value": DOC_ID},
            "sheetName":  {"__rl": True, "value": sheet_gid, "mode": "list",
                          "cachedResultName": sheet_name,
                          "cachedResultUrl": f"https://docs.google.com/spreadsheets/d/{DOC_ID}/edit#gid={sheet_gid}"},
            "columns": {
                "mappingMode": "defineBelow",
                "value": columns_value,
                "matchingColumns": [],
                "schema": []
            },
            "options": {}
        }
    }

def code_node(name, pos, js, once_for_all=True):
    return {
        "id": name.lower().replace(' ','_'),
        "name": name,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": pos,
        "parameters": {
            "jsCode": js,
            "mode": "runOnceForAllItems" if once_for_all else "runOnceForEachItem"
        }
    }

# ── New nodes ─────────────────────────────────────────

new_nodes = [

    # ── get_inbox (output 5) ──────────────────────────
    gs_read("Read All Messages Inbox", MSGS_GID, "CRM_Messages", [704, 1120]),
    code_node("Format Inbox", [928, 1120], """
const rows = $input.all().map(i => i.json);
const received = rows
  .filter(r => (r.Direction || r.direction || '').toLowerCase() === 'received')
  .map(r => ({
    contactId:   r.ContactID   || r.contactid   || '',
    contactName: r.ContactName || r.contactname || '',
    company:     r.Company     || r.company     || '',
    email:       r.Email       || r.email       || '',
    direction:   'Received',
    message:     r.Message     || r.message     || '',
    channel:     r.Channel     || r.channel     || '',
    timestamp:   r.Timestamp   || r.timestamp   || '',
    read:        false
  }));
received.sort((a,b) => new Date(b.timestamp||0) - new Date(a.timestamp||0));
return [{ json: { action: 'get_inbox', messages: received, total: received.length } }];
"""),

    # ── get_sent (output 6) ──────────────────────────
    gs_read("Read All Messages Sent", MSGS_GID, "CRM_Messages", [704, 1280]),
    code_node("Format Sent", [928, 1280], """
const rows = $input.all().map(i => i.json);
const sent = rows
  .filter(r => (r.Direction || r.direction || '').toLowerCase() === 'sent')
  .map(r => ({
    contactId:   r.ContactID   || r.contactid   || '',
    contactName: r.ContactName || r.contactname || '',
    company:     r.Company     || r.company     || '',
    email:       r.Email       || r.email       || '',
    direction:   'Sent',
    message:     r.Message     || r.message     || '',
    channel:     r.Channel     || r.channel     || '',
    timestamp:   r.Timestamp   || r.timestamp   || ''
  }));
sent.sort((a,b) => new Date(b.timestamp||0) - new Date(a.timestamp||0));
return [{ json: { action: 'get_sent', messages: sent, total: sent.length } }];
"""),

    # ── client_message (output 7) ──────────────────────
    code_node("Prepare Client Message", [704, 1440], """
const item = $input.first().json;
const d = item.data || item;
return [{
  json: {
    ContactID:   d.contactId   || (d.contactName||'').replace(/\\s+/g,'_'),
    ContactName: d.contactName || d.name || '',
    Company:     d.company     || '',
    Email:       d.email       || '',
    Direction:   'Received',
    Message:     d.message     || '',
    Channel:     d.channel     || 'In-App',
    Timestamp:   d.timestamp   || new Date().toISOString()
  }
}];
"""),
    gs_append("Append Client Message", MSGS_GID, "CRM_Messages", [928, 1440], {
        "ContactID":   "={{ $json.ContactID }}",
        "ContactName": "={{ $json.ContactName }}",
        "Company":     "={{ $json.Company }}",
        "Email":       "={{ $json.Email }}",
        "Direction":   "={{ $json.Direction }}",
        "Message":     "={{ $json.Message }}",
        "Channel":     "={{ $json.Channel }}",
        "Timestamp":   "={{ $json.Timestamp }}"
    }),
    code_node("Client Message Confirm", [1152, 1440], """
return [{ json: { action: 'client_message', success: true, message: 'Client message received and logged.' } }];
"""),

    # ── create_ticket (output 8) ──────────────────────
    code_node("Prepare Ticket Row", [704, 1600], """
const item = $input.first().json;
const d = item.data || item;
return [{
  json: {
    TicketID:    d.id          || 'TKT-' + Date.now().toString().slice(-5),
    Subject:     d.subject     || '',
    Client:      d.client      || '',
    Priority:    d.priority    || 'Medium',
    Category:    d.category    || 'Other',
    AssignedTo:  d.assigned    || '',
    Description: d.description || '',
    Status:      'Open',
    CreatedAt:   d.createdAt   || new Date().toISOString()
  }
}];
"""),
    gs_append("Append to CRM Tickets", "new", "CRM_Tickets", [928, 1600], {
        "TicketID":    "={{ $json.TicketID }}",
        "Subject":     "={{ $json.Subject }}",
        "Client":      "={{ $json.Client }}",
        "Priority":    "={{ $json.Priority }}",
        "Category":    "={{ $json.Category }}",
        "AssignedTo":  "={{ $json.AssignedTo }}",
        "Description": "={{ $json.Description }}",
        "Status":      "={{ $json.Status }}",
        "CreatedAt":   "={{ $json.CreatedAt }}"
    }),
    code_node("Ticket Confirm", [1152, 1600], """
return [{ json: { action: 'create_ticket', success: true, message: 'Ticket created successfully.' } }];
"""),

    # ── get_tickets (output 9) ──────────────────────
    gs_read("Read CRM Tickets", "new", "CRM_Tickets", [704, 1760]),
    code_node("Format Tickets", [928, 1760], """
const rows = $input.all().map(i => i.json);
const tickets = rows.map(r => ({
  id:          r.TicketID    || r.ticketid    || '',
  subject:     r.Subject     || r.subject     || '',
  client:      r.Client      || r.client      || '',
  priority:    r.Priority    || r.priority    || 'Medium',
  category:    r.Category    || r.category    || '',
  assigned:    r.AssignedTo  || r.assignedto  || '',
  description: r.Description || r.description || '',
  status:      r.Status      || r.status      || 'Open',
  createdAt:   r.CreatedAt   || r.createdat   || ''
}));
return [{ json: { action: 'get_tickets', tickets, total: tickets.length } }];
"""),
]

# ── Handle CRM_Tickets sheet ─────────────────────────
# CRM_Tickets might not exist yet — use sheet name by URL style
# n8n will create it when first append happens if using URL mode
# Switch to URL mode for Tickets nodes
for n in new_nodes:
    if n['name'] in ('Append to CRM Tickets', 'Read CRM Tickets') and \
       n['parameters'].get('sheetName',{}).get('value') == 'new':
        n['parameters']['sheetName'] = {
            "__rl": True,
            "value": "CRM_Tickets",
            "mode": "list",
            "cachedResultName": "CRM_Tickets"
        }

# ── Add new rules to Switch node ────────────────────
switch = next(n for n in nodes if n['name'] == 'Route by Action')
new_rules = [
    ('a6', 'get_inbox'),
    ('a7', 'get_sent'),
    ('a8', 'client_message'),
    ('a9', 'create_ticket'),
    ('a10','get_tickets'),
]
for rid, action in new_rules:
    switch['parameters']['rules']['values'].append({
        "conditions": {
            "options": {"caseSensitive": False, "typeValidation": "strict"},
            "combinator": "and",
            "conditions": [{
                "id": rid,
                "leftValue": "={{ $json.action }}",
                "rightValue": action,
                "operator": {"type": "string", "operation": "equals"}
            }]
        }
    })

# ── Add nodes ────────────────────────────────────────
nodes.extend(new_nodes)

# ── Add connections ──────────────────────────────────
switch_conns = conns['Route by Action']['main']
# Indices 5–9 for the new switch outputs
switch_conns.append([{"node": "Read All Messages Inbox",  "type": "main", "index": 0}])
switch_conns.append([{"node": "Read All Messages Sent",   "type": "main", "index": 0}])
switch_conns.append([{"node": "Prepare Client Message",   "type": "main", "index": 0}])
switch_conns.append([{"node": "Prepare Ticket Row",       "type": "main", "index": 0}])
switch_conns.append([{"node": "Read CRM Tickets",         "type": "main", "index": 0}])

# get_inbox chain
conns['Read All Messages Inbox'] = {"main": [[{"node": "Format Inbox", "type": "main", "index": 0}]]}

# get_sent chain
conns['Read All Messages Sent'] = {"main": [[{"node": "Format Sent", "type": "main", "index": 0}]]}

# client_message chain
conns['Prepare Client Message'] = {"main": [[{"node": "Append Client Message", "type": "main", "index": 0}]]}
conns['Append Client Message']  = {"main": [[{"node": "Client Message Confirm", "type": "main", "index": 0}]]}

# create_ticket chain
conns['Prepare Ticket Row']       = {"main": [[{"node": "Append to CRM Tickets", "type": "main", "index": 0}]]}
conns['Append to CRM Tickets']    = {"main": [[{"node": "Ticket Confirm", "type": "main", "index": 0}]]}

# get_tickets chain
conns['Read CRM Tickets'] = {"main": [[{"node": "Format Tickets", "type": "main", "index": 0}]]}

# ── Push update ──────────────────────────────────────
payload = {
    "name":     wf['name'],
    "nodes":    nodes,
    "connections": conns,
    "settings": wf.get('settings', {}),
    "staticData": wf.get('staticData')
}

result = api('PUT', f'/workflows/{WF_ID}', payload)
print('Workflow updated:', result.get('name'))
print('Total nodes:', len(result.get('nodes', [])))

# Re-activate
act = api('POST', f'/workflows/{WF_ID}/activate')
print('Activated:', act.get('active', False))
print('Done.')
