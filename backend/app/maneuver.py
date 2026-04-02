from __future__ import annotations
import numpy as np
from .state import state, ObjectState
from .models import ManeuverCommand, ManeuverResult

ISP = 300.0
g0 = 9.80665
MAX_DELTA_V = 15.0
COOLDOWN = 600.0


def apply_maneuver(cmd: ManeuverCommand) -> ManeuverResult:
    if cmd.satellite_id not in state.objects:
        return ManeuverResult(satellite_id=cmd.satellite_id, applied=False, reason='not found')
    sat: ObjectState = state.objects[cmd.satellite_id]
    if sat.type != 'satellite':
        return ManeuverResult(satellite_id=cmd.satellite_id, applied=False, reason='not satellite')

    dv = np.array(cmd.delta_v, dtype=float)
    dv_mag = float(np.linalg.norm(dv))
    if dv_mag <= 0.0:
        return ManeuverResult(satellite_id=sat.id, applied=False, reason='zero delta-v')
    if dv_mag > MAX_DELTA_V:
        return ManeuverResult(satellite_id=sat.id, applied=False, reason='delta-v over max')
    if state.current_time - sat.last_maneuver_time < COOLDOWN:
        return ManeuverResult(satellite_id=sat.id, applied=False, reason='cooldown')
    if sat.fuel_kg <= 0.0:
        return ManeuverResult(satellite_id=sat.id, applied=False, reason='no fuel')

    m0 = sat.mass + sat.fuel_kg
    try:
        m1 = m0 / np.exp(dv_mag/(ISP*g0))
    except OverflowError:
        return ManeuverResult(satellite_id=sat.id, applied=False, reason='too much delta-v')

    fuel_used = float(m0 - m1)
    if fuel_used > sat.fuel_kg:
        return ManeuverResult(satellite_id=sat.id, applied=False, reason='insufficient fuel')

    sat.velocity = sat.velocity + dv
    sat.fuel_kg -= fuel_used
    sat.last_maneuver_time = state.current_time
    sat.maneuvers.append({
        'time': state.current_time,
        'delta_v': dv.tolist(),
        'fuel_used': fuel_used,
    })

    return ManeuverResult(
        satellite_id=sat.id,
        applied=True,
        fuel_used=fuel_used,
        delta_v_mag=dv_mag,
    )


def schedule_avoidance():
    threats = state.collision_warnings
    results = []
    for t in threats:
        sat = state.objects.get(t['satellite_id'])
        if sat is None or sat.type != 'satellite':
            continue
        # simple avoidance burn: small radial outward along position vector
        pos_norm = np.linalg.norm(sat.position)
        if pos_norm == 0:
            continue
        dv = (sat.position / pos_norm) * 0.5
        cmd = ManeuverCommand(satellite_id=sat.id, delta_v=tuple(dv), scheduled_time=state.current_time)
        results.append(apply_maneuver(cmd))
    return results


def station_keeping():
    updates = []
    for sat in state.objects.values():
        if sat.type != 'satellite':
            continue
        radius_km = np.linalg.norm(sat.position)
        if abs(radius_km - sat.target_orbit_radius_km) > 10.0:
            # burn radial correction up to 3 m/s
            sign = 1.0 if radius_km < sat.target_orbit_radius_km else -1.0
            dv = (sat.position / radius_km) * (sign * 1.5)
            cmd = ManeuverCommand(satellite_id=sat.id, delta_v=tuple(dv), scheduled_time=state.current_time)
            res = apply_maneuver(cmd)
            updates.append(res)
    return updates
