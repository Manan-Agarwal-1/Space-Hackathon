from __future__ import annotations
from typing import Dict, List
from .models import TelemetryItem, ManeuverCommand
import numpy as np

class ObjectState:
    def __init__(self, item: TelemetryItem):
        self.id = item.id
        self.type = item.type
        self.position = np.array(item.position, dtype=float)
        self.velocity = np.array(item.velocity, dtype=float)
        self.mass = item.mass
        self.fuel_kg = item.fuel_kg
        self.target_orbit_radius_km = item.target_orbit_radius_km
        self.last_maneuver_time = -1e9
        self.maneuvers: List[Dict] = []

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'position': self.position.tolist(),
            'velocity': self.velocity.tolist(),
            'mass': self.mass,
            'fuel_kg': self.fuel_kg,
            'target_orbit_radius_km': self.target_orbit_radius_km,
            'last_maneuver_time': self.last_maneuver_time,
            'maneuvers': self.maneuvers,
        }

class GlobalState:
    def __init__(self):
        self.objects: Dict[str, ObjectState] = {}
        self.current_time: float = 0.0
        self.collision_warnings: List[Dict] = []

    def upsert(self, item: TelemetryItem):
        if item.id in self.objects:
            obj = self.objects[item.id]
            obj.position = np.array(item.position, dtype=float)
            obj.velocity = np.array(item.velocity, dtype=float)
            obj.mass = item.mass
            obj.fuel_kg = item.fuel_kg
            obj.target_orbit_radius_km = item.target_orbit_radius_km
        else:
            self.objects[item.id] = ObjectState(item)

    def snapshot(self):
        sats = {};
        debris = {}
        for k,v in self.objects.items():
            if v.type == 'satellite':
                sats[k] = v.to_dict()
            else:
                debris[k] = v.to_dict()
        return {
            'satellites': sats,
            'debris': debris,
            'maneuvers': {k:v.maneuvers for k,v in self.objects.items()},
            'collisions': list(self.collision_warnings),
        }

state = GlobalState()
