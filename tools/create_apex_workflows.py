"""
create_apex_workflows.py
Creates all n8n backend workflows for the Apex Auto Care Dashboard.

Workflows created:
  1. Apex Auto — Appointments   (read + write appointments)
  2. Apex Auto — Work Orders    (read + write work orders)
  3. Apex Auto — Services       (read + write service catalog)
  4. Apex Auto — Customers      (read + write customers)
  5. Apex Auto — Staff          (read + write staff)
  6. Apex Auto — Analytics      (aggregated charts/trends)
  7. Apex Auto Dashboard — MASTER (webhook, routes to sub-workflows)

After running:
  - Add Google Sheets credentials in n8n (Settings > Credentials > New > Google Sheets OAuth2)
  - Open each sub-workflow and connect credentials + set your spreadsheet URL
  - Required sheet tab names: Appointments | WorkOrders | Services | Customers | Staff
  - Activate the MASTER workflow (toggle in n8n)
  - Update CONFIG.webhookUrl in Apex Auto index.html to the printed webhook URL
"""

import json
import os
import requests
import sys

# Load credentials from .mcp.json
_mcp_path = os.path.join(os.path.dirname(__file__), '..', '.mcp.json')
try:
    with open(_mcp_path) as f:
        _cfg = json.load(f)
    N8N_URL = _cfg['mcpServers']['n8n-mcp']['env']['N8N_API_URL']
    API_KEY  = _cfg['mcpServers']['n8n-mcp']['env']['N8N_API_KEY']
except (FileNotFoundError, KeyError) as e:
    sys.exit(f"ERROR: Could not load credentials from .mcp.json — {e}\n"
             "Make sure .mcp.json exists in the project root.")

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
# SUB-WORKFLOW 1: APPOINTMENTS
# Actions: read_appointments | write_appointment
# Sheet tab: Appointments
# Columns: ApptID, Customer, Vehicle, Service, Date, Time, Status, Notes
# ==============================================================================
APPOINTMENTS_WORKFLOW = {
    "name": "Apex Auto — Appointments",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "appt-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 500],
            "parameters": {}
        },
        {
            "id": "appt-switch",
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
                                "conditions": [{"id": "a1", "leftValue": "={{ $json.action }}", "rightValue": "write_appointment", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 1  # default to read
            }
        },
        # ACTION 0: WRITE
        {
            "id": "appt-write-sheet",
            "name": "Write Appointment Row",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 300],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Appointments"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "ApptID":   "={{ $json.data.apptId || $json.data.id || ('A' + Date.now()) }}",
                        "Customer": "={{ $json.data.customer }}",
                        "Vehicle":  "={{ $json.data.vehicle }}",
                        "Service":  "={{ $json.data.service }}",
                        "Date":     "={{ $json.data.date }}",
                        "Time":     "={{ $json.data.time }}",
                        "Status":   "={{ $json.data.status || 'Scheduled' }}",
                        "Notes":    "={{ $json.data.notes || '' }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "appt-write-result",
            "name": "Return Write Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 300],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { module: 'appointments', action: 'write_appointment', success: true } }];"
            }
        },
        # ACTION 1: READ (fallback)
        {
            "id": "appt-read-sheet",
            "name": "Read Appointments Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 680],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Appointments"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "appt-process",
            "name": "Process Appointments Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 680],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Apex Auto Appointments Processor --
// Columns: ApptID, Customer, Vehicle, Service, Date, Time, Status, Notes
const rows = $input.all().map(i => i.json);

const today = new Date().toISOString().split('T')[0];
let scheduled = 0, inService = 0, completed = 0, cancelled = 0;
const todayAppts = [];
const serviceMap = {};

for (const row of rows) {
  const status = (row['Status'] || row['status'] || 'Scheduled').toString();
  const date   = row['Date'] || row['date'] || '';
  const svc    = row['Service'] || row['service'] || 'Other';

  if (status === 'Scheduled')   scheduled++;
  if (status === 'In Service')  inService++;
  if (status === 'Completed')   completed++;
  if (status === 'Cancelled')   cancelled++;

  if (date === today) {
    todayAppts.push({
      id:       row['ApptID']   || row['apptid']   || '—',
      customer: row['Customer'] || row['customer'] || '—',
      vehicle:  row['Vehicle']  || row['vehicle']  || '—',
      service:  svc,
      time:     row['Time']     || row['time']     || '—',
      status,
      notes:    row['Notes']    || row['notes']    || ''
    });
  }

  serviceMap[svc] = (serviceMap[svc] || 0) + 1;
}

const topServices = Object.entries(serviceMap)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 5)
  .map(([name, count]) => ({ name, count }));

const appointments = rows.map(r => ({
  id:       r['ApptID']   || '—',
  customer: r['Customer'] || '—',
  vehicle:  r['Vehicle']  || '—',
  service:  r['Service']  || '—',
  date:     r['Date']     || '—',
  time:     r['Time']     || '—',
  status:   r['Status']   || 'Scheduled',
  notes:    r['Notes']    || ''
}));

return [{
  json: {
    module: 'appointments',
    totalAppointments: rows.length,
    scheduled, inService, completed, cancelled,
    todayCount: todayAppts.length,
    todayAppointments: todayAppts,
    topServices,
    appointments,
    generatedAt: new Date().toISOString()
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
                [{"node": "Write Appointment Row",   "type": "main", "index": 0}],
                [{"node": "Read Appointments Sheet", "type": "main", "index": 0}]
            ]
        },
        "Write Appointment Row":   {"main": [[{"node": "Return Write Result",          "type": "main", "index": 0}]]},
        "Read Appointments Sheet": {"main": [[{"node": "Process Appointments Data",    "type": "main", "index": 0}]]}
    }
}


# ==============================================================================
# SUB-WORKFLOW 2: WORK ORDERS
# Actions: read_workorders | write_workorder
# Sheet tab: WorkOrders
# Columns: WOID, Customer, Vehicle, Services, Mechanic, Status, Total, Date
# ==============================================================================
WORKORDERS_WORKFLOW = {
    "name": "Apex Auto — Work Orders",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "wo-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 500],
            "parameters": {}
        },
        {
            "id": "wo-switch",
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
                                "conditions": [{"id": "w1", "leftValue": "={{ $json.action }}", "rightValue": "write_workorder", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 1
            }
        },
        # ACTION 0: WRITE
        {
            "id": "wo-write-sheet",
            "name": "Write Work Order Row",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 300],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "WorkOrders"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "WOID":     "={{ $json.data.woId || $json.data.id || ('WO' + Date.now()) }}",
                        "Customer": "={{ $json.data.customer }}",
                        "Vehicle":  "={{ $json.data.vehicle }}",
                        "Services": "={{ $json.data.services }}",
                        "Mechanic": "={{ $json.data.mechanic || '' }}",
                        "Status":   "={{ $json.data.status || 'Open' }}",
                        "Total":    "={{ $json.data.total || 0 }}",
                        "Date":     "={{ $json.data.date || new Date().toISOString().split('T')[0] }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "wo-write-result",
            "name": "Return Write Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 300],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { module: 'workorders', action: 'write_workorder', success: true } }];"
            }
        },
        # ACTION 1: READ (fallback)
        {
            "id": "wo-read-sheet",
            "name": "Read Work Orders Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 680],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "WorkOrders"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "wo-process",
            "name": "Process Work Orders Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 680],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Apex Auto Work Orders Processor --
// Columns: WOID, Customer, Vehicle, Services, Mechanic, Status, Total, Date
const rows = $input.all().map(i => i.json);

const today = new Date();
const thisMonth = today.getMonth();
const thisYear  = today.getFullYear();

let openCount = 0, inProgressCount = 0, completedCount = 0;
let totalRevenue = 0, monthRevenue = 0;
const mechanicMap = {};

for (const row of rows) {
  const status = (row['Status'] || row['status'] || 'Open').toString();
  const total  = parseFloat(row['Total'] || row['total'] || 0);
  const date   = new Date(row['Date'] || row['date'] || '');
  const mech   = row['Mechanic'] || row['mechanic'] || 'Unassigned';

  if (status === 'Open')        openCount++;
  if (status === 'In Progress') inProgressCount++;
  if (status === 'Completed')   completedCount++;

  if (status === 'Completed') {
    totalRevenue += total;
    if (!isNaN(date.getTime()) &&
        date.getMonth() === thisMonth &&
        date.getFullYear() === thisYear) {
      monthRevenue += total;
    }
  }

  mechanicMap[mech] = (mechanicMap[mech] || 0) + 1;
}

const topMechanics = Object.entries(mechanicMap)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 5)
  .map(([name, count]) => ({ name, count }));

const workorders = rows.map(r => ({
  id:       r['WOID']     || '—',
  customer: r['Customer'] || '—',
  vehicle:  r['Vehicle']  || '—',
  services: r['Services'] || '—',
  mechanic: r['Mechanic'] || '—',
  status:   r['Status']   || 'Open',
  total:    parseFloat(r['Total'] || 0),
  date:     r['Date']     || '—'
}));

return [{
  json: {
    module: 'workorders',
    totalWorkOrders: rows.length,
    openCount, inProgressCount, completedCount,
    totalRevenue, monthRevenue,
    topMechanics,
    workorders,
    generatedAt: new Date().toISOString()
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
                [{"node": "Write Work Order Row",   "type": "main", "index": 0}],
                [{"node": "Read Work Orders Sheet", "type": "main", "index": 0}]
            ]
        },
        "Write Work Order Row":   {"main": [[{"node": "Return Write Result",         "type": "main", "index": 0}]]},
        "Read Work Orders Sheet": {"main": [[{"node": "Process Work Orders Data",    "type": "main", "index": 0}]]}
    }
}


# ==============================================================================
# SUB-WORKFLOW 3: SERVICES
# Actions: read_services | write_service
# Sheet tab: Services
# Columns: ServiceID, Name, Category, Duration, Price, Description
# ==============================================================================
SERVICES_WORKFLOW = {
    "name": "Apex Auto — Services",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "svc-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 500],
            "parameters": {}
        },
        {
            "id": "svc-switch",
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
                                "conditions": [{"id": "s1", "leftValue": "={{ $json.action }}", "rightValue": "write_service", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 1
            }
        },
        # ACTION 0: WRITE
        {
            "id": "svc-write-sheet",
            "name": "Write Service Row",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 300],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Services"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "ServiceID":   "={{ $json.data.serviceId || $json.data.id || ('SVC' + Date.now()) }}",
                        "Name":        "={{ $json.data.name }}",
                        "Category":    "={{ $json.data.category || 'Other' }}",
                        "Duration":    "={{ $json.data.duration || '' }}",
                        "Price":       "={{ $json.data.price || 0 }}",
                        "Description": "={{ $json.data.desc || $json.data.description || '' }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "svc-write-result",
            "name": "Return Write Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 300],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { module: 'services', action: 'write_service', success: true } }];"
            }
        },
        # ACTION 1: READ (fallback)
        {
            "id": "svc-read-sheet",
            "name": "Read Services Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 680],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Services"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "svc-process",
            "name": "Process Services Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 680],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Apex Auto Services Processor --
// Columns: ServiceID, Name, Category, Duration, Price, Description
const rows = $input.all().map(i => i.json);

const categoryMap = {};
let totalServices = rows.length;

const services = rows.map(r => {
  const cat = r['Category'] || r['category'] || 'Other';
  categoryMap[cat] = (categoryMap[cat] || 0) + 1;
  return {
    id:       r['ServiceID']    || '—',
    name:     r['Name']         || '—',
    category: cat,
    duration: r['Duration']     || '—',
    price:    parseFloat(r['Price'] || 0),
    desc:     r['Description']  || ''
  };
});

const categories = Object.entries(categoryMap)
  .map(([name, count]) => ({ name, count }))
  .sort((a, b) => b.count - a.count);

return [{
  json: {
    module: 'services',
    totalServices,
    categories,
    services,
    generatedAt: new Date().toISOString()
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
                [{"node": "Write Service Row",   "type": "main", "index": 0}],
                [{"node": "Read Services Sheet", "type": "main", "index": 0}]
            ]
        },
        "Write Service Row":   {"main": [[{"node": "Return Write Result",   "type": "main", "index": 0}]]},
        "Read Services Sheet": {"main": [[{"node": "Process Services Data", "type": "main", "index": 0}]]}
    }
}


# ==============================================================================
# SUB-WORKFLOW 4: CUSTOMERS
# Actions: read_customers | write_customer
# Sheet tab: Customers
# Columns: CustomerID, Name, Mobile, Email, Vehicles, Visits, LastVisit
# ==============================================================================
CUSTOMERS_WORKFLOW = {
    "name": "Apex Auto — Customers",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "cust-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 500],
            "parameters": {}
        },
        {
            "id": "cust-switch",
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
                                "conditions": [{"id": "c1", "leftValue": "={{ $json.action }}", "rightValue": "write_customer", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 1
            }
        },
        # ACTION 0: WRITE
        {
            "id": "cust-write-sheet",
            "name": "Write Customer Row",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 300],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Customers"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "CustomerID": "={{ $json.data.customerId || $json.data.id || ('C' + Date.now()) }}",
                        "Name":       "={{ $json.data.name }}",
                        "Mobile":     "={{ $json.data.mobile || '' }}",
                        "Email":      "={{ $json.data.email || '' }}",
                        "Vehicles":   "={{ $json.data.vehicles || '' }}",
                        "Visits":     "={{ $json.data.visits || 0 }}",
                        "LastVisit":  "={{ $json.data.lastVisit || new Date().toISOString().split('T')[0] }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "cust-write-result",
            "name": "Return Write Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 300],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { module: 'customers', action: 'write_customer', success: true } }];"
            }
        },
        # ACTION 1: READ (fallback)
        {
            "id": "cust-read-sheet",
            "name": "Read Customers Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 680],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Customers"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "cust-process",
            "name": "Process Customers Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 680],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Apex Auto Customers Processor --
// Columns: CustomerID, Name, Mobile, Email, Vehicles, Visits, LastVisit
const rows = $input.all().map(i => i.json);

let newCustomers = 0;
let returningCustomers = 0;

const customers = rows.map(r => {
  const visits = parseInt(r['Visits'] || r['visits'] || 0);
  if (visits <= 1) newCustomers++;
  else returningCustomers++;

  return {
    id:        r['CustomerID'] || '—',
    name:      r['Name']       || '—',
    mobile:    r['Mobile']     || '—',
    email:     r['Email']      || '—',
    vehicles:  r['Vehicles']   || '—',
    visits,
    lastVisit: r['LastVisit']  || '—',
    isNew:     visits <= 1
  };
});

// Top customers by visits
const topCustomers = [...customers]
  .sort((a, b) => b.visits - a.visits)
  .slice(0, 5);

return [{
  json: {
    module: 'customers',
    totalCustomers: rows.length,
    newCustomers,
    returningCustomers,
    topCustomers,
    customers,
    generatedAt: new Date().toISOString()
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
                [{"node": "Write Customer Row",   "type": "main", "index": 0}],
                [{"node": "Read Customers Sheet", "type": "main", "index": 0}]
            ]
        },
        "Write Customer Row":   {"main": [[{"node": "Return Write Result",    "type": "main", "index": 0}]]},
        "Read Customers Sheet": {"main": [[{"node": "Process Customers Data", "type": "main", "index": 0}]]}
    }
}


# ==============================================================================
# SUB-WORKFLOW 5: STAFF
# Actions: read_staff | write_staff
# Sheet tab: Staff
# Columns: StaffID, Name, Role, Specialty, Status, Mobile, Salary
# ==============================================================================
STAFF_WORKFLOW = {
    "name": "Apex Auto — Staff",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "staff-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 500],
            "parameters": {}
        },
        {
            "id": "staff-switch",
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
                                "conditions": [{"id": "st1", "leftValue": "={{ $json.action }}", "rightValue": "write_staff", "operator": {"type": "string", "operation": "equals"}}]
                            }
                        }
                    ]
                },
                "fallbackOutput": 1
            }
        },
        # ACTION 0: WRITE
        {
            "id": "staff-write-sheet",
            "name": "Write Staff Row",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 300],
            "parameters": {
                "operation": "append",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Staff"},
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "StaffID":   "={{ $json.data.staffId || $json.data.id || ('ST' + Date.now()) }}",
                        "Name":      "={{ $json.data.name }}",
                        "Role":      "={{ $json.data.role || 'Mechanic' }}",
                        "Specialty": "={{ $json.data.specialty || '' }}",
                        "Status":    "={{ $json.data.status || 'Present' }}",
                        "Mobile":    "={{ $json.data.mobile || '' }}",
                        "Salary":    "={{ $json.data.salary || 0 }}"
                    }
                },
                "options": {}
            },
            "credentials": {}
        },
        {
            "id": "staff-write-result",
            "name": "Return Write Result",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 300],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": "return [{ json: { module: 'staff', action: 'write_staff', success: true } }];"
            }
        },
        # ACTION 1: READ (fallback)
        {
            "id": "staff-read-sheet",
            "name": "Read Staff Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [700, 680],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Staff"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "staff-process",
            "name": "Process Staff Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [920, 680],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Apex Auto Staff Processor --
// Columns: StaffID, Name, Role, Specialty, Status, Mobile, Salary
const rows = $input.all().map(i => i.json);

let presentCount = 0, onLeaveCount = 0, absentCount = 0;
let totalPayroll = 0;
const roleMap = {};

const staff = rows.map(r => {
  const status  = (r['Status'] || r['status'] || 'Present').toString();
  const salary  = parseFloat(r['Salary'] || r['salary'] || 0);
  const role    = r['Role'] || r['role'] || 'Staff';

  if (status === 'Present')  presentCount++;
  if (status === 'On Leave') onLeaveCount++;
  if (status === 'Absent')   absentCount++;
  totalPayroll += salary;

  roleMap[role] = (roleMap[role] || 0) + 1;

  return {
    id:        r['StaffID']   || '—',
    name:      r['Name']      || '—',
    role,
    specialty: r['Specialty'] || '—',
    status,
    mobile:    r['Mobile']    || '—',
    salary
  };
});

const roleBreakdown = Object.entries(roleMap)
  .map(([name, count]) => ({ name, count }))
  .sort((a, b) => b.count - a.count);

return [{
  json: {
    module: 'staff',
    totalStaff: rows.length,
    presentCount, onLeaveCount, absentCount,
    totalPayroll,
    roleBreakdown,
    staff,
    generatedAt: new Date().toISOString()
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
                [{"node": "Write Staff Row",   "type": "main", "index": 0}],
                [{"node": "Read Staff Sheet",  "type": "main", "index": 0}]
            ]
        },
        "Write Staff Row":  {"main": [[{"node": "Return Write Result", "type": "main", "index": 0}]]},
        "Read Staff Sheet": {"main": [[{"node": "Process Staff Data",  "type": "main", "index": 0}]]}
    }
}


# ==============================================================================
# SUB-WORKFLOW 6: ANALYTICS
# Reads Appointments + WorkOrders for trends and charts
# ==============================================================================
ANALYTICS_WORKFLOW = {
    "name": "Apex Auto — Analytics",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "an-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 400],
            "parameters": {}
        },
        {
            "id": "an-read-appts",
            "name": "Read Appointments for Analytics",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 240],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "Appointments"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "an-read-wo",
            "name": "Read Work Orders for Analytics",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 560],
            "parameters": {
                "operation": "read",
                "documentId": {"__rl": True, "mode": "url", "value": SHEET_PLACEHOLDER},
                "sheetName": {"__rl": True, "mode": "name", "value": "WorkOrders"},
                "filtersUI": {},
                "combineFilters": "AND",
                "options": {"headerRow": 1}
            },
            "credentials": {}
        },
        {
            "id": "an-merge",
            "name": "Merge Analytics Sources",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 3,
            "position": [700, 400],
            "parameters": {
                "mode": "combine",
                "combinationMode": "multiplex"
            }
        },
        {
            "id": "an-process",
            "name": "Compute Analytics",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [940, 400],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Apex Auto Analytics Processor --
const all = $input.all().map(i => i.json);

// Separate by data type
const apptRows = all.filter(r => r['ApptID'] || r['apptid'] || r['Status'] && r['Service']);
const woRows   = all.filter(r => r['WOID']   || r['woid']   || r['Mechanic'] || r['mechanic']);

// -- Monthly Revenue Trend (last 6 months from completed work orders) --
const now = new Date();
const monthlyRevenue = {};
for (let i = 5; i >= 0; i--) {
  const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
  const key = d.toLocaleString('default', { month: 'short', year: '2-digit' });
  monthlyRevenue[key] = 0;
}

for (const row of woRows) {
  const status = (row['Status'] || '').toString();
  if (status !== 'Completed') continue;
  const date  = new Date(row['Date'] || row['date'] || '');
  const total = parseFloat(row['Total'] || row['total'] || 0);
  if (!isNaN(date.getTime())) {
    const key = date.toLocaleString('default', { month: 'short', year: '2-digit' });
    if (monthlyRevenue[key] !== undefined) monthlyRevenue[key] += total;
  }
}

const revenueChart = {
  labels: Object.keys(monthlyRevenue),
  values: Object.values(monthlyRevenue)
};

// -- Appointment Status Breakdown --
const apptStatusMap = {};
for (const row of apptRows) {
  const s = row['Status'] || 'Scheduled';
  apptStatusMap[s] = (apptStatusMap[s] || 0) + 1;
}
const apptStatusChart = Object.entries(apptStatusMap)
  .map(([status, count]) => ({ status, count }));

// -- Service Popularity (from appointments) --
const serviceMap = {};
for (const row of apptRows) {
  const svc = row['Service'] || row['service'] || 'Other';
  serviceMap[svc] = (serviceMap[svc] || 0) + 1;
}
const serviceChart = Object.entries(serviceMap)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 6)
  .map(([name, count]) => ({ name, count }));

// -- Work Order Status Breakdown --
const woStatusMap = {};
for (const row of woRows) {
  const s = row['Status'] || 'Open';
  woStatusMap[s] = (woStatusMap[s] || 0) + 1;
}
const woStatusChart = Object.entries(woStatusMap)
  .map(([status, count]) => ({ status, count }));

return [{
  json: {
    module: 'analytics',
    revenueChart,
    apptStatusChart,
    serviceChart,
    woStatusChart,
    totalAppointments: apptRows.length,
    totalWorkOrders:   woRows.length,
    generatedAt: new Date().toISOString()
  }
}];
"""
            }
        }
    ],
    "connections": {
        "When Called by Master": {
            "main": [
                [{"node": "Read Appointments for Analytics", "type": "main", "index": 0}],
                [{"node": "Read Work Orders for Analytics",  "type": "main", "index": 0}]
            ]
        },
        "Read Appointments for Analytics": {"main": [[{"node": "Merge Analytics Sources", "type": "main", "index": 0}]]},
        "Read Work Orders for Analytics":  {"main": [[{"node": "Merge Analytics Sources", "type": "main", "index": 1}]]},
        "Merge Analytics Sources":         {"main": [[{"node": "Compute Analytics",       "type": "main", "index": 0}]]}
    }
}


# ==============================================================================
# HELPER
# ==============================================================================
def create_workflow(workflow_def):
    """POST to n8n API to create a workflow. Returns the created workflow dict."""
    resp = requests.post(
        f"{N8N_URL}/api/v1/workflows",
        headers=HEADERS,
        json=workflow_def,
        timeout=30
    )
    if resp.status_code not in (200, 201):
        print(f"  FAIL ({resp.status_code}): {resp.text[:300]}")
        return None
    return resp.json()


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    created_ids = {}

    # -- Step 1: Create sub-workflows ------------------------------------------
    sub_workflows = [
        ("appointments", APPOINTMENTS_WORKFLOW),
        ("workorders",   WORKORDERS_WORKFLOW),
        ("services",     SERVICES_WORKFLOW),
        ("customers",    CUSTOMERS_WORKFLOW),
        ("staff",        STAFF_WORKFLOW),
        ("analytics",    ANALYTICS_WORKFLOW),
    ]

    print("\n-- Creating sub-workflows --")
    for key, wf_def in sub_workflows:
        print(f"  Creating: {wf_def['name']} ...", end=" ", flush=True)
        result = create_workflow(wf_def)
        if result:
            wf_id = result.get("id") or result.get("data", {}).get("id", "?")
            created_ids[key] = wf_id
            print(f"OK  (id: {wf_id})")
        else:
            print("FAIL")

    # -- Step 2: Build MASTER with real sub-workflow IDs -----------------------
    appt_id     = created_ids.get("appointments", "APPT_WF_ID")
    wo_id       = created_ids.get("workorders",   "WO_WF_ID")
    svc_id      = created_ids.get("services",     "SVC_WF_ID")
    cust_id     = created_ids.get("customers",    "CUST_WF_ID")
    staff_id    = created_ids.get("staff",        "STAFF_WF_ID")
    analytics_id= created_ids.get("analytics",    "ANALYTICS_WF_ID")

    MASTER_WORKFLOW = {
        "name": "Apex Auto Dashboard — MASTER",
        "settings": {
            **SETTINGS,
            "callerPolicy": "any"
        },
        "nodes": [
            # Webhook trigger
            {
                "id": "master-webhook",
                "name": "Dashboard Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 500],
                "webhookId": "apex-auto-dashboard-api",
                "parameters": {
                    "httpMethod": "POST",
                    "path": "apex-auto",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            # Parse all fields from body (pass module, action, data, message, history)
            {
                "id": "master-parse",
                "name": "Parse Request",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 500],
                "parameters": {
                    "mode": "runOnceForEachItem",
                    "jsCode": """
const body    = $json.body || {};
const module  = body.module  || $json.query?.module || 'all';
const action  = body.action  || '';
const data    = body.data    || {};
const message = body.message || '';
const history = body.history || [];
return [{ json: { module, action, data, message, history } }];
"""
                }
            },
            # Router — 6 modules + fallback
            {
                "id": "master-switch",
                "name": "Route by Module",
                "type": "n8n-nodes-base.switch",
                "typeVersion": 3,
                "position": [700, 500],
                "parameters": {
                    "mode": "rules",
                    "options": {},
                    "rules": {
                        "values": [
                            {"conditions": {"options": {"caseSensitive": False, "typeValidation": "strict"}, "combinator": "and", "conditions": [{"id": "m1", "leftValue": "={{ $json.module }}", "rightValue": "appointments", "operator": {"type": "string", "operation": "equals"}}]}},
                            {"conditions": {"options": {"caseSensitive": False, "typeValidation": "strict"}, "combinator": "and", "conditions": [{"id": "m2", "leftValue": "={{ $json.module }}", "rightValue": "workorders",   "operator": {"type": "string", "operation": "equals"}}]}},
                            {"conditions": {"options": {"caseSensitive": False, "typeValidation": "strict"}, "combinator": "and", "conditions": [{"id": "m3", "leftValue": "={{ $json.module }}", "rightValue": "services",     "operator": {"type": "string", "operation": "equals"}}]}},
                            {"conditions": {"options": {"caseSensitive": False, "typeValidation": "strict"}, "combinator": "and", "conditions": [{"id": "m4", "leftValue": "={{ $json.module }}", "rightValue": "customers",    "operator": {"type": "string", "operation": "equals"}}]}},
                            {"conditions": {"options": {"caseSensitive": False, "typeValidation": "strict"}, "combinator": "and", "conditions": [{"id": "m5", "leftValue": "={{ $json.module }}", "rightValue": "staff",        "operator": {"type": "string", "operation": "equals"}}]}},
                            {"conditions": {"options": {"caseSensitive": False, "typeValidation": "strict"}, "combinator": "and", "conditions": [{"id": "m6", "leftValue": "={{ $json.module }}", "rightValue": "analytics",    "operator": {"type": "string", "operation": "equals"}}]}}
                        ]
                    },
                    "fallbackOutput": 6  # index 6 = 'all'
                }
            },
            # Execute sub-workflows (single module paths)
            {"id": "exec-appts",     "name": "Get Appointments Data", "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960,  180], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": appt_id},      "options": {}}},
            {"id": "exec-wo",        "name": "Get Work Orders Data",  "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960,  340], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": wo_id},        "options": {}}},
            {"id": "exec-svc",       "name": "Get Services Data",     "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960,  500], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": svc_id},       "options": {}}},
            {"id": "exec-cust",      "name": "Get Customers Data",    "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960,  660], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": cust_id},      "options": {}}},
            {"id": "exec-staff",     "name": "Get Staff Data",        "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960,  820], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": staff_id},     "options": {}}},
            {"id": "exec-analytics", "name": "Get Analytics Data",    "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960,  980], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": analytics_id}, "options": {}}},
            # "all" path — sequential chain
            {"id": "all-appts",      "name": "All — Get Appointments","type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960, 1160], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": appt_id},      "options": {}}},
            {"id": "all-wo",         "name": "All — Get Work Orders", "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960, 1320], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": wo_id},        "options": {}}},
            {"id": "all-svc",        "name": "All — Get Services",    "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960, 1480], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": svc_id},       "options": {}}},
            {"id": "all-cust",       "name": "All — Get Customers",   "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960, 1640], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": cust_id},      "options": {}}},
            {"id": "all-staff",      "name": "All — Get Staff",       "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960, 1800], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": staff_id},     "options": {}}},
            {"id": "all-analytics",  "name": "All — Get Analytics",   "type": "n8n-nodes-base.executeWorkflow", "typeVersion": 1, "position": [960, 1960], "parameters": {"workflowId": {"__rl": True, "mode": "id", "value": analytics_id}, "options": {}}},
            # Merge all
            {
                "id": "master-merge",
                "name": "Merge All Modules",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1200, 1560],
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": """
const items = $input.all().map(i => i.json);
const result = {};
for (const item of items) {
  if (item.module) result[item.module] = item;
}
return [{ json: { modules: result, generatedAt: new Date().toISOString() } }];
"""
                }
            },
            # Respond
            {
                "id": "master-respond",
                "name": "Respond to Dashboard",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1440, 500],
                "parameters": {
                    "options": {
                        "responseHeaders": {
                            "entries": [
                                {"name": "Access-Control-Allow-Origin", "value": "*"},
                                {"name": "Content-Type", "value": "application/json"}
                            ]
                        }
                    }
                }
            }
        ],
        "connections": {
            "Dashboard Webhook":     {"main": [[{"node": "Parse Request",    "type": "main", "index": 0}]]},
            "Parse Request":         {"main": [[{"node": "Route by Module",  "type": "main", "index": 0}]]},
            "Route by Module": {
                "main": [
                    [{"node": "Get Appointments Data", "type": "main", "index": 0}],
                    [{"node": "Get Work Orders Data",  "type": "main", "index": 0}],
                    [{"node": "Get Services Data",     "type": "main", "index": 0}],
                    [{"node": "Get Customers Data",    "type": "main", "index": 0}],
                    [{"node": "Get Staff Data",        "type": "main", "index": 0}],
                    [{"node": "Get Analytics Data",    "type": "main", "index": 0}],
                    [{"node": "All — Get Appointments","type": "main", "index": 0}]
                ]
            },
            "Get Appointments Data": {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]},
            "Get Work Orders Data":  {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]},
            "Get Services Data":     {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]},
            "Get Customers Data":    {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]},
            "Get Staff Data":        {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]},
            "Get Analytics Data":    {"main": [[{"node": "Respond to Dashboard", "type": "main", "index": 0}]]},
            "All — Get Appointments":{"main": [[{"node": "All — Get Work Orders",  "type": "main", "index": 0}]]},
            "All — Get Work Orders": {"main": [[{"node": "All — Get Services",     "type": "main", "index": 0}]]},
            "All — Get Services":    {"main": [[{"node": "All — Get Customers",    "type": "main", "index": 0}]]},
            "All — Get Customers":   {"main": [[{"node": "All — Get Staff",        "type": "main", "index": 0}]]},
            "All — Get Staff":       {"main": [[{"node": "All — Get Analytics",    "type": "main", "index": 0}]]},
            "All — Get Analytics":   {"main": [[{"node": "Merge All Modules",      "type": "main", "index": 0}]]},
            "Merge All Modules":     {"main": [[{"node": "Respond to Dashboard",   "type": "main", "index": 0}]]}
        }
    }

    print("\n-- Creating Master Workflow --")
    print(f"  Creating: Apex Auto Dashboard — MASTER ...", end=" ", flush=True)
    master_result = create_workflow(MASTER_WORKFLOW)
    if master_result:
        master_id = master_result.get("id") or master_result.get("data", {}).get("id", "?")
        created_ids["master"] = master_id
        print(f"OK  (id: {master_id})")
    else:
        print("FAIL")

    # -- Summary ---------------------------------------------------------------
    print("\n==========================================")
    print("  APEX AUTO — WORKFLOW SUMMARY")
    print("==========================================")
    labels = {
        "appointments": "Apex Auto — Appointments",
        "workorders":   "Apex Auto — Work Orders",
        "services":     "Apex Auto — Services",
        "customers":    "Apex Auto — Customers",
        "staff":        "Apex Auto — Staff",
        "analytics":    "Apex Auto — Analytics",
        "master":       "Apex Auto Dashboard — MASTER"
    }
    for key, label in labels.items():
        wid = created_ids.get(key, "FAILED")
        print(f"  {label:42s}  id: {wid}")

    if "master" in created_ids:
        webhook_url = f"{N8N_URL.rstrip('/')}/webhook/apex-auto"
        print(f"\n  Webhook URL (activate master first):")
        print(f"  {webhook_url}")
        print(f"\n  Test with:")
        print(f'  curl -X POST "{webhook_url}" \\')
        print(f'    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"module":"appointments"}}\'')

    print("\n  NEXT STEPS:")
    print("  1. Go to n8n > Settings > Credentials > New > Google Sheets OAuth2 API")
    print("  2. Create a Google Sheet with tabs: Appointments | WorkOrders | Services | Customers | Staff")
    print("  3. Open each sub-workflow, click the Google Sheets node, add your credential")
    print("  4. Replace PASTE_YOUR_GOOGLE_SHEET_URL_HERE with your sheet URL in each node")
    print("  5. Required column headers per tab:")
    print("       Appointments: ApptID, Customer, Vehicle, Service, Date, Time, Status, Notes")
    print("       WorkOrders:   WOID, Customer, Vehicle, Services, Mechanic, Status, Total, Date")
    print("       Services:     ServiceID, Name, Category, Duration, Price, Description")
    print("       Customers:    CustomerID, Name, Mobile, Email, Vehicles, Visits, LastVisit")
    print("       Staff:        StaffID, Name, Role, Specialty, Status, Mobile, Salary")
    print("  6. Activate the MASTER workflow (toggle at top right in n8n)")
    print("  7. Update CONFIG.webhookUrl in Apex Auto index.html:")
    if "master" in created_ids:
        print(f"       '{webhook_url}'")
    print("==========================================\n")

    return created_ids


if __name__ == "__main__":
    main()
