"""Klebstoff: verbindet alle Teile. Die GUI ruft nur diese Funktion auf.   Gehört: allen

Nicht ändern, solange die Schnittstellen gleich bleiben.
"""
from imu import load_imu
from sync import synchronize
from video import track_video


def analyse(video_path, imu_csv, marker_id=0, marker_size_m=0.05):
    """Datei-Modus: Video + IMU-CSV rein, synchrone Signale raus."""
    video = track_video(video_path, marker_id, marker_size_m)
    imu = load_imu(imu_csv)
    return synchronize(video, imu)
