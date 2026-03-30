"""
create_crm_leads_workflows.py
Creates CRM and Leads n8n workflows for Hiraya Construction Supply Dashboard.

Workflows created:
  1. Hiraya — CRM          (handles read contacts, write contact, get messages, send message)
  2. Hiraya — Leads        (handles read leads, write lead)
  3. Updates Master workflow routing (adds crm + leads routes)

Sheet tabs required in your Google Sheet:
  CRM_Contacts | CRM_Messages | Leads
"""

import json
import os
import requests
import sys

# Load credentials from .mcp.json (never commit that file — it's in .gitignore)
_mcp_path = os.path.join(os.path.dirname(__file__), '..', '.mcp.json')
try:
    with open(_mcp_path) as f:
        _cfg = json.load(f)
    N8N_URL = _cfg['mcpServers']['n8n-mcp']['env']['N8N_API_URL']
    API_KEY = _cfg['mcpServers']['n8n-mcp']['env']['N8N_API_KEY']
except (FileNotFoundError, KeyError) as e:
    sys.exit(f"ERROR: Could not load credentials from .mcp.json — {e}\n"
             "Make sure .mcp.json exists in the project root.")

MASTER_ID = "NlxMBnjPepSitXeC"

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

SETTINGS = {
    "executionOrder": "v1",
    "saveManualExecutions": True,
    "callerPolicy": "workflowsFromSameOwner"
}

SHEET_PLACEHOLDER = "PASTE_YOUR_GOOGLE_SHEET_URL_HERE"

# ==============================================================================
# WORKFLOW 1: HIRAYA — CRM
# Handles 4 actions via internal Switch:
#   read_contacts   — read all CRM_Contacts rows
#   write_contact   — append a new row to CRM_Contacts
#   get_messages    — read CRM_Messages filtered by contactId
#   send_message    — append a new row to CRM_Messages
# ==============================================================================
CRM_WORKFLOW = {
    "name": "Hiraya — CRM",
    "settings": SETTINGS,
    "nodes": [
        # Trigger
        {
            "id": "crm-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 500],
            "parameters": {}
        },
        # Route by action
        {
            "id": "crm-switch",
            "name": "Route by Action",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [460, 500],
            "parameters": {
                "mode": "rules",
                "options": {},
                "rules": {
                    "values": [
                        {
                            "conditions": {
                                "options": {"caseSensitive": False, "typeValidation": "strict"},
                                "combinator": "and",
                                "conditions": [{"id": "a1", "leftValue": "={{ $json.action }}", "rightValue": "read_contacts", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        },
                        {
                            "conditions": {
                                "options": {"caseSensitive": False, "typeValidation": "strict"},
                                "combinator": "and",
                                "conditions": [{"id": "a2", "leftValue": "={{ $json.action }}", "rightValue": "write_contact", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        },
                        {
                            "conditions": {
                                "options": {"caseSensitive": False, "typeValidation": "strict"},
                                "combinator": "and",
                                "conditions": [{"id": "a3", "leftValue": "={{ $json.action }}", "rightValue": "get_messages", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        },
                        {
                            "conditions": {
                                "options": {"caseSensitive": False, "typeValidation": "strict"},
                                "combinator": "and",
                                "conditions": [{"id": "a4", "leftValue": "={{ $json.action }}", "rightValue": "send_message", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 0  # default to read_contacts
            }
        },

        # ── ACTION 0: READ CONTACTS ──────────────────────────────────────────
        {
            "id": "crm-read-sheet",
            "name": "Read CRM Contacts",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 200],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "CRM_Contacts"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "crm-read-process",
            "name": "Format Contacts",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 200],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
const rows = $input.all().map(i => i.json);
const contacts = rows.map(r => ({
  id:        r['ContactID']  || r['contactid']  || '',
  name:      r['Name']       || r['name']       || '',
  company:   r['Company']    || r['company']    || '',
  position:  r['Position']   || r['position']   || '',
  email:     r['Email']      || r['email']      || '',
  mobile:    r['Mobile']     || r['mobile']     || '',
  status:    r['Status']     || r['status']     || 'Active',
  source:    r['Source']     || r['source']     || '',
  notes:     r['Notes']      || r['notes']      || '',
  createdAt: r['CreatedAt']  || r['createdat']  || ''
}));
return [{ json: { action: 'read_contacts', contacts, total: contacts.length } }];
"""
            }
        },

        # ── ACTION 1: WRITE CONTACT ──────────────────────────────────────────
        {
            "id": "crm-prep-contact",
            "name": "Prepare Contact Row",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [700, 380],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": """
const d = $json.data || $json;
const now = new Date().toISOString().split('T')[0];
// Generate ContactID: C + timestamp last 5 digits
const id = 'C' + Date.now().toString().slice(-5);
return [{
  json: {
    ContactID:  d.id        || id,
    Name:       d.name      || '',
    Company:    d.company   || '',
    Position:   d.position  || '',
    Email:      d.email     || '',
    Mobile:     d.mobile    || '',
    Status:     d.status    || 'Active',
    Source:     d.source    || '',
    Notes:      d.notes     || '',
    CreatedAt:  d.createdAt || now
  }
}];
"""
            }
        },
        {
            "id": "crm-write-sheet",
            "name": "Append to CRM Contacts",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [920, 380],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "CRM_Contacts"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "ContactID": "={{ $json.ContactID }}",
                        "Name":      "={{ $json.Name }}",
                        "Company":   "={{ $json.Company }}",
                        "Position":  "={{ $json.Position }}",
                        "Email":     "={{ $json.Email }}",
                        "Mobile":    "={{ $json.Mobile }}",
                        "Status":    "={{ $json.Status }}",
                        "Source":    "={{ $json.Source }}",
                        "Notes":     "={{ $json.Notes }}",
                        "CreatedAt": "={{ $json.CreatedAt }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "crm-write-confirm",
            "name": "Write Confirm",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1140, 380],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { action: 'write_contact', success: true, message: 'Contact saved to Google Sheets.' } }];"
            }
        },

        # ── ACTION 2: GET MESSAGES for a contact ─────────────────────────────
        {
            "id": "crm-get-msg-sheet",
            "name": "Read CRM Messages",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 560],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "CRM_Messages"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "crm-get-msg-process",
            "name": "Filter Messages by Contact",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 560],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// contactId comes from the original trigger input, not the sheet data
// We need to get it from the workflow context
const allItems = $input.all();
const rows = allItems.map(i => i.json);

// The contactId was passed in the original call — read from first item metadata
// Since we can't easily pass it through, filter all if no contactId given
// The master should pass it as part of the payload
const contactId = $('When Called by Master').first().json.contactId || '';

const messages = rows
  .filter(r => !contactId || (r['ContactID'] || r['contactid'] || '') === contactId)
  .map(r => ({
    id:          r['MessageID']   || r['messageid']   || '',
    contactId:   r['ContactID']   || r['contactid']   || '',
    contactName: r['ContactName'] || r['contactname'] || '',
    direction:   r['Direction']   || r['direction']   || 'Sent',
    message:     r['Message']     || r['message']     || '',
    channel:     r['Channel']     || r['channel']     || 'In-App',
    timestamp:   r['Timestamp']   || r['timestamp']   || '',
    readStatus:  r['ReadStatus']  || r['readstatus']  || 'Read'
  }))
  .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

return [{ json: { action: 'get_messages', contactId, messages, total: messages.length } }];
"""
            }
        },

        # ── ACTION 3: SEND MESSAGE ────────────────────────────────────────────
        {
            "id": "crm-send-msg-prep",
            "name": "Prepare Message Row",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [700, 740],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": """
const d = $json.data || $json;
const now = new Date().toISOString();
const msgId = 'M' + Date.now().toString().slice(-6);
return [{
  json: {
    MessageID:   d.messageId   || msgId,
    ContactID:   d.contactId   || '',
    ContactName: d.contactName || '',
    Direction:   d.direction   || 'Sent',
    Message:     d.message     || '',
    Channel:     d.channel     || 'In-App',
    Timestamp:   d.timestamp   || now,
    ReadStatus:  'Unread'
  }
}];
"""
            }
        },
        {
            "id": "crm-send-msg-sheet",
            "name": "Append to CRM Messages",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [920, 740],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "CRM_Messages"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "MessageID":   "={{ $json.MessageID }}",
                        "ContactID":   "={{ $json.ContactID }}",
                        "ContactName": "={{ $json.ContactName }}",
                        "Direction":   "={{ $json.Direction }}",
                        "Message":     "={{ $json.Message }}",
                        "Channel":     "={{ $json.Channel }}",
                        "Timestamp":   "={{ $json.Timestamp }}",
                        "ReadStatus":  "={{ $json.ReadStatus }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "crm-send-msg-confirm",
            "name": "Message Confirm",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1140, 740],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { action: 'send_message', success: true, message: 'Message saved.' } }];"
            }
        }
    ],
    "connections": {
        "When Called by Master": {
            "main": [[{"node": "Route by Action", "type": "main", "index": 0}]]
        },
        "Route by Action": {
            "main": [
                [{"node": "Read CRM Contacts",      "type": "main", "index": 0}],
                [{"node": "Prepare Contact Row",     "type": "main", "index": 0}],
                [{"node": "Read CRM Messages",       "type": "main", "index": 0}],
                [{"node": "Prepare Message Row",     "type": "main", "index": 0}]
            ]
        },
        "Read CRM Contacts":      {"main": [[{"node": "Format Contacts",            "type": "main", "index": 0}]]},
        "Prepare Contact Row":    {"main": [[{"node": "Append to CRM Contacts",     "type": "main", "index": 0}]]},
        "Append to CRM Contacts": {"main": [[{"node": "Write Confirm",              "type": "main", "index": 0}]]},
        "Read CRM Messages":      {"main": [[{"node": "Filter Messages by Contact", "type": "main", "index": 0}]]},
        "Prepare Message Row":    {"main": [[{"node": "Append to CRM Messages",     "type": "main", "index": 0}]]},
        "Append to CRM Messages": {"main": [[{"node": "Message Confirm",            "type": "main", "index": 0}]]}
    }
}

# ==============================================================================
# WORKFLOW 2: HIRAYA — LEADS
# Handles 2 actions:
#   read_leads  — read all Leads rows
#   write_lead  — append a new lead row
# ==============================================================================
LEADS_WORKFLOW = {
    "name": "Hiraya — Leads",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "leads-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 400],
            "parameters": {}
        },
        {
            "id": "leads-switch",
            "name": "Route by Action",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [460, 400],
            "parameters": {
                "mode": "rules",
                "options": {},
                "rules": {
                    "values": [
                        {
                            "conditions": {
                                "options": {"caseSensitive": False, "typeValidation": "strict"},
                                "combinator": "and",
                                "conditions": [{"id": "l1", "leftValue": "={{ $json.action }}", "rightValue": "write_lead", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 1  # default output 1 = read
            }
        },

        # ── WRITE LEAD ───────────────────────────────────────────────────────
        {
            "id": "leads-prep-write",
            "name": "Prepare Lead Row",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [700, 260],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": """
const d = $json.data || $json;
const now = new Date().toISOString().split('T')[0];
const id = 'L' + Date.now().toString().slice(-5);
return [{
  json: {
    LeadID:     d.id         || id,
    Name:       d.name       || '',
    Company:    d.company    || '',
    Email:      d.email      || '',
    Mobile:     d.mobile     || '',
    Source:     d.source     || '',
    Status:     d.status     || 'New',
    Value:      d.value      || '0',
    AssignedTo: d.assignedTo || '',
    Notes:      d.notes      || '',
    CreatedAt:  d.createdAt  || now
  }
}];
"""
            }
        },
        {
            "id": "leads-write-sheet",
            "name": "Append to Leads Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [920, 260],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Leads"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "LeadID":     "={{ $json.LeadID }}",
                        "Name":       "={{ $json.Name }}",
                        "Company":    "={{ $json.Company }}",
                        "Email":      "={{ $json.Email }}",
                        "Mobile":     "={{ $json.Mobile }}",
                        "Source":     "={{ $json.Source }}",
                        "Status":     "={{ $json.Status }}",
                        "Value":      "={{ $json.Value }}",
                        "AssignedTo": "={{ $json.AssignedTo }}",
                        "Notes":      "={{ $json.Notes }}",
                        "CreatedAt":  "={{ $json.CreatedAt }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "leads-write-confirm",
            "name": "Lead Write Confirm",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1140, 260],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { action: 'write_lead', success: true, message: 'Lead saved to Google Sheets.' } }];"
            }
        },

        # ── READ LEADS ───────────────────────────────────────────────────────
        {
            "id": "leads-read-sheet",
            "name": "Read Leads Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 540],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Leads"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "leads-read-process",
            "name": "Format Leads",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 540],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
const rows = $input.all().map(i => i.json);

let totalValue = 0;
const statusCount = {};
const sourceCount = {};

const leads = rows.map(r => {
  const val = parseFloat(r['Value'] || r['value'] || 0);
  const status = r['Status'] || r['status'] || 'New';
  const source = r['Source'] || r['source'] || 'Unknown';

  totalValue += val;
  statusCount[status] = (statusCount[status] || 0) + 1;
  sourceCount[source] = (sourceCount[source] || 0) + 1;

  return {
    id:         r['LeadID']     || r['leadid']     || '',
    name:       r['Name']       || r['name']        || '',
    company:    r['Company']    || r['company']     || '',
    email:      r['Email']      || r['email']       || '',
    mobile:     r['Mobile']     || r['mobile']      || '',
    source,
    status,
    value:      val,
    assignedTo: r['AssignedTo'] || r['assignedto']  || '',
    notes:      r['Notes']      || r['notes']       || '',
    createdAt:  r['CreatedAt']  || r['createdat']   || ''
  };
});

const byStatus = Object.entries(statusCount).map(([status, count]) => ({ status, count }));
const bySource = Object.entries(sourceCount).map(([source, count]) => ({ source, count }));

return [{
  json: {
    action: 'read_leads',
    leads,
    total: leads.length,
    totalValue,
    byStatus,
    bySource
  }
}];
"""
            }
        }
    ],
    "connections": {
        "When Called by Master": {
            "main": [[{"node": "Route by Action", "type": "main", "index": 0}]]
        },
        "Route by Action": {
            "main": [
                [{"node": "Prepare Lead Row",    "type": "main", "index": 0}],
                [{"node": "Read Leads Sheet",    "type": "main", "index": 0}]
            ]
        },
        "Prepare Lead Row":    {"main": [[{"node": "Append to Leads Sheet", "type": "main", "index": 0}]]},
        "Append to Leads Sheet":{"main": [[{"node": "Lead Write Confirm",   "type": "main", "index": 0}]]},
        "Read Leads Sheet":    {"main": [[{"node": "Format Leads",          "type": "main", "index": 0}]]}
    }
}


def create_workflow(wf_def):
    resp = requests.post(
        f"{N8N_URL}/api/v1/workflows",
        headers=HEADERS,
        json=wf_def,
        timeout=30
    )
    if resp.status_code not in (200, 201):
        print(f"  FAIL ({resp.status_code}): {resp.text[:300]}")
        return None
    return resp.json()


def get_master_workflow():
    resp = requests.get(
        f"{N8N_URL}/api/v1/workflows/{MASTER_ID}",
        headers=HEADERS,
        timeout=30
    )
    if resp.status_code != 200:
        print(f"  Could not fetch master workflow: {resp.status_code}")
        return None
    return resp.json()


def update_master_workflow(master, crm_id, leads_id):
    """Add CRM and Leads routing to the Master workflow."""
    nodes = master.get("nodes", [])
    connections = master.get("connections", {})

    # ── New Execute Workflow nodes ────────────────────────────────────────────
    new_nodes = [
        {
            "id": "master-exec-crm",
            "name": "Get CRM Data",
            "type": "n8n-nodes-base.executeWorkflow",
            "typeVersion": 1,
            "position": [900, 780],
            "parameters": {
                "workflowId": {"__rl": True, "mode": "id", "value": crm_id},
                "options": {}
            }
        },
        {
            "id": "master-exec-leads",
            "name": "Get Leads Data",
            "type": "n8n-nodes-base.executeWorkflow",
            "typeVersion": 1,
            "position": [900, 940],
            "parameters": {
                "workflowId": {"__rl": True, "mode": "id", "value": leads_id},
                "options": {}
            }
        }
    ]

    # Add new nodes
    nodes.extend(new_nodes)

    # ── Update Switch node to include crm and leads rules ────────────────────
    switch_node = next((n for n in nodes if n.get("name") == "Route by Module"), None)
    if switch_node:
        existing_rules = switch_node["parameters"]["rules"]["values"]
        existing_rules.append({
            "conditions": {
                "options": {"caseSensitive": False, "typeValidation": "strict"},
                "combinator": "and",
                "conditions": [{"id": "r5", "leftValue": "={{ $json.module }}", "rightValue": "crm", "operator": {"type": "string", "operation": "equals"}}]
            }
        })
        existing_rules.append({
            "conditions": {
                "options": {"caseSensitive": False, "typeValidation": "strict"},
                "combinator": "and",
                "conditions": [{"id": "r6", "leftValue": "={{ $json.module }}", "rightValue": "leads", "operator": {"type": "string", "operation": "equals"}}]
            }
        })

    # ── Add connections from Switch to new nodes ──────────────────────────────
    switch_conns = connections.get("Route by Module", {}).get("main", [])
    # Output index 5 = crm, index 6 = leads (indices 0-4 already exist)
    while len(switch_conns) < 5:
        switch_conns.append([])
    switch_conns.append([{"node": "Get CRM Data",   "type": "main", "index": 0}])   # index 5
    switch_conns.append([{"node": "Get Leads Data", "type": "main", "index": 0}])   # index 6

    connections["Route by Module"] = {"main": switch_conns}

    # Connect new nodes to Respond
    connections["Get CRM Data"]   = {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]}
    connections["Get Leads Data"] = {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]}

    # ── PUT updated master back ───────────────────────────────────────────────
    update_payload = {
        "name":        master["name"],
        "nodes":       nodes,
        "connections": connections,
        "settings":    master.get("settings", {})
    }
    resp = requests.put(
        f"{N8N_URL}/api/v1/workflows/{MASTER_ID}",
        headers=HEADERS,
        json=update_payload,
        timeout=30
    )
    if resp.status_code not in (200, 201):
        print(f"  Master update FAIL ({resp.status_code}): {resp.text[:300]}")
        return False
    return True


def main():
    created_ids = {}

    # ── Create CRM workflow ───────────────────────────────────────────────────
    print("\n-- Creating CRM Workflow --")
    print("  Creating: Hiraya — CRM ...", end=" ")
    result = create_workflow(CRM_WORKFLOW)
    if result:
        crm_id = result.get("id") or result.get("data", {}).get("id", "?")
        created_ids["crm"] = crm_id
        print(f"OK  (id: {crm_id})")
    else:
        print("FAIL")
        crm_id = None

    # ── Create Leads workflow ─────────────────────────────────────────────────
    print("\n-- Creating Leads Workflow --")
    print("  Creating: Hiraya — Leads ...", end=" ")
    result = create_workflow(LEADS_WORKFLOW)
    if result:
        leads_id = result.get("id") or result.get("data", {}).get("id", "?")
        created_ids["leads"] = leads_id
        print(f"OK  (id: {leads_id})")
    else:
        print("FAIL")
        leads_id = None

    # ── Update Master workflow ────────────────────────────────────────────────
    if crm_id and leads_id:
        print("\n-- Updating Master Workflow --")
        print("  Fetching master ...", end=" ")
        master = get_master_workflow()
        if master:
            print("OK")
            print("  Adding CRM + Leads routes ...", end=" ")
            ok = update_master_workflow(master, crm_id, leads_id)
            print("OK" if ok else "FAIL")
        else:
            print("FAIL (could not fetch master)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n==========================================")
    print("  CRM + LEADS WORKFLOWS SUMMARY")
    print("==========================================")
    for key, wid in created_ids.items():
        label = {"crm": "Hiraya — CRM", "leads": "Hiraya — Leads"}.get(key, key)
        print(f"  {label:35s}  id: {wid}")

    print("""
  HOW TO CALL FROM DASHBOARD:

  READ contacts:
    POST /webhook/hiraya-dashboard
    { "module": "crm", "action": "read_contacts" }

  ADD contact:
    POST /webhook/hiraya-dashboard
    { "module": "crm", "action": "write_contact",
      "data": { "name":"Juan Dela Cruz", "company":"ABC", "email":"...", "mobile":"...",
                "position":"Manager", "status":"Active", "source":"Referral" } }

  GET messages for a contact:
    POST /webhook/hiraya-dashboard
    { "module": "crm", "action": "get_messages", "contactId": "C00123" }

  SEND a message:
    POST /webhook/hiraya-dashboard
    { "module": "crm", "action": "send_message",
      "data": { "contactId":"C00123", "contactName":"Juan", "message":"Hello!",
                "direction":"Sent", "channel":"In-App" } }

  READ leads:
    POST /webhook/hiraya-dashboard
    { "module": "leads", "action": "read_leads" }

  ADD lead:
    POST /webhook/hiraya-dashboard
    { "module": "leads", "action": "write_lead",
      "data": { "name":"Maria Santos", "company":"XYZ", "source":"Facebook",
                "status":"New", "value":"50000", "assignedTo":"Staff Name" } }

  SHEET TABS NEEDED:
    CRM_Contacts | CRM_Messages | Leads
==========================================
""")

    return created_ids


if __name__ == "__main__":
    main()
