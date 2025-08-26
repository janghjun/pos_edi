# POS-EDI Frontend (Vite + React)

## Run
```bash
cd frontend/app
npm install
npm run dev
# open http://localhost:5173
```

백엔드는 `pos-edi/infra`에서 `docker compose up -d --build`로 기동하세요.

- POS 판매 입력 탭: `http://localhost:8001/sales`로 이벤트 발행
- 본사 PO 목록 탭: `http://localhost:8000/po/list` 조회
