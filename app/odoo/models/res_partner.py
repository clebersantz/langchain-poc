"""Odoo 16 res.partner model helpers."""

from app.odoo.client import odoo_client

FIELDS = [
    "id",
    "name",
    "email",
    "phone",
    "mobile",
    "street",
    "city",
    "country_id",
    "is_company",
    "customer_rank",
    "supplier_rank",
    "active",
]


def search_partners(query: str, limit: int = 20) -> list[dict]:
    """Search partners by name or email.

    Args:
        query: Search string matched against name and email.
        limit: Maximum records to return.

    Returns:
        list[dict]: Matching partner records.
    """
    domain = ["|", ["name", "ilike", query], ["email", "ilike", query]]
    return odoo_client.search_read("res.partner", domain, FIELDS, limit=limit)


def get_partner(partner_id: int) -> dict:
    """Return a single partner by id.

    Args:
        partner_id: Odoo record id.

    Returns:
        dict: Partner record, or empty dict if not found.
    """
    results = odoo_client.search_read(
        "res.partner", [["id", "=", partner_id]], FIELDS, limit=1
    )
    return results[0] if results else {}


def create_partner(values: dict) -> int:
    """Create a new partner.

    Args:
        values: Field values for the new partner.

    Returns:
        int: The id of the newly created partner.
    """
    return odoo_client.create("res.partner", values)


def update_partner(partner_id: int, values: dict) -> bool:
    """Update an existing partner.

    Args:
        partner_id: Record id to update.
        values: Fields to write.

    Returns:
        bool: True on success.
    """
    return odoo_client.write("res.partner", [partner_id], values)
