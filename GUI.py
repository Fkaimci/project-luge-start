import numpy as np
import tkinter as tk
from plot import plot_aruco_coordinates, plot_aruco_coordinates_animated
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_gui(results):
    window = tk.Tk()
    window.title("BestLugeStart EUWEST analyzing tool")
    window.geometry("1100x650")

    label = tk.Label(window, text="Analyze des BestLugeStart EUWEST", font=("Arial", 14))
    label.pack(pady=20)

    fig = plot_aruco_coordinates(results)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    
    window.mainloop()

