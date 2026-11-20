import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import fake_data as fd
from storage import save_run, load_run

from video import find_video_event

# True: Fake-Daten benutzen, solange imu.py / sync.py noch fehlen.
# Sobald Franka fertig ist: auf False stellen.
USE_FAKE = True


def fake_analyse(video_path, imu_csv):
    """Macht dasselbe dict wie pipeline.analyse, aber aus den Fake-Daten."""
    video = fd.truth_video()
    imu = fd.truth_imu()
    t = video["t"]
    t_imu = imu["t"] + fd.TRUE_OFFSET          # IMU-Zeit auf die Video-Uhr schieben
    ax = np.interp(t, t_imu, imu["a"][:, 0])   # IMU-Werte auf die Video-Zeitpunkte umrechnen
    v = np.interp(t, t_imu, imu["v"])
    zeros = np.zeros(len(t))
    return {"t": t, "x": video["x"], "y": video["y"],
            "a": np.column_stack([ax, zeros, zeros]),
            "w": np.zeros((len(t), 3)),
            "v": v, "offset": fd.TRUE_OFFSET}

def get_sync_time(data):
    """Zeitpunkt des Sync-Events: Simons Funktion sucht die letzte max. Streckung."""
    return find_video_event(data["t"], data["x"])

def draw_plot(axes, canvas, data, markers):
    """Zeichnet x, v und a untereinander, plus Sync-Linie und Marker."""
    ax_x, ax_v, ax_a = axes
    for ax in axes:
        ax.clear()                              # alte Kurven löschen

    t = data["t"]
    ax_x.plot(t, data["x"])
    ax_v.plot(t, data["v"])
    ax_a.plot(t, data["a"][:, 0])               # nur a_x (Fahrtrichtung)

    ax_x.set_ylabel("x [m]")
    ax_v.set_ylabel("v [m/s]")
    ax_a.set_ylabel("a [m/s²]")
    ax_a.set_xlabel("Zeit [s]")

    sync_time = get_sync_time(data)
    for ax in axes:
        ax.axvline(sync_time, color="red", linestyle="--")      # Sync-Event
        for name, time in markers.items():
            ax.axvline(time, color="green")                     # Marker
    ax_x.set_title("rot = Sync-Event, grün = Marker")

    canvas.draw()

def create_gui(video_path, imu_csv):
    window = tk.Tk()
    window.title("BestLugeStart EUWEST analyzing tool")
    window.geometry("1100x750")

    # ---------- Tabs ----------
    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    measurement_tab = ttk.Frame(notebook)
    analysis_tab = ttk.Frame(notebook)
    notebook.add(measurement_tab, text="Measurement")
    notebook.add(analysis_tab, text="Analysis")

    # Hier merkt sich die GUI die aktuelle Messung.
    # Ein dict kann man in Funktionen ändern, ohne "global" zu brauchen.
    current = {"data": None}
    markers = {}

    # ---------- Measurement-Tab ----------
    status = tk.StringVar(value=f"Video: {video_path}\nIMU: {imu_csv}")
    tk.Label(measurement_tab, textvariable=status, justify="left").pack(anchor="w", padx=10)

    button_row = tk.Frame(measurement_tab)
    button_row.pack(fill="x", padx=10, pady=5)

    fig = Figure(figsize=(9, 6), dpi=100)
    axes = fig.subplots(3, 1, sharex=True)      # 3 Plots untereinander, gleiche Zeitachse
    canvas = FigureCanvasTkAgg(fig, master=measurement_tab)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    def on_analyse():
        if USE_FAKE:
            current["data"] = fake_analyse(video_path, imu_csv)
        else:
            from pipeline import analyse
            current["data"] = analyse(video_path, imu_csv)
        markers.clear()
        draw_plot(axes, canvas, current["data"], markers)
        status.set("Analyse fertig. Klick in den Plot setzt den Marker '1st push'.")

    tk.Button(button_row, text="Analysieren", command=on_analyse).pack(side="left")

    def on_plot_click(event):
        # event.xdata ist die Zeit an der Klickstelle (None, wenn neben den Plot geklickt)
        if current["data"] is None or event.xdata is None:
            return
        markers["1st push"] = round(event.xdata, 3)
        draw_plot(axes, canvas, current["data"], markers)
        status.set(f"Marker '1st push' bei {event.xdata:.3f} s")

    def on_save():
        if current["data"] is None:
            messagebox.showwarning("Keine Daten", "Bitte zuerst 'Analysieren' klicken.")
            return
        folder = filedialog.askdirectory(title="Ordner zum Speichern wählen")
        if not folder:
            return
        save_run(folder, current["data"], video_path, markers)
        messagebox.showinfo("Gespeichert", f"Gespeichert in:\n{folder}")

    tk.Button(button_row, text="Speichern", command=on_save).pack(side="left", padx=(10, 0))
    canvas.mpl_connect("button_press_event", on_plot_click)

        # ---------- Analysis-Tab ----------
    load_row = tk.Frame(analysis_tab)
    load_row.pack(fill="x", padx=10, pady=5)

    fig2 = Figure(figsize=(6, 6), dpi=100)
    axes2 = fig2.subplots(3, 1, sharex=True)
    canvas2 = FigureCanvasTkAgg(fig2, master=analysis_tab)
    canvas2.get_tk_widget().pack(side="left", fill="both", expand=True)

    # Platz für den Video-Player
    video_frame = tk.Frame(analysis_tab, width=400)
    video_frame.pack(side="right", fill="both", padx=10)
    video_label = tk.Label(video_frame, text="Hier kommt der Video-Player hin")
    video_label.pack(pady=20)

    def on_load():
        folder = filedialog.askdirectory(title="Gespeicherte Messung wählen")
        if not folder:
            return
        data, saved_video, saved_markers = load_run(folder)
        draw_plot(axes2, canvas2, data, saved_markers)
        video_label.config(text=f"Video: {saved_video}\nMarker: {saved_markers}")
        # Wenn Simons Player fertig ist, z. B.:
        # from player import VideoPlayer
        # VideoPlayer(video_frame, saved_video).pack()

    tk.Button(load_row, text="Messung laden", command=on_load).pack(side="left")

    window.mainloop()

