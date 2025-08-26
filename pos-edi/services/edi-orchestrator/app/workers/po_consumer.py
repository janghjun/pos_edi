import threading, os, httpx, json
from kafka import KafkaConsumer

BROKER=os.getenv('KAFKA_BROKER','kafka:9092')
SUPPLIER_BASE=os.getenv('SUPPLIER_BASE','http://supplier-edi:8000')

class POConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer('po.v1', bootstrap_servers=[BROKER], value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        self.thread = threading.Thread(target=self.run, daemon=True)
    def start(self):
        self.thread.start()
    def run(self):
        with httpx.Client(timeout=10.0) as client:
            for msg in self.consumer:
                po = msg.value
                try:
                    client.post(f"{SUPPLIER_BASE}/supplier/po", json=po)
                except Exception as e:
                    print('PO dispatch error', e)
