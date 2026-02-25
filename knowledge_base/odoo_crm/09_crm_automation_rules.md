# Odoo 16 CRM Automation Rules

## Overview

Odoo 16 includes an **Automated Actions** engine (`base.automation`) that can trigger workflows based on record changes, time conditions, or user actions. For CRM, automation rules are essential for hands-free lead nurturing and follow-up.

---

## Types of Automated Actions

| Trigger | Description |
|---|---|
| Record Created | Fires when a new record is created |
| Record Updated | Fires when specific fields change |
| Record Created or Updated | Either of the above |
| Time Condition | Fires based on a date field (e.g. X days after `date_deadline`) |
| Based on timed condition | Recurring check based on an interval |
| External | Triggered via `action_base_automation.base_automation` |

---

## Common CRM Automation Rules

### 1. Auto-convert Lead to Opportunity After 3 Days
- **Model**: `crm.lead`
- **Trigger**: Time-based, 3 days after `create_date`
- **Condition**: `type == 'lead' and active == True`
- **Action**: Write `type = 'opportunity'`

### 2. Send Follow-Up Email for Stale Opportunities
- **Model**: `crm.lead`
- **Trigger**: Time-based, 7 days after `write_date`
- **Condition**: `type == 'opportunity' and active == True`
- **Action**: Send email template "Stale Opportunity Follow-Up"

### 3. Notify Manager on High-Value Opportunity
- **Model**: `crm.lead`
- **Trigger**: Record Updated (when `expected_revenue` changes)
- **Condition**: `expected_revenue > 50000`
- **Action**: Send notification to sales manager

### 4. Auto-schedule Activity on Stage Change
- **Model**: `crm.lead`
- **Trigger**: Record Updated (when `stage_id` changes)
- **Condition**: `stage_id.name == 'Proposal'`
- **Action**: Create activity "Send Proposal" due in 2 days

---

## Creating an Automation Rule via JSON-RPC

```python
# Create a time-based automation rule
rule_id = models.execute_kw(db, uid, api_key, 'base.automation', 'create', [{
    'name': 'Follow-up: Stale Opportunity (7 days)',
    'model_id': crm_lead_model_id,
    'trigger': 'on_time',
    'trg_date_id': write_date_field_id,  # ir.model.fields id for write_date
    'trg_date_range': 7,
    'trg_date_range_type': 'days',
    'filter_pre_domain': "[('type', '=', 'opportunity'), ('active', '=', True)]",
    'action_server_id': action_id,
    'active': True,
}])
```

---

## Querying Automation Rules via JSON-RPC

```python
# List all CRM automation rules
rules = models.execute_kw(db, uid, api_key, 'base.automation', 'search_read',
    [[['model_id.model', '=', 'crm.lead']]],
    {'fields': ['name', 'trigger', 'active', 'filter_pre_domain']})

for rule in rules:
    print(f"[{'ON' if rule['active'] else 'OFF'}] {rule['name']} — {rule['trigger']}")
```

---

## base.automation Fields

| Field | Type | Description |
|---|---|---|
| `name` | Char | Rule display name |
| `model_id` | Many2one (ir.model) | Model the rule applies to |
| `trigger` | Selection | Trigger type (see above) |
| `trg_date_id` | Many2one (ir.model.fields) | Date field for time triggers |
| `trg_date_range` | Integer | Number of units for time trigger |
| `trg_date_range_type` | Selection | `"minutes"`, `"hours"`, `"days"` |
| `filter_pre_domain` | Char | Python domain filter (before action) |
| `filter_domain` | Char | Python domain filter (after action) |
| `action_server_id` | Many2one (ir.actions.server) | Server action to execute |
| `active` | Boolean | Is the rule enabled? |

---

## Best Practices

1. Always test automation rules in a staging environment before production
2. Use `filter_pre_domain` to narrow the scope and avoid unintended triggers
3. Keep automation rules simple — complex logic belongs in custom Python code
4. Monitor automation logs in **Settings → Technical → Automation → Automated Actions → Runs**
5. Disable (rather than delete) automation rules you want to pause temporarily
