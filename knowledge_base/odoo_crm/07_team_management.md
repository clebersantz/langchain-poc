# Odoo 16 CRM Team Management

## Overview

Sales teams in Odoo 16 group salespeople together for pipeline management, reporting, and target tracking. Each team can have its own pipeline stages, email alias, and performance targets.

---

## Creating a Sales Team

1. Go to **CRM → Configuration → Sales Teams**
2. Click **New**
3. Fill in the team name, team leader, and email alias
4. Add members (salespeople)
5. Configure optional target revenue

---

## crm.team Fields Table

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Auto | Record identifier |
| `name` | Char | Yes | Team display name |
| `user_id` | Many2one (res.users) | No | Team leader / manager |
| `member_ids` | Many2many (res.users) | No | Salespeople in the team |
| `alias_id` | Many2one (mail.alias) | No | Email alias for lead capture |
| `alias_email` | Char (related) | No | Email alias address |
| `target_sales_won` | Integer | No | Monthly target: won opportunities |
| `target_sales_done` | Integer | No | Monthly target: activities done |
| `target_sales_invoiced` | Integer | No | Monthly target: invoiced revenue |
| `active` | Boolean | No | False = archived (default True) |

---

## Assigning Salespeople to Teams

### Via UI
1. Open a Sales Team record
2. Add users to the **Members** field
3. Save

### Via XML-RPC

```python
# Get team
team = models.execute_kw(db, uid, api_key, 'crm.team', 'search_read',
    [[['name', '=', 'Sales']]],
    {'fields': ['id', 'member_ids']})[0]

# Add a member
new_user_id = 5
models.execute_kw(db, uid, api_key, 'crm.team', 'write',
    [[team['id']], {'member_ids': [(4, new_user_id)]}])
# (4, id) = link existing record; (3, id) = unlink; (5,) = unlink all
```

---

## Round-Robin Assignment

Odoo 16 CRM supports automatic lead assignment in round-robin order:
- Enable: **CRM → Configuration → Settings → Leads Assignment**
- Leads are distributed equally among team members
- Assignment runs on a configurable schedule (daily/weekly/manual)

### Triggering Assignment via XML-RPC

```python
# Trigger manual assignment for a team
models.execute_kw(db, uid, api_key, 'crm.team', 'action_assign_leads',
    [[team_id]])
```

---

## Team-Specific Pipeline Stages

By setting `team_id` on a `crm.stage`, you restrict that stage to a specific team:

```python
# Create a team-specific stage
stage_id = models.execute_kw(db, uid, api_key, 'crm.stage', 'create', [{
    'name': 'Custom Stage',
    'sequence': 5,
    'probability': 40,
    'team_id': team_id,  # Link to a specific team
}])
```

---

## Querying Teams via XML-RPC

```python
# Get all active teams
teams = models.execute_kw(db, uid, api_key, 'crm.team', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['id', 'name', 'user_id', 'member_ids']})

# Get team members
team_id = 1
team = models.execute_kw(db, uid, api_key, 'crm.team', 'search_read',
    [[['id', '=', team_id]]],
    {'fields': ['member_ids']})[0]

members = models.execute_kw(db, uid, api_key, 'res.users', 'search_read',
    [[['id', 'in', team['member_ids']]]],
    {'fields': ['id', 'name', 'email', 'login']})
```

---

## Best Practices

1. Keep teams small and focused (5–10 salespeople per team)
2. Assign a dedicated team leader to manage performance
3. Use team-specific stages only when the sales process differs significantly
4. Set realistic monthly targets based on historical data
5. Review team performance weekly using the CRM Dashboard
