from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from multiprocessing import Queue
from kivy.vector import Vector
import math


class TouchInput(Widget):
    def __init__(self, **kwargs):
        super(TouchInput, self).__init__(**kwargs)
        self.touch_positions = TouchPositions()

    def on_touch_down(self, touch):
        self.touch_positions.add_touch(touch)

    def on_touch_up(self, touch):
        self.touch_positions.remove_touch(touch)

class TouchPositions(object):
    def __init__(self):
        self.segments = {}
        self.touchs = {}
        self.events = Queue()

    def add_touch(self, touch):
        if len(self.touchs) < 4:
            self.touchs[touch.id] = touch.pos
            print(len(self.touchs))
            self.calculate_distance()

    def remove_touch(self, touch):
        if touch.id in self.touchs:
            self.touchs.pop(touch.id)
            print(self.touchs)

        for points in self.segments.copy():
            values = self.segments[points]

            if touch.id in values[1]:
                self.segments.pop(points)
                event = ("no_located", "", "")
                self.events.put(event)

    def calculate_distance(self):
        xy = []
        i = 0
        dist = []
        if len(self.touchs) > 2:
            for name, pos in self.touchs.items():
                xy.append((pos, name))
                print("XY", xy)
                if i > 0:
                    dist.append((abs(Vector(pos).distance(xy[i - 1][0])), (name, xy[i - 1][1])))

                i += 1
            dist.append((abs(Vector(xy[len(xy) - 1][0]).distance(xy[0][0])), (xy[0][1], xy[len(xy) - 1][1])))
            print(len(dist))

            self.calculate_segments(dist)

    def calculate_segments(self, d):
        segment = d
        for i in range(len(segment)):

            if segment[i][0] > 310 and segment[i][0] < 380:
                self.segments['0A'] = segment[i]
                print("DISTANCIA 0A OK")

            if segment[i][0] > 400 and segment[i][0] < 440:
                self.segments['0B'] = segment[i]
                print("DISTANCIA 0B OK")

            if segment[i][0] > 50 and segment[i][0] < 80:
                self.segments['AB'] = segment[i]
                print("DISTANCIA AB OK")

        self.calculate_points()

    def calculate_points(self):
        if len(self.segments) > 2:
            if self.segments['0A'][1][0] == self.segments['0B'][1][0]:
                id_point_0 = self.segments['0A'][1][0]
                id_point_A = self.segments['0A'][1][1]
            else:
                id_point_0 = self.segments['0A'][1][1]
                id_point_A = self.segments['0A'][1][0]

            if self.segments['0B'][1][0] == self.segments['AB'][1][0]:
                id_point_B = self.segments['0B'][1][0]
            else:
                id_point_B = self.segments['0B'][1][1]

            point_0 = self.touchs[id_point_0]
            point_A = self.touchs[id_point_A]
            point_B = self.touchs[id_point_B]

            self.calculate_angle(point_0, point_A, point_B)

    def calculate_angle(self, point_0, point_A, point_B):

        print(point_A)
        print(point_B)
        print(point_0)

        x1 = point_0[0]
        y1 = point_0[1]
        x2 = point_B[0]
        y2 = point_B[1]

        x = x2 - x1
        y = y2 - y1

        angle = math.atan2(y, x) * (180 / math.pi)

        print("ANGULO", angle)

        event = ("located", *point_0, round(angle, 2), 0)
        self.events.put(event)