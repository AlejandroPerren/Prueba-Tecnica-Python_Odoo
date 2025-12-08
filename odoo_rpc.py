import xmlrpc.client

class OdooRPC:
    def __init__(self, url, db, user, password):
        self.url = url
        self.db = db
        self.user = user
        self.password = password
        
        self.common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        self.uid = self.common.authenticate(db, user, password, {})
        self.models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def create_move(self, amount):
        move_vals = {
            "journal_id": 1, 
            "ref": "Pago recibido via API",
            "line_ids": [
                (0, 0, {
                    "account_id": 1,  
                    "debit": amount,
                    "credit": 0,
                }),
                (0, 0, {
                    "account_id": 2, 
                    "debit": 0,
                    "credit": amount,
                }),
            ]
        }
        
        move_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "account.move",
            "create",
            [move_vals]
        )

        return move_id
