import sys

from GUI import create_gui
from video import iter_video

# Video als Argument: python main.py data/VIDEO/Marius1.mov  (ohne Argument: Simon3)
video_path = sys.argv[1] if len(sys.argv) > 1 else "data/VIDEO/Simon3.mov"
results = [(t, 1, x) for t, x, _y, _frame in iter_video(video_path, marker_id=1)]  # (Zeit, Marker, x) wie bisher
create_gui(results)
