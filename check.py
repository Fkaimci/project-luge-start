"""Prüft jedes Teil gegen die Fake-Daten und dann alles zusammen.   Gehört: allen

    python check.py

Vor jedem Push laufen lassen. Dein Teil ist fertig, wenn seine Zeilen OK zeigen.
"""
import tempfile

import numpy as np

import fake_data as fd

results = []


def check(owner, name, fn):
    try:
        fn()
        results.append(("OK    ", owner, name, ""))
    except NotImplementedError as e:
        results.append(("OFFEN ", owner, name, str(e)))
    except Exception as e:
        results.append(("FEHLER", owner, name, f"{type(e).__name__}: {e}"))


def near(got, want, tol, what):
    assert abs(got - want) <= tol, f"{what}: erwartet {want}, bekommen {got:.3f}"


video_path, imu_csv = fd.write_files()
true_v, true_i = fd.truth_video(), fd.truth_imu()


def video_tracking():
    from video import track_video
    v = track_video(video_path, fd.MARKER_ID, fd.MARKER_SIZE_M)
    assert set(v) >= {"t", "x", "y"}, "dict braucht t, x, y"
    assert len(v["t"]) == len(true_v["t"]), f"{len(true_v['t'])} Frames erwartet, {len(v['t'])} bekommen"
    near(v["t"][1] - v["t"][0], 1 / fd.FPS, 1e-3, "Zeitschritt [s]")
    dx = (v["x"] - v["x"][0]) - (true_v["x"] - true_v["x"][0])  # Startpunkt egal, Weg muss stimmen
    near(np.nanmax(np.abs(dx)), 0, 0.03, "Abweichung x [m]")  # 3 cm: 1 px Fehler an der Kante = 2,5 %


def video_event():
    from video import find_video_event
    near(find_video_event(true_v["t"], true_v["x"]), fd.VIDEO_EVENT, 1 / fd.FPS, "Video-Event [s]")


def imu_load():
    from imu import load_imu
    i = load_imu(imu_csv)
    assert set(i) >= {"t", "a", "w", "v"}, "dict braucht t, a, w, v"
    assert i["a"].shape == (len(true_i["t"]), 3), f"a muss Form (n, 3) haben, ist {i['a'].shape}"
    near(i["t"][1] - i["t"][0], 1 / fd.IMU_HZ, 1e-4, "Zeitschritt [s]")
    near(np.abs(i["a"][:, 2]).max(), 0, 0.1, "a_z ohne Erdbeschleunigung [m/s²]")
    near(np.abs(i["v"] - true_i["v"]).max(), 0, 0.05, "Abweichung v [m/s]")


def imu_event():
    from imu import find_imu_event
    near(find_imu_event(true_i["t"], true_i["v"]), fd.IMU_EVENT, 1 / fd.IMU_HZ, "IMU-Event [s]")


def sync():
    from sync import synchronize
    d = synchronize(true_v, true_i)
    near(d["offset"], fd.TRUE_OFFSET, 1 / fd.FPS, "Versatz [s]")
    n = len(d["t"])
    assert all(len(d[k]) == n for k in ("x", "y", "a", "w", "v")), "alle Signale brauchen dieselbe Länge wie t"


def storage():
    from storage import load_run, save_run
    d = {"t": np.array([0.0, 0.1]), "x": np.zeros(2), "y": np.zeros(2), "a": np.zeros((2, 3)),
         "w": np.zeros((2, 3)), "v": np.zeros(2), "offset": 0.4}
    with tempfile.TemporaryDirectory() as folder:
        save_run(folder, d, video_path, {"1st push": 2.31})
        d2, vp, markers = load_run(folder)
    near(d2["offset"], 0.4, 1e-9, "offset nach Laden")
    assert markers == {"1st push": 2.31}, f"Marker nach Laden: {markers}"
    assert np.allclose(d2["a"], d["a"]), "a nach Laden anders"


def everything():
    from pipeline import analyse
    d = analyse(video_path, imu_csv, fd.MARKER_ID, fd.MARKER_SIZE_M)
    near(d["offset"], fd.TRUE_OFFSET, 2 / fd.FPS, "Versatz Gesamtablauf [s]")


check("Simon ", "video.track_video", video_tracking)
check("Simon ", "video.find_video_event", video_event)
check("Franka", "imu.load_imu", imu_load)
check("Franka", "imu.find_imu_event", imu_event)
check("Franka", "sync.synchronize", sync)
check("Marius", "storage save/load", storage)
check("alle  ", "pipeline.analyse (alles zusammen)", everything)

for status, owner, name, msg in results:
    print(f"{status} {owner}  {name:36s} {msg}")
