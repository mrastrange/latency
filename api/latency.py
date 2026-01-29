from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json, os, numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "../q-vercel-latency.json")
with open(DATA_FILE) as f:
    telemetry = json.load(f)

@app.post("/latency")
async def latency_metrics(req: Request):
    data = await req.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    result = {}
    for region in regions:
        records = [r for r in telemetry if r.get("region") == region]

        if not records:
            result[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue

        latencies = [r.get("latency_ms", 0) for r in records]
        uptimes = [r.get("uptime_pct", 0) for r in records]
        breaches = sum(1 for l in latencies if l > threshold)

        result[region] = {
            "avg_latency": round(np.mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(np.mean(uptimes), 2),
            "breaches": breaches,
        }

    return JSONResponse(content=result)
