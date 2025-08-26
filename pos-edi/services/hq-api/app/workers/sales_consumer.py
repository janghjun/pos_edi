import os, json, threading
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.sales_service import process_sale_event

BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

class SalesConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer('sales.v1', bootstrap_servers=[BROKER], value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        self.thread = threading.Thread(target=self.run, daemon=True)
    def start(self):
        self.thread.start()
    def run(self):
        for msg in self.consumer:
            event = msg.value
            with SessionLocal() as db:
                try:
                    process_sale_event(db, event)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print("sales_consumer error:", e)
