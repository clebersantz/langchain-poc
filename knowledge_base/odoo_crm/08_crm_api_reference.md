# Odoo 16 CRM XML-RPC API Reference

## Authentication

Odoo 16 uses XML-RPC for its external API. All operations require a valid `uid` obtained by authentication.

```python
import xmlrpc.client

url = "http://localhost:8069"  # Base URL (no /xmlrpc/2 suffix)
db = "odoo"
username = "admin@example.com"
api_key = "your_odoo_api_key"  # Preferences → Account Security

# Create proxies
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Authenticate — returns uid (integer)
uid = common.authenticate(db, username, api_key, {})
print(f"Authenticated as uid: {uid}")

# Check Odoo version
version = common.version()
print(f"Odoo version: {version['server_version']}")
```

---

## CRUD Operations

All CRUD goes through `execute_kw`:
```
models.execute_kw(db, uid, api_key, model, method, args, kwargs)
```

### Create

```python
lead_id = models.execute_kw(db, uid, api_key, 'crm.lead', 'create', [{
    'name': 'Enterprise Deal — Acme Corp',
    'contact_name': 'Alice Smith',
    'email_from': 'alice@acme.com',
    'phone': '+1-555-9876',
    'expected_revenue': 50000,
    'type': 'opportunity',
    'stage_id': 1,
}])
```

### Read (search_read)

```python
leads = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['active', '=', True], ['type', '=', 'opportunity']]],
    {
        'fields': ['name', 'email_from', 'stage_id', 'expected_revenue', 'user_id'],
        'limit': 20,
        'offset': 0,
        'order': 'expected_revenue desc',
    })
```

### Update (write)

```python
# Returns True on success
result = models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {
        'stage_id': new_stage_id,
        'probability': 75,
        'date_deadline': '2024-07-31',
    }])
```

### Delete (unlink)

```python
# Returns True on success
result = models.execute_kw(db, uid, api_key, 'crm.lead', 'unlink', [[lead_id]])
```

---

## Stage Operations

```python
# Get all stages
stages = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[]],
    {'fields': ['id', 'name', 'sequence', 'probability', 'fold', 'team_id']})

# Find stage by name (case-insensitive)
qualified = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[['name', 'ilike', 'qualified']]],
    {'fields': ['id', 'name'], 'limit': 1})

# Move opportunity to a stage
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[opp_id], {'stage_id': qualified[0]['id']}])
```

---

## Partner Operations

```python
# Search partners
partners = models.execute_kw(db, uid, api_key, 'res.partner', 'search_read',
    [[['name', 'ilike', 'Acme']]],
    {'fields': ['id', 'name', 'email', 'phone', 'is_company']})

# Create a partner
partner_id = models.execute_kw(db, uid, api_key, 'res.partner', 'create', [{
    'name': 'Acme Corporation',
    'email': 'contact@acme.com',
    'phone': '+1-555-0000',
    'is_company': True,
}])

# Link partner to a lead
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {'partner_id': partner_id}])
```

---

## Activity Operations

```python
# Get model id for crm.lead
model_id = models.execute_kw(db, uid, api_key, 'ir.model', 'search',
    [[['model', '=', 'crm.lead']]])[0]

# Get call activity type id
call_type = models.execute_kw(db, uid, api_key, 'mail.activity.type', 'search_read',
    [[['name', 'ilike', 'call']]],
    {'fields': ['id', 'name'], 'limit': 1})

# Schedule a call activity
activity_id = models.execute_kw(db, uid, api_key, 'mail.activity', 'create', [{
    'res_model_id': model_id,
    'res_id': lead_id,
    'activity_type_id': call_type[0]['id'],
    'summary': 'Discovery call',
    'note': '<p>Discuss requirements</p>',
    'date_deadline': '2024-06-20',
}])

# Mark activity done
models.execute_kw(db, uid, api_key, 'mail.activity', 'action_feedback',
    [[activity_id]], {'feedback': 'Call completed. Interested in Enterprise.'})
```

---

## Common Search Domains

```python
# Open opportunities
[['type', '=', 'opportunity'], ['active', '=', True]]

# Leads only (not opportunities)
[['type', '=', 'lead'], ['active', '=', True]]

# High priority opportunities
[['priority', '>=', '2'], ['type', '=', 'opportunity']]

# Opportunities closing this month
[['date_deadline', '>=', '2024-06-01'], ['date_deadline', '<=', '2024-06-30']]

# Opportunities for a specific salesperson
[['user_id', '=', salesperson_id]]

# Opportunities for a specific team
[['team_id', '=', team_id]]

# Lost opportunities (archived)
[['active', '=', False], ['type', '=', 'opportunity']]

# Opportunities with expected revenue > 10000
[['expected_revenue', '>', 10000]]

# Leads from a specific email domain
[['email_from', 'ilike', '@acme.com']]

# Opportunities tagged with 'VIP'
[['tag_ids.name', '=', 'VIP']]
```

---

## Error Handling

```python
import xmlrpc.client

try:
    result = models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
        [[99999], {'name': 'Test'}])
except xmlrpc.client.Fault as e:
    print(f"Odoo error: {e.faultCode} — {e.faultString}")
    # faultCode 1 = general error
    # faultCode 2 = access rights error
except ConnectionError as e:
    print(f"Connection error: {e}")
```

---

## Checking Available Fields

```python
# Get all fields for a model
fields = models.execute_kw(db, uid, api_key, 'crm.lead', 'fields_get',
    [], {'attributes': ['string', 'type', 'required']})
for name, info in sorted(fields.items()):
    print(f"{name}: {info['type']} — {info['string']}")
```
