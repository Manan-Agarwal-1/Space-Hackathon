from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Dict
import numpy as np

Vector3 = tuple[float, float, float]

class TelemetryItem(BaseModel):
    id: str
    type: Literal['satellite', 'debris']
    position: Vector3
    velocity: Vector3
    mass: Optional[float] = Field(default=1000.0, gt=0.0)
    fuel_kg: Optional[float] = Field(default=100.0, ge=0.0)
    target_orbit_radius_km: Optional[float] = Field(default=6771.0)

    @validator('position', 'velocity')
    def check_vec(cls, v):
        if len(v) != 3:
            raise ValueError('must be 3-element vector')
        return v

class ManeuverCommand(BaseModel):
    satellite_id: str
    delta_v: Vector3
    scheduled_time: Optional[float] = None

class ManeuverResult(BaseModel):
    satellite_id: str
    applied: bool
    reason: Optional[str] = None
    fuel_used: float = 0.0
    delta_v_mag: float = 0.0

class SimulationStepRequest(BaseModel):
    dt: float = Field(gt=0.0, le=3600.0)

class Snapshot(BaseModel):
    satellites: Dict[str, Dict]
    debris: Dict[str, Dict]
    maneuvers: Dict[str, list[Dict]]
    collisions: list[Dict]
