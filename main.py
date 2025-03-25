import matplotlib.pyplot as plt
import numpy as np
import uuid
from typing import Dict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import time

# Track appearance constants
TRACK_COLOR = (243 / 255, 167 / 255, 18 / 255)
TRACK_HIGHLIGHT_COLOR = (219 / 255, 43 / 255, 57 / 255)
TRAIN_COLOR = (220 / 255, 50 / 255, 50 / 255)
SWITCH_COLOR = (50 / 255, 200 / 255, 50 / 255)
SWITCH_ACTIVE_COLOR = (200 / 255, 200 / 255, 50 / 255)
STATION_COLOR = (50 / 255, 50 / 255, 200 / 255)

# Line thickness
LINE_THICKNESS = 4

# Global list to keep references to track segments
track_segments = []

class Point:
    """
    A 2D point.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f})"

class TrackSegment:
    """
    Default class for a track segment.
    """

    def __init__(self, id=None):
        self.id = id or str(uuid.uuid4())[:8]
        self.connections = {}
        self.color = TRACK_COLOR

    def draw(self, ax):
        """Draw the track segment on the Matplotlib axes."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_point_at_distance(self, start_point, distance) -> Point:
        """Get coordinates at a specific distance from a start point."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_length(self) -> float:
        """Get the length of the track segment."""
        raise NotImplementedError("Subclasses must implement this method")

    def get_connection_points(self) -> Dict[str, Point]:
        """Get a list of connection points for the track segment."""
        raise NotImplementedError("Subclasses must implement this method")

    def highlight(self):
        """Highlight the track segment."""
        self.color = TRACK_HIGHLIGHT_COLOR

    def remove_highlight(self):
        """Remove highlight on the track segment."""
        self.color = TRACK_COLOR

class StraightTrackSegment(TrackSegment):
    """
    Straight track segment with rounded caps.
    """

    def __init__(self, start: Point, end: Point, id=None):
        super().__init__(id)
        self.start = start
        self.end = end
        self.length = start.distance_to(end)

    def draw(self, ax):
        """Draw the track segment on the Matplotlib axes."""
        ax.plot([self.start.x, self.end.x],
                [self.start.y, self.end.y],
                color=self.color,
                linewidth=LINE_THICKNESS,
                solid_capstyle='round')

    def get_point_at_distance(self, start_point, distance) -> Point:
        """Determines which point end is the start point."""
        t = distance / self.length
        if start_point.distance_to(self.start) < 1:
            x = self.start.x + t * (self.end.x - self.start.x)
            y = self.start.y + t * (self.end.y - self.start.y)
        else:
            x = self.end.x + t * (self.start.x - self.end.x)
            y = self.end.y + t * (self.start.y - self.end.y)
        return Point(x, y)

    def get_length(self) -> float:
        return self.length

    def get_connection_points(self) -> Dict[str, Point]:
        return {"start": self.start, "end": self.end}


class TrackViewer(tk.Tk):
    """
    Tkinter window to display the track network using Matplotlib.
    """

    def __init__(self):
        super().__init__()
        self.title("OnTrack Line Intelligent Network")
        self.geometry("1200x800")

        # Create a frame for the visualization
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create matplotlib figure and canvas
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor='#222222')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#000000')

        # Configure the plot
        self.ax.set_aspect('equal')
        self.ax.set_xlim(300, 900)
        self.ax.set_ylim(300, 700)
        self.ax.axis('off')  # Hide the axes

        # Create the canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Draw the track segments
        self.update_display()

        # Animation variables
        self.animation_running = False
        self.after_id = None

        # Start animation
        self.animate()

    def animate(self):
        """Basic animation loop."""
        if self.animation_running:
            # Add animation code here
            pass

        self.after_id = self.after(33, self.animate)  # ~30fps

    def update_display(self):
        """Update the display with all track segments."""
        self.ax.clear()
        self.ax.set_facecolor('#000000')
        self.ax.set_xlim(300, 900)
        self.ax.set_ylim(300, 700)
        self.ax.axis('off')

        # Draw all track segments
        for segment in track_segments:
            segment.draw(self.ax)

        self.canvas.draw()

    def toggle_animation(self):
        """Toggle animation on/off."""
        self.animation_running = not self.animation_running

    def __del__(self):
        if self.after_id:
            self.after_cancel(self.after_id)


def main():
    main_line = StraightTrackSegment(Point(450, 500), Point(600, 500))
    connected_line = StraightTrackSegment(Point(600, 500), Point(710, 620))

    track_segments.append(main_line)
    track_segments.append(connected_line)

    window = TrackViewer()
    window.mainloop()


if __name__ == "__main__":
    main()