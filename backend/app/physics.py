from __future__ import annotations
import numpy as np

mu = 398600.4418  # km^3/s^2
Re = 6378.137  # Earth radius km
J2 = 1.08262668e-3


def gravity_acceleration(r: np.ndarray) -> np.ndarray:
    rnorm = np.linalg.norm(r)
    if rnorm == 0:
        return np.zeros(3)
    a0 = -mu * r / (rnorm**3)
    z2 = r[2]**2
    r2 = rnorm**2
    factor = 1.5 * J2 * mu * Re**2 / (rnorm**5)
    a_j2 = np.zeros(3)
    a_j2[0] = r[0] * (5*z2/r2 - 1)
    a_j2[1] = r[1] * (5*z2/r2 - 1)
    a_j2[2] = r[2] * (5*z2/r2 - 3)
    return a0 + factor * a_j2


def rk4_step(pos: np.ndarray, vel: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    def deriv(p, v):
        return v, gravity_acceleration(p)

    k1v, k1a = deriv(pos, vel)
    k2v, k2a = deriv(pos + 0.5*dt*k1v, vel + 0.5*dt*k1a)
    k3v, k3a = deriv(pos + 0.5*dt*k2v, vel + 0.5*dt*k2a)
    k4v, k4a = deriv(pos + dt*k3v, vel + dt*k3a)

    new_pos = pos + dt*(k1v + 2*k2v + 2*k3v + k4v)/6
    new_vel = vel + dt*(k1a + 2*k2a + 2*k3a + k4a)/6
    return new_pos, new_vel


def orbital_radius(pos: np.ndarray) -> float:
    return np.linalg.norm(pos)
