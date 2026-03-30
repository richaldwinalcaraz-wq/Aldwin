"""
create_hiraya_workflows.py
Creates all n8n backend workflows for the Hiraya Construction Supply Dashboard.

Workflows created:
  1. Hiraya — Sales Data         (sub-workflow)
  2. Hiraya — Inventory Data     (sub-workflow)
  3. Hiraya — HR Data            (sub-workflow)
  4. Hiraya — Analytics          (sub-workflow)
  5. Hiraya Dashboard — MASTER   (main workflow, orchestrates all modules)

After running:
  - Add Google Sheets credentials in n8n (Settings > Credentials > New > Google Sheets OAuth2)
  - Open each sub-workflow and connect credentials + set your spreadsheet ID
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

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

# -- SHARED SETTINGS ------------------------------------------------------------
SETTINGS = {
    "executionOrder": "v1",
    "saveManualExecutions": True,
    "callerPolicy": "workflowsFromSameOwner"
}

# ==============================================================================
# SUB-WORKFLOW 1: SALES DATA
# ==============================================================================
SALES_WORKFLOW = {
    "name": "Hiraya — Sales Data",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "sales-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 300],
            "parameters": {}
        },
        {
            "id": "sales-sheets",
            "name": "Read Sales Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 300],
            "parameters": {
                "operation": "read",
                "documentId": { "__rl": True, "mode": "url", "value": "PASTE_YOUR_GOOGLE_SHEET_URL_HERE" },
                "sheetName": { "__rl": True, "mode": "name", "value": "Sales" },
                "filtersUI": {},
                "combineFilters": "AND",
                "options": { "headerRow": 1 }
            },
            "credentials": {}
        },
        {
            "id": "sales-process",
            "name": "Process Sales Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 300],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Hiraya Sales Data Processor --
// Expects columns: Date, OrderID, Customer, Product, Qty, UnitPrice, Total, Status
const rows = $input.all().map(i => i.json);

const today = new Date();
const thisMonth = today.getMonth();
const thisYear  = today.getFullYear();

let totalRevenue    = 0;
let monthRevenue    = 0;
let totalOrders     = rows.length;
let completedOrders = 0;
let pendingOrders   = 0;
const productMap    = {};

for (const row of rows) {
  const total  = parseFloat(row['Total'] || row['total'] || 0);
  const status = (row['Status'] || row['status'] || '').toString().toLowerCase();
  const date   = new Date(row['Date'] || row['date'] || '');

  totalRevenue += total;

  if (!isNaN(date.getTime()) &&
      date.getMonth() === thisMonth &&
      date.getFullYear() === thisYear) {
    monthRevenue += total;
  }

  if (status === 'completed' || status === 'delivered') completedOrders++;
  if (status === 'pending')                              pendingOrders++;

  const product = row['Product'] || row['product'] || 'Unknown';
  productMap[product] = (productMap[product] || 0) + total;
}

// Top 5 products by revenue
const topProducts = Object.entries(productMap)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 5)
  .map(([name, revenue]) => ({ name, revenue }));

// Recent 10 orders (last rows)
const recentOrders = rows.slice(-10).reverse().map(r => ({
  id:       r['OrderID']  || r['orderid']  || r['Order ID'] || '—',
  customer: r['Customer'] || r['customer'] || '—',
  product:  r['Product']  || r['product']  || '—',
  total:    parseFloat(r['Total'] || r['total'] || 0),
  status:   r['Status']   || r['status']   || '—',
  date:     r['Date']     || r['date']     || '—'
}));

return [{
  json: {
    module:        'sales',
    totalRevenue,
    monthRevenue,
    totalOrders,
    completedOrders,
    pendingOrders,
    topProducts,
    recentOrders,
    generatedAt: new Date().toISOString()
  }
}];
"""
            }
        }
    ],
    "connections": {
        "When Called by Master": {
            "main": [[{ "node": "Read Sales Sheet", "type": "main", "index": 0 }]]
        },
        "Read Sales Sheet": {
            "main": [[{ "node": "Process Sales Data", "type": "main", "index": 0 }]]
        }
    }
}

# ==============================================================================
# SUB-WORKFLOW 2: INVENTORY DATA
# ==============================================================================
INVENTORY_WORKFLOW = {
    "name": "Hiraya — Inventory Data",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "inv-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 300],
            "parameters": {}
        },
        {
            "id": "inv-sheets",
            "name": "Read Inventory Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 300],
            "parameters": {
                "operation": "read",
                "documentId": { "__rl": True, "mode": "url", "value": "PASTE_YOUR_GOOGLE_SHEET_URL_HERE" },
                "sheetName": { "__rl": True, "mode": "name", "value": "Inventory" },
                "filtersUI": {},
                "combineFilters": "AND",
                "options": { "headerRow": 1 }
            },
            "credentials": {}
        },
        {
            "id": "inv-process",
            "name": "Process Inventory Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 300],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Hiraya Inventory Data Processor --
// Expects columns: SKU, ProductName, Category, Stock, ReorderLevel, UnitCost, Supplier, Status
const rows = $input.all().map(i => i.json);

let totalItems   = rows.length;
let totalValue   = 0;
let lowStock     = [];
let outOfStock   = [];
const categories = {};

for (const row of rows) {
  const stock  = parseInt(row['Stock']        || row['stock']        || 0);
  const reorder= parseInt(row['ReorderLevel'] || row['reorderlevel'] || row['Reorder Level'] || 5);
  const cost   = parseFloat(row['UnitCost']   || row['unitcost']     || row['Unit Cost']    || 0);
  const cat    = row['Category']   || row['category']   || 'Uncategorized';
  const name   = row['ProductName']|| row['productname']|| row['Product Name'] || '—';
  const sku    = row['SKU']        || row['sku']        || '—';

  totalValue += stock * cost;

  categories[cat] = (categories[cat] || 0) + 1;

  if (stock === 0) {
    outOfStock.push({ sku, name, category: cat, stock });
  } else if (stock <= reorder) {
    lowStock.push({ sku, name, category: cat, stock, reorder });
  }
}

const categoryBreakdown = Object.entries(categories)
  .map(([name, count]) => ({ name, count }))
  .sort((a, b) => b.count - a.count);

// All items for the inventory table
const items = rows.map(r => ({
  sku:      r['SKU']         || r['sku']         || '—',
  name:     r['ProductName'] || r['Product Name']|| '—',
  category: r['Category']    || r['category']    || '—',
  stock:    parseInt(r['Stock'] || 0),
  reorder:  parseInt(r['ReorderLevel'] || r['Reorder Level'] || 5),
  cost:     parseFloat(r['UnitCost'] || r['Unit Cost'] || 0),
  supplier: r['Supplier']    || r['supplier']    || '—',
  status:   r['Status']      || r['status']      || '—'
}));

return [{
  json: {
    module: 'inventory',
    totalItems,
    totalValue,
    lowStockCount:   lowStock.length,
    outOfStockCount: outOfStock.length,
    lowStock,
    outOfStock,
    categoryBreakdown,
    items,
    generatedAt: new Date().toISOString()
  }
}];
"""
            }
        }
    ],
    "connections": {
        "When Called by Master": {
            "main": [[{ "node": "Read Inventory Sheet", "type": "main", "index": 0 }]]
        },
        "Read Inventory Sheet": {
            "main": [[{ "node": "Process Inventory Data", "type": "main", "index": 0 }]]
        }
    }
}

# ==============================================================================
# SUB-WORKFLOW 3: HR DATA
# ==============================================================================
HR_WORKFLOW = {
    "name": "Hiraya — HR Data",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "hr-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 300],
            "parameters": {}
        },
        {
            "id": "hr-sheets",
            "name": "Read HR Sheet",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 300],
            "parameters": {
                "operation": "read",
                "documentId": { "__rl": True, "mode": "url", "value": "PASTE_YOUR_GOOGLE_SHEET_URL_HERE" },
                "sheetName": { "__rl": True, "mode": "name", "value": "HR" },
                "filtersUI": {},
                "combineFilters": "AND",
                "options": { "headerRow": 1 }
            },
            "credentials": {}
        },
        {
            "id": "hr-process",
            "name": "Process HR Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 300],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Hiraya HR Data Processor --
// Expects columns: EmployeeID, Name, Position, Status, LeaveBalance, Salary,
//                  Mobile, Email, EmergencyName, EmergencyRelation, EmergencyMobile
const rows = $input.all().map(i => i.json);

let totalEmployees = rows.length;
let presentCount   = 0;
let onLeaveCount   = 0;
let absentCount    = 0;
let totalPayroll   = 0;
const positions    = {};

const employees = rows.map(r => {
  const status = (r['Status'] || r['status'] || 'Present').toString();
  const salary = parseFloat(r['Salary'] || r['salary'] || 0);

  if (status === 'Present')  presentCount++;
  if (status === 'On Leave') onLeaveCount++;
  if (status === 'Absent')   absentCount++;

  totalPayroll += salary;

  const pos = r['Position'] || r['position'] || 'Staff';
  positions[pos] = (positions[pos] || 0) + 1;

  return {
    id:       r['EmployeeID']    || r['employeeid']    || r['Employee ID']    || '—',
    name:     r['Name']          || r['name']          || '—',
    position: pos,
    status,
    leave:    parseInt(r['LeaveBalance'] || r['leavelance'] || r['Leave Balance'] || 0),
    salary,
    mobile:   r['Mobile']        || r['mobile']        || '—',
    email:    r['Email']         || r['email']         || '—',
    ecName:   r['EmergencyName'] || r['Emergency Name']|| '—',
    ecRel:    r['EmergencyRelation'] || r['Emergency Relation'] || '—',
    ecMobile: r['EmergencyMobile']   || r['Emergency Mobile']   || '—'
  };
});

const positionBreakdown = Object.entries(positions)
  .map(([name, count]) => ({ name, count }))
  .sort((a, b) => b.count - a.count);

return [{
  json: {
    module: 'hr',
    totalEmployees,
    presentCount,
    onLeaveCount,
    absentCount,
    totalPayroll,
    positionBreakdown,
    employees,
    generatedAt: new Date().toISOString()
  }
}];
"""
            }
        }
    ],
    "connections": {
        "When Called by Master": {
            "main": [[{ "node": "Read HR Sheet", "type": "main", "index": 0 }]]
        },
        "Read HR Sheet": {
            "main": [[{ "node": "Process HR Data", "type": "main", "index": 0 }]]
        }
    }
}

# ==============================================================================
# SUB-WORKFLOW 4: ANALYTICS
# ==============================================================================
ANALYTICS_WORKFLOW = {
    "name": "Hiraya — Analytics",
    "settings": SETTINGS,
    "nodes": [
        {
            "id": "analytics-trigger",
            "name": "When Called by Master",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [240, 300],
            "parameters": {}
        },
        {
            "id": "analytics-sales",
            "name": "Read Sales for Analytics",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 200],
            "parameters": {
                "operation": "read",
                "documentId": { "__rl": True, "mode": "url", "value": "PASTE_YOUR_GOOGLE_SHEET_URL_HERE" },
                "sheetName": { "__rl": True, "mode": "name", "value": "Sales" },
                "filtersUI": {},
                "combineFilters": "AND",
                "options": { "headerRow": 1 }
            },
            "credentials": {}
        },
        {
            "id": "analytics-inv",
            "name": "Read Inventory for Analytics",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4,
            "position": [460, 400],
            "parameters": {
                "operation": "read",
                "documentId": { "__rl": True, "mode": "url", "value": "PASTE_YOUR_GOOGLE_SHEET_URL_HERE" },
                "sheetName": { "__rl": True, "mode": "name", "value": "Inventory" },
                "filtersUI": {},
                "combineFilters": "AND",
                "options": { "headerRow": 1 }
            },
            "credentials": {}
        },
        {
            "id": "analytics-merge",
            "name": "Merge Data Sources",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 3,
            "position": [680, 300],
            "parameters": {
                "mode": "combine",
                "combinationMode": "multiplex"
            }
        },
        {
            "id": "analytics-process",
            "name": "Compute Analytics",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 300],
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": """
// -- Hiraya Analytics Processor --
// Computes monthly trends, revenue vs inventory value, top performers
const all = $input.all().map(i => i.json);

// Separate sales vs inventory rows by detecting columns
const salesRows = all.filter(r => r['Total'] || r['total'] || r['OrderID'] || r['orderid']);
const invRows   = all.filter(r => r['Stock'] || r['stock'] || r['SKU']   || r['sku']);

// -- Monthly Revenue Trend (last 6 months) --
const now = new Date();
const monthlyRevenue = {};
for (let i = 5; i >= 0; i--) {
  const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
  const key = d.toLocaleString('default', { month: 'short', year: '2-digit' });
  monthlyRevenue[key] = 0;
}

for (const row of salesRows) {
  const date  = new Date(row['Date'] || row['date'] || '');
  const total = parseFloat(row['Total'] || row['total'] || 0);
  if (!isNaN(date.getTime())) {
    const key = date.toLocaleString('default', { month: 'short', year: '2-digit' });
    if (monthlyRevenue[key] !== undefined) {
      monthlyRevenue[key] += total;
    }
  }
}

const revenueChart = {
  labels: Object.keys(monthlyRevenue),
  values: Object.values(monthlyRevenue)
};

// -- Inventory Health --
let inventoryValue = 0;
let stockOk = 0, stockLow = 0, stockOut = 0;
for (const row of invRows) {
  const stock  = parseInt(row['Stock'] || 0);
  const cost   = parseFloat(row['UnitCost'] || row['Unit Cost'] || 0);
  const reorder= parseInt(row['ReorderLevel'] || row['Reorder Level'] || 5);
  inventoryValue += stock * cost;
  if (stock === 0)          stockOut++;
  else if (stock <= reorder) stockLow++;
  else                       stockOk++;
}

const inventoryHealth = { stockOk, stockLow, stockOut, totalValue: inventoryValue };

// -- Sales by Status --
const statusMap = {};
for (const row of salesRows) {
  const s = row['Status'] || row['status'] || 'Unknown';
  statusMap[s] = (statusMap[s] || 0) + 1;
}

return [{
  json: {
    module: 'analytics',
    revenueChart,
    inventoryHealth,
    salesByStatus: Object.entries(statusMap).map(([status, count]) => ({ status, count })),
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
                [{ "node": "Read Sales for Analytics", "type": "main", "index": 0 }],
                [{ "node": "Read Inventory for Analytics", "type": "main", "index": 0 }]
            ]
        },
        "Read Sales for Analytics": {
            "main": [[{ "node": "Merge Data Sources", "type": "main", "index": 0 }]]
        },
        "Read Inventory for Analytics": {
            "main": [[{ "node": "Merge Data Sources", "type": "main", "index": 1 }]]
        },
        "Merge Data Sources": {
            "main": [[{ "node": "Compute Analytics", "type": "main", "index": 0 }]]
        }
    }
}


def create_workflow(workflow_def):
    """POST to n8n API to create a workflow. Returns the created workflow dict."""
    resp = requests.post(
        f"{N8N_URL}/api/v1/workflows",
        headers=HEADERS,
        json=workflow_def,
        timeout=30
    )
    if resp.status_code not in (200, 201):
        print(f"  FAIL Failed ({resp.status_code}): {resp.text[:300]}")
        return None
    return resp.json()


def main():
    created_ids = {}

    # -- Step 1: Create sub-workflows -----------------------------------------
    sub_workflows = [
        ("sales",     SALES_WORKFLOW),
        ("inventory", INVENTORY_WORKFLOW),
        ("hr",        HR_WORKFLOW),
        ("analytics", ANALYTICS_WORKFLOW),
    ]

    print("\n-- Creating sub-workflows --")
    for key, wf_def in sub_workflows:
        print(f"  Creating: {wf_def['name']} ...", end=" ")
        result = create_workflow(wf_def)
        if result:
            wf_id = result.get("id") or result.get("data", {}).get("id", "?")
            created_ids[key] = wf_id
            print(f"OK  (id: {wf_id})")
        else:
            print("FAIL")

    # -- Step 2: Build Master Workflow using sub-workflow IDs ------------------
    sales_id     = created_ids.get("sales",     "SALES_WF_ID")
    inventory_id = created_ids.get("inventory", "INVENTORY_WF_ID")
    hr_id        = created_ids.get("hr",        "HR_WF_ID")
    analytics_id = created_ids.get("analytics", "ANALYTICS_WF_ID")

    MASTER_WORKFLOW = {
        "name": "Hiraya Dashboard — MASTER",
        "settings": {
            **SETTINGS,
            "callerPolicy": "any"  # allow external webhook calls
        },
        "nodes": [
            # -- Trigger: Webhook ----------------------------------------------
            {
                "id": "master-webhook",
                "name": "Dashboard Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 400],
                "webhookId": "hiraya-dashboard-api",
                "parameters": {
                    "httpMethod": "POST",
                    "path": "hiraya-dashboard",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            # -- CORS header for browser fetch ---------------------------------
            {
                "id": "master-cors",
                "name": "Set CORS Headers",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [440, 400],
                "parameters": {
                    "mode": "runOnceForEachItem",
                    "jsCode": """
// Pass through, just read the requested module
const module = $json.body?.module || $json.query?.module || 'all';
return [{ json: { module } }];
"""
                }
            },
            # -- Router: Switch by module --------------------------------------
            {
                "id": "master-switch",
                "name": "Route by Module",
                "type": "n8n-nodes-base.switch",
                "typeVersion": 3,
                "position": [660, 400],
                "parameters": {
                    "mode": "rules",
                    "options": {},
                    "rules": {
                        "values": [
                            { "conditions": { "options": { "caseSensitive": False, "leftValue": "", "typeValidation": "strict" }, "combinator": "and", "conditions": [{ "id": "r1", "leftValue": "={{ $json.module }}", "rightValue": "sales", "operator": { "type": "string", "operation": "equals" } }] } },
                            { "conditions": { "options": { "caseSensitive": False, "leftValue": "", "typeValidation": "strict" }, "combinator": "and", "conditions": [{ "id": "r2", "leftValue": "={{ $json.module }}", "rightValue": "inventory", "operator": { "type": "string", "operation": "equals" } }] } },
                            { "conditions": { "options": { "caseSensitive": False, "leftValue": "", "typeValidation": "strict" }, "combinator": "and", "conditions": [{ "id": "r3", "leftValue": "={{ $json.module }}", "rightValue": "hr", "operator": { "type": "string", "operation": "equals" } }] } },
                            { "conditions": { "options": { "caseSensitive": False, "leftValue": "", "typeValidation": "strict" }, "combinator": "and", "conditions": [{ "id": "r4", "leftValue": "={{ $json.module }}", "rightValue": "analytics", "operator": { "type": "string", "operation": "equals" } }] } }
                        ]
                    },
                    "fallbackOutput": 4  # 'all' — output index 4
                }
            },
            # -- Execute Sub-Workflows -----------------------------------------
            {
                "id": "master-exec-sales",
                "name": "Get Sales Data",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 140],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": sales_id },
                    "options": {}
                }
            },
            {
                "id": "master-exec-inv",
                "name": "Get Inventory Data",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 300],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": inventory_id },
                    "options": {}
                }
            },
            {
                "id": "master-exec-hr",
                "name": "Get HR Data",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 460],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": hr_id },
                    "options": {}
                }
            },
            {
                "id": "master-exec-analytics",
                "name": "Get Analytics Data",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 620],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": analytics_id },
                    "options": {}
                }
            },
            # -- "all" path: call all 4 in parallel then merge -----------------
            {
                "id": "master-all-sales",
                "name": "All — Get Sales",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 820],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": sales_id },
                    "options": {}
                }
            },
            {
                "id": "master-all-inv",
                "name": "All — Get Inventory",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 980],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": inventory_id },
                    "options": {}
                }
            },
            {
                "id": "master-all-hr",
                "name": "All — Get HR",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 1140],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": hr_id },
                    "options": {}
                }
            },
            {
                "id": "master-all-analytics",
                "name": "All — Get Analytics",
                "type": "n8n-nodes-base.executeWorkflow",
                "typeVersion": 1,
                "position": [900, 1300],
                "parameters": {
                    "workflowId": { "__rl": True, "mode": "id", "value": analytics_id },
                    "options": {}
                }
            },
            # -- Merge "all" results --------------------------------------------
            {
                "id": "master-merge",
                "name": "Merge All Modules",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1120, 1060],
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
            # -- Respond to Webhook ---------------------------------------------
            {
                "id": "master-respond",
                "name": "Respond to Dashboard",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1340, 400],
                "parameters": {
                    "options": {
                        "responseHeaders": {
                            "entries": [
                                { "name": "Access-Control-Allow-Origin", "value": "*" },
                                { "name": "Content-Type", "value": "application/json" }
                            ]
                        }
                    }
                }
            }
        ],
        "connections": {
            "Dashboard Webhook": {
                "main": [[{ "node": "Set CORS Headers", "type": "main", "index": 0 }]]
            },
            "Set CORS Headers": {
                "main": [[{ "node": "Route by Module", "type": "main", "index": 0 }]]
            },
            "Route by Module": {
                "main": [
                    [{ "node": "Get Sales Data",     "type": "main", "index": 0 }],
                    [{ "node": "Get Inventory Data", "type": "main", "index": 0 }],
                    [{ "node": "Get HR Data",        "type": "main", "index": 0 }],
                    [{ "node": "Get Analytics Data", "type": "main", "index": 0 }],
                    [{ "node": "All — Get Sales",    "type": "main", "index": 0 }]
                ]
            },
            "Get Sales Data":     { "main": [[{ "node": "Respond to Dashboard", "type": "main", "index": 0 }]] },
            "Get Inventory Data": { "main": [[{ "node": "Respond to Dashboard", "type": "main", "index": 0 }]] },
            "Get HR Data":        { "main": [[{ "node": "Respond to Dashboard", "type": "main", "index": 0 }]] },
            "Get Analytics Data": { "main": [[{ "node": "Respond to Dashboard", "type": "main", "index": 0 }]] },
            "All — Get Sales":    { "main": [[{ "node": "All — Get Inventory", "type": "main", "index": 0 }]] },
            "All — Get Inventory":{ "main": [[{ "node": "All — Get HR",        "type": "main", "index": 0 }]] },
            "All — Get HR":       { "main": [[{ "node": "All — Get Analytics", "type": "main", "index": 0 }]] },
            "All — Get Analytics":{ "main": [[{ "node": "Merge All Modules",   "type": "main", "index": 0 }]] },
            "Merge All Modules":  { "main": [[{ "node": "Respond to Dashboard", "type": "main", "index": 0 }]] }
        }
    }

    print("\n-- Creating Master Workflow --")
    print(f"  Creating: Hiraya Dashboard — MASTER ...", end=" ")
    master_result = create_workflow(MASTER_WORKFLOW)
    if master_result:
        master_id = master_result.get("id") or master_result.get("data", {}).get("id", "?")
        print(f"OK  (id: {master_id})")
        created_ids["master"] = master_id
    else:
        print("FAIL")

    # -- Summary ---------------------------------------------------------------
    print("\n==========================================")
    print("  HIRAYA DASHBOARD — WORKFLOW SUMMARY")
    print("==========================================")
    labels = {
        "sales":     "Hiraya — Sales Data",
        "inventory": "Hiraya — Inventory Data",
        "hr":        "Hiraya — HR Data",
        "analytics": "Hiraya — Analytics",
        "master":    "Hiraya Dashboard — MASTER"
    }
    for key, label in labels.items():
        wid = created_ids.get(key, "FAILED")
        print(f"  {label:40s}  id: {wid}")

    if "master" in created_ids:
        webhook_url = f"{N8N_URL}/webhook/hiraya-dashboard"
        print(f"\n  Webhook URL (activate master first):")
        print(f"  {webhook_url}")
        print(f"\n  Test with:")
        print(f'  curl -X POST "{webhook_url}" -H "Content-Type: application/json" -d \'{{"module":"all"}}\'')

    print("\n  NEXT STEPS:")
    print("  1. Go to n8n > Settings > Credentials > New > Google Sheets OAuth2 API")
    print("  2. Open each sub-workflow, click the Google Sheets node, add your credential")
    print("  3. Set the spreadsheet URL (same Google Sheet, different sheet tabs)")
    print("  4. Required sheet tab names: Sales | Inventory | HR")
    print("  5. Activate the Master workflow (toggle at top right in n8n)")
    print("  6. Dashboard will call: POST /webhook/hiraya-dashboard  body: {module:'all'}")
    print("==========================================\n")

    return created_ids


if __name__ == "__main__":
    main()
