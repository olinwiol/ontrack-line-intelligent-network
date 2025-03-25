import pyglet  # Animation library for visualization
from pyglet import *
import numpy as np
import uuid  # Identification library
from typing import Dict

# Create window with visible=True to ensure it's displayed
window = pyglet.window.Window(width=1200, height=800, caption="OnTrack Line Intelligent Network", visible=True)
batch = pyglet.graphics.Batch()

# Global list to keep references to track segments
track_segments = []

TRACK_COLOR = (243, 167, 18)
TRACK_HIGHLIGHT_COLOR = (219, 43, 57)
TRAIN_COLOR = (220, 50, 50)
SWITCH_COLOR = (50, 200, 50)
SWITCH_ACTIVE_COLOR = (200, 200, 50)
STATION_COLOR = (50, 50, 200)

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
        self.visual_elements = []

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
        for element in self.visual_elements:
            if hasattr(element, "color"):
                element.color = TRACK_HIGHLIGHT_COLOR

    def remove_highlight(self):
        """Remove highlight on the track segment."""
        for element in self.visual_elements:
            if hasattr(element, "color"):
                element.color = TRACK_COLOR

class StraightTrackSegment(TrackSegment):
    """
    Straight track segment.
    """

    def __init__(self, start: Point, end: Point, id=None):
        super().__init__(id)
        self.start = start
        self.end = end
        self.length = start.distance_to(end)

        self.line = shapes.Line(
            start.x, start.y, end.x, end.y,
            thickness=4, color=TRACK_COLOR, batch=batch
        )
        self.visual_elements.append(self.line)

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

@window.event
def on_draw():
    window.clear()
    batch.draw()

def update(dt):
    pass

def main():
    straight = StraightTrackSegment(Point(400, 400), Point(700, 400))
    track_segments.append(straight)
    pyglet.clock.schedule_interval(update, 1 / 60.0)

if __name__ == "__main__":
    main()
    pyglet.app.run()