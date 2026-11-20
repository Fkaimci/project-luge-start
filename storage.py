"""Speichern/Laden einer Messung.                          Gehört: Marius

Schnittstelle (nicht ändern ohne Absprache):
    save_run(folder, data, video_path, markers)  -> nichts
    load_run(folder)                             -> (data, video_path, markers)
        data:    dict aus sync.synchronize
        markers: dict Name -> Zeit [s], z. B. {"1st push": 2.31}

Ordner-Inhalt: video.mp4 (Kopie), signals.csv (t,x,y,ax,ay,az,wx,wy,wz,v),
meta.json (offset, markers).
"""
import json
import os
import shutil
import numpy as np


def save_run(folder, data, video_path, markers):
    # Ordner anlegen (exist_ok=True: kein Fehler, wenn es ihn schon gibt)
    os.makedirs(folder, exist_ok=True)

    # 1) Video in den Ordner kopieren
    shutil.copy(video_path, os.path.join(folder, "video.mp4"))

    # 2) Alle Signale nebeneinander in eine Tabelle legen und als CSV speichern.
    #    a und w haben je 3 Spalten (x, y, z), der Rest je 1 Spalte -> 10 Spalten.
    table = np.column_stack([data["t"], data["x"], data["y"],
                             data["a"], data["w"], data["v"]])
    np.savetxt(os.path.join(folder, "signals.csv"), table, delimiter=",",
               header="t,x,y,ax,ay,az,wx,wy,wz,v", comments="")

    # 3) Offset und Marker als JSON speichern
    meta = {"offset": data["offset"], "markers": markers}
    with open(os.path.join(folder, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def load_run(folder):
    # 1) CSV lesen. skiprows=1 überspringt die Kopfzeile.
    table = np.loadtxt(os.path.join(folder, "signals.csv"), delimiter=",", skiprows=1)

    # 2) JSON lesen
    with open(os.path.join(folder, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)

    # 3) Spalten wieder in das dict zurückverteilen
    data = {
        "t": table[:, 0],
        "x": table[:, 1],
        "y": table[:, 2],
        "a": table[:, 3:6],   # Spalten 3, 4, 5 = ax, ay, az
        "w": table[:, 6:9],   # Spalten 6, 7, 8 = wx, wy, wz
        "v": table[:, 9],
        "offset": meta["offset"],
    }
    video_path = os.path.join(folder, "video.mp4")
    return data, video_path, meta["markers"]
