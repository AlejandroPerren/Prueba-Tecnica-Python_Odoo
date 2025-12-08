# technical_test_odoo/services/db_service.py
import mysql.connector
from src.config import settings

def get_db_connection():
    """Establishes a new database connection."""
    return mysql.connector.connect(**settings.MYSQL_CONFIG)

def create_payment_event(cursor, amount, date):
    """Inserts a new payment event with a 'PENDING' status."""
    cursor.execute("""
        INSERT INTO payment_events (amount, event_date, sync_status)
        VALUES (%s, %s, 'PENDING')
    """, (amount, date))
    return cursor.lastrowid

def update_payment_event_success(cursor, event_id, odoo_move_id):
    """Updates a payment event to 'COMPLETED'."""
    cursor.execute("""
        UPDATE payment_events
        SET sync_status = 'COMPLETED', odoo_move_id = %s
        WHERE event_id = %s
    """, (odoo_move_id, event_id))

def update_payment_event_failed(cursor, event_id):
    """Updates a payment event to 'FAILED'."""
    cursor.execute("""
        UPDATE payment_events
        SET sync_status = 'FAILED'
        WHERE event_id = %s
    """, (event_id,))
