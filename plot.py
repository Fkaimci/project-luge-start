import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def plot_aruco_coordinates(results):
    if not results:
        print("No results to plot.")
        return

    # Extract frame indices and x-coordinates
    frame_indices = [result[0] for result in results]
    x_coordinates = [result[2] for result in results]

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.plot(frame_indices, x_coordinates, marker='o', linestyle='-', color='b')
    ax.set_title("ArUco Marker X-Coordinates Over Time")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("X-Coordinate (pixels)")
    ax.grid()

    return fig


def plot_aruco_coordinates_animated(results, interval=33):

    return fig, ani