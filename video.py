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

arucodict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)


def iter_video(source, marker_id=0, marker_size_m=0.05):
    parameters = cv2.aruco.DetectorParameters()
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(arucodict, parameters)

    cap = cv2.VideoCapture(source)  # Dateipfad oder 0 für Live-Kamera
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Bilder pro Sekunde
    live = isinstance(source, int)  # 0 = Kamera, sonst Dateipfad
    start = time.time()
    frame_idx = 0
    while True:
        ret, frame = cap.read()  # ret = gab es noch einen Frame?
        if not ret:
            break

        if live:
            t = time.time() - start  # echte Uhr, fps der Webcam ist oft 0
        else:
            t = frame_idx / fps  # Frame-Nummer -> Sekunden
        x, y = np.nan, np.nan  # Standard: kein Marker gefunden
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            for corner, id_ in zip(corners, ids.flatten()):
                if id_ != marker_id:
                    continue
                pts = corner[0]  # die 4 Ecken, je (x, y) in Pixel
                breite_px = np.linalg.norm(pts[1] - pts[0])  # Kante oben-links -> oben-rechts
                m_pro_px = marker_size_m / breite_px  # Meter pro Pixel
                x = float(pts[0][0]) * m_pro_px  # obere linke Ecke
                y = float(pts[0][1]) * m_pro_px

        yield t, x, y, frame  # immer liefern, auch mit nan
        frame_idx += 1

    cap.release()


def track_video(path, marker_id=0, marker_size_m=0.05):
    """Ganze Datei auf einmal: sammelt einfach iter_video ein."""
    t, x, y = [], [], []
    for ti, xi, yi, _frame in iter_video(path, marker_id, marker_size_m):
        t.append(ti); x.append(xi); y.append(yi)
    return {"t": np.array(t), "x": np.array(x), "y": np.array(y)}


def find_video_event(t, x):
    letztes_tal = None
    for i in range(1, len(x) - 1):  # alle Plätze außer erster und letzter (brauchen 2 Nachbarn)
        if x[i] < x[i - 1] and x[i] < x[i + 1]:  # kleiner als beide Nachbarn = Tal
            letztes_tal = i  # merken, wird bei jedem neuen Tal überschrieben
    return t[letztes_tal]  # Platz -> Zeit in Sekunden
