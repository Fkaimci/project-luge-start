import cv2
import numpy as np

print("OpenCV version:", cv2.__version__)

# Create ArUco markers

arucodict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
marker_id0 = 0
marker_id1 = 1
marker_size = 200  # Size of the marker in pixels
marker_image0 = cv2.aruco.generateImageMarker(arucodict, marker_id0, marker_size)
marker_image1 = cv2.aruco.generateImageMarker(arucodict, marker_id1, marker_size)

cv2.imwrite("marker_0.png", marker_image0)
cv2.imwrite("marker_1.png", marker_image1)


# Detect ArUco markers in an video

def GetXCoordinatesAruco(video_path, marker_id=None):
    parameters = cv2.aruco.DetectorParameters()
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(arucodict, parameters)

    cap = cv2.VideoCapture(video_path)
    results = []  # (frame_idx, marker_id, x)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return results

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            for corner, id_ in zip(corners, ids.flatten()):
                if marker_id is not None and id_ != marker_id:
                    continue
                x = float(corner[0][0][0])  # obere linke Ecke
                results.append((frame_idx, int(id_), x))

        frame_idx += 1

    cap.release()
    return results