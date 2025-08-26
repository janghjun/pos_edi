INSERT INTO stores (store_id, store_name, region) VALUES
('ST001','강남점','SEOUL');

INSERT INTO suppliers (supplier_id, supplier_name, biz_reg_no, contact_email, contact_phone) VALUES
('SUP-1001','블루에디션','123-45-67890','blue@supplier.com','02-0000-0000');

INSERT INTO products (sku, product_name, supplier_id, category, brand, unit_price, cost_price) VALUES
('A001','블루 셔츠','SUP-1001','TOP','BLUE',45000,25000),
('A002','화이트 셔츠','SUP-1001','TOP','BLUE',48000,27000);

INSERT INTO inventory_snapshot (store_id, sku, on_hand) VALUES
('ST001','A001', 22),
('ST001','A002', 30);

INSERT INTO inventory_policy (store_id, sku, safety_stock, reorder_point, lead_time_day) VALUES
('ST001','A001', 10, 20, 2),
('ST001','A002', 10, 20, 2);
