"""Speichern/Laden einer Messung.                          Gehört: Marius

Schnittstelle (nicht ändern ohne Absprache):
    save_run(folder, data, video_path, markers)  -> nichts
    load_run(folder)                             -> (data, video_path, markers)
        data:    dict aus sync.synchronize
        markers: dict Name -> Zeit [s], z. B. {"1st push": 2.31}

Ordner-Inhalt: video.mp4 (Kopie), signals.csv (t,x,y,ax,ay,az,wx,wy,wz,v),
meta.json (offset, markers).
"""


def save_run(folder, data, video_path, markers):
    raise NotImplementedError("Marius: save_run fehlt noch")


def load_run(folder):
    raise NotImplementedError("Marius: load_run fehlt noch")
