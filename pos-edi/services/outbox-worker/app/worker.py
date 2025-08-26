import os, time, json
from kafka import KafkaProducer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_HOST=os.getenv('DB_HOST','hq-mysql'); DB_PORT=os.getenv('DB_PORT','3306')
DB_USER=os.getenv('DB_USER','root'); DB_PASS=os.getenv('DB_PASS','root')
DB_NAME=os.getenv('DB_NAME','hqdb')
BROKER=os.getenv('KAFKA_BROKER','kafka:9092')

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4", pool_pre_ping=True, future=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
producer = KafkaProducer(bootstrap_servers=[BROKER], value_serializer=lambda v: json.dumps(v).encode('utf-8'))

while True:
    try:
        with Session() as db:
            rows = db.execute(text("SELECT id, topic, payload FROM event_outbox WHERE status='PENDING' ORDER BY id LIMIT 50")).mappings().all()
            for r in rows:
                payload = json.loads(r['payload'])
                producer.send(r['topic'], payload)
                db.execute(text("UPDATE event_outbox SET status='PUBLISHED', published_at=NOW() WHERE id=:id"), {"id": r['id']})
            db.commit()
    except Exception as e:
        print("outbox error:", e)
    time.sleep(1)
