from __future__ import annotations
from .state import state
from .physics import rk4_step, orbital_radius
from .collision import detect_conjunctions
from .maneuver import schedule_avoidance, station_keeping


def simulate_step(dt: float):
    state.current_time += dt
    for obj in state.objects.values():
        new_pos, new_vel = rk4_step(obj.position, obj.velocity, dt)
        obj.position = new_pos
        obj.velocity = new_vel
        if obj.type == 'satellite':
            if obj.fuel_kg / (obj.mass + obj.fuel_kg + 1e-6) < 0.05:
                obj.maneuvers.append({'time': state.current_time, 'status': 'low_fuel', 'fuel_pct': obj.fuel_kg/(obj.mass+obj.fuel_kg+1e-6)})
                # no graveyard orbit by code physicalu
    collisions = detect_conjunctions(100.0)
    avoidance = schedule_avoidance() if collisions else []
    keepers = station_keeping()
    return {
        'time': state.current_time,
        'collisions': collisions,
        'avoidance': [r.model_dump() if hasattr(r,'model_dump') else r for r in avoidance],
        'station_keeping': [r.model_dump() if hasattr(r,'model_dump') else r for r in keepers],
    }


def communication_check(ground_lat: float, ground_lon: float):
    import numpy as np
    earth_radius = 6378.137
    lat = np.radians(ground_lat)
    lon = np.radians(ground_lon)
    gs = earth_radius * np.array([np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)])
    in_view = []
    for sat in state.objects.values():
        if sat.type != 'satellite':
            continue
        dot = np.dot(sat.position, gs)
        if dot / (np.linalg.norm(sat.position)*np.linalg.norm(gs)+1e-9) > 0.0:
            in_view.append(sat.id)
    return {'ground_station': [ground_lat,ground_lon], 'visible_satellites': in_view}
