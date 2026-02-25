# Odoo 16 Email Marketing Integration

## Overview

Odoo 16 CRM integrates tightly with the Email module, enabling automated lead capture from inbound emails and outbound campaigns via mass mailing.

---

## Email Aliases Creating Leads

Each Sales Team can have a dedicated email alias. When an email is sent to that alias:
1. Odoo creates a new `crm.lead` record
2. The lead is assigned to the team's email alias
3. The email body becomes the lead description
4. The sender's email is stored in `email_from`

### Configuring an Email Alias
1. Go to **CRM → Configuration → Sales Teams**
2. Select a team
3. Set the **Email Alias** field (e.g. `sales@yourcompany.com`)
4. Save

### How Aliases Work
- Odoo's `mail.catchall` domain handles routing
- Emails not matching any alias go to the catchall
- Requires mail server configuration (`Settings → Technical → Email → Incoming Mail Servers`)

---

## Mass Mailing Integration

Odoo 16 includes a **Email Marketing** module that integrates with CRM:

1. Create a mailing list from CRM leads
2. Design an email campaign with the drag-and-drop editor
3. Send to a segment of leads/contacts
4. Track opens, clicks, and bounces
5. Automatically log activity on leads whose emails are opened

### Creating a Mailing from CRM Leads via XML-RPC

```python
# Get lead email addresses
leads = models.execute_kw(db, uid, api_key, 'crm.lead', 'search_read',
    [[['type', '=', 'lead'], ['active', '=', True]]],
    {'fields': ['email_from', 'contact_name', 'partner_id']})

# Create a contact list
contact_list_id = models.execute_kw(db, uid, api_key, 'mailing.list', 'create', [{
    'name': 'New Leads Q1 2024',
}])
```

---

## Email Templates for CRM

Odoo uses `mail.template` records for standardised emails. CRM-related templates can be triggered by:
- Manual send from a lead
- Automated actions
- Scheduled activities of type "Email"

### Sending a Template Email to a Lead via XML-RPC

```python
# Find the template id
templates = models.execute_kw(db, uid, api_key, 'mail.template', 'search_read',
    [[['model', '=', 'crm.lead'], ['name', 'ilike', 'Follow']]],
    {'fields': ['id', 'name']})
template_id = templates[0]['id']

# Send the email
models.execute_kw(db, uid, api_key, 'mail.template', 'send_mail',
    [template_id, lead_id], {'force_send': True})
```

---

## Lead Scoring from Email Engagement

Odoo 16 supports basic lead scoring through email engagement metrics:
- Email **open** → increases `probability` by a configured amount
- Email **click** → increases `probability` further
- Email **bounce/unsubscribe** → may decrease priority

Lead scoring rules are configured in **CRM → Configuration → Lead Mining** (requires `crm_iap_lead` module).

---

## Best Practices

1. Use meaningful alias names to make routing predictable
2. Set up a catchall address to avoid losing emails with no alias match
3. Combine email campaigns with lead scoring for warm lead identification
4. Archive leads that bounce or unsubscribe to keep the pipeline clean
5. Use email templates to standardise follow-up messaging across the team
