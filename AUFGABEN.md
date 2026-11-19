# Aufgaben bis zur FAT (10.12.2026)

## So passt am Ende alles zusammen

1. **Die Schnittstellen stehen schon im Code.** `video.py`, `imu.py`, `sync.py` und `storage.py` enthalten
   die Funktionen mit Namen, Eingaben und Rückgabe. Ihr füllt nur den Inhalt. Namen, Eingaben und
   Rückgabe ändert ihr nur nach Absprache in der Gruppe.
2. **Jede Datei hat eine Besitzerin oder einen Besitzer** (steht oben in der Datei). In fremden Dateien nichts ändern.
3. **Niemand wartet auf andere.** `fake_data.py` erzeugt ein Testvideo und eine IMU-CSV, deren richtige
   Lösung bekannt ist. Damit testet jede:r den eigenen Teil.
4. **`python check.py` vor jedem Push.** Es prüft jeden Teil gegen die Fake-Daten und am Ende den
   ganzen Ablauf. Dein Teil ist fertig, wenn deine Zeilen `OK` zeigen. Pushe nie, wenn eine vorher
   grüne Zeile auf `FEHLER` springt.
5. **Die GUI ruft nur `pipeline.analyse(...)` auf** und nicht die einzelnen Module. So hängt die GUI an
   genau einer Stelle an den anderen Teilen.
6. Alle Werte in SI: Zeit `t` in s, Weg in m, `v` in m/s, `a` in m/s², `w` in rad/s.

Stand 15.11.: Alles steht auf `OFFEN`. `ArUco.py`, `GUI.py`, `plot.py` und `main.py` sind Marius'
erster Prototyp. Sie laufen weiter, bis die neuen Teile fertig sind.

## Live kommt später dazu, ohne Umbau

Video und IMU liefern ihre Daten **Sample für Sample** über einen Generator (`iter_video`, `iter_imu`).
Die Datei-Funktionen (`track_video`, `load_imu`) sammeln nur diesen Generator ein.

- Video live: `iter_video(0, ...)` statt `iter_video("datei.mp4", ...)`. `cv2.VideoCapture` nimmt beides.
- IMU live: später eine zweite Quelle in `iter_imu` (Bluetooth), die dasselbe `(t, a, w)` liefert.
- GUI live: der Measurement-Tab holt mit `window.after(...)` immer das nächste Sample und zeichnet es.
  Bei „Stop“ werden die gesammelten Samples an `synchronize` gegeben, genau wie im Datei-Modus.

Live wird erst gebaut, wenn der Datei-Modus läuft und Hollaus/Nocker bestätigt haben, dass sie es wollen.

## Simon: Video (`video.py`)

1. `iter_video(source, marker_id, marker_size_m)`: pro Frame `(t, x, y, frame)` liefern.
   `t = frame_nr / fps`. Mittelpunkt des Markers aus den 4 Ecken. Pixel → Meter über die Markerkante.
   y nach oben positiv. Frame ohne Marker: `x = y = nan`, nicht weglassen.
2. `find_video_event(t, x)`: Zeitpunkt der letzten max. Streckung = letztes lokales Minimum von x vor dem
   Abstoß. Muss mit Rauschen und `nan` klarkommen (glätten), sonst scheitert die Zeile „alles zusammen“.
3. Fertig, wenn `check.py` bei Simon zweimal `OK` zeigt. Dann mit dem echten Video
   `data/VIDEO/BesterLugeStartEUWEST.mp4` (Marker 0 und 1) prüfen, ob die Kurve plausibel aussieht.
4. Danach: Video-Player für den Analysis-Tab als eigenes Widget in `video_player.py` (Frame zeigen,
   zu Zeit `t` springen). Marius baut es in die GUI ein. Dann optional Pose Estimation.

Vorlage: `mci-luge-start/tracking.py`.

## Franka: IMU und Sync (`imu.py`, `sync.py`)

1. `iter_imu(source)`: CSV lesen, pro Sample `(t, a, w)` liefern. Zeit in s, `a` ohne Erdbeschleunigung
   in m/s², `w` in rad/s. Die Fake-CSV hat die Spalten wie ein Movella-Export (µs, m/s², deg/s).
   iMit einer echten Aufnahme vergleichen und anpassen.
2. `ntegrate_velocity(t, a_x)`: v aus a, Start bei v = 0.
3. `find_imu_event(t, v)`: Umkehrpunkt v ≈ 0 direkt vor dem Abstoß (nicht irgendeine Nullstelle).
4. `synchronize(video, imu)`: Versatz = Video-Event minus IMU-Event, IMU-Zeit verschieben, beide auf
   eine gemeinsame Zeitachse resamplen (`np.interp`). Rückgabe: ein dict mit allen Signalen + `offset`.
5. Fertig, wenn `check.py` bei Franka dreimal `OK` zeigt. Dann eine echte Aufnahme mit dem Xsens DOT.

Vorlage: `mci-luge-start/sync.py`.

## Marius: GUI und Speichern (`GUI.py`, `storage.py`, `main.py`)

1. `storage.py`: `save_run` und `load_run` (Format steht oben in der Datei). Fertig, wenn `check.py`
   bei Marius `OK` zeigt.
2. `main.py`: fester Windows-Pfad raus, Video und IMU-CSV per Datei-Dialog wählen.
3. GUI mit zwei Tabs (`ttk.Notebook`): Measurement und Analysis.
4. Measurement-Tab: Button „Analysieren“ ruft `pipeline.analyse(video, csv)` auf und zeigt x, v und a
   untereinander auf derselben Zeitachse, mit einer Linie beim Sync-Event.
5. Save-Button (ruft `save_run`), Marker setzen per Klick in den Plot („1st push“, wird mitgespeichert).
6. Analysis-Tab: gespeicherte Messung laden (`load_run`) und anzeigen, Simons Video-Player einbauen.

Bis die anderen fertig sind, testest du die GUI mit `fake_data.truth_video()` und `fake_data.truth_imu()`.

## Termine

| bis | was | Test |
|---|---|---|
| 22.11. | alle Zeilen in `check.py` auf `OK` | `python check.py` |
| 26.11. | GUI zeigt eine echte Messung (Video + Xsens), alle 4 Must-Punkte | gemeinsam vorführen |
| 03.12. | Optionals: Save, Marker, Analysis-Tab, Video-Player, evtl. Pose, evtl. Live | gemeinsam vorführen |
| 09.12. | README (Setup, Quick Start, Credits), FAT-Probelauf | jede:r führt einen fremden Teil vor |

Offen an Hollaus/Nocker: Wie läuft die FAT ab (Dauer, Folien)? Live oder aus Datei?
Wo liegen Video und CSV vom 30.10.?
