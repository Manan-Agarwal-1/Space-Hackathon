from __future__ import annotations
import numpy as np
from scipy.spatial import cKDTree
from .state import state


def detect_conjunctions(threshold_m: float = 100.0) -> list[dict]:
    threshold_km = threshold_m / 1000.0
    coords = []
    ids = []
    for obj in state.objects.values():
        coords.append(obj.position)
        ids.append(obj.id)
    if len(coords) < 2:
        return []
    tree = cKDTree(coords)
    pairs = tree.query_pairs(threshold_km)
    collisions = []
    for i,j in pairs:
        a = state.objects[ids[i]]
        b = state.objects[ids[j]]
        collisions.append({
            'satellite_id': a.id,
            'threat_id': b.id,
            'distance_m': float(np.linalg.norm(a.position - b.position) * 1000.0),
        })
    state.collision_warnings = collisions
    return collisions
