# AI Multi-Step Attack Detector

Local deployment for the completed ML pipeline.

## Backend

```powershell
pip install -r requirements.txt
uvicorn app:app --reload
```

The API runs at `http://localhost:8000`.

Endpoints:

- `POST /reset`
- `POST /inject` with `{ "flow_type": "Port_Scan" }`
- `GET /history`
- `GET /metrics`

Accepted `flow_type` values:

- `Normal`
- `Port_Scan`
- `Web_Crwling`
- `Brute_Force`
- `HTTP_DDoS`
- `ICMP_Flood`

## Frontend

```powershell
npm install
npm run dev
```

The dashboard runs at `http://localhost:5173` and calls the backend REST API.

If your backend runs somewhere else, set:

```powershell
$env:VITE_API_BASE_URL="http://localhost:8000"
npm run dev
```
