# Odoo 16 CRM Overview

## Purpose and Positioning

Odoo 16 CRM (Customer Relationship Management) is the sales pipeline management module in the Odoo ERP suite. It provides sales teams with a visual Kanban pipeline, lead and opportunity tracking, activity scheduling, revenue forecasting, and deep integration with email, marketing, invoicing, and other Odoo modules.

CRM is designed to help organisations:
- Capture and qualify sales leads from multiple channels (web, email, phone, import)
- Manage the full sales pipeline from first contact to closed deal
- Schedule and track follow-up activities (calls, emails, meetings)
- Forecast revenue and analyse win/loss performance
- Collaborate across sales teams with shared pipeline views

---

## Key Concepts

### Lead
A **lead** (type = `"lead"`) is an unqualified sales inquiry. It represents a contact or company that has shown interest but has not yet been evaluated. Leads can be created manually, via email aliases, or through web forms.

### Opportunity
An **opportunity** (type = `"opportunity"`) is a qualified lead that has a realistic chance of becoming a sale. Opportunities are tracked through pipeline stages and have associated expected revenue, probability, and deadline.

### Pipeline
The **pipeline** is the visual representation of all active opportunities organised by stage. In Odoo 16, the pipeline is displayed as a Kanban board where each column is a stage.

### Stage
A **stage** (`crm.stage`) represents a step in the sales process (e.g. New, Qualified, Proposal, Negotiation, Won). Stages can be shared across all teams or restricted to a specific sales team.

### Activity
An **activity** (`mail.activity`) is a scheduled task linked to any Odoo record. In CRM, activities are used for follow-up calls, emails, and meetings. They appear in the activity column of the pipeline Kanban view.

### Sales Team
A **sales team** (`crm.team`) groups salespeople together. Each team can have its own pipeline stages, email alias for lead capture, and team targets.

### Partner
A **partner** (`res.partner`) is a contact or company in Odoo's shared address book. Partners can be linked to multiple leads and opportunities.

---

## Main Models

| Model | Technical Name | Description |
|---|---|---|
| Lead/Opportunity | `crm.lead` | Core CRM record; type field distinguishes leads from opportunities |
| Pipeline Stage | `crm.stage` | Stages in the sales pipeline |
| Sales Team | `crm.team` | Groups of salespeople |
| Contact/Company | `res.partner` | Shared address book; linked to leads |
| Activity | `mail.activity` | Scheduled follow-up tasks |
| CRM Tag | `crm.tag` | Labels for categorising leads |
| Lost Reason | `crm.lost.reason` | Reasons for losing an opportunity |
| Activity Type | `mail.activity.type` | Types of activities (call, email, meeting) |

---

## Module Relationships

```
crm.lead ──── stage_id ────► crm.stage
crm.lead ──── team_id ─────► crm.team
crm.lead ──── partner_id ──► res.partner
crm.lead ──── user_id ─────► res.users (salesperson)
crm.lead ──── tag_ids ─────► crm.tag (many2many)
mail.activity ─ res_id ────► crm.lead (via res_model)
crm.team ──── member_ids ──► res.users (salespeople)
```

---

## Reference Links

- Odoo 16 CRM documentation: https://www.odoo.com/documentation/16.0/applications/sales/crm.html
- Odoo JSON-RPC API: https://www.odoo.com/documentation/16.0/developer/reference/external_api.html
- crm.lead model: https://github.com/odoo/odoo/blob/16.0/addons/crm/models/crm_lead.py
