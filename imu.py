"""IMU: Movella/Xsens-DOT-Daten -> a, w, v.               Gehört: Franka

Schnittstelle (nicht ändern ohne Absprache):
    iter_imu(source)      -> liefert pro Sample (t, a, w)   t [s], a (3,) [m/s²], w (3,) [rad/s]
    load_imu(csv_path)    -> {"t", "a", "w", "v"}   a, w: (n, 3), v: (n,) Geschwindigkeit in x [m/s]
    find_imu_event(t, v)  -> Zeitpunkt [s] des Umkehrpunkts (v ≈ 0)

source = CSV-Pfad. Später Live-Sensor (Bluetooth) mit derselben Ausgabe.
"""
import numpy as np


def iter_imu(source):
    raise NotImplementedError("Franka: iter_imu fehlt noch")
    yield


def integrate_velocity(t, a_x):
    raise NotImplementedError("Franka: integrate_velocity fehlt noch")


def load_imu(csv_path):
    """Ganze Datei auf einmal: sammelt iter_imu ein und rechnet v dazu."""
    t, a, w = [], [], []
    for ti, ai, wi in iter_imu(csv_path):
        t.append(ti); a.append(ai); w.append(wi)
    t, a, w = np.array(t), np.array(a), np.array(w)
    return {"t": t, "a": a, "w": w, "v": integrate_velocity(t, a[:, 0])}


def find_imu_event(t, v):
    raise NotImplementedError("Franka: find_imu_event fehlt noch")
