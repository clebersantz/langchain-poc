#!/usr/bin/env python3
"""CLI script to seed 5 sample leads into Odoo 16 for testing.

Usage:
    python scripts/seed_test_data.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.odoo.models.crm_lead import create_lead

SAMPLE_LEADS = [
    {
        "name": "Enterprise Deal — Acme Corp",
        "contact_name": "Alice Johnson",
        "email_from": "alice@acme.com",
        "phone": "+1-555-0001",
        "expected_revenue": 50000,
        "description": "Interested in the Enterprise plan. Budget approved for Q3.",
        "type": "lead",
    },
    {
        "name": "SMB Opportunity — BrightTech",
        "contact_name": "Bob Williams",
        "email_from": "bob@brighttech.io",
        "phone": "+1-555-0002",
        "expected_revenue": 12000,
        "description": "Looking for CRM integration with existing ERP.",
        "type": "lead",
    },
    {
        "name": "Startup Inquiry — NovaSoft",
        "contact_name": "Carol Davis",
        "email_from": "carol@novasoft.dev",
        "phone": "+1-555-0003",
        "expected_revenue": 5000,
        "description": "Early stage startup, limited budget but high growth potential.",
        "type": "lead",
    },
    {
        "name": "Renewal — RetailPlus",
        "contact_name": "David Martinez",
        "email_from": "david@retailplus.com",
        "phone": "+1-555-0004",
        "expected_revenue": 25000,
        "description": "Contract renewal coming up. Interested in upgrading to Pro.",
        "type": "opportunity",
    },
    {
        "name": "Upsell — HealthCo",
        "contact_name": "Emma Wilson",
        "email_from": "emma@healthco.org",
        "phone": "+1-555-0005",
        "expected_revenue": 18000,
        "description": "Current customer. Interested in adding 10 more user licenses.",
        "type": "opportunity",
    },
]


def main() -> None:
    """Create 5 sample leads in Odoo."""
    print("Seeding test data into Odoo...")
    created = []
    for lead_data in SAMPLE_LEADS:
        try:
            lead_id = create_lead(lead_data)
            print(f"  Created lead id={lead_id}: {lead_data['name']}")
            created.append(lead_id)
        except Exception as exc:
            print(f"  ERROR creating '{lead_data['name']}': {exc}")

    print(f"\nDone. Created {len(created)}/{len(SAMPLE_LEADS)} leads: {created}")


if __name__ == "__main__":
    main()
