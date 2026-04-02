from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import TelemetryItem, ManeuverCommand, SimulationStepRequest, Snapshot
from .state import state
from .simulation import simulate_step, communication_check
from .maneuver import apply_maneuver

app = FastAPI(title='Autonomous Constellation Manager (ACM)', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/api/health')
def health():
    return {'status': 'ok', 'time': state.current_time, 'objects': len(state.objects)}

@app.post('/api/telemetry')
def post_telemetry(items: list[TelemetryItem]):
    for item in items:
        state.upsert(item)
    return {'received': len(items)}

@app.post('/api/maneuver/schedule')
def post_maneuver(cmd: ManeuverCommand):
    res = apply_maneuver(cmd)
    if not res.applied:
        raise HTTPException(status_code=400, detail=res.reason)
    return res

@app.post('/api/simulate/step')
def post_simulate(req: SimulationStepRequest):
    result = simulate_step(req.dt)
    return result

@app.get('/api/visualization/snapshot')
def snapshot() -> Snapshot:
    return Snapshot(**state.snapshot())

@app.get('/api/communication/check')
def check_comm(ground_lat: float = 0.0, ground_lon: float = 0.0):
    return communication_check(ground_lat, ground_lon)
