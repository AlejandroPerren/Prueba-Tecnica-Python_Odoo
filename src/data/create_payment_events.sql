CREATE TABLE IF NOT EXISTS CREATE TABLE payment_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    event_date DATETIME NOT NULL,
    odoo_move_id INT NULL,
    sync_status ENUM('PENDING', 'COMPLETED', 'FAILED') NOT NULL
);
