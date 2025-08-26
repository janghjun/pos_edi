from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mysql.connector as my
import psycopg2
import pandas as pd

DEFAULT_ARGS = {"owner":"me","depends_on_past":False,"retries":1,"retry_delay":timedelta(minutes=5)}

def extract_hq_sales(**ctx):
    cn = my.connect(host='hq-mysql', user='root', password='root', database='hqdb')
    df = pd.read_sql(
        """
        SELECT s.sale_id, s.store_id, si.sku, si.qty, si.net_amount, DATE(s.sale_ts) AS d
        FROM sales s JOIN sale_items si ON s.sale_id=si.sale_id
        WHERE s.sale_ts >= DATE_SUB(NOW(), INTERVAL 2 DAY)
        """, cn)
    ctx['ti'].xcom_push(key='sales', value=df.to_json(orient='records'))
    cn.close()

def load_dw_sales(**ctx):
    data = ctx['ti'].xcom_pull(key='sales')
    if not data: return
    df = pd.read_json(data)
    pg = psycopg2.connect(host='dw-postgres', user='dw', password='dw', dbname='dwh')
    cur = pg.cursor()
    for _, r in df.iterrows():
        cur.execute("INSERT INTO dim_store(store_id) VALUES(%s) ON CONFLICT DO NOTHING", (r.store_id,))
        cur.execute("INSERT INTO dim_product(sku) VALUES(%s) ON CONFLICT DO NOTHING", (r.sku,))
        cur.execute("INSERT INTO dim_date(date_key,y,m,d,dow,week) VALUES(%s,EXTRACT(YEAR FROM %s),EXTRACT(MONTH FROM %s),EXTRACT(DAY FROM %s),EXTRACT(DOW FROM %s),EXTRACT(WEEK FROM %s)) ON CONFLICT DO NOTHING",
                    (r.d, r.d, r.d, r.d, r.d, r.d))
        cur.execute("""
            INSERT INTO fact_sales(sale_id, date_key, store_id, sku, qty, net_amount)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (sale_id, sku) DO UPDATE SET qty=EXCLUDED.qty, net_amount=EXCLUDED.net_amount
        """, (r.sale_id, r.d, r.store_id, r.sku, int(r.qty), float(r.net_amount)))
    pg.commit(); cur.close(); pg.close()

def extract_po(**ctx):
    cn = my.connect(host='hq-mysql', user='root', password='root', database='hqdb')
    df = pd.read_sql(
        """
        SELECT po_no, supplier_id, store_id, l.sku, l.order_qty, DATE(created_at) AS d
        FROM purchase_orders p JOIN po_lines l ON p.po_id=l.po_id
        WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 2 DAY)
        """, cn)
    ctx['ti'].xcom_push(key='po', value=df.to_json(orient='records'))
    cn.close()

def load_po(**ctx):
    data = ctx['ti'].xcom_pull(key='po')
    if not data: return
    df = pd.read_json(data)
    pg = psycopg2.connect(host='dw-postgres', user='dw', password='dw', dbname='dwh')
    cur = pg.cursor()
    for _, r in df.iterrows():
        cur.execute("INSERT INTO dim_store(store_id) VALUES(%s) ON CONFLICT DO NOTHING", (r.store_id,))
        cur.execute("INSERT INTO dim_supplier(supplier_id) VALUES(%s) ON CONFLICT DO NOTHING", (r.supplier_id,))
        cur.execute("INSERT INTO dim_product(sku) VALUES(%s) ON CONFLICT DO NOTHING", (r.sku,))
        cur.execute("INSERT INTO dim_date(date_key,y,m,d,dow,week) VALUES(%s,EXTRACT(YEAR FROM %s),EXTRACT(MONTH FROM %s),EXTRACT(DAY FROM %s),EXTRACT(DOW FROM %s),EXTRACT(WEEK FROM %s)) ON CONFLICT DO NOTHING",
                    (r.d, r.d, r.d, r.d, r.d, r.d))
        cur.execute("""
            INSERT INTO fact_po(po_no, date_key, supplier_id, store_id, sku, order_qty)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (po_no, sku) DO UPDATE SET order_qty=EXCLUDED.order_qty
        """, (r.po_no, r.d, r.supplier_id, r.store_id, r.sku, int(r.order_qty)))
    pg.commit(); cur.close(); pg.close()

def extract_inbound(**ctx):
    cn = my.connect(host='hq-mysql', user='root', password='root', database='hqdb')
    df = pd.read_sql(
        """
        SELECT a.asn_no, r.store_id, l.sku, l.accept_qty, DATE(r.received_at) AS d
        FROM inbound_receipts r
        JOIN asn a ON a.asn_id=r.asn_id
        JOIN inbound_receipt_lines l ON r.receipt_id=l.receipt_id
        WHERE r.received_at >= DATE_SUB(NOW(), INTERVAL 2 DAY)
        """, cn)
    ctx['ti'].xcom_push(key='inb', value=df.to_json(orient='records'))
    cn.close()

def load_inbound(**ctx):
    data = ctx['ti'].xcom_pull(key='inb')
    if not data: return
    df = pd.read_json(data)
    pg = psycopg2.connect(host='dw-postgres', user='dw', password='dw', dbname='dwh')
    cur = pg.cursor()
    for _, r in df.iterrows():
        cur.execute("INSERT INTO dim_store(store_id) VALUES(%s) ON CONFLICT DO NOTHING", (r.store_id,))
        cur.execute("INSERT INTO dim_product(sku) VALUES(%s) ON CONFLICT DO NOTHING", (r.sku,))
        cur.execute("INSERT INTO dim_date(date_key,y,m,d,dow,week) VALUES(%s,EXTRACT(YEAR FROM %s),EXTRACT(MONTH FROM %s),EXTRACT(DAY FROM %s),EXTRACT(DOW FROM %s),EXTRACT(WEEK FROM %s)) ON CONFLICT DO NOTHING",
                    (r.d, r.d, r.d, r.d, r.d, r.d))
        cur.execute("""
            INSERT INTO fact_inbound(asn_no, date_key, store_id, sku, accept_qty)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (asn_no, sku) DO UPDATE SET accept_qty=EXCLUDED.accept_qty
        """, (r.asn_no, r.d, r.store_id, r.sku, int(r.accept_qty)))
    pg.commit(); cur.close(); pg.close()

with DAG(
    dag_id='dw_etl_daily',
    default_args=DEFAULT_ARGS,
    schedule='0 2 * * *',
    start_date=datetime(2025,8,1),
    catchup=False
) as dag:
    t1 = PythonOperator(task_id='extract_sales', python_callable=extract_hq_sales)
    t2 = PythonOperator(task_id='load_sales', python_callable=load_dw_sales)
    t3 = PythonOperator(task_id='extract_po', python_callable=extract_po)
    t4 = PythonOperator(task_id='load_po', python_callable=load_po)
    t5 = PythonOperator(task_id='extract_inbound', python_callable=extract_inbound)
    t6 = PythonOperator(task_id='load_inbound', python_callable=load_inbound)

    t1 >> t2
    t3 >> t4
    t5 >> t6
