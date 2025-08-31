import asyncio
import datetime

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routes import router
from core.realtime_processor import RealTimeProcessor

# --- Add this block! ---
def serialize(obj):
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize(v) for v in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj
# ----------------------

real_time_processor = RealTimeProcessor()

app = FastAPI(
    title="Coastal Threat Alert API",
    description="API to access coastal threat monitoring live data, analytics, and system status",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

app.include_router(router, prefix="/api")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/live_monitoring")
async def live_monitoring(request: Request):
    return templates.TemplateResponse("live_monitoring.html", {"request": request})

@app.get("/")
async def root():
    return {"message": "Coastal Threat Alert System API running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                live_data = real_time_processor.get_live_statistics()
                live_data = serialize(live_data)    # serialization now works
                await websocket.send_json(live_data)
            except Exception as e:
                print("WebSocket error:", e)
                await websocket.send_json({"error": str(e)})
                break
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("WebSocket disconnected by client")
