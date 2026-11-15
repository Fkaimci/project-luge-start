"""Sync: Video und IMU auf eine Zeitachse.                 Gehört: Franka

Schnittstelle (nicht ändern ohne Absprache):
    synchronize(video, imu) -> {"t", "x", "y", "a", "w", "v", "offset"}
        video, imu: dicts aus video.track_video / imu.load_imu
        offset [s]: so viel wird zur IMU-Zeit addiert
        alle Signale auf derselben Zeitachse t (nur der Bereich, wo beide Daten haben)

Idee des Kunden: Event im Video = Event in der IMU. Nur verschieben, Form bleibt.
Vorlage: mci-luge-start/sync.py (resample_to_common_time).
"""
import numpy as np


def synchronize(video, imu):
    raise NotImplementedError("Franka: synchronize fehlt noch")
