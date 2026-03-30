# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture: WAT Framework (Workflows, Agents, Tools)

This project separates concerns so probabilistic AI handles reasoning while deterministic code handles execution.

- **Workflows** (`workflows/`): Markdown SOPs defining objectives, required inputs, which tools to use, expected outputs, and edge case handling.
- **Agents**: Claude's role — read workflows, run tools in sequence, handle failures, ask clarifying questions. Connect intent to execution without doing everything directly.
- **Tools** (`tools/`): Python scripts for deterministic execution — API calls, data transformations, file operations. Credentials loaded from `env/.env` via `python-dotenv`.

**Why this matters:** When AI handles every step directly, accuracy compounds poorly. Offloading execution to deterministic scripts keeps Claude focused on orchestration.

## Directory Layout

```
.tmp/        # Temporary/intermediate files — regenerated as needed, disposable
tools/       # Python scripts for deterministic execution
workflows/   # Markdown SOPs
env/         # API keys and OAuth credentials (NEVER store secrets elsewhere)
```

Deliverables go to cloud services (Google Sheets, Slides, etc.). Local files are for processing only.

## Running Tools

```bash
python tools/<script_name>.py
```

Scripts use `python-dotenv` to load `env/.env` automatically. Install dependencies:

```bash
pip install python-dotenv
# or, when requirements.txt exists:
pip install -r requirements.txt
```

## n8n Backend (Hiraya Construction Supply Dashboard)

**n8n instance:** `https://n8n.srv1326251.hstgr.cloud`
**API key:** stored in `.mcp.json` (project root)
**MCP config:** `.mcp.json` — restart Claude Code to activate n8n MCP tools

### Workflow Architecture

All 5 workflows live in n8n under the "Hiraya" prefix:

| Workflow | ID | Role |
|---|---|---|
| Hiraya Dashboard — MASTER | `NlxMBnjPepSitXeC` | Webhook receiver, routes to sub-workflows |
| Hiraya — Sales Data | `rV3NrWUPvEMzYNsf` | Reads Sales sheet, returns aggregated sales JSON |
| Hiraya — Inventory Data | `8HWkhy4E6Gf95cz4` | Reads Inventory sheet, returns stock summary |
| Hiraya — HR Data | `BaF3GmxnlS8xYfgy` | Reads HR sheet, returns employee directory |
| Hiraya — Analytics | `y2GAAdbAgt6yloTj` | Reads Sales+Inventory, returns charts/trends |

**Webhook endpoint (activate master first):**
`POST https://n8n.srv1326251.hstgr.cloud/webhook/hiraya-dashboard`
Body: `{ "module": "sales" | "inventory" | "hr" | "analytics" | "all" }`

### Google Sheets Setup Required

Each sub-workflow has a Google Sheets node that needs:
1. **Credential:** Add "Google Sheets OAuth2 API" credential in n8n Settings > Credentials
2. **Spreadsheet URL:** Replace `PASTE_YOUR_GOOGLE_SHEET_URL_HERE` in each node
3. **Sheet tab names** must match exactly: `Sales`, `Inventory`, `HR`

### Required Column Headers per Sheet Tab

**Sales:** `Date, OrderID, Customer, Product, Qty, UnitPrice, Total, Status`
**Inventory:** `SKU, ProductName, Category, Stock, ReorderLevel, UnitCost, Supplier, Status`
**HR:** `EmployeeID, Name, Position, Status, LeaveBalance, Salary, Mobile, Email, EmergencyName, EmergencyRelation, EmergencyMobile`

### Re-creating Workflows

If workflows need to be rebuilt: `python -X utf8 tools/create_hiraya_workflows.py`

## Operating Rules

1. **Check `tools/` before building anything new.** Only create scripts when nothing exists for the task.
2. **On errors:** Read the full trace, fix and retest (check before re-running if the script uses paid API calls), then update the workflow with what you learned.
3. **Keep workflows current** as you discover constraints, better methods, or recurring issues. Don't create or overwrite workflows without asking unless explicitly told to.
4. **`tools/` and `workflows/` directories are created as needed** — always check what already exists before starting a task.
