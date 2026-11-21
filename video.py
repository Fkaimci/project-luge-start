"""Video: ArUco-Marker -> Position in Metern.            Gehört: Simon

Schnittstelle (nicht ändern ohne Absprache):
    iter_video(source, marker_id, marker_size_m)  -> liefert pro Frame (t, x, y, frame)
    track_video(path, marker_id, marker_size_m)   -> {"t", "x", "y"}  (alle Arrays, s und m)
    find_video_event(t, x)                        -> Zeitpunkt [s] der letzten max. Streckung

source = Dateipfad (Video) oder 0 (Live-Kamera). cv2.VideoCapture nimmt beides,
deshalb ist Live später nur ein anderes source.
Frames ohne Marker: x und y = nan (nicht weglassen, sonst passt das Video nicht mehr zur Zeit).
"""
import time

import cv2
import numpy as np
from scipy.signal import find_peaks, medfilt

arucodict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)


def iter_video(source, marker_id=0, marker_size_m=0.05):
    parameters = cv2.aruco.DetectorParameters()
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(arucodict, parameters)

    cap = cv2.VideoCapture(source)  # Dateipfad oder 0 für Live-Kamera
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    live = isinstance(source, int)  # 0 = Kamera, sonst Dateipfad
    start = time.time()
    while True:
        ret, frame = cap.read()  # ret = gab es noch einen Frame?
        if not ret:
            break

        if live:
            t = time.time() - start  # echte Uhr, fps der Webcam ist oft 0
        else:
            t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # Zeitstempel des Frames aus der Datei, ms -> s
            # (nicht frame_nr / fps: iPhone-Videos haben Lücken, fps in der Datei ist nur ein Durchschnitt)
        x, y = np.nan, np.nan  # Standard: kein Marker gefunden
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            for corner, id_ in zip(corners, ids.flatten()):
                if id_ != marker_id:
                    continue
                pts = corner[0]  # die 4 Ecken, je (x, y) in Pixel
                breite_px = np.linalg.norm(pts[1] - pts[0])  # Kante oben-links -> oben-rechts
                m_pro_px = marker_size_m / breite_px  # Meter pro Pixel
                mitte = pts.mean(axis=0)  # Mittelpunkt = Durchschnitt der 4 Ecken
                x = float(mitte[0]) * m_pro_px
                y = -float(mitte[1]) * m_pro_px  # Bild-y zeigt nach unten, wir wollen y nach oben

        yield t, x, y, frame  # immer liefern, auch mit nan

    cap.release()


def track_video(path, marker_id=0, marker_size_m=0.05):
    """Ganze Datei auf einmal: sammelt einfach iter_video ein."""
    t, x, y = [], [], []
    for ti, xi, yi, _frame in iter_video(path, marker_id, marker_size_m):
        t.append(ti); x.append(xi); y.append(yi)
    return {"t": np.array(t), "x": np.array(x), "y": np.array(y)}


def find_video_event(t, x):
    ok = ~np.isnan(x)  # Frames ohne Marker rauswerfen, find_peaks verträgt kein nan
    t, x = np.asarray(t)[ok], np.asarray(x)[ok]
    x = medfilt(x, 5)  # Median über 5 Frames: einzelne Fehl-Erkennungen (Ausreißer) fliegen raus
    taeler, _ = find_peaks(-x, prominence=0.05)  # Tal = Berg von -x, mind. 5 cm tief (Rauschen fliegt raus)
    return t[taeler[-1]]  # letztes Tal -> Zeit in Sekunden
