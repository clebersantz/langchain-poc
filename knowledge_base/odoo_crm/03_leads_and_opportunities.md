# Odoo 16 Leads and Opportunities

## Lead vs Opportunity in Odoo 16

Both leads and opportunities are stored in the same model: `crm.lead`. The `type` field distinguishes them:

| Value | Meaning |
|---|---|
| `"lead"` | Unqualified inquiry — not yet in the pipeline |
| `"opportunity"` | Qualified, in the pipeline with a stage |

### Enabling Leads

By default in Odoo 16, only opportunities are shown. To enable the leads step:
1. Go to **CRM → Configuration → Settings**
2. Enable **Leads** under the "Pipeline" section
3. Save

When leads are enabled, new incoming contacts start as leads and must be manually or automatically converted to opportunities.

---

## Lead Creation Methods

### 1. Manual Creation
- Go to CRM → Leads → New
- Fill in the name, contact details, and assign a team/salesperson

### 2. Email Alias
- Each sales team can have an email alias (e.g. `sales@company.com`)
- Incoming emails automatically create leads assigned to that team

### 3. Web Form
- Install the `website_crm` module
- Contact forms on the Odoo website create leads automatically

### 4. Import
- CRM → Leads → Import (CSV/Excel)
- Map spreadsheet columns to crm.lead fields

### 5. JSON-RPC API
- Create programmatically via the Odoo external API (see code examples below)

---

## Converting a Lead to an Opportunity

### Via UI
1. Open the lead record
2. Click **Convert to Opportunity** button
3. Optionally merge with existing opportunities or link to a partner
4. Select the pipeline stage and assign a salesperson

### Via JSON-RPC

```python
# Method 1: Update type and stage_id directly
client.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {
        'type': 'opportunity',
        'stage_id': qualified_stage_id,
        'partner_id': partner_id,  # optional
    }])

# Method 2: Use the action_set_won equivalent — convert_opportunity_to_lead
# Note: In Odoo 16, direct write on type is the recommended JSON-RPC approach
```

---

## crm.lead Fields Table

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Auto | Record identifier |
| `name` | Char | Yes | Lead/opportunity title |
| `type` | Selection | No | `"lead"` or `"opportunity"` |
| `stage_id` | Many2one (crm.stage) | No | Pipeline stage (required for opportunities) |
| `kanban_state` | Selection | No | `"normal"`, `"done"`, `"blocked"` |
| `user_id` | Many2one (res.users) | No | Assigned salesperson |
| `team_id` | Many2one (crm.team) | No | Assigned sales team |
| `partner_id` | Many2one (res.partner) | No | Linked customer/partner |
| `partner_name` | Char | No | Company name (if no partner linked) |
| `contact_name` | Char | No | Contact person name |
| `email_from` | Char | No | Contact email address |
| `phone` | Char | No | Phone number |
| `mobile` | Char | No | Mobile number |
| `street` | Char | No | Street address |
| `city` | Char | No | City |
| `country_id` | Many2one (res.country) | No | Country |
| `description` | Text | No | Internal notes / description |
| `probability` | Float | No | Win probability (0–100%) |
| `expected_revenue` | Monetary | No | Expected deal value |
| `recurring_revenue` | Monetary | No | Recurring revenue (MRR/ARR) |
| `date_deadline` | Date | No | Expected closing date |
| `date_conversion` | Datetime | No | Date converted to opportunity |
| `date_closed` | Datetime | No | Date won or lost |
| `active` | Boolean | No | False = lost/archived |
| `priority` | Selection | No | `"0"` normal, `"1"` high, `"2"` very high, `"3"` critical |
| `tag_ids` | Many2many (crm.tag) | No | Labels / tags |
| `lost_reason_id` | Many2one (crm.lost.reason) | No | Reason for losing |
| `company_id` | Many2one (res.company) | No | Company (multi-company) |
| `create_date` | Datetime | Auto | Creation timestamp |
| `write_date` | Datetime | Auto | Last modification timestamp |

---

## JSON-RPC Code Examples

### Authenticate

```python
import requests

url = "http://localhost:8069"  # Base URL (no /jsonrpc suffix)
db = "odoo"
username = "admin@example.com"
api_key = "your_api_key"  # Preferences → Account Security

def json_rpc(service, method, args):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"service": service, "method": method, "args": args},
        "id": 1,
    }
    return requests.post(f"{url}/jsonrpc", json=payload).json()["result"]

class JsonRpcModels:
    def execute_kw(self, db, uid, api_key, model, method, args, kwargs=None):
        return json_rpc(
            "object",
            "execute_kw",
            [db, uid, api_key, model, method, args, kwargs or {}],
        )

uid = json_rpc("common", "login", [db, username, api_key])
models = JsonRpcModels()
```

### Create a Lead

```python
lead_id = models.execute_kw(db, uid, api_key, 'crm.lead', 'create', [{
    'name': 'New Enterprise Inquiry',
    'contact_name': 'John Doe',
    'email_from': 'john.doe@example.com',
    'phone': '+1-555-1234',
    'expected_revenue': 25000,
    'description': 'Interested in the Enterprise plan',
    'type': 'lead',
}])
print(f"Created lead id: {lead_id}")
```

### Search Leads

```python
leads = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['type', '=', 'lead'], ['active', '=', True]]],
    {'fields': ['name', 'email_from', 'stage_id', 'expected_revenue'], 'limit': 20})
```

### Update a Lead

```python
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {'expected_revenue': 30000, 'priority': '1'}])
```

### Mark as Won

```python
# Use action_set_won for proper Odoo workflow
models.execute_kw(db, uid, api_key, 'crm.lead', 'action_set_won', [[lead_id]])
```

### Mark as Lost

```python
models.execute_kw(db, uid, api_key, 'crm.lead', 'action_set_lost', [[lead_id]])
# Optionally set lost reason
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {'lost_reason_id': lost_reason_id}])
```
