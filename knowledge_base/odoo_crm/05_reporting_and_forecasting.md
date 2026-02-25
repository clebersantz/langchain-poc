# Odoo 16 CRM Reporting and Forecasting

## Overview

Odoo 16 CRM includes built-in reporting and forecasting tools to help sales managers understand pipeline health, individual and team performance, and projected revenue.

---

## Available Reports

### 1. Pipeline Analysis
- **Path**: CRM → Reporting → Pipeline Analysis
- Shows opportunities grouped by stage, salesperson, or team
- Filter by date range, team, tag, or probability
- Pivot table and bar/line/pie chart views

### 2. Win/Loss Analysis
- Compares won vs. lost opportunities over time
- Shows win rate as a percentage
- Breakdown by lost reason, team, or salesperson

### 3. Activity Report
- Lists scheduled and overdue activities
- Filter by activity type, user, or due date

### 4. Revenue Forecast
- Projects expected revenue based on opportunity probability × expected_revenue
- Grouped by month/quarter/year

---

## Key Metrics

| Metric | How to Compute |
|---|---|
| Pipeline value | `SUM(expected_revenue)` where `type='opportunity'` and `active=True` |
| Weighted pipeline | `SUM(expected_revenue * probability / 100)` |
| Win rate | `COUNT(won) / (COUNT(won) + COUNT(lost)) * 100` |
| Average deal size | `SUM(expected_revenue) / COUNT(id)` where won |
| Days to close | `AVG(date_closed - date_conversion)` |

---

## JSON-RPC Queries for Reporting

### Pipeline Value by Stage

```python
stages = models.execute_kw(db, uid, api_key, 'crm.stage', 'search_read',
    [[]], {'fields': ['id', 'name']})

for stage in stages:
    opps = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
        [[['stage_id', '=', stage['id']], ['type', '=', 'opportunity'], ['active', '=', True]]],
        {'fields': ['expected_revenue']})
    total = sum(o['expected_revenue'] for o in opps)
    print(f"{stage['name']}: ${total:,.0f}")
```

### Win Rate Calculation

```python
total_closed = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_count',
    [[['type', '=', 'opportunity'], ['date_closed', '!=', False]]])

won = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_count',
    [[['type', '=', 'opportunity'], ['probability', '=', 100], ['active', '=', True]]])

win_rate = (won / total_closed * 100) if total_closed else 0
print(f"Win rate: {win_rate:.1f}%")
```

### Monthly Revenue Forecast

```python
import calendar
from datetime import datetime

year, month = 2024, 6
_, last_day = calendar.monthrange(year, month)

opps = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[
        ['type', '=', 'opportunity'],
        ['active', '=', True],
        ['date_deadline', '>=', f'{year}-{month:02d}-01'],
        ['date_deadline', '<=', f'{year}-{month:02d}-{last_day}'],
    ]],
    {'fields': ['name', 'expected_revenue', 'probability']})

forecast = sum(o['expected_revenue'] * o['probability'] / 100 for o in opps)
print(f"June {year} forecast: ${forecast:,.0f}")
```

### Top Salespeople by Revenue

```python
salespeople = models.execute_kw(db, uid, api_key, 'crm.lead', 'read_group',
    [[['type', '=', 'opportunity'], ['active', '=', True]]],
    ['user_id', 'expected_revenue:sum'],
    ['user_id'],
    {'orderby': 'expected_revenue desc', 'limit': 10})
```

---

## Revenue Forecast Fields

The `crm.lead` model includes these forecast-related fields in Odoo 16:

| Field | Description |
|---|---|
| `expected_revenue` | The expected deal value |
| `recurring_revenue` | Monthly recurring revenue (MRR/ARR) |
| `probability` | Current win probability (0–100) |
| `date_deadline` | Expected closing date |
| `date_closed` | Actual closing date (won or lost) |
