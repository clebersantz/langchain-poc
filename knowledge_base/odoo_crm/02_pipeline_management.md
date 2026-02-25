# Odoo 16 CRM Pipeline Management

## Overview

The CRM pipeline in Odoo 16 is the central workspace for managing sales opportunities. It provides a visual Kanban board where each column represents a pipeline stage and each card represents an opportunity.

---

## Views

### Kanban View (default)
- Each column = one pipeline stage
- Cards show: opportunity name, expected revenue, activity status, assigned user
- Drag-and-drop to move opportunities between stages
- Quick-create opportunities directly from a column header
- Folded stages collapse to save space

### List View
- Tabular display with sortable columns
- Useful for bulk actions (assign, stage change, delete)
- Supports advanced filters and group-by

---

## Configuring Stages

Stages are configured in **CRM → Configuration → Stages**.

### Stage Fields

| Field | Type | Description |
|---|---|---|
| `name` | Char | Display name of the stage |
| `sequence` | Integer | Order of the stage in the pipeline (lower = earlier) |
| `probability` | Float | Default probability (0–100%) for opportunities in this stage |
| `fold` | Boolean | Whether to fold (collapse) this stage in the Kanban view |
| `team_id` | Many2one (crm.team) | If set, stage is only visible for this team; otherwise shared |
| `requirements` | Text | Internal notes on what is required to reach this stage |
| `is_won` | Boolean | Marks this stage as the "Won" stage (read-only, managed by Odoo) |

### Default Stages in Odoo 16

1. **New** (sequence 1, probability 10%)
2. **Qualified** (sequence 2, probability 25%)
3. **Proposition** (sequence 3, probability 50%)
4. **Won** (sequence 70, probability 100%, is_won=True)

---

## Moving Opportunities Through Stages

### Via UI
- Drag and drop in Kanban view
- Click the stage name in the form view status bar
- Use the "Won" button (sets probability=100 and closes the opportunity)

### Via JSON-RPC

```python
# Move opportunity to a stage by stage_id
client.execute_kw(db, uid, api_key, 'crm.lead', 'write',
    [[opportunity_id], {'stage_id': target_stage_id}])

# Get stage id by name
stages = client.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[['name', '=', 'Qualified']]], {'fields': ['id', 'name']})
stage_id = stages[0]['id']
```

---

## crm.stage Model Fields Table

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Auto | Record identifier |
| `name` | Char | Yes | Stage display name |
| `sequence` | Integer | No | Display order (default 1) |
| `probability` | Float | No | Automated probability override (0–100) |
| `fold` | Boolean | No | Fold in Kanban? (default False) |
| `team_id` | Many2one | No | Limit stage to one team; None = shared |
| `requirements` | Text | No | Notes on stage requirements |
| `is_won` | Boolean | Computed | True if this is a "Won" stage |

---

## Filters and Grouping

### Common Filters
- **My Pipeline** — filter to current user's opportunities
- **My Team** — filter to current user's sales team
- **Won** / **Lost** — show closed opportunities
- **Overdue** — activities past their deadline

### Common Group-By
- **Stage** (default)
- **Salesperson**
- **Sales Team**
- **Expected Closing** (month/quarter)
- **Company**

### JSON-RPC Domain Examples

```python
# All open opportunities
[['type', '=', 'opportunity'], ['active', '=', True]]

# Opportunities for a specific stage
[['stage_id.name', '=', 'Qualified'], ['type', '=', 'opportunity']]

# Opportunities closing this month
from datetime import datetime, timedelta
[['date_deadline', '>=', '2024-01-01'], ['date_deadline', '<=', '2024-01-31']]

# High-value opportunities (> 10000)
[['expected_revenue', '>', 10000], ['type', '=', 'opportunity']]
```

---

## Best Practices

1. Keep stages to 5–7 steps to avoid complexity
2. Use team-specific stages only when teams have fundamentally different sales processes
3. Set meaningful default probabilities for each stage for accurate forecasting
4. Archive (fold) stages that are no longer active rather than deleting them
5. Use the "Won" button rather than manually setting stage, to properly close revenue
