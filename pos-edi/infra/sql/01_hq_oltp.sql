SET NAMES utf8mb4;

CREATE TABLE stores (
  store_id    VARCHAR(20) PRIMARY KEY,
  store_name  VARCHAR(100) NOT NULL,
  region      VARCHAR(50),
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE suppliers (
  supplier_id   VARCHAR(20) PRIMARY KEY,
  supplier_name VARCHAR(100) NOT NULL,
  biz_reg_no    VARCHAR(30),
  contact_email VARCHAR(100),
  contact_phone VARCHAR(30),
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE products (
  sku           VARCHAR(30) PRIMARY KEY,
  product_name  VARCHAR(200) NOT NULL,
  supplier_id   VARCHAR(20) NOT NULL,
  category      VARCHAR(100),
  brand         VARCHAR(100),
  unit_price    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  cost_price    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  status        ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_products_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inventory_policy (
  store_id      VARCHAR(20) NOT NULL,
  sku           VARCHAR(30) NOT NULL,
  safety_stock  INT NOT NULL DEFAULT 0,
  reorder_point INT NOT NULL DEFAULT 0,
  lead_time_day INT NOT NULL DEFAULT 2,
  PRIMARY KEY (store_id, sku),
  CONSTRAINT fk_invpol_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
  CONSTRAINT fk_invpol_sku   FOREIGN KEY (sku) REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inventory_snapshot (
  store_id    VARCHAR(20) NOT NULL,
  sku         VARCHAR(30) NOT NULL,
  on_hand     INT NOT NULL DEFAULT 0,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (store_id, sku),
  CONSTRAINT fk_invsnap_store FOREIGN KEY (store_id) REFERENCES stores(store_id),
  CONSTRAINT fk_invsnap_sku   FOREIGN KEY (sku) REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE sales (
  sale_id       VARCHAR(40) PRIMARY KEY,
  store_id      VARCHAR(20) NOT NULL,
  customer_id   VARCHAR(30),
  total_amount  DECIMAL(12,2) NOT NULL,
  discount_amt  DECIMAL(12,2) NOT NULL DEFAULT 0,
  net_amount    DECIMAL(12,2) NOT NULL,
  payment_method ENUM('CASH','CARD','POINT','MIXED') NOT NULL,
  sale_ts       DATETIME NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_sales_store_time (store_id, sale_ts),
  CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES stores(store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE sale_items (
  sale_item_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
  sale_id       VARCHAR(40) NOT NULL,
  sku           VARCHAR(30) NOT NULL,
  qty           INT NOT NULL,
  unit_price    DECIMAL(12,2) NOT NULL,
  discount_amt  DECIMAL(12,2) NOT NULL DEFAULT 0,
  net_amount    DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_sitem_sale FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
  CONSTRAINT fk_sitem_sku  FOREIGN KEY (sku) REFERENCES products(sku),
  INDEX idx_sitem_sale (sale_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE purchase_orders (
  po_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  po_no         VARCHAR(40) NOT NULL UNIQUE,
  supplier_id   VARCHAR(20) NOT NULL,
  store_id      VARCHAR(20) NOT NULL,
  status        ENUM('CREATED','SENT','CONFIRMED','PARTIAL','RECEIVED','CANCELLED') NOT NULL DEFAULT 'CREATED',
  expected_date DATE,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_po_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
  CONSTRAINT fk_po_store    FOREIGN KEY (store_id) REFERENCES stores(store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE po_lines (
  po_line_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  po_id         BIGINT NOT NULL,
  sku           VARCHAR(30) NOT NULL,
  order_qty     INT NOT NULL,
  unit_cost     DECIMAL(12,2) NOT NULL DEFAULT 0,
  received_qty  INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_pl_po  FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
  CONSTRAINT fk_pl_sku FOREIGN KEY (sku) REFERENCES products(sku),
  INDEX idx_pl_po (po_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE asn (
  asn_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  asn_no        VARCHAR(40) NOT NULL UNIQUE,
  po_id         BIGINT NOT NULL,
  eta           DATETIME,
  status        ENUM('CREATED','IN_TRANSIT','ARRIVED','CLOSED','CANCELLED') NOT NULL DEFAULT 'CREATED',
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_asn_po FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE asn_lines (
  asn_line_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
  asn_id        BIGINT NOT NULL,
  sku           VARCHAR(30) NOT NULL,
  ship_qty      INT NOT NULL,
  CONSTRAINT fk_asnl_asn FOREIGN KEY (asn_id) REFERENCES asn(asn_id),
  CONSTRAINT fk_asnl_sku FOREIGN KEY (sku) REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inbound_receipts (
  receipt_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  asn_id        BIGINT NOT NULL,
  store_id      VARCHAR(20) NOT NULL,
  received_at   DATETIME NOT NULL,
  status        ENUM('RECEIVED','PARTIAL','REJECTED') NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_rcp_asn   FOREIGN KEY (asn_id) REFERENCES asn(asn_id),
  CONSTRAINT fk_rcp_store FOREIGN KEY (store_id) REFERENCES stores(store_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE inbound_receipt_lines (
  rcp_line_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
  receipt_id    BIGINT NOT NULL,
  sku           VARCHAR(30) NOT NULL,
  accept_qty    INT NOT NULL,
  reject_qty    INT NOT NULL DEFAULT 0,
  reject_reason VARCHAR(200),
  CONSTRAINT fk_rcpl_rcp FOREIGN KEY (receipt_id) REFERENCES inbound_receipts(receipt_id),
  CONSTRAINT fk_rcpl_sku FOREIGN KEY (sku) REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE settlements (
  settlement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  period        CHAR(7) NOT NULL,
  supplier_id   VARCHAR(20) NOT NULL,
  gross_sales   DECIMAL(14,2) NOT NULL DEFAULT 0,
  fee_rate_pct  DECIMAL(5,2)  NOT NULL DEFAULT 0,
  fee_amount    DECIMAL(14,2) NOT NULL DEFAULT 0,
  payable_amt   DECIMAL(14,2) NOT NULL DEFAULT 0,
  status        ENUM('DRAFT','FINALIZED','PAID') NOT NULL DEFAULT 'DRAFT',
  generated_at  DATETIME NOT NULL,
  UNIQUE KEY uk_settle_period_supplier (period, supplier_id),
  CONSTRAINT fk_settle_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE settlement_lines (
  stl_line_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
  settlement_id BIGINT NOT NULL,
  sku           VARCHAR(30) NOT NULL,
  sales_amt     DECIMAL(14,2) NOT NULL DEFAULT 0,
  fee_amount    DECIMAL(14,2) NOT NULL DEFAULT 0,
  pay_amount    DECIMAL(14,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_stll_settle FOREIGN KEY (settlement_id) REFERENCES settlements(settlement_id),
  CONSTRAINT fk_stll_sku    FOREIGN KEY (sku) REFERENCES products(sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE event_outbox (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  topic         VARCHAR(100) NOT NULL,
  payload       JSON NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  published_at  TIMESTAMP NULL,
  status        ENUM('PENDING','PUBLISHED','FAILED') NOT NULL DEFAULT 'PENDING',
  INDEX idx_outbox_status_created (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
