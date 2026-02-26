# Lost Lead Recovery Workflow

## Purpose

Re-engage lost CRM leads/opportunities that meet configurable recovery criteria after a cooling-off period has elapsed.

---

## Trigger

- Odoo webhook: `lead.lost` event (scheduled for review after cooling-off)
- Scheduled cron job (weekly review of lost leads)
- Manually triggered via the chat interface

---

## Inputs

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `lead_id` | Integer | No | — | Target a specific lost lead |
| `cooling_off_days` | Integer | No | 30 | Days to wait before attempting recovery |
| `min_revenue` | Float | No | 0 | Minimum `expected_revenue` to attempt recovery |

---

## Workflow Steps

### Step 1: Get Lost Lead(s)
- If `lead_id` provided: retrieve specific lost lead
- Otherwise: search for all lost leads matching criteria:
  ```python
  [
    ['active', '=', False],  # Lost leads are archived
    ['type', '=', 'opportunity'],
    ['write_date', '<', cutoff_date],  # Past cooling-off period
  ]
  ```
- **Edge case**: If no leads found → exit with message "No eligible leads"

### Step 2: Check Recovery Criteria

A lost lead is eligible for recovery if ALL of the following are true:

| Criterion | Condition |
|---|---|
| Revenue threshold | `expected_revenue >= min_revenue` |
| Not already recovered | No open opportunity exists for same partner |
| Lost reason is recoverable | Lost reason is not "Competitor Won" or "Not Interested" |
| Cooling-off period passed | `write_date < today - cooling_off_days` |

### Step 3: Re-activate Lead
- Set `active = True` on the `crm.lead` record
- Reset `stage_id` to "New" or "Qualified" depending on original score
- Clear `lost_reason_id`

### Step 4: Draft Re-engagement Message
Generate a personalised message:
- Reference the original opportunity name
- Acknowledge the time that has passed
- Offer a new value proposition or promotion
- Keep tone warm and non-pushy

### Step 5: Schedule Follow-Up Activity
- Create a `mail.activity` of type "Phone Call"
- Set `date_deadline` to today + 3 days
- Set `summary` to "Recovery call: {lead_name}"
- Include re-engagement message as the `note`

### Step 6: Log Execution
- Write results to `workflow_log` table
- Include count of leads re-activated

---

## Recovery Scoring

Lost leads can be prioritised for recovery based on:

| Factor | Weight |
|---|---|
| High `expected_revenue` | High |
| Lost reason = "Not ready" or "Too expensive" | Medium |
| Previously engaged partner (has email history) | Medium |
| Short time since lost (30–60 days) | High |
| Lost reason = "Competitor won" | Low |

---

## Edge Cases

1. **Lead is already active** — it was re-activated manually; skip
2. **Lead has no partner** — cannot check for duplicate opportunity; proceed anyway
3. **Lost reason is "Spam" or "Duplicate"** — skip; do not re-engage
4. **Salesperson no longer active** — reassign to team leader
5. **JSON-RPC error on write** — log error, mark lead as failed, continue with next

---

## Output

```json
{
  "success": true,
  "steps_executed": ["get_lost_lead", "check_criteria", "draft_reengagement", "schedule_follow_up"],
  "message": "3 lost lead(s) eligible for recovery after 30-day cooling-off period.",
  "error": null
}
```
