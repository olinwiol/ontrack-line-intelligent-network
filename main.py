import matplotlib.pyplot as plt
import numpy as np
import uuid
from typing import Dict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import time

from pyglet.extlibs.earcut import zOrder

# Global constants
TRACK_COLOR = (243 / 255, 167 / 255, 18 / 255)
TRACK_HIGHLIGHT_COLOR = (219 / 255, 43 / 255, 57 / 255)
TRAIN_COLOR = (220 / 255, 50 / 255, 50 / 255)
SWITCH_COLOR = (243 / 255, 167 / 255, 18 / 255)
SWITCH_ACTIVE_COLOR = (170 / 255, 34 / 255, 45 / 255)
STATION_COLOR = (50 / 255, 50 / 255, 200 / 255)
LINE_THICKNESS = 4

# Global variables
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
    Straight track segment
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

class CircularTrackSegment(TrackSegment):
    """
    Circular track segment.
    """

    def __init__(self, start: Point, rotation_start: float, rotation_end: float, radius: float, id=None):
        super().__init__(id)
        self.start = start
        self.rotation_start = rotation_start
        self.rotation_end = rotation_end
        self.rotation = rotation_end - rotation_start
        self.radius = radius
        self.length = np.deg2rad(self.rotation) * radius

        theta_start_rad = np.deg2rad(self.rotation_start)

        self.center = Point(
            self.start.x - self.radius * np.cos(theta_start_rad),
            self.start.y - self.radius * np.sin(theta_start_rad)
        )

        theta_end_rad = np.deg2rad(self.rotation_end)
        self.end = Point(
            self.center.x + self.radius * np.cos(theta_end_rad),
            self.center.y + self.radius * np.sin(theta_end_rad)
        )

    def draw(self, ax):
        numeric_points = 100

        theta = np.linspace(np.deg2rad(self.rotation_start),
                            np.deg2rad(self.rotation_end),
                            numeric_points)

        x = self.center.x + self.radius * np.cos(theta)
        y = self.center.y + self.radius * np.sin(theta)

        ax.plot(x, y, color=self.color, linewidth=LINE_THICKNESS, solid_capstyle='round')

    def get_point_at_distance(self, start_point, distance) -> Point:
        if start_point.distance_to(self.start) < 1:
            theta = np.deg2rad(self.rotation_start) + distance / self.length * np.deg2rad(self.rotation)
            x = self.start.x + self.radius * np.cos(theta)
            y = self.start.y + self.radius * np.sin(theta)
        else:
            theta = np.deg2rad(self.rotation_end) - distance / self.length * np.deg2rad(self.rotation)
            x = self.end.x + self.radius * np.cos(theta)
            y = self.end.y + self.radius * np.sin(theta)
        return Point(x, y)

    def get_length(self) -> float:
        return self.length

    def get_connection_points(self) -> Dict[str, Point]:
        return {"start": self.start, "end": self.end}

class SwitchSegment(TrackSegment):
    """
    Straight track segment with a switch.
    """

    def __init__(self, start: Point, main_end: Point, alt_end: Point, id=None):
        super().__init__(id)
        self.start = start
        self.main_end = main_end
        self.alt_end = alt_end
        self.active = False
        self.length = start.distance_to(main_end)

    def draw(self, ax):
        """Draw the track segment on the Matplotlib axes."""
        ax.plot([self.start.x, self.main_end.x],
                [self.start.y, self.main_end.y],
                color=TRACK_COLOR if not self.active else SWITCH_ACTIVE_COLOR,
                linewidth=LINE_THICKNESS,
                solid_capstyle='round',
                zorder=2 if not self.active else 1
        )
        ax.plot([self.start.x, self.alt_end.x],
                [self.start.y, self.alt_end.y],
                color=TRACK_COLOR if self.active else SWITCH_ACTIVE_COLOR,
                linewidth=LINE_THICKNESS,
                solid_capstyle='round',
                zorder=2 if self.active else 1
        )


    def get_point_at_distance(self, start_point, distance) -> Point:
        """Determine which point end is the start point."""
        if start_point.distance_to(self.start) < 1:
            t = distance / self.length
            x = self.start.x + t * (self.main_end.x - self.start.x)
            y = self.start.y + t * (self.main_end.y - self.start.y)
        else:
            t = distance / self.length
            x = self.start.x + t * (self.alt_end.x - self.start.x)
            y = self.start.y + t * (self.alt_end.y - self.start.y)
        return Point(x, y)

    def get_length(self) -> float:
        self.length = self.start.distance_to(self.main_end) if not self.active else self.start.distance_to(self.alt_end)
        return self.length

    def get_connection_points(self) -> Dict[str, Point]:
        return {"start": self.start, "main_end": self.main_end, "alt_end": self.alt_end}

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

        # Keybindings
        self.bind("<space>", self.on_spacebar_press)

    def on_spacebar_press(self, event):
        self.toggle_activate()

    def toggle_activate(self):
        """Toggle the activation of the track."""
        for segment in track_segments:
            if isinstance(segment, SwitchSegment):
                segment.active = not segment.active
                self.update_display()
                time.sleep(0.1)

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
    track_line_1 = StraightTrackSegment(Point(400, 500), Point(600, 500))
    switch_1 = SwitchSegment(track_line_1.end, Point(625, 525), Point(625, 500))
    turn_1 = CircularTrackSegment(switch_1.alt_end, 90, -140, 40)
    turn_2 = CircularTrackSegment(turn_1.end, 40, 95, 80)
    track_line_2 = StraightTrackSegment(turn_2.end, Point(450, 450))
    turn_3 = CircularTrackSegment(track_line_2.end, -85, -270, 25)
    turn_4 = CircularTrackSegment(switch_1.main_end, -45, 90, 30)
    track_line_3 = StraightTrackSegment(turn_4.end, Point(400, turn_4.end.y))
    turn_5 = CircularTrackSegment(track_line_3.end, 90, 270, 38.1)


    track_segments.append(track_line_1)
    track_segments.append(switch_1)
    track_segments.append(turn_1)
    track_segments.append(turn_2)
    track_segments.append(track_line_2)
    track_segments.append(turn_3)
    track_segments.append(turn_4)
    track_segments.append(track_line_3)
    track_segments.append(turn_5)

    print(turn_5.get_connection_points())

    window = TrackViewer()
    window.update_display()
    window.mainloop()


if __name__ == "__main__":
    main()