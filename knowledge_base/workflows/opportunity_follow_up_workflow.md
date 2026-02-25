# Opportunity Follow-Up Workflow

## Purpose

Detect stale opportunities that have not been updated within a configurable threshold and automatically schedule follow-up activities to re-engage them.

---

## Trigger

- Scheduled job (daily, via Odoo automation or external cron)
- Manually triggered via the chat interface
- API call to `POST /workflows/run` with `workflow_name: "opportunity_follow_up"`

---

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `stale_days` | Integer | No | 14 | Days without update before considering stale |
| `user_id` | Integer | No | — | Filter to a specific salesperson's opportunities |
| `team_id` | Integer | No | — | Filter to a specific team's opportunities |

---

## Workflow Steps

### Step 1: Detect Stale Opportunities
- Query `crm.lead` with domain:
  ```python
  [
    ['type', '=', 'opportunity'],
    ['active', '=', True],
    ['write_date', '<', cutoff_date],
  ]
  ```
- `cutoff_date = today - stale_days`
- **Edge case**: If no stale opportunities → exit with success message

### Step 2: Filter Eligible Opportunities
- Skip opportunities that already have a pending activity (type = "planned")
- Skip opportunities in the "Won" stage
- Optionally filter by `user_id` or `team_id` from context

### Step 3: Draft Re-Engagement Message
For each stale opportunity, generate a personalised message:
- Include the opportunity name and days since last update
- Reference any previously completed activities
- Tailor the message based on the pipeline stage

### Step 4: Schedule Follow-Up Activity
For each eligible opportunity:
- Create a `mail.activity` of type "Phone Call" or "Email"
- Set `date_deadline` to today + 2 days
- Set `summary` to "Re-engage: {opportunity_name} (stale {days} days)"
- Set `note` with the drafted message

### Step 5: Log Execution
- Write results to `workflow_log` table
- Include count of opportunities processed and activities created

---

## Configurable Thresholds

| Setting | Default | Recommendation |
|---|---|---|
| `stale_days` | 14 | Adjust based on average sales cycle length |
| Activity type | Phone Call | Use Email for passive re-engagement |
| Days until deadline | 2 | Keep short to ensure prompt follow-up |

---

## Edge Cases

1. **All opportunities have recent activity** — exit early with count=0
2. **Opportunity stage is "Won"** — skip; already closed
3. **User has too many overdue activities** — log warning; still create activity
4. **XML-RPC error on activity creation** — log error, continue with next opportunity
5. **Context has invalid `user_id`** — ignore filter, process all eligible

---

## Output

```json
{
  "success": true,
  "steps_executed": ["detect_stale", "draft_message", "schedule_activity"],
  "message": "Found 8 stale opportunities older than 14 days. Follow-up activities scheduled.",
  "error": null
}
```
