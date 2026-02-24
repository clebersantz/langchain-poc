# Odoo XML-RPC API Troubleshooting

## Common Issues and Solutions

---

**Problem 1: Authentication Fails — Returns `False` or 0**

*Symptoms*: `uid = common.authenticate(...)` returns `False` or `0`

*Causes and Solutions*:
1. **Wrong credentials** — Verify `ODOO_USER` is the login email, not display name
2. **API Key not enabled** — Go to Settings → Technical → API Keys and create one
3. **API Key expired** — Generate a new API key in Settings → API Keys
4. **Wrong database** — Verify `ODOO_DB` matches the database name in Odoo
5. **User not active** — Check that the user account is active in Settings → Users

```python
# Debug: check version endpoint (no auth required)
version = common.version()
print(version)  # Should return dict with server_version
```

---

**Problem 2: Access Rights Error (Fault 2)**

*Symptoms*: `xmlrpc.client.Fault: <Fault 2: "Access Denied">`

*Causes and Solutions*:
1. **Insufficient permissions** — The API user must have appropriate access rights for the model
2. **Model access rules** — Check Settings → Technical → Security → Access Rights
3. **Record rules** — Check if record-level rules restrict access
4. **Group restriction** — The user may not belong to the required security group

```python
# Check which groups the user belongs to
user_info = models.execute_kw(db, uid, api_key, 'res.users', 'read',
    [uid], {'fields': ['groups_id', 'name']})
```

---

**Problem 3: Field Not Found Error**

*Symptoms*: `ValueError: Invalid field 'field_name' on model 'crm.lead'`

*Solutions*:
1. Check the exact field name using `fields_get`:
```python
fields = models.execute_kw(db, uid, api_key, 'crm.lead', 'fields_get',
    [], {'attributes': ['string', 'type']})
# Search for your field
matching = {k: v for k, v in fields.items() if 'revenue' in k.lower()}
```

2. Common field name mistakes:
   - `email` → use `email_from` on `crm.lead`
   - `name` on activity → use `summary`
   - `partner` → use `partner_id`

---

**Problem 4: Wrong Model Name**

*Symptoms*: `KeyError: model not found` or `MissingError`

*Common model name mistakes*:

| Wrong | Correct |
|---|---|
| `crm_lead` | `crm.lead` |
| `CrmLead` | `crm.lead` |
| `lead` | `crm.lead` |
| `opportunity` | `crm.lead` |
| `partner` | `res.partner` |
| `user` | `res.users` |
| `activity` | `mail.activity` |
| `stage` | `crm.stage` |
| `team` | `crm.team` |

*Verify model exists*:
```python
model_info = models.execute_kw(db, uid, api_key, 'ir.model', 'search_read',
    [[['model', '=', 'crm.lead']]], {'fields': ['name', 'model']})
```

---

**Problem 5: How to Check Available Fields on a Model**

```python
# Get all fields with their types and labels
fields = models.execute_kw(db, uid, api_key, 'crm.lead', 'fields_get',
    [], {'attributes': ['string', 'type', 'required', 'readonly']})

# Print in sorted order
for name, info in sorted(fields.items()):
    print(f"{name:40} {info['type']:15} {info['string']}")
```

---

**Problem 6: Connection Timeout**

*Symptoms*: `socket.timeout` or `TimeoutError`

*Solutions*:
1. Increase timeout:
```python
import xmlrpc.client
import socket

socket.setdefaulttimeout(30)  # 30 seconds
models = xmlrpc.client.ServerProxy("http://localhost:8069/xmlrpc/2/object")
```

2. Check Odoo server status — it may be starting up or under heavy load
3. Verify the `ODOO_URL` includes the correct protocol and port

---

**Problem 7: search_read Returns Empty List**

*Symptoms*: `search_read` returns `[]` even though records exist

*Debugging steps*:
```python
# Step 1: Count matching records
count = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_count',
    [[['type', '=', 'opportunity']]])
print(f"Count: {count}")

# Step 2: Check if records are archived
all_leads = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['active', 'in', [True, False]]]],  # Include archived
    {'fields': ['name', 'active', 'type'], 'limit': 5})

# Step 3: Simplify the domain
simple = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[]], {'fields': ['name'], 'limit': 3})
```

---

**Problem 8: Many2one Field Returns a List, Not an Id**

*Symptoms*: `stage_id` returns `[1, 'New']` instead of just `1`

*Explanation*: This is by design in Odoo. Many2one fields are returned as `[id, display_name]`.

*How to handle*:
```python
lead = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['id', '=', lead_id]]], {'fields': ['stage_id', 'user_id']})[0]

stage_id = lead['stage_id'][0] if lead['stage_id'] else None
stage_name = lead['stage_id'][1] if lead['stage_id'] else None
user_name = lead['user_id'][1] if lead['user_id'] else 'Unassigned'
```

---

**Problem 9: execute_kw Raises Fault on action_set_won**

*Symptoms*: Error when calling `action_set_won` via XML-RPC

*Explanation*: Some Odoo server actions return client actions (JavaScript redirects) that are not meaningful via XML-RPC.

*Workaround*:
```python
try:
    models.execute_kw(db, uid, api_key, 'crm.lead', 'action_set_won', [[lead_id]])
except xmlrpc.client.Fault:
    # Fallback: direct write to mark as won
    won_stage = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
        [[['is_won', '=', True]]], {'fields': ['id'], 'limit': 1})
    if won_stage:
        models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
            [[lead_id], {'stage_id': won_stage[0]['id'], 'probability': 100}])
```

---

**Problem 10: Creating an Activity Fails with Missing res_model_id**

*Symptoms*: `IntegrityError` or validation error when creating `mail.activity`

*Solution*: You must provide `res_model_id` (the `ir.model` id), NOT the model name string.

```python
# Get the ir.model id for crm.lead
model_id = models.execute_kw(db, uid, api_key, 'ir.model', 'search',
    [[['model', '=', 'crm.lead']]])[0]

# Now create the activity with res_model_id
models.execute_kw(db, uid, api_key, 'mail.activity', 'create', [{
    'res_model_id': model_id,  # Integer, NOT 'crm.lead'
    'res_id': lead_id,
    'activity_type_id': type_id,
    'summary': 'Call',
    'date_deadline': '2024-07-01',
}])
```

---

**Problem 11: XML-RPC vs REST API**

*Question*: Should I use XML-RPC or the REST API?

*Odoo 16 answer*: Odoo 16 does not have a stable REST API. Use XML-RPC (`/xmlrpc/2/object`).

The Odoo 17/18 REST API is available via `/api/{model}` but is not present in Odoo 16.

---

**Problem 12: Unicode/Encoding Errors**

*Symptoms*: `UnicodeDecodeError` when reading fields with special characters

*Solution*:
```python
# Ensure you're using Python 3 (which handles Unicode natively)
# When using TextLoader for KB ingestion, specify encoding:
loader = TextLoader(file_path, encoding='utf-8')
```

---

**Problem 13: Pagination — Results Truncated**

*Symptoms*: Only getting 80 or 100 results when more exist

*Solution*: Use `limit` and `offset` for pagination:
```python
all_results = []
offset = 0
limit = 100

while True:
    batch = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
        [[['type', '=', 'opportunity']]],
        {'fields': ['name'], 'limit': limit, 'offset': offset})
    if not batch:
        break
    all_results.extend(batch)
    offset += len(batch)
    if len(batch) < limit:
        break
```

---

**Problem 14: Odoo 16 Specific — API Key Authentication**

*Note*: Odoo 16 introduced API Key authentication. The old password-based auth still works but API keys are preferred.

```python
# Using API Key (recommended for Odoo 16)
uid = common.authenticate(db, 'admin@example.com', 'your_api_key', {})

# Using password (still works but deprecated)
uid = common.authenticate(db, 'admin@example.com', 'admin_password', {})
```

---

**Problem 15: Import Error — Model Not Found After Migration**

*Symptoms*: After updating Odoo, some model or field names have changed

*Solution*: Check the Odoo upgrade notes for your version. Use `fields_get` and `ir.model` queries to verify current field and model names.

```python
# Verify model exists
exists = models.execute_kw(db, uid, api_key, 'ir.model', 'search_count',
    [[['model', '=', 'crm.lead']]])
print(f"crm.lead exists: {bool(exists)}")
```
