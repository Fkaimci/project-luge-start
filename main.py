import tkinter as tk
from tkinter import filedialog

from GUI import create_gui

# Ein unsichtbares Hauptfenster, damit die Datei-Dialoge funktionieren
root = tk.Tk()
root.withdraw()

video_path = filedialog.askopenfilename(title="Video wählen",
                                        filetypes=[("Video", "*.mp4 *.mov *.avi"), ("Alle Dateien", "*.*")])
imu_csv = filedialog.askopenfilename(title="IMU-CSV wählen",
                                     filetypes=[("CSV", "*.csv"), ("Alle Dateien", "*.*")])
root.destroy()

create_gui(video_path, imu_csv)
