# What is Odoo and Odoo CRM?

## What is Odoo?

**Odoo** is an open-source suite of integrated business applications (ERP — Enterprise Resource Planning) designed to help companies manage all aspects of their operations from a single platform. Originally named OpenERP, it was rebranded to Odoo in 2014.

Key characteristics of Odoo:
- **Open-source**: The Community Edition is free and open-source (LGPL licence). An Enterprise Edition with additional features and official support is available via subscription.
- **Modular**: Organisations install only the modules they need and add more as the business grows.
- **Integrated**: All modules share a common database and framework, so data flows automatically between them (e.g., a sales order created in CRM becomes an invoice in Accounting without re-entry).
- **Web-based**: Accessible via any modern browser; no desktop client required.
- **Versions**: The current stable version is Odoo 16 (LTS). Odoo 17 is the latest release.

### Main Odoo Application Modules

| Module | Description |
|---|---|
| **CRM** | Customer Relationship Management — leads, opportunities, pipeline |
| **Sales** | Quotations, sales orders, customer management |
| **Invoicing / Accounting** | Invoices, payments, journal entries, financial reports |
| **Inventory** | Stock management, warehousing, delivery orders |
| **Purchase** | Purchase orders, vendor management, RFQs |
| **Project** | Task management, project planning, timesheets |
| **HR / Employees** | Employee records, leaves, payroll |
| **Marketing** | Email marketing, SMS campaigns, social media |
| **Website / eCommerce** | Website builder, online store |
| **Helpdesk** | Customer support tickets |
| **Manufacturing** | Production orders, BoMs, work centres |
| **Point of Sale** | Retail POS system |

---

## What is Odoo CRM?

**Odoo CRM** (Customer Relationship Management) is the sales pipeline and lead management module within the Odoo suite. It helps sales teams capture leads, qualify opportunities, manage the full sales cycle, and forecast revenue — all through a visual Kanban interface.

### Core Purpose

Odoo CRM is designed to:
- **Capture leads** from multiple sources: web forms, emails, phone calls, imports, live chat
- **Qualify and convert** leads into sales opportunities
- **Manage the sales pipeline** visually with drag-and-drop Kanban stages
- **Track activities** such as calls, emails, and meetings with automated reminders
- **Forecast revenue** based on opportunity probability and expected closing dates
- **Analyse performance** through win/loss reports, sales team metrics, and forecasting dashboards
- **Collaborate** across sales teams with shared pipeline views and assignments

---

## How Odoo CRM Works — Workflow

### Typical Sales Workflow in Odoo CRM

```
1. Lead Capture
   (web form / email alias / manual entry / import)
        ↓
2. Lead Qualification
   (sales rep reviews: add contact info, assign to team, assess potential)
        ↓
3. Convert Lead → Opportunity
   (type changes from "lead" to "opportunity", added to pipeline)
        ↓
4. Pipeline Stages
   New → Qualified → Proposition → Negotiation → Won / Lost
        ↓
5. Activities & Follow-ups
   (schedule calls, meetings, emails; mark done when complete)
        ↓
6. Close Deal
   - Won: marks opportunity as won (probability = 100%)
   - Lost: archives opportunity with a lost reason
```

### Pipeline Stages (Default in Odoo 16)

| Stage | Default Probability | Description |
|---|---|---|
| New | 10% | Freshly created opportunity |
| Qualified | 25% | Interest confirmed, needs assessed |
| Proposition | 50% | Proposal or quote sent |
| Won | 100% | Deal closed successfully |

Stages are configurable: teams can create custom stages with specific sequences, probabilities, and requirements.

---

## Key Odoo CRM Features

### 1. Visual Kanban Pipeline
The pipeline is displayed as a Kanban board (columns = stages, cards = opportunities). Sales reps can drag and drop opportunities between stages, see activity status indicators, and quick-create new opportunities.

### 2. Lead and Opportunity Management
- **Leads** (`type = "lead"`): unqualified inquiries not yet added to the pipeline
- **Opportunities** (`type = "opportunity"`): qualified prospects tracked through the pipeline
- Both are stored in the `crm.lead` model in Odoo's database

### 3. Activity Scheduling
Activities (`mail.activity`) are scheduled tasks: phone calls, emails, meetings. They have deadlines, assignees, and summary notes. Overdue activities are highlighted in red on the Kanban board.

### 4. Email Integration
- Each sales team has an email alias (e.g., `sales@company.com`) — inbound emails auto-create leads
- Outbound emails are logged on the opportunity chatter
- Email templates are available for common communications

### 5. Revenue Forecasting
The CRM forecasting view shows expected revenue per stage and per month, using opportunity probability to calculate weighted revenue. Sales managers use this for pipeline reviews and quota tracking.

### 6. Reporting and Dashboards
Built-in reports include:
- Pipeline analysis (opportunities by stage, team, salesperson)
- Win/Loss analysis by reason, team, or period
- Activity reports (overdue, upcoming)
- Revenue forecasting by month/quarter

### 7. Sales Teams
Sales teams (`crm.team`) group salespeople together. Each team can have:
- Its own pipeline stages
- Dedicated email alias for lead capture
- Team-specific revenue targets

### 8. Integration with Other Odoo Modules
- **Sales**: Won opportunities can be converted directly to sales quotations
- **Invoicing**: Sales orders from CRM flow into invoices
- **Email Marketing**: Mass campaigns target leads/contacts in CRM
- **Calendar**: CRM meetings sync with the shared calendar
- **Website**: Web forms capture leads directly into CRM

---

## Odoo CRM Data Model

The core models used in Odoo 16 CRM:

| Model | Technical Name | Role |
|---|---|---|
| Lead / Opportunity | `crm.lead` | Central CRM record; `type` field distinguishes leads from opportunities |
| Pipeline Stage | `crm.stage` | Steps in the sales process |
| Sales Team | `crm.team` | Groups of salespeople |
| Contact / Company | `res.partner` | Shared address book linked to leads |
| Activity | `mail.activity` | Scheduled follow-up tasks |
| CRM Tag | `crm.tag` | Labels for categorising leads |
| Lost Reason | `crm.lost.reason` | Reasons recorded when an opportunity is lost |
| Activity Type | `mail.activity.type` | Types: call, email, meeting, to-do |

---

## Odoo CRM API

Odoo CRM is fully accessible via the **Odoo JSON-RPC external API** (also called the XML-RPC compatible JSON endpoint). All CRM operations — creating leads, reading pipeline stages, updating opportunities, scheduling activities — can be performed programmatically.

### Authentication

```python
uid = json_rpc("common", "login", [db, username, api_key])
```

### Create a Lead

```python
lead_id = json_rpc("object", "execute_kw",
    [db, uid, api_key, "crm.lead", "create", [{
        "name": "New Inquiry",
        "contact_name": "John Doe",
        "email_from": "john@example.com",
        "type": "lead",
    }]])
```

### Read Opportunities

```python
opportunities = json_rpc("object", "execute_kw",
    [db, uid, api_key, "crm.lead", "search_read",
     [[["type", "=", "opportunity"], ["active", "=", True]]],
     {"fields": ["name", "stage_id", "expected_revenue"], "limit": 50}])
```

Full API reference: see `08_crm_api_reference.md`.

---

## Odoo CRM — Frequently Asked Questions

**Q: What is Odoo CRM?**
A: Odoo CRM is the Customer Relationship Management module in the Odoo open-source ERP platform. It provides a visual Kanban pipeline to manage leads and sales opportunities through stages from first contact to closed deal.

**Q: Is Odoo CRM free?**
A: The Community Edition of Odoo CRM is free and open-source. The Enterprise Edition, which includes additional features such as advanced forecasting and mobile apps, requires an Odoo subscription.

**Q: What is the difference between a Lead and an Opportunity in Odoo?**
A: Both are records in the `crm.lead` model. A **Lead** is an unqualified contact that has not yet been evaluated. An **Opportunity** is a qualified lead that has been added to the pipeline with a stage, expected revenue, and probability.

**Q: How does Odoo CRM integrate with other Odoo modules?**
A: Won opportunities can be converted to quotations in the Sales module, which then flow to Invoicing. CRM contacts are shared with the full Odoo address book. Marketing campaigns target CRM leads directly. Calendar activities appear in the shared company calendar.

**Q: What versions of Odoo CRM are available?**
A: Odoo releases new major versions annually. Odoo 16 is a Long-Term Support (LTS) release widely used in production. Odoo 17 is the latest version. This system is configured for **Odoo 16**.
