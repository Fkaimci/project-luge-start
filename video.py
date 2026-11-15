"""Video: ArUco-Marker -> Position in Metern.            Gehört: Simon

Schnittstelle (nicht ändern ohne Absprache):
    iter_video(source, marker_id, marker_size_m)  -> liefert pro Frame (t, x, y, frame)
    track_video(path, marker_id, marker_size_m)   -> {"t", "x", "y"}  (alle Arrays, s und m)
    find_video_event(t, x)                        -> Zeitpunkt [s] der letzten max. Streckung

source = Dateipfad (Video) oder 0 (Live-Kamera). cv2.VideoCapture nimmt beides,
deshalb ist Live später nur ein anderes source.
Frames ohne Marker: x und y = nan (nicht weglassen, sonst passt das Video nicht mehr zur Zeit).
"""
import numpy as np


def iter_video(source, marker_id=0, marker_size_m=0.05):
    raise NotImplementedError("Simon: iter_video fehlt noch")
    yield  # macht die Funktion zum Generator


def track_video(path, marker_id=0, marker_size_m=0.05):
    """Ganze Datei auf einmal: sammelt einfach iter_video ein."""
    t, x, y = [], [], []
    for ti, xi, yi, _frame in iter_video(path, marker_id, marker_size_m):
        t.append(ti); x.append(xi); y.append(yi)
    return {"t": np.array(t), "x": np.array(x), "y": np.array(y)}


def find_video_event(t, x):
    raise NotImplementedError("Simon: find_video_event fehlt noch")
