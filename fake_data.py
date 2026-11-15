"""Fake-Daten mit bekannter Lösung, damit jede:r ohne die anderen testen kann.   Gehört: allen

    python fake_data.py   -> schreibt data/fake/video.mp4 und data/fake/imu.csv

Szenario: Ruhe bis 0,75 s, Schaukeln vor und zurück, letzte max. Streckung bei t = 3,0 s (Video-Uhr),
dann Abstoß. Die IMU-Uhr läuft 0,40 s hinterher, ihr Umkehrpunkt liegt also bei 2,6 s.
"""
import os

import cv2
import numpy as np

MARKER_ID = 0
MARKER_SIZE_M = 0.05
TRUE_OFFSET = 0.40           # IMU-Zeit + 0,40 s = Video-Zeit
VIDEO_EVENT = 3.0            # s, Video-Uhr
IMU_EVENT = VIDEO_EVENT - TRUE_OFFSET
FPS, IMU_HZ = 60, 120
PX_PER_M = 800               # 5 cm Marker = 40 px
W = 2 * np.pi / 1.5          # Schaukel-Frequenz [rad/s]
REST = 0.75                  # s, bis hier steht der Schlitten still (wie beim echten Start)


def _x(t):
    """Position [m]: Ruhe, Schaukeln bis 3 s, danach gleichmäßig beschleunigter Abstoß."""
    t = np.maximum(t, REST)
    return np.where(t < VIDEO_EVENT, 0.1 - 0.05 * np.cos(W * (t - VIDEO_EVENT)),
                    0.05 + 0.4 * (t - VIDEO_EVENT) ** 2)


def _v(t):
    still = t < REST
    return np.where(still, 0.0, _v_move(t))


def _v_move(t):
    return np.where(t < VIDEO_EVENT, 0.05 * W * np.sin(W * (t - VIDEO_EVENT)), 0.8 * (t - VIDEO_EVENT))


def _a(t):
    still = t < REST
    return np.where(still, 0.0, _a_move(t))


def _a_move(t):
    return np.where(t < VIDEO_EVENT, 0.05 * W ** 2 * np.cos(W * (t - VIDEO_EVENT)), 0.8)


def truth_video():
    t = np.arange(0, 4.5, 1 / FPS)
    return {"t": t, "x": _x(t), "y": np.zeros_like(t)}


def truth_imu():
    t = np.arange(0, 4.0, 1 / IMU_HZ)
    tv = t + TRUE_OFFSET     # gleicher Moment auf der Video-Uhr
    a = np.column_stack([_a(tv), np.zeros_like(t), np.zeros_like(t)])
    return {"t": t, "a": a, "w": np.zeros((len(t), 3)), "v": _v(tv)}


def write_files(folder="data/fake"):
    os.makedirs(folder, exist_ok=True)
    video_path, csv_path = os.path.join(folder, "video.mp4"), os.path.join(folder, "imu.csv")

    edge = int(MARKER_SIZE_M * PX_PER_M)
    marker = cv2.aruco.generateImageMarker(
        cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250), MARKER_ID, edge)
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (900, 300))
    for x in truth_video()["x"]:
        frame = np.full((300, 900, 3), 255, np.uint8)
        left = int(round(50 + x * PX_PER_M))
        frame[130:130 + edge, left:left + edge] = marker[:, :, None]
        out.write(frame)
    out.release()

    # Spalten wie im Movella-DOT-Export (an echte Datei anpassen!): Zeit in µs, Acc in m/s², Gyr in deg/s.
    # Acc_Z enthält die Erdbeschleunigung, wie bei einem echten Sensor.
    imu = truth_imu()
    rows = np.column_stack([np.arange(len(imu["t"])), imu["t"] * 1e6,
                            imu["a"][:, 0], imu["a"][:, 1], imu["a"][:, 2] + 9.81,
                            np.degrees(imu["w"])])
    np.savetxt(csv_path, rows, delimiter=",", comments="", fmt="%.6f",
               header="PacketCounter,SampleTimeFine,Acc_X,Acc_Y,Acc_Z,Gyr_X,Gyr_Y,Gyr_Z")
    return video_path, csv_path


if __name__ == "__main__":
    print("Geschrieben:", *write_files())
