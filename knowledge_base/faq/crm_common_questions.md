# CRM Common Questions

## General CRM Questions

**Q: What is the difference between a Lead and an Opportunity in Odoo 16?**

A: Both are stored in the `crm.lead` model. A **Lead** (`type = "lead"`) is an unqualified inquiry — a contact that showed interest but hasn't been evaluated yet. An **Opportunity** (`type = "opportunity"`) is a qualified lead that has been added to the sales pipeline with a stage, expected revenue, and probability. Leads must be converted to opportunities before they appear in the pipeline Kanban view.

---

**Q: How do I create a lead via the Odoo XML-RPC API?**

A:
```python
import xmlrpc.client
models = xmlrpc.client.ServerProxy("http://localhost:8069/xmlrpc/2/object")

lead_id = models.execute_kw(db, uid, api_key, 'crm.lead', 'create', [{
    'name': 'New Inquiry — Acme Corp',
    'contact_name': 'John Doe',
    'email_from': 'john@acme.com',
    'phone': '+1-555-1234',
    'type': 'lead',
}])
```

---

**Q: How do I move a lead to a specific pipeline stage?**

A: First get the stage id by name, then write it to the lead:
```python
# Find stage
stages = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[['name', '=', 'Qualified']]], {'fields': ['id']})
stage_id = stages[0]['id']

# Update lead
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {'stage_id': stage_id}])
```

---

**Q: What are the required fields for creating a lead in Odoo 16?**

A: Only `name` is strictly required by the model. However, for useful leads you should also provide:
- `contact_name` — the person's name
- `email_from` — contact email
- `type` — `"lead"` or `"opportunity"`
- `team_id` — sales team assignment

---

**Q: How do I assign a lead to a specific salesperson?**

A:
```python
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {'user_id': salesperson_user_id}])
```
You can find a salesperson's `user_id` using:
```python
users = models.execute_kw(db, uid, api_key, 'res.users', 'search_read',
    [[['name', 'ilike', 'Alice']]], {'fields': ['id', 'name', 'email']})
```

---

**Q: How do I get all open opportunities?**

A:
```python
opportunities = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['type', '=', 'opportunity'], ['active', '=', True]]],
    {'fields': ['name', 'stage_id', 'expected_revenue', 'user_id', 'date_deadline'],
     'limit': 50})
```

---

**Q: How do I check if a stage is the "Won" stage?**

A: Query the stage and check the `is_won` field (or check if probability = 100):
```python
stages = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[]],
    {'fields': ['id', 'name', 'probability', 'is_won']})
won_stages = [s for s in stages if s.get('is_won') or s['probability'] == 100]
```

---

**Q: How do I get the total pipeline value per sales team?**

A:
```python
teams = models.execute_kw(db, uid, api_key, 'crm.team', 'search_read',
    [[['active', '=', True]]], {'fields': ['id', 'name']})

for team in teams:
    opps = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
        [[['team_id', '=', team['id']], ['type', '=', 'opportunity'], ['active', '=', True]]],
        {'fields': ['expected_revenue']})
    total = sum(o['expected_revenue'] for o in opps)
    print(f"{team['name']}: ${total:,.0f}")
```

---

**Q: How do I search for leads/opportunities by partner name?**

A:
```python
results = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['partner_id.name', 'ilike', 'Acme'], ['type', '=', 'opportunity']]],
    {'fields': ['name', 'partner_id', 'stage_id', 'expected_revenue']})
```

---

**Q: How do I list all overdue activities in the CRM?**

A:
```python
overdue = models.execute_kw(db, uid, api_key, 'mail.activity', 'search_read',
    [[['res_model', '=', 'crm.lead'], ['state', '=', 'overdue']]],
    {'fields': ['id', 'res_id', 'res_name', 'summary', 'date_deadline', 'user_id']})
```

---

**Q: How do I convert a lead to an opportunity?**

A:
```python
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {
        'type': 'opportunity',
        'stage_id': first_stage_id,  # Required for opportunities
    }])
```

---

**Q: How do I mark an opportunity as Won?**

A:
```python
# Preferred: use Odoo's built-in action
models.execute_kw(db, uid, api_key, 'crm.lead', 'action_set_won', [[opp_id]])

# Alternative: direct write
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[opp_id], {'stage_id': won_stage_id, 'probability': 100}])
```

---

**Q: How do I mark an opportunity as Lost?**

A:
```python
models.execute_kw(db, uid, api_key, 'crm.lead', 'action_set_lost', [[opp_id]])
# Optionally add lost reason
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[opp_id], {'lost_reason_id': lost_reason_id}])
```
Note: Lost leads are archived (`active = False`).

---

**Q: How do I get available lost reasons?**

A:
```python
reasons = models.execute_kw(db, uid, api_key, 'crm.lost.reason', 'search_read',
    [[]], {'fields': ['id', 'name']})
```

---

**Q: How do I get the pipeline Kanban stages in order?**

A:
```python
stages = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[]],
    {'fields': ['id', 'name', 'sequence', 'probability'],
     'order': 'sequence asc'})
```

---

**Q: How do I add a tag to a lead?**

A:
```python
# Get or create tag
tags = models.execute_kw(db, uid, api_key, 'crm.tag', 'search_read',
    [[['name', '=', 'VIP']]], {'fields': ['id']})
if not tags:
    tag_id = models.execute_kw(db, uid, api_key, 'crm.tag', 'create', [{'name': 'VIP'}])
else:
    tag_id = tags[0]['id']

# Add tag using many2many tuple syntax: (4, id) = link
models.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[lead_id], {'tag_ids': [(4, tag_id)]}])
```

---

**Q: How do I schedule a follow-up call on a lead?**

A:
```python
# Get model id
model_id = models.execute_kw(db, uid, api_key, 'ir.model', 'search',
    [[['model', '=', 'crm.lead']]])[0]

# Get call activity type
call_type = models.execute_kw(db, uid, api_key, 'mail.activity.type', 'search_read',
    [[['name', 'ilike', 'phone']]], {'fields': ['id'], 'limit': 1})

# Create activity
models.execute_kw(db, uid, api_key, 'mail.activity', 'create', [{
    'res_model_id': model_id,
    'res_id': lead_id,
    'activity_type_id': call_type[0]['id'],
    'summary': 'Follow-up call',
    'date_deadline': '2024-07-10',
}])
```

---

**Q: How do I get the count of open opportunities by stage?**

A:
```python
stage_counts = models.execute_kw(db, uid, api_key, 'crm.lead', 'read_group',
    [[['type', '=', 'opportunity'], ['active', '=', True]]],
    ['stage_id', '__count'],
    ['stage_id'])
for row in stage_counts:
    print(f"{row['stage_id'][1]}: {row['stage_id_count']} opportunities")
```

---

**Q: What is the Kanban state on a lead and what does it mean?**

A: The `kanban_state` field reflects the salesperson's assessment:
- `"normal"` — In progress, no blocker (grey dot)
- `"done"` — Ready to move to next stage (green dot)
- `"blocked"` — Something is blocking progress (red dot)

---

**Q: How do I filter leads by email domain?**

A:
```python
leads = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['email_from', 'ilike', '@acme.com']]],
    {'fields': ['name', 'email_from', 'contact_name']})
```

---

**Q: How do I get all CRM leads created this week?**

A:
```python
from datetime import datetime, timedelta

monday = (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())).strftime('%Y-%m-%d')
leads = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['create_date', '>=', monday]]],
    {'fields': ['name', 'email_from', 'create_date', 'user_id']})
```

---

**Q: How do I get the win probability for each stage?**

A:
```python
stages = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[]],
    {'fields': ['name', 'probability'], 'order': 'sequence asc'})
for s in stages:
    print(f"{s['name']}: {s['probability']}%")
```
