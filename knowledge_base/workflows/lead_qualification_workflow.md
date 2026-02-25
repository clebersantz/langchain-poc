# Lead Qualification Workflow

## Purpose

Automatically evaluate new leads using the BANT framework (Budget, Authority, Need, Timeline) and assign them to the appropriate pipeline stage based on their qualification score.

---

## Trigger

- A new lead is created (via API, email, or web form)
- Manually requested by a salesperson via the chat interface
- Odoo webhook: `lead.created` event

---

## Inputs

| Parameter | Type | Required | Description |
|---|---|---|---|
| `lead_id` | Integer | Yes | The `crm.lead` record id to qualify |

---

## Workflow Steps

### Step 1: Get Lead
- Retrieve the full lead record using `get_lead(lead_id)`
- Verify the lead exists and is active
- **Edge case**: If lead not found → abort with error message

### Step 2: BANT Scoring
Score the lead on 4 criteria (25 points each, max 100):

| Criterion | Check | Points |
|---|---|---|
| **Budget** | `expected_revenue > 0` | 25 |
| **Authority** | `partner_id` is set | 25 |
| **Need** | `description` is not empty | 25 |
| **Timeline** | `date_deadline` is set | 25 |

### Step 3: Determine Target Stage

| Score Range | Assigned Stage |
|---|---|
| 75–100 | Qualified |
| 50–74 | In Progress |
| 0–49 | New |

### Step 4: Update Lead
- Write `stage_id` to the target stage
- Update `probability` to the BANT score
- Set `type = 'opportunity'` if score ≥ 50

### Step 5: Assign Salesperson
- If `user_id` is not set, assign to the team's round-robin queue
- **Edge case**: If no team is assigned, leave unassigned and flag for review

### Step 6: Schedule Follow-Up Call
- Create a `mail.activity` of type "Phone Call"
- Set `date_deadline` to today + 1 day (next business day)
- Set `summary` to "Qualification call: {lead_name}"

### Step 7: Log Result
- Write execution result to `workflow_log` table
- Post a note to the lead's chatter with the BANT score and assigned stage

---

## Decision Points

```
Lead exists? ──No──► Abort with error
     │
    Yes
     │
BANT Score ──0-49──► Stage: New (keep as lead)
     │
    50-74──► Stage: In Progress (convert to opportunity)
     │
    75-100──► Stage: Qualified (convert to opportunity)
```

---

## Edge Cases

1. **Lead already an opportunity** — skip conversion step, only update stage and score
2. **Stage "Qualified" doesn't exist** — fall back to the first available stage
3. **No salesperson available** — leave `user_id` unset and add a chatter note
4. **Lead is archived (active=False)** — log warning, do not process
5. **JSON-RPC error on write** — log error, mark workflow as failed

---

## Output

```json
{
  "success": true,
  "steps_executed": ["get_lead", "score", "assign_stage", "schedule_call"],
  "message": "Lead 'Enterprise Inquiry — Acme Corp' scored 75/100 (BANT) and moved to stage 'Qualified'.",
  "error": null
}
```
