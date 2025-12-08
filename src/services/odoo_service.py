# technical_test_odoo/services/odoo_service.py
import xmlrpc.client
from src.config import settings

def get_odoo_uid():
    """Authenticate with Odoo and return the user ID."""
    common = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD, {})
    if not uid:
        raise Exception("Authentication failed to Odoo.")
    return uid

def get_odoo_models_proxy():
    """Return the Odoo models proxy."""
    return xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/object")

def get_account_id_by_code(models, db, uid, pwd, code):
    """Fetch an account ID from Odoo by its code."""
    account_ids = models.execute_kw(
        db, uid, pwd,
        "account.account", "search_read",
        [[["code", "=", code]]],
        {"fields": ["id"], "limit": 1}
    )
    if not account_ids:
        raise Exception(f"Account with code {code} not found in Odoo.")
    return account_ids[0]["id"]

def get_cash_journal_id(models, db, uid, pwd):
    """Fetch the first cash journal ID from Odoo."""
    journal_ids = models.execute_kw(
        db, uid, pwd,
        "account.journal", "search_read",
        [[["type", "=", "cash"]]],
        {"fields": ["id"], "limit": 1}
    )
    if not journal_ids:
        raise Exception("No cash journal found in Odoo.")
    return journal_ids[0]["id"]

def create_account_move(models, db, uid, pwd, move_vals):
    """Create a new account move in Odoo."""
    move_id = models.execute_kw(
        db, uid, pwd,
        "account.move", "create", [move_vals]
    )
    return move_id
