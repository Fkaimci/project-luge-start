from ArUco import GetXCoordinatesAruco
from plot import plot_aruco_coordinates
from GUI import create_gui

video_path = "C:/Users/maval/Documents/mandc/05_sem5/device development/project_dev_dev/luge_start_2.0/project-luge-start/data/VIDEO/BesterLugeStartEUWEST.mp4"  # Path to video file
results = GetXCoordinatesAruco(video_path, marker_id=1)  # Specify the marker ID to track (optional)
create_gui(results)  # Create the GUI and pass the results to it
