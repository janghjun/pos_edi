from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db, q
import csv, os

router = APIRouter()

@router.get("/run")
def run_settlement(period: str, db: Session = Depends(get_db)):
    rows = q(db, """
      SELECT pr.supplier_id, si.sku, SUM(si.net_amount) AS sales_amt
      FROM sales s JOIN sale_items si ON s.sale_id=si.sale_id
      JOIN products pr ON pr.sku=si.sku
      WHERE DATE_FORMAT(s.sale_ts, '%Y-%m') = :period
      GROUP BY pr.supplier_id, si.sku
    """, period=period).mappings().all()

    fee_rate = 20.0
    suppliers = {}
    for r in rows:
        suppliers.setdefault(r['supplier_id'], []).append(r)
    for sup, lines in suppliers.items():
        q(db, """
          INSERT INTO settlements(period, supplier_id, gross_sales, fee_rate_pct, fee_amount, payable_amt, status, generated_at)
          VALUES (:p,:s,0,:rate,0,0,'DRAFT',NOW())
          ON DUPLICATE KEY UPDATE generated_at=NOW(), fee_rate_pct=:rate
        """, p=period, s=sup, rate=fee_rate)
        stl_id = q(db, "SELECT settlement_id FROM settlements WHERE period=:p AND supplier_id=:s", p=period, s=sup).scalar_one()
        q(db, "DELETE FROM settlement_lines WHERE settlement_id=:id", id=stl_id)
        gross = 0
        for ln in lines:
            sales_amt = float(ln['sales_amt'])
            fee_amt = sales_amt * fee_rate/100
            pay_amt = sales_amt - fee_amt
            gross += sales_amt
            q(db, """
              INSERT INTO settlement_lines(settlement_id, sku, sales_amt, fee_amount, pay_amount)
              VALUES (:sid,:sku,:s,:f,:p)
            """, sid=stl_id, sku=ln['sku'], s=sales_amt, f=fee_amt, p=pay_amt)
        fee_amount = gross * fee_rate/100
        payable = gross - fee_amount
        q(db, "UPDATE settlements SET gross_sales=:g, fee_amount=:f, payable_amt=:p, status='FINALIZED' WHERE settlement_id=:id",
          g=gross, f=fee_amount, p=payable, id=stl_id)
    db.commit()

    out_dir = "/data/reports"
    os.makedirs(out_dir, exist_ok=True)
    fname = os.path.join(out_dir, f"settlement_{period}.csv")
    with open(fname, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["period","supplier_id","gross_sales","fee_rate_pct","fee_amount","payable_amt"])
        hdrs = q(db, "SELECT period, supplier_id, gross_sales, fee_rate_pct, fee_amount, payable_amt FROM settlements WHERE period=:p", p=period).fetchall()
        for h in hdrs:
            w.writerow(list(h))
    return {"ok": True, "report": fname}
