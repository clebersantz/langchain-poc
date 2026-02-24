#!/usr/bin/env python3
"""CLI script to test the Odoo XML-RPC connection.

Usage:
    python scripts/test_odoo_connection.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.odoo.client import odoo_client


def main() -> None:
    """Authenticate to Odoo and print version info."""
    print("Testing Odoo connection...")
    print(f"  URL: {odoo_client._url}")
    print(f"  DB:  {odoo_client._db}")
    print(f"  User: {odoo_client._user}")

    try:
        version = odoo_client.get_version()
        print(f"\n  Odoo server version: {version.get('server_version')}")
        print(f"  Protocol version:    {version.get('protocol_version')}")

        uid = odoo_client.authenticate()
        print(f"\n  Authentication successful. UID: {uid}")

        # Quick sanity check
        lead_count = odoo_client.execute("crm.lead", "search_count", [])
        print(f"  Total crm.lead records: {lead_count}")

        print("\nConnection test PASSED.")
    except Exception as exc:
        print(f"\nConnection test FAILED: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
