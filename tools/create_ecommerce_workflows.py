#!/usr/bin/env python3
"""
create_ecommerce_workflows.py  —  NexaShop E-Commerce Dashboard
Deploys 7 n8n workflows:
  1. NexaShop — Orders
  2. NexaShop — Products
  3. NexaShop — Customers
  4. NexaShop — Inventory
  5. NexaShop — Marketing
  6. NexaShop — Analytics
  7. NexaShop Dashboard — MASTER

Run: python -X utf8 tools/create_ecommerce_workflows.py

Google Sheet tab names required:
  Orders | Products | Customers | Inventory | Marketing

Column headers:
  Orders:    OrderID, CustomerName, CustomerEmail, Items, Subtotal, Total,
             Status, PaymentMethod, ShippingAddress, Date, Notes
  Products:  ProductID, Name, SKU, Category, Price, CostPrice, Stock,
             ReorderLevel, Description, Status
  Customers: CustomerID, Name, Email, Mobile, TotalOrders, TotalSpent,
             LastOrderDate, Tier, Address, Notes
  Inventory: SKU, ProductName, Category, CurrentStock, ReorderLevel,
             UnitCost, Supplier, LastRestocked
  Marketing: CampaignID, Name, Type, Status, DiscountType, DiscountValue,
             Code, Budget, Spent, Conversions, StartDate, EndDate,
             UsageLimit, UsageCount
"""

import json
import os
import sys
import requests

# ── credentials ───────────────────────────────────────────────────────────────
_cfg_path = os.path.join(os.path.dirname(__file__), '..', '.mcp.json')
try:
    with open(_cfg_path) as f:
        _cfg = json.load(f)
except FileNotFoundError:
    sys.exit(f'ERROR: .mcp.json not found at {_cfg_path}')

N8N_URL  = _cfg['mcpServers']['n8n-mcp']['env']['N8N_API_URL']
API_KEY  = _cfg['mcpServers']['n8n-mcp']['env']['N8N_API_KEY']
HEADERS  = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

# ── replace before running ────────────────────────────────────────────────────
SHEET_URL     = 'PASTE_YOUR_GOOGLE_SHEET_URL_HERE'
WEBHOOK_PATH  = 'nexashop-dashboard'

# ── helper ────────────────────────────────────────────────────────────────────
def create_workflow(payload):
    r = requests.post(f'{N8N_URL}/api/v1/workflows', headers=HEADERS, json=payload)
    if not r.ok:
        print(f'  ERROR {r.status_code}: {r.text[:300]}')
        r.raise_for_status()
    wf = r.json()
    print(f'  created  {wf["name"]}  (ID: {wf["id"]})')
    return wf['id']

def gsheet_cred():
    return {'id': '', 'name': 'Google Sheets OAuth2 API', 'type': 'oAuth2'}

# ── generic sub-workflow builder ──────────────────────────────────────────────
def build_sub_workflow(name, sheet_tab, read_key, read_code, write_code):
    """Trigger → Switch(read/write) → GSheets read/append → Code → return."""
    return {
        'name': name,
        'nodes': [
            {
                'id': 'trigger', 'name': 'Workflow Trigger',
                'type': 'n8n-nodes-base.executeWorkflowTrigger',
                'typeVersion': 1, 'position': [0, 200], 'parameters': {}
            },
            {
                'id': 'router', 'name': 'Action Router',
                'type': 'n8n-nodes-base.switch',
                'typeVersion': 3, 'position': [240, 200],
                'parameters': {
                    'mode': 'rules',
                    'rules': {
                        'values': [
                            {
                                'conditions': {
                                    'options': {'caseSensitive': False, 'typeValidation': 'strict'},
                                    'conditions': [{'leftValue': '={{ $json.action }}',
                                                    'rightValue': f'read_{read_key}',
                                                    'operator': {'type': 'string', 'operation': 'startsWith'}}],
                                    'combinator': 'and'
                                },
                                'renameOutput': True, 'outputKey': 'read'
                            },
                            {
                                'conditions': {
                                    'options': {'caseSensitive': False, 'typeValidation': 'strict'},
                                    'conditions': [{'leftValue': '={{ $json.action }}',
                                                    'rightValue': f'write_{read_key}',
                                                    'operator': {'type': 'string', 'operation': 'startsWith'}}],
                                    'combinator': 'and'
                                },
                                'renameOutput': True, 'outputKey': 'write'
                            }
                        ]
                    },
                    'options': {}
                }
            },
            {
                'id': 'read_sheet', 'name': 'Read Sheet',
                'type': 'n8n-nodes-base.googleSheets',
                'typeVersion': 4, 'position': [480, 80],
                'credentials': {'googleSheetsOAuth2Api': gsheet_cred()},
                'parameters': {
                    'operation': 'read',
                    'documentId': {'__rl': True, 'value': SHEET_URL, 'mode': 'url'},
                    'sheetName': {'__rl': True, 'value': sheet_tab, 'mode': 'name'},
                    'filtersUI': {}, 'combineFilters': 'AND', 'options': {}
                }
            },
            {
                'id': 'process', 'name': 'Process Data',
                'type': 'n8n-nodes-base.code',
                'typeVersion': 2, 'position': [720, 80],
                'parameters': {'mode': 'runOnceForAllItems', 'jsCode': read_code}
            },
            {
                'id': 'append_sheet', 'name': 'Append Row',
                'type': 'n8n-nodes-base.googleSheets',
                'typeVersion': 4, 'position': [480, 320],
                'credentials': {'googleSheetsOAuth2Api': gsheet_cred()},
                'parameters': {
                    'operation': 'append',
                    'documentId': {'__rl': True, 'value': SHEET_URL, 'mode': 'url'},
                    'sheetName': {'__rl': True, 'value': sheet_tab, 'mode': 'name'},
                    'columns': {
                        'mappingMode': 'autoMapInputData',
                        'value': {}, 'matchingColumns': [], 'schema': []
                    },
                    'options': {}
                }
            },
            {
                'id': 'write_result', 'name': 'Write Result',
                'type': 'n8n-nodes-base.code',
                'typeVersion': 2, 'position': [720, 320],
                'parameters': {'mode': 'runOnceForAllItems', 'jsCode': write_code}
            }
        ],
        'connections': {
            'Workflow Trigger': {'main': [[{'node': 'Action Router', 'type': 'main', 'index': 0}]]},
            'Action Router': {
                'main': [
                    [{'node': 'Read Sheet', 'type': 'main', 'index': 0}],
                    [{'node': 'Append Row', 'type': 'main', 'index': 0}]
                ]
            },
            'Read Sheet':   {'main': [[{'node': 'Process Data', 'type': 'main', 'index': 0}]]},
            'Append Row':   {'main': [[{'node': 'Write Result', 'type': 'main', 'index': 0}]]}
        },
        'settings': {'executionOrder': 'v1'}
    }

# ── per-module code ───────────────────────────────────────────────────────────

ORDERS_READ = r"""
const rows = $input.all().map(i => i.json);
const orders = rows.filter(r => r.OrderID).map(r => ({
  id: r.OrderID,
  customer: r.CustomerName || '',
  email: r.CustomerEmail || '',
  items: (() => { try { return JSON.parse(r.Items || '[]'); } catch(e) { return []; } })(),
  subtotal: parseFloat(r.Subtotal || 0),
  total: parseFloat(r.Total || 0),
  status: (r.Status || 'pending').toLowerCase(),
  payment: r.PaymentMethod || '',
  shipping: r.ShippingAddress || '',
  date: r.Date || '',
  notes: r.Notes || ''
}));
return [{ json: { orders, count: orders.length } }];
"""

ORDERS_WRITE = "return [{ json: { success: true, action: 'order_saved' } }];"

PRODUCTS_READ = r"""
const rows = $input.all().map(i => i.json);
const products = rows.filter(r => r.ProductID).map(r => ({
  id: r.ProductID,
  name: r.Name || '',
  sku: r.SKU || '',
  category: r.Category || '',
  price: parseFloat(r.Price || 0),
  cost: parseFloat(r.CostPrice || 0),
  stock: parseInt(r.Stock || 0),
  reorder: parseInt(r.ReorderLevel || 5),
  description: r.Description || '',
  status: (r.Status || 'active').toLowerCase()
}));
return [{ json: { products, count: products.length } }];
"""

PRODUCTS_WRITE = "return [{ json: { success: true, action: 'product_saved' } }];"

CUSTOMERS_READ = r"""
const rows = $input.all().map(i => i.json);
const customers = rows.filter(r => r.CustomerID).map(r => ({
  id: r.CustomerID,
  name: r.Name || '',
  email: r.Email || '',
  mobile: r.Mobile || '',
  orders: parseInt(r.TotalOrders || 0),
  spent: parseFloat(r.TotalSpent || 0),
  lastOrder: r.LastOrderDate || '',
  tier: r.Tier || 'New',
  address: r.Address || '',
  notes: r.Notes || ''
}));
return [{ json: { customers, count: customers.length } }];
"""

CUSTOMERS_WRITE = "return [{ json: { success: true, action: 'customer_saved' } }];"

INVENTORY_READ = r"""
const rows = $input.all().map(i => i.json);
const inventory = rows.filter(r => r.SKU).map(r => ({
  sku: r.SKU,
  product: r.ProductName || '',
  category: r.Category || '',
  stock: parseInt(r.CurrentStock || 0),
  reorder: parseInt(r.ReorderLevel || 5),
  cost: parseFloat(r.UnitCost || 0),
  supplier: r.Supplier || '',
  lastRestocked: r.LastRestocked || '',
  status: parseInt(r.CurrentStock || 0) === 0 ? 'out'
        : parseInt(r.CurrentStock || 0) <= parseInt(r.ReorderLevel || 5) ? 'low'
        : 'ok'
}));
const lowStockCount = inventory.filter(i => i.status !== 'ok').length;
return [{ json: { inventory, count: inventory.length, lowStockCount } }];
"""

INVENTORY_WRITE = "return [{ json: { success: true, action: 'inventory_updated' } }];"

MARKETING_READ = r"""
const rows = $input.all().map(i => i.json);
const items = rows.filter(r => r.CampaignID).map(r => ({
  id: r.CampaignID,
  name: r.Name || '',
  type: r.Type || 'campaign',
  status: (r.Status || 'draft').toLowerCase(),
  discountType: r.DiscountType || 'percent',
  discountValue: parseFloat(r.DiscountValue || 0),
  code: r.Code || '',
  budget: parseFloat(r.Budget || 0),
  spent: parseFloat(r.Spent || 0),
  conversions: parseInt(r.Conversions || 0),
  startDate: r.StartDate || '',
  endDate: r.EndDate || '',
  usageLimit: parseInt(r.UsageLimit || 0),
  usageCount: parseInt(r.UsageCount || 0)
}));
const campaigns = items.filter(i => i.type === 'campaign');
const discounts  = items.filter(i => i.type === 'discount');
return [{ json: { campaigns, discounts, count: items.length } }];
"""

MARKETING_WRITE = "return [{ json: { success: true, action: 'marketing_saved' } }];"

# ── analytics workflow (reads two sheets) ─────────────────────────────────────
def build_analytics_workflow():
    code = r"""
const ordersData   = ($('Read Orders').all()   || []).map(i => i.json).filter(r => r.OrderID);
const productsData = ($('Read Products').all() || []).map(i => i.json).filter(r => r.ProductID);

// Monthly revenue (last 6 months)
const monthlyRev = {};
ordersData.forEach(o => {
  const m = (o.Date || '').substring(0, 7);
  if (m) monthlyRev[m] = (monthlyRev[m] || 0) + parseFloat(o.Total || 0);
});
const months = Object.keys(monthlyRev).sort().slice(-6);

// Orders by status
const statusCounts = {};
ordersData.forEach(o => {
  const s = o.Status || 'Pending';
  statusCounts[s] = (statusCounts[s] || 0) + 1;
});

// Top products by units sold
const prodSales = {};
ordersData.forEach(o => {
  let items = [];
  try { items = JSON.parse(o.Items || '[]'); } catch(e) {}
  items.forEach(item => {
    prodSales[item.name] = (prodSales[item.name] || 0) + (parseInt(item.qty) || 1);
  });
});
const topProds = Object.entries(prodSales).sort((a, b) => b[1] - a[1]).slice(0, 5);

// Totals
const totalRevenue  = ordersData.reduce((s, o) => s + parseFloat(o.Total || 0), 0);
const totalOrders   = ordersData.length;
const avgOrderValue = totalOrders ? totalRevenue / totalOrders : 0;
const lowStockCount = productsData.filter(p =>
  parseInt(p.Stock || 0) <= parseInt(p.ReorderLevel || 5)
).length;

return [{ json: {
  summary: { totalRevenue, totalOrders, avgOrderValue, lowStockCount },
  revenueChart: {
    labels: months,
    values: months.map(m => parseFloat((monthlyRev[m] || 0).toFixed(2)))
  },
  statusChart: {
    labels: Object.keys(statusCounts),
    values: Object.values(statusCounts)
  },
  topProducts: topProds.map(([name, qty]) => ({ name, qty }))
}}];
"""
    return {
        'name': 'NexaShop — Analytics',
        'nodes': [
            {
                'id': 'trigger', 'name': 'Workflow Trigger',
                'type': 'n8n-nodes-base.executeWorkflowTrigger',
                'typeVersion': 1, 'position': [0, 200], 'parameters': {}
            },
            {
                'id': 'read_orders', 'name': 'Read Orders',
                'type': 'n8n-nodes-base.googleSheets',
                'typeVersion': 4, 'position': [240, 80],
                'credentials': {'googleSheetsOAuth2Api': gsheet_cred()},
                'parameters': {
                    'operation': 'read',
                    'documentId': {'__rl': True, 'value': SHEET_URL, 'mode': 'url'},
                    'sheetName': {'__rl': True, 'value': 'Orders', 'mode': 'name'},
                    'filtersUI': {}, 'combineFilters': 'AND', 'options': {}
                }
            },
            {
                'id': 'read_products', 'name': 'Read Products',
                'type': 'n8n-nodes-base.googleSheets',
                'typeVersion': 4, 'position': [240, 320],
                'credentials': {'googleSheetsOAuth2Api': gsheet_cred()},
                'parameters': {
                    'operation': 'read',
                    'documentId': {'__rl': True, 'value': SHEET_URL, 'mode': 'url'},
                    'sheetName': {'__rl': True, 'value': 'Products', 'mode': 'name'},
                    'filtersUI': {}, 'combineFilters': 'AND', 'options': {}
                }
            },
            {
                'id': 'compute', 'name': 'Compute Analytics',
                'type': 'n8n-nodes-base.code',
                'typeVersion': 2, 'position': [500, 200],
                'parameters': {'mode': 'runOnceForAllItems', 'jsCode': code}
            }
        ],
        'connections': {
            'Workflow Trigger': {
                'main': [
                    [{'node': 'Read Orders',   'type': 'main', 'index': 0}],
                    [{'node': 'Read Products', 'type': 'main', 'index': 0}]
                ]
            },
            'Read Orders':   {'main': [[{'node': 'Compute Analytics', 'type': 'main', 'index': 0}]]},
            'Read Products': {'main': [[{'node': 'Compute Analytics', 'type': 'main', 'index': 1}]]}
        },
        'settings': {'executionOrder': 'v1'}
    }

# ── MASTER workflow ───────────────────────────────────────────────────────────
def build_master_workflow(orders_id, products_id, customers_id,
                          inventory_id, marketing_id, analytics_id):
    parse_code = r"""
const body    = $json.body    || {};
const module  = body.module   || $json.query?.module || 'all';
const action  = body.action   || '';
const data    = body.data     || {};
const message = body.message  || '';
const history = body.history  || [];
return [{ json: { module, action, data, message, history } }];
"""

    modules = ['orders', 'products', 'customers', 'inventory', 'marketing', 'analytics']
    module_ids = {
        'orders':    orders_id,
        'products':  products_id,
        'customers': customers_id,
        'inventory': inventory_id,
        'marketing': marketing_id,
        'analytics': analytics_id
    }

    switch_cases = [
        {
            'conditions': {
                'options': {'caseSensitive': False, 'typeValidation': 'strict'},
                'conditions': [{'leftValue': '={{ $json.module }}',
                                'rightValue': mod,
                                'operator': {'type': 'string', 'operation': 'equals'}}],
                'combinator': 'and'
            },
            'renameOutput': True, 'outputKey': mod
        }
        for mod in modules
    ]

    nodes = [
        {
            'id': 'webhook', 'name': 'Webhook',
            'type': 'n8n-nodes-base.webhook',
            'typeVersion': 2, 'position': [0, 300],
            'parameters': {
                'httpMethod': 'POST', 'path': WEBHOOK_PATH,
                'responseMode': 'responseNode', 'options': {}
            },
            'webhookId': WEBHOOK_PATH
        },
        {
            'id': 'parse', 'name': 'Parse Request',
            'type': 'n8n-nodes-base.code',
            'typeVersion': 2, 'position': [240, 300],
            'parameters': {'mode': 'runOnceForAllItems', 'jsCode': parse_code}
        },
        {
            'id': 'module_switch', 'name': 'Module Router',
            'type': 'n8n-nodes-base.switch',
            'typeVersion': 3, 'position': [480, 300],
            'parameters': {
                'mode': 'rules',
                'rules': {'values': switch_cases},
                'options': {'fallbackOutput': len(modules)}
            }
        }
    ]

    connections = {
        'Webhook':       {'main': [[{'node': 'Parse Request', 'type': 'main', 'index': 0}]]},
        'Parse Request': {'main': [[{'node': 'Module Router', 'type': 'main', 'index': 0}]]},
        'Module Router': {'main': []}
    }

    router_outputs = []

    for i, mod in enumerate(modules):
        exec_name = f'Run {mod.capitalize()}'
        nodes.append({
            'id': f'exec_{mod}', 'name': exec_name,
            'type': 'n8n-nodes-base.executeWorkflow',
            'typeVersion': 1, 'position': [720, i * 110],
            'parameters': {
                'workflowId': module_ids[mod],
                'options': {}
            }
        })
        router_outputs.append([{'node': exec_name, 'type': 'main', 'index': 0}])
        connections[exec_name] = {
            'main': [[{'node': 'Merge Results', 'type': 'main', 'index': i}]]
        }

    # fallback 'all' → analytics
    nodes.append({
        'id': 'exec_all', 'name': 'Run Analytics (all)',
        'type': 'n8n-nodes-base.executeWorkflow',
        'typeVersion': 1, 'position': [720, len(modules) * 110],
        'parameters': {'workflowId': analytics_id, 'options': {}}
    })
    router_outputs.append([{'node': 'Run Analytics (all)', 'type': 'main', 'index': 0}])
    connections['Run Analytics (all)'] = {
        'main': [[{'node': 'Merge Results', 'type': 'main', 'index': len(modules)}]]
    }

    connections['Module Router']['main'] = router_outputs

    nodes.append({
        'id': 'merge', 'name': 'Merge Results',
        'type': 'n8n-nodes-base.merge',
        'typeVersion': 3, 'position': [960, 300],
        'parameters': {'mode': 'passThrough', 'output': 'input1', 'options': {}}
    })
    connections['Merge Results'] = {
        'main': [[{'node': 'Respond to Webhook', 'type': 'main', 'index': 0}]]
    }

    nodes.append({
        'id': 'respond', 'name': 'Respond to Webhook',
        'type': 'n8n-nodes-base.respondToWebhook',
        'typeVersion': 1, 'position': [1200, 300],
        'parameters': {
            'respondWith': 'json',
            'responseBody': '={{ $json }}',
            'options': {'responseCode': 200}
        }
    })

    return {
        'name': 'NexaShop Dashboard — MASTER',
        'nodes': nodes,
        'connections': connections,
        'settings': {'executionOrder': 'v1'}
    }

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print('NexaShop — Creating n8n Workflows')
    print('=' * 45)

    orders_id    = create_workflow(build_sub_workflow(
        'NexaShop — Orders',    'Orders',    'orders',    ORDERS_READ,    ORDERS_WRITE))
    products_id  = create_workflow(build_sub_workflow(
        'NexaShop — Products',  'Products',  'products',  PRODUCTS_READ,  PRODUCTS_WRITE))
    customers_id = create_workflow(build_sub_workflow(
        'NexaShop — Customers', 'Customers', 'customers', CUSTOMERS_READ, CUSTOMERS_WRITE))
    inventory_id = create_workflow(build_sub_workflow(
        'NexaShop — Inventory', 'Inventory', 'inventory', INVENTORY_READ, INVENTORY_WRITE))
    marketing_id = create_workflow(build_sub_workflow(
        'NexaShop — Marketing', 'Marketing', 'marketing', MARKETING_READ, MARKETING_WRITE))
    analytics_id = create_workflow(build_analytics_workflow())
    master_id    = create_workflow(build_master_workflow(
        orders_id, products_id, customers_id, inventory_id, marketing_id, analytics_id))

    host = N8N_URL.replace('/api', '')

    print()
    print('All workflows created successfully!')
    print()
    print('Workflow IDs:')
    print(f'  Orders:    {orders_id}')
    print(f'  Products:  {products_id}')
    print(f'  Customers: {customers_id}')
    print(f'  Inventory: {inventory_id}')
    print(f'  Marketing: {marketing_id}')
    print(f'  Analytics: {analytics_id}')
    print(f'  MASTER:    {master_id}')
    print()
    print(f'Webhook URL: {host}/webhook/{WEBHOOK_PATH}')
    print()
    print('Next steps:')
    print('  1. Add Google Sheets OAuth2 credential in n8n Settings > Credentials')
    print('  2. Create Google Sheet with tabs: Orders | Products | Customers | Inventory | Marketing')
    print('  3. Open each sub-workflow: add credential + replace PASTE_YOUR_GOOGLE_SHEET_URL_HERE')
    print('  4. Add column headers per tab (see script header for full list)')
    print('  5. Activate the MASTER workflow in n8n')

if __name__ == '__main__':
    main()
