"""Video-Player für den Analysis-Tab.                      Gehört: Marius

    seek = create_player(parent, video_path)   baut Bild + Slider + Play-Button in `parent`
    seek(t)                                    springt zur Zeit t [s]
"""
import tkinter as tk

import cv2
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_player(parent, video_path):
    # ---------- Video öffnen ----------
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = n_frames / fps                    # Länge in Sekunden

    # ---------- Bild ----------
    fig = Figure(figsize=(4, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.axis("off")                               # keine Achsen um das Bild
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_frame(t):
        """Liest das Bild zur Zeit t [s] und zeigt es an."""
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   # OpenCV: BGR, Matplotlib: RGB
        ax.clear()
        ax.axis("off")
        ax.imshow(frame)
        ax.set_title(f"t = {t:.2f} s")
        canvas.draw()

        # ---------- Slider ----------
    time_var = tk.DoubleVar(value=0.0)

    def seek(t):
        """Springt zur Zeit t (z. B. nach Klick in den Plot)."""
        time_var.set(t)                          # Slider mitbewegen
        show_frame(t)

    def on_slide(value):
        show_frame(float(value))                 # Slider liefert den Wert als Text

    slider = tk.Scale(parent, from_=0, to=duration, resolution=0.01, variable=time_var,
                      orient=tk.HORIZONTAL, label="Zeit [s]", command=on_slide)
    slider.pack(fill="x", padx=10)

        # ---------- Play/Pause ----------
    playing = {"on": False}                      # dict, damit Funktionen es ändern können

    def next_frame():
        if not playing["on"]:
            return
        t = time_var.get() + 1 / fps             # ein Bild weiter
        if t >= duration:                        # Ende erreicht
            playing["on"] = False
            play_button.config(text="Play")
            return
        seek(t)
        parent.after(int(1000 / fps), next_frame)   # in 1/fps Sekunden nochmal aufrufen

    def on_play():
        playing["on"] = not playing["on"]        # an <-> aus
        if playing["on"]:
            play_button.config(text="Pause")
            next_frame()
        else:
            play_button.config(text="Play")

    play_button = tk.Button(parent, text="Play", command=on_play)
    play_button.pack(pady=5)

    show_frame(0.0)                              # erstes Bild anzeigen
    return seek



if __name__ == "__main__":
    window = tk.Tk()
    create_player(window, "data/VIDEO/BesterLugeStartEUWEST.mp4")
    window.mainloop()

    cap = cv2.VideoCapture("data/VIDEO/BesterLugeStartEUWEST.mp4")
    fps = cap.get(cv2.CAP_PROP_FPS)
    n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("geöffnet:", cap.isOpened(), "fps:", fps, "frames:", n_frames)   # NEU

    ret, frame = cap.read()
    print("Bild gelesen:", ret)                                          # NEU