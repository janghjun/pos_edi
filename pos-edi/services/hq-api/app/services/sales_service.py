from datetime import datetime, timedelta
from app.db.session import q
import json

def process_sale_event(db, event):
    # 1) persist sale
    total = sum(i["unit_price"] * i["qty"] for i in event["items"])
    discount = sum(i.get("discount",0) for i in event["items"])
    net = total - discount
    q(db, """
        INSERT INTO sales (sale_id, store_id, customer_id, total_amount, discount_amt, net_amount, payment_method, sale_ts)
        VALUES (:sale_id,:store_id,:customer_id,:total,:disc,:net,:pm,:ts)
        ON DUPLICATE KEY UPDATE sale_id=sale_id
    """, sale_id=event["pos_txn_id"], store_id=event["store_id"], customer_id=event.get("customer_id"),
        total=total, disc=discount, net=net, pm=event.get("payment",{}).get("method","CARD"), ts=event["event_ts"])
    for it in event["items"]:
        net_amt = it["qty"] * it["unit_price"] - it.get("discount",0)
        q(db, """
            INSERT INTO sale_items (sale_id, sku, qty, unit_price, discount_amt, net_amount)
            VALUES (:sale_id,:sku,:qty,:price,:disc,:net)
        """, sale_id=event["pos_txn_id"], sku=it["sku"], qty=it["qty"], price=it["unit_price"], disc=it.get("discount",0), net=net_amt)
        q(db, """
            INSERT INTO inventory_snapshot (store_id, sku, on_hand)
            VALUES (:store,:sku, GREATEST(0, 0-:qty))
            ON DUPLICATE KEY UPDATE on_hand = GREATEST(0, on_hand-:qty)
        """, store=event["store_id"], sku=it["sku"], qty=it["qty"])

    # 2) reorder check -> create PO + outbox po.v1
    auto_po = []
    for it in event["items"]:
        row = q(db, """
            SELECT s.on_hand, p.reorder_point, p.lead_time_day, pr.supplier_id
            FROM inventory_snapshot s
            JOIN inventory_policy p ON p.store_id=s.store_id AND p.sku=s.sku
            JOIN products pr ON pr.sku=s.sku
            WHERE s.store_id=:store AND s.sku=:sku
        """, store=event["store_id"], sku=it["sku"]).mappings().first()
        if not row:
            continue
        on_hand, rp, lead, sup = row["on_hand"], row["reorder_point"], row["lead_time_day"], row["supplier_id"]
        if on_hand < rp:
            order_qty = max(rp * 2 - on_hand, 1)
            po_no = f"PO-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{it['sku']}"
            q(db, """
                INSERT INTO purchase_orders (po_no, supplier_id, store_id, status, expected_date)
                VALUES (:po_no,:sup,:store,'CREATED',:exp)
            """, po_no=po_no, sup=sup, store=event["store_id"], exp=(datetime.utcnow()+timedelta(days=lead)).date())
            po_id = q(db, "SELECT po_id FROM purchase_orders WHERE po_no=:po_no", po_no=po_no).scalar_one()
            q(db, "INSERT INTO po_lines (po_id, sku, order_qty, unit_cost) VALUES (:po,:sku,:qty,(SELECT cost_price FROM products WHERE sku=:sku))",
              po=po_id, sku=it["sku"], qty=order_qty)
            # outbox enqueue
            payload = {
              "po_no": po_no,
              "supplier_id": sup,
              "store_id": event["store_id"],
              "lines": [{"sku": it["sku"], "qty": order_qty}],
              "expected_date": (datetime.utcnow()+timedelta(days=lead)).isoformat()+"Z"
            }
            q(db, "INSERT INTO event_outbox(topic, payload) VALUES(:t,:p)", t="po.v1", p=json.dumps(payload))
            auto_po.append(po_no)
    return auto_po
