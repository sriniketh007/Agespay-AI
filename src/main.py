from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import time
import json
import os
from schemas import TransactionRequest, TransactionResponse
from ml_engine import evaluate_transaction

app = FastAPI(
    title="AegisPay AI",
    description="Pluggable Real-Time Fraud Detection API",
    version="1.0.0"
)

# Active WebSocket connections for live UI streaming
active_connections: list[WebSocket] = []

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_event(event_data: dict):
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(event_data))
        except Exception:
            pass

@app.post("/v1/evaluate-transaction", response_model=TransactionResponse)
async def evaluate(request: TransactionRequest):
    start_time = time.time()
    
    try:
        risk_score, verdict, reasons = evaluate_transaction(
            amount=request.amount,
            account_id=request.account_id,
            device_ip=request.device.ip_address
        )
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        challenge = None
        if verdict == "CHALLENGE_PUSH":
            challenge = {"push_notification_id": f"push_{int(time.time())}", "timeout_seconds": 30}
            
        response_data = TransactionResponse(
            eval_id=f"ev_{int(time.time()*1000)}",
            transaction_id=request.transaction_id,
            risk_score=risk_score,
            verdict=verdict,
            latency_ms=latency_ms,
            reasons=reasons,
            challenge_details=challenge
        )

        # Stream payload live to dashboard UI via WebSockets
        await broadcast_event({
            "eval_id": response_data.eval_id,
            "transaction_id": response_data.transaction_id,
            "account_id": request.account_id,
            "amount": request.amount,
            "merchant": request.merchant.id,
            "risk_score": round(risk_score, 4),
            "verdict": verdict,
            "latency_ms": latency_ms,
            "reasons": reasons
        })
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static dashboard UI
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
if os.path.exists(STATIC_DIR):
    app.mount("/dashboard", StaticFiles(directory=STATIC_DIR, html=True), name="static")