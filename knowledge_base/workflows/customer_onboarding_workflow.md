# Customer Onboarding Workflow

## Purpose

Initiate a structured onboarding process when a CRM opportunity is marked as Won. The workflow validates the partner record, assigns an account manager, creates a series of onboarding activities, and logs a welcome message to the chatter.

---

## Trigger

- Odoo webhook: `lead.won` event
- The `action_set_won` method is called on `crm.lead`
- Manually triggered via the chat interface with a `lead_id`

---

## Inputs

| Parameter | Type | Required | Description |
|---|---|---|---|
| `lead_id` | Integer | Yes | The won opportunity's record id |
| `account_manager_id` | Integer | No | Override account manager assignment |

---

## Workflow Steps

### Step 1: Validate Partner
- Retrieve the won opportunity using `get_lead(lead_id)`
- Check that `partner_id` is set
- Validate required partner fields:
  - `name` (must not be empty)
  - `email` (must be a valid format)
  - `phone` (recommended)
- **Edge case**: If partner is missing → create a minimal partner from lead data and link it

### Step 2: Assign Account Manager
- If `account_manager_id` is provided in context, use it
- Otherwise, assign the salesperson (`user_id`) from the won opportunity
- Update the partner's `user_id` (account manager field)
- **Edge case**: If no salesperson → assign to team leader

### Step 3: Create Onboarding Activities
Create the following activities on `crm.lead`:

| Activity | Type | Due Date | Summary |
|---|---|---|---|
| 1 | Email | today + 1 day | Send welcome email with onboarding guide |
| 2 | Phone Call | today + 3 days | Kickoff call: introductions and expectations |
| 3 | Meeting | today + 7 days | Onboarding session: product walkthrough |
| 4 | To-Do | today + 14 days | Check-in: first two weeks review |

### Step 4: Log to Chatter
- Post an internal note on the opportunity: "Onboarding workflow started on [date]"
- List the activities created with their deadlines
- Tag the account manager in the message

### Step 5: Update CRM Record
- Set a custom tag `onboarding_started` on the opportunity (create if not exists)
- Update `description` to include onboarding start date

---

## Post-Win Partner Validation Checklist

- [ ] Partner name is set
- [ ] Partner email is valid (contains `@`)
- [ ] Partner phone is set
- [ ] Partner `is_company` is correct
- [ ] Account manager is assigned
- [ ] Billing address is set (for invoicing)

---

## Edge Cases

1. **Opportunity not found** → abort with error
2. **Opportunity is not Won** (probability < 100) → log warning, continue anyway
3. **No partner linked** → create partner from lead contact fields
4. **Partner email already exists** → merge or link to existing partner
5. **Activity type IDs not found** → use default type_id 4 (To-Do)

---

## Output

```json
{
  "success": true,
  "steps_executed": ["validate_partner", "assign_am", "create_activities", "log_chatter"],
  "message": "Onboarding initiated for 'Acme Corp — Enterprise Deal'. Partner fields missing: none. 4 activities created.",
  "error": null
}
```
