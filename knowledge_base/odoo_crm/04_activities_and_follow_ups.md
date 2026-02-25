# Odoo 16 Activities and Follow-Ups

## Overview

Activities in Odoo 16 represent scheduled tasks linked to any model record. In CRM, they are essential for tracking follow-up calls, emails, and meetings.

The `mail.activity` model is shared across all Odoo modules (CRM, Sales, Helpdesk, etc.).

---

## Activity Types

Odoo 16 ships with these default activity types (`mail.activity.type`):

| Name | Technical | Default Days | Icon |
|---|---|---|---|
| Email | `mail_mail` | 5 | envelope |
| Phone Call | `call` | 1 | phone |
| Meeting | `calendar_event` | 0 | calendar |
| To-Do | `todo` | 5 | clock |
| Upload Document | `upload_mail` | 5 | upload |

### Getting Activity Type IDs via XML-RPC

```python
types = models.execute_kw(db, uid, api_key, 'mail.activity.type', 'search_read',
    [[]],
    {'fields': ['id', 'name', 'delay_days']})
```

---

## Scheduling an Activity

### Via UI
1. Open a lead/opportunity
2. Click the **Activities** button or the clock icon in the Kanban card
3. Select activity type, assign to a user, set deadline, add summary and note
4. Click **Schedule**

### Via XML-RPC

```python
# Get ir.model id for crm.lead
model_id = models.execute_kw(db, uid, api_key, 'ir.model', 'search',
    [[['model', '=', 'crm.lead']]])[0]

# Create an activity
activity_id = models.execute_kw(db, uid, api_key, 'mail.activity', 'create', [{
    'res_model_id': model_id,
    'res_id': lead_id,
    'activity_type_id': call_type_id,
    'summary': 'Discovery call',
    'note': '<p>Discuss requirements and budget</p>',
    'date_deadline': '2024-06-15',
    'user_id': salesperson_uid,
}])
```

---

## Marking an Activity as Done

### Via UI
1. Click the activity icon on the Kanban card or in the activity chatter
2. Click **Mark Done**
3. Enter optional feedback
4. Click **Done**

### Via XML-RPC

```python
# Method 1: action_feedback (preferred)
models.execute_kw(db, uid, api_key, 'mail.activity', 'action_feedback',
    [[activity_id]], {'feedback': 'Call completed, interested in Enterprise plan'})

# Method 2: Unlink (delete) the activity
models.execute_kw(db, uid, api_key, 'mail.activity', 'unlink', [[activity_id]])
```

---

## Activity States

The `state` field on `mail.activity` is computed:

| State | Condition |
|---|---|
| `overdue` | `date_deadline < today` |
| `today` | `date_deadline == today` |
| `planned` | `date_deadline > today` |

---

## Handling Overdue Activities

### Query Overdue Activities

```python
# All overdue activities for crm.lead
overdue = models.execute_kw(db, uid, api_key, 'mail.activity', 'search_read',
    [[['res_model', '=', 'crm.lead'], ['state', '=', 'overdue']]],
    {'fields': ['id', 'res_id', 'summary', 'date_deadline', 'user_id']})

# Overdue for a specific user
overdue_mine = models.execute_kw(db, uid, api_key, 'mail.activity', 'search_read',
    [[['state', '=', 'overdue'], ['user_id', '=', uid]]],
    {'fields': ['id', 'res_id', 'res_name', 'summary', 'date_deadline']})
```

---

## mail.activity Model Fields Table

| Field | Type | Description |
|---|---|---|
| `id` | Integer | Record identifier |
| `res_id` | Integer | Id of the linked record |
| `res_model` | Char | Technical model name (e.g. `"crm.lead"`) |
| `res_model_id` | Many2one (ir.model) | Model reference |
| `res_name` | Char | Display name of the linked record (computed) |
| `activity_type_id` | Many2one (mail.activity.type) | Type of activity |
| `summary` | Char | Short title / subject |
| `note` | Html | Detailed notes |
| `date_deadline` | Date | Due date |
| `user_id` | Many2one (res.users) | Assigned user |
| `state` | Char (computed) | `"overdue"`, `"today"`, `"planned"` |
| `create_date` | Datetime | Creation timestamp |
| `write_date` | Datetime | Last update timestamp |

---

## Best Practices

1. Always set a `date_deadline` — activities without deadlines are hard to prioritise
2. Use specific activity types (Call, Email) rather than generic To-Do for better reporting
3. Write meaningful `summary` values (e.g. "Follow-up call after demo") for clarity
4. Review overdue activities daily via CRM → Activities view
5. Add feedback when marking done to create a paper trail in the chatter
