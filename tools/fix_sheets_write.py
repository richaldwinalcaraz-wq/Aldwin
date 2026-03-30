# fix_sheets_write.py
# 1. Fix mappingMode on CRM Contacts + CRM Messages append nodes (value was {})
# 2. Fix mappingMode on Leads append node
# 3. Add write_employee action to HR workflow
# 4. Add HR sheet GID lookup if needed

import json, urllib.request, urllib.error, sys

with open('.mcp.json') as f:
    cfg = json.load(f)

API_KEY = cfg['mcpServers']['n8n-mcp']['env']['N8N_API_KEY']
BASE    = 'https://n8n.srv1326251.hstgr.cloud/api/v1'
DOC_ID  = '1U8g4vVOh5zaPIvnFNg60cl24I2HLJcxtfZBuTZPP3vY'
GS_CRED = 'EH6hrB4uQNUUb6Qv'
HR_GID  = 1846680084

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

# ═══════════════════════════════════════════════════════
#  1. FIX CRM WORKFLOW — CRM Contacts + CRM Messages append
# ═══════════════════════════════════════════════════════

print('--- Fixing CRM workflow append nodes ---')
crm = api('GET', '/workflows/G4l053ovnCmHW7nA')

for node in crm['nodes']:
    if node['name'] == 'Append to CRM Contacts':
        node['parameters']['columns'] = {
            'mappingMode': 'defineBelow',
            'value': {
                'ContactID':  '={{ $json.ContactID }}',
                'Name':       '={{ $json.Name }}',
                'Company':    '={{ $json.Company }}',
                'Position':   '={{ $json.Position }}',
                'Email':      '={{ $json.Email }}',
                'Mobile':     '={{ $json.Mobile }}',
                'Status':     '={{ $json.Status }}',
                'Source':     '={{ $json.Source }}',
                'Notes':      '={{ $json.Notes }}',
                'CreatedAt':  '={{ $json.CreatedAt }}'
            },
            'matchingColumns': [],
            'schema': node['parameters']['columns'].get('schema', []),
            'attemptToConvertTypes': False,
            'convertFieldsToString': False
        }
        print('  Fixed: Append to CRM Contacts')

    elif node['name'] == 'Append to CRM Messages':
        node['parameters']['columns'] = {
            'mappingMode': 'defineBelow',
            'value': {
                'MessageID':   '={{ $json.MessageID }}',
                'ContactID':   '={{ $json.ContactID }}',
                'ContactName': '={{ $json.ContactName }}',
                'Direction':   '={{ $json.Direction }}',
                'Message':     '={{ $json.Message }}',
                'Channel':     '={{ $json.Channel }}',
                'Timestamp':   '={{ $json.Timestamp }}',
                'ReadStatus':  '={{ $json.ReadStatus }}'
            },
            'matchingColumns': [],
            'schema': node['parameters']['columns'].get('schema', []),
            'attemptToConvertTypes': False,
            'convertFieldsToString': False
        }
        print('  Fixed: Append to CRM Messages')

r = api('PUT', '/workflows/G4l053ovnCmHW7nA', {
    'name': crm['name'], 'nodes': crm['nodes'],
    'connections': crm['connections'], 'settings': crm.get('settings', {}),
    'staticData': crm.get('staticData')
})
api('POST', '/workflows/G4l053ovnCmHW7nA/activate')
print('  CRM workflow saved & activated. Nodes:', len(r.get('nodes', [])))

# ═══════════════════════════════════════════════════════
#  2. FIX LEADS WORKFLOW — Append column mapping
# ═══════════════════════════════════════════════════════

print('\n--- Fixing Leads workflow append node ---')
leads = api('GET', '/workflows/LQiu9K6mUhCK2H2V')

for node in leads['nodes']:
    if node['name'] == 'Append to Leads Sheet':
        node['parameters']['columns'] = {
            'mappingMode': 'defineBelow',
            'value': {
                'LeadID':     '={{ $json.LeadID }}',
                'Name':       '={{ $json.Name }}',
                'Company':    '={{ $json.Company }}',
                'Email':      '={{ $json.Email }}',
                'Mobile':     '={{ $json.Mobile }}',
                'Source':     '={{ $json.Source }}',
                'Status':     '={{ $json.Status }}',
                'Value':      '={{ $json.Value }}',
                'AssignedTo': '={{ $json.AssignedTo }}',
                'Notes':      '={{ $json.Notes }}',
                'CreatedAt':  '={{ $json.CreatedAt }}'
            },
            'matchingColumns': [],
            'schema': node['parameters']['columns'].get('schema', []),
            'attemptToConvertTypes': False,
            'convertFieldsToString': False
        }
        print('  Fixed: Append to Leads Sheet')

r = api('PUT', '/workflows/LQiu9K6mUhCK2H2V', {
    'name': leads['name'], 'nodes': leads['nodes'],
    'connections': leads['connections'], 'settings': leads.get('settings', {}),
    'staticData': leads.get('staticData')
})
api('POST', '/workflows/LQiu9K6mUhCK2H2V/activate')
print('  Leads workflow saved & activated. Nodes:', len(r.get('nodes', [])))

# ═══════════════════════════════════════════════════════
#  3. RESTRUCTURE HR WORKFLOW — Add write_employee action
# ═══════════════════════════════════════════════════════

print('\n--- Restructuring HR workflow ---')
hr = api('GET', '/workflows/BaF3GmxnlS8xYfgy')

nodes = hr['nodes']
conns = hr['connections']

# Find trigger node
trigger = next(n for n in nodes if 'executeWorkflowTrigger' in n['type'])
read_node = next(n for n in nodes if 'Read HR Sheet' in n['name'])

# 1. Insert Switch node between trigger and existing read
switch_node = {
    'id': 'hr_switch',
    'name': 'Route HR Action',
    'type': 'n8n-nodes-base.switch',
    'typeVersion': 3,
    'position': [464, 400],
    'parameters': {
        'mode': 'rules',
        'rules': {
            'values': [
                {
                    'conditions': {
                        'options': {'caseSensitive': False, 'typeValidation': 'strict'},
                        'combinator': 'and',
                        'conditions': [{
                            'id': 'h1',
                            'leftValue': '={{ $json.action }}',
                            'rightValue': 'write_employee',
                            'operator': {'type': 'string', 'operation': 'equals'}
                        }]
                    }
                }
            ]
        },
        'options': {}
    }
}

# 2. Prepare Employee Row
prep_node = {
    'id': 'hr_prep_emp',
    'name': 'Prepare Employee Row',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [704, 272],
    'parameters': {
        'mode': 'runOnceForAllItems',
        'jsCode': """
const item = $input.first().json;
const d = item.data || item;
const now = new Date().toISOString().split('T')[0];
const empId = d.employeeId || ('E' + Date.now().toString().slice(-5));
return [{
  json: {
    EmployeeID:         empId,
    Name:               d.name        || '',
    Position:           d.position    || '',
    Status:             d.status      || 'Present',
    LeaveBalance:       d.leaveBalance || '0',
    Salary:             d.salary      || '0',
    Mobile:             d.mobile      || '',
    Email:              d.email       || '',
    EmergencyName:      d.emergencyName     || '',
    EmergencyRelation:  d.emergencyRelation || '',
    EmergencyMobile:    d.emergencyMobile   || '',
    CreatedAt:          d.createdAt   || now
  }
}];
"""
    }
}

# 3. Append to HR Sheet
append_node = {
    'id': 'hr_append',
    'name': 'Append to HR Sheet',
    'type': 'n8n-nodes-base.googleSheets',
    'typeVersion': 4.5,
    'position': [928, 272],
    'credentials': {'googleSheetsOAuth2Api': {'id': GS_CRED, 'name': 'Google Sheets account 5'}},
    'parameters': {
        'operation': 'append',
        'documentId': {'__rl': True, 'mode': 'id', 'value': DOC_ID},
        'sheetName':  {'__rl': True, 'value': HR_GID, 'mode': 'list',
                       'cachedResultName': 'HR',
                       'cachedResultUrl': f'https://docs.google.com/spreadsheets/d/{DOC_ID}/edit#gid={HR_GID}'},
        'columns': {
            'mappingMode': 'defineBelow',
            'value': {
                'EmployeeID':        '={{ $json.EmployeeID }}',
                'Name':              '={{ $json.Name }}',
                'Position':          '={{ $json.Position }}',
                'Status':            '={{ $json.Status }}',
                'LeaveBalance':      '={{ $json.LeaveBalance }}',
                'Salary':            '={{ $json.Salary }}',
                'Mobile':            '={{ $json.Mobile }}',
                'Email':             '={{ $json.Email }}',
                'EmergencyName':     '={{ $json.EmergencyName }}',
                'EmergencyRelation': '={{ $json.EmergencyRelation }}',
                'EmergencyMobile':   '={{ $json.EmergencyMobile }}'
            },
            'matchingColumns': [],
            'schema': [],
            'attemptToConvertTypes': False,
            'convertFieldsToString': False
        },
        'options': {}
    }
}

# 4. Employee Write Confirm
confirm_node = {
    'id': 'hr_emp_confirm',
    'name': 'Employee Write Confirm',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [1152, 272],
    'parameters': {
        'mode': 'runOnceForAllItems',
        'jsCode': "return [{ json: { action: 'write_employee', success: true, message: 'Employee saved to HR sheet.' } }];"
    }
}

# Reposition existing nodes
for n in nodes:
    if n['name'] == 'When Called by Master':
        n['position'] = [240, 400]
    elif n['name'] == 'Read HR Sheet':
        n['position'] = [704, 544]
    elif n['name'] == 'Process HR Data':
        n['position'] = [928, 544]

nodes.extend([switch_node, prep_node, append_node, confirm_node])

# Rewire connections:
# Trigger → Switch
# Switch output 0 (write_employee) → Prepare Employee Row → Append → Confirm
# Switch output 1 (default/read) → Read HR Sheet → Process HR Data
conns[trigger['name']] = {'main': [[{'node': 'Route HR Action', 'type': 'main', 'index': 0}]]}
conns['Route HR Action'] = {'main': [
    [{'node': 'Prepare Employee Row', 'type': 'main', 'index': 0}],  # output 0: write
    [{'node': 'Read HR Sheet',        'type': 'main', 'index': 0}],  # output 1: read
]}
conns['Prepare Employee Row'] = {'main': [[{'node': 'Append to HR Sheet',      'type': 'main', 'index': 0}]]}
conns['Append to HR Sheet']   = {'main': [[{'node': 'Employee Write Confirm',  'type': 'main', 'index': 0}]]}
# Read HR Sheet → Process HR Data already exists, keep it
conns.setdefault('Read HR Sheet', {'main': [[{'node': 'Process HR Data', 'type': 'main', 'index': 0}]]})

r = api('PUT', '/workflows/BaF3GmxnlS8xYfgy', {
    'name': hr['name'], 'nodes': nodes,
    'connections': conns, 'settings': hr.get('settings', {}),
    'staticData': hr.get('staticData')
})
api('POST', '/workflows/BaF3GmxnlS8xYfgy/activate')
print('  HR workflow saved & activated. Nodes:', len(r.get('nodes', [])))
print('\nAll done.')
