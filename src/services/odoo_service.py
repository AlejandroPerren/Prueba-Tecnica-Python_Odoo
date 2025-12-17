import xmlrpc.client
from functools import lru_cache
from src.config import settings


class OdooService:
    def __init__(self, settings):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.user = settings.ODOO_USER
        self.password = settings.ODOO_PASSWORD

        try:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            if not self.uid:
                raise ConnectionAbortedError("Authentication failed to Odoo.")
            self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        except Exception as e:
            # Wrap lower-level exceptions into a more specific one
            raise ConnectionError(f"Failed to connect to Odoo: {e}") from e

    def get_account_id_by_code(self, code: str) -> int:
        """Fetch an account ID from Odoo by its code."""
        account_ids = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "account.account",
            "search_read",
            [[["code", "=", code]]],
            {"fields": ["id"], "limit": 1},
        )
        if not account_ids:
            raise ValueError(f"Account with code {code} not found in Odoo.")
        return account_ids[0]["id"]

    def get_cash_journal_id(self) -> int:
        """Fetch the first cash journal ID from Odoo."""
        journal_ids = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "account.journal",
            "search_read",
            [[["type", "=", "cash"]]],
            {"fields": ["id"], "limit": 1},
        )
        if not journal_ids:
            raise ValueError("No cash journal found in Odoo.")
        return journal_ids[0]["id"]

    def create_account_move(self, move_vals: dict) -> int:
        """Create a new account move in Odoo."""
        move_id = self.models.execute_kw(
            self.db, self.uid, self.password, "account.move", "create", [move_vals]
        )
        return move_id

    def post_account_move(self, move_id: int):
        """Post (publish) an account move in Odoo."""
        self.models.execute_kw(
            self.db, self.uid, self.password, "account.move", "action_post", [[move_id]]
        )


@lru_cache()
def get_odoo_service():
    return OdooService(settings)


odoo_service_instance = get_odoo_service()
