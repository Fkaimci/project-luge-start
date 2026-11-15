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
    if not results:
        print("No results to plot.")
        return None, None

    frame_indices = [r[0] for r in results]
    x_coordinates = [r[2] for r in results]

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    line, = ax.plot([], [], marker='o', linestyle='-', color='b')
    ax.set_xlim(min(frame_indices), max(frame_indices))
    pad = (max(x_coordinates) - min(x_coordinates)) * 0.05 or 1
    ax.set_ylim(min(x_coordinates) - pad, max(x_coordinates) + pad)
    ax.set_title("ArUco Marker X-Coordinates Over Time")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("X-Coordinate (pixels)")
    ax.grid()

    def update(i):
        line.set_data(frame_indices[:i+1], x_coordinates[:i+1])
        return line,

    ani = FuncAnimation(fig, update, frames=len(results),
                        interval=interval, blit=True, repeat=False)
    return fig, ani