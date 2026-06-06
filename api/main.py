from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/latency")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    # Load telemetry data (from q-vercel-latency.json)
    import json
    with open("q-vercel-latency.json") as f:
        telemetry = json.load(f)

    response = {}
    for region in regions:
        data = [r for r in telemetry if r["region"] == region]
        latencies = [r["latency_ms"] for r in data]
        uptimes = [r["uptime_pct"] for r in data]

        if latencies:
            avg_latency = float(np.mean(latencies))
            p95_latency = float(np.percentile(latencies, 95))
            avg_uptime = float(np.mean(uptimes))
            breaches = sum(1 for l in latencies if l > threshold)

            response[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches,
            }

    return response
