#!/usr/bin/env python3
"""
Mathematical Utilities for Dynamic Art Generator
Provides mathematical functions, geometric operations, and physics calculations

Author: Claude Assistant
Version: 1.0
"""

import numpy as np
import math
from typing import Tuple, List, Union, Optional
from dataclasses import dataclass

@dataclass
class Vector2D:
    """2D Vector class with common operations"""
    x: float
    y: float
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalize(self) -> 'Vector2D':
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)
    
    def dot(self, other: 'Vector2D') -> float:
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector2D') -> float:
        return self.x * other.y - self.y * other.x
    
    def rotate(self, angle: float) -> 'Vector2D':
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))


class ColorUtils:
    """Color space conversions and operations"""
    
    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB color space"""
        h = h % 360.0
        c = v * s
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255)
        )
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV color space"""
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        v = max_val
        
        # Saturation
        s = 0 if max_val == 0 else diff / max_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        return (h, s, v)
    
    @staticmethod
    def interpolate_color(color1: Tuple[int, int, int], 
                         color2: Tuple[int, int, int], 
                         t: float) -> Tuple[int, int, int]:
        """Interpolate between two RGB colors"""
        t = max(0, min(1, t))
        return (
            int(color1[0] * (1 - t) + color2[0] * t),
            int(color1[1] * (1 - t) + color2[1] * t),
            int(color1[2] * (1 - t) + color2[2] * t)
        )
    
    @staticmethod
    def get_complementary_color(r: int, g: int, b: int) -> Tuple[int, int, int]:
        """Get complementary color"""
        return (255 - r, 255 - g, 255 - b)
    
    @staticmethod
    def get_analogous_colors(h: float, s: float, v: float, 
                           count: int = 3, spread: float = 30) -> List[Tuple[int, int, int]]:
        """Get analogous colors around a base hue"""
        colors = []
        for i in range(count):
            offset = (i - count // 2) * spread
            new_h = (h + offset) % 360
            colors.append(ColorUtils.hsv_to_rgb(new_h, s, v))
        return colors


class GeometryUtils:
    """Geometric calculations and operations"""
    
    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate distance between two points"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    @staticmethod
    def angle_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate angle between two points in radians"""
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    
    @staticmethod
    def rotate_point(point: Tuple[float, float], center: Tuple[float, float], 
                    angle: float) -> Tuple[float, float]:
        """Rotate a point around a center by given angle (radians)"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Translate to origin
        x = point[0] - center[0]
        y = point[1] - center[1]
        
        # Rotate
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        # Translate back
        return (new_x + center[0], new_y + center[1])
    
    @staticmethod
    def point_in_circle(point: Tuple[float, float], center: Tuple[float, float], 
                       radius: float) -> bool:
        """Check if point is inside a circle"""
        return GeometryUtils.distance(point, center) <= radius
    
    @staticmethod
    def point_in_rectangle(point: Tuple[float, float], rect: Tuple[float, float, float, float]) -> bool:
        """Check if point is inside a rectangle (x, y, width, height)"""
        x, y = point
        rx, ry, rw, rh = rect
        return rx <= x <= rx + rw and ry <= y <= ry + rh
    
    @staticmethod
    def line_intersection(line1: Tuple[Tuple[float, float], Tuple[float, float]],
                         line2: Tuple[Tuple[float, float], Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """Find intersection point of two lines"""
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None  # Lines are parallel
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        
        intersection_x = x1 + t * (x2 - x1)
        intersection_y = y1 + t * (y2 - y1)
        
        return (intersection_x, intersection_y)
    
    @staticmethod
    def bezier_curve(p0: Tuple[float, float], p1: Tuple[float, float], 
                    p2: Tuple[float, float], p3: Tuple[float, float], 
                    t: float) -> Tuple[float, float]:
        """Calculate point on cubic Bezier curve"""
        t = max(0, min(1, t))
        u = 1 - t
        
        x = (u**3 * p0[0] + 
             3 * u**2 * t * p1[0] + 
             3 * u * t**2 * p2[0] + 
             t**3 * p3[0])
        
        y = (u**3 * p0[1] + 
             3 * u**2 * t * p1[1] + 
             3 * u * t**2 * p2[1] + 
             t**3 * p3[1])
        
        return (x, y)
    
    @staticmethod
    def generate_circle_points(center: Tuple[float, float], radius: float, 
                             num_points: int) -> List[Tuple[float, float]]:
        """Generate points around a circle"""
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        return points
    
    @staticmethod
    def generate_ellipse_points(center: Tuple[float, float], a: float, b: float, 
                              num_points: int, rotation: float = 0) -> List[Tuple[float, float]]:
        """Generate points around an ellipse"""
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = a * math.cos(angle)
            y = b * math.sin(angle)
            
            # Apply rotation
            if rotation != 0:
                cos_r = math.cos(rotation)
                sin_r = math.sin(rotation)
                rotated_x = x * cos_r - y * sin_r
                rotated_y = x * sin_r + y * cos_r
                x, y = rotated_x, rotated_y
            
            points.append((center[0] + x, center[1] + y))
        return points


class PhysicsUtils:
    """Physics simulation utilities"""
    
    @staticmethod
    def integrate_verlet(position: Vector2D, velocity: Vector2D, acceleration: Vector2D, 
                        dt: float) -> Tuple[Vector2D, Vector2D]:
        """Verlet integration for stable physics simulation"""
        new_position = position + velocity * dt + acceleration * (0.5 * dt * dt)
        new_velocity = velocity + acceleration * dt
        return new_position, new_velocity
    
    @staticmethod
    def spring_force(position: Vector2D, target: Vector2D, spring_constant: float, 
                    damping: float, velocity: Vector2D) -> Vector2D:
        """Calculate spring force with damping"""
        displacement = target - position
        spring_force = displacement * spring_constant
        damping_force = velocity * -damping
        return spring_force + damping_force
    
    @staticmethod
    def gravitational_force(pos1: Vector2D, mass1: float, pos2: Vector2D, 
                           mass2: float, g_constant: float = 1.0) -> Vector2D:
        """Calculate gravitational force between two masses"""
        displacement = pos2 - pos1
        distance_sq = displacement.magnitude()**2
        
        if distance_sq < 1e-6:  # Avoid division by zero
            return Vector2D(0, 0)
        
        force_magnitude = g_constant * mass1 * mass2 / distance_sq
        force_direction = displacement.normalize()
        
        return force_direction * force_magnitude
    
    @staticmethod
    def collision_response_elastic(v1: Vector2D, m1: float, v2: Vector2D, m2: float) -> Tuple[Vector2D, Vector2D]:
        """Calculate velocities after elastic collision"""
        total_mass = m1 + m2
        
        new_v1 = ((m1 - m2) * v1 + 2 * m2 * v2) / total_mass
        new_v2 = ((m2 - m1) * v2 + 2 * m1 * v1) / total_mass
        
        return new_v1, new_v2
    
    @staticmethod
    def pendulum_force(position: Vector2D, anchor: Vector2D, length: float, 
                      gravity: float) -> Vector2D:
        """Calculate force on a pendulum"""
        displacement = position - anchor
        current_length = displacement.magnitude()
        
        if current_length < 1e-6:
            return Vector2D(0, 0)
        
        # Tension force (towards anchor)
        tension_magnitude = gravity * (current_length - length) / length
        tension_direction = displacement.normalize() * -1
        tension_force = tension_direction * tension_magnitude
        
        # Gravity force
        gravity_force = Vector2D(0, gravity)
        
        return tension_force + gravity_force


class NoiseUtils:
    """Noise generation utilities"""
    
    @staticmethod
    def perlin_noise_1d(x: float, octaves: int = 4, persistence: float = 0.5, 
                       scale: float = 1.0) -> float:
        """Simple 1D Perlin-like noise"""
        value = 0.0
        amplitude = 1.0
        frequency = scale
        
        for _ in range(octaves):
            value += amplitude * math.sin(x * frequency)
            amplitude *= persistence
            frequency *= 2
        
        return value
    
    @staticmethod
    def perlin_noise_2d(x: float, y: float, octaves: int = 4, 
                       persistence: float = 0.5, scale: float = 1.0) -> float:
        """Simple 2D Perlin-like noise"""
        value = 0.0
        amplitude = 1.0
        frequency = scale
        
        for _ in range(octaves):
            noise_x = math.sin(x * frequency) * math.cos(y * frequency)
            noise_y = math.cos(x * frequency) * math.sin(y * frequency)
            value += amplitude * (noise_x + noise_y) / 2
            amplitude *= persistence
            frequency *= 2
        
        return value
    
    @staticmethod
    def random_walk_2d(start: Vector2D, steps: int, step_size: float) -> List[Vector2D]:
        """Generate a 2D random walk"""
        points = [start]
        current = start
        
        for _ in range(steps):
            angle = np.random.uniform(0, 2 * math.pi)
            step = Vector2D(
                step_size * math.cos(angle),
                step_size * math.sin(angle)
            )
            current = current + step
            points.append(current)
        
        return points


class InterpolationUtils:
    """Interpolation and easing functions"""
    
    @staticmethod
    def linear_interpolate(a: float, b: float, t: float) -> float:
        """Linear interpolation"""
        return a + (b - a) * t
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out function"""
        if t < 0.5:
            return 4 * t**3
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_in_sine(t: float) -> float:
        """Sine ease-in function"""
        return 1 - math.cos((t * math.pi) / 2)
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce ease-out function"""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    @staticmethod
    def smoothstep(edge0: float, edge1: float, x: float) -> float:
        """Smooth interpolation between two values"""
        t = max(0, min(1, (x - edge0) / (edge1 - edge0)))
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def smootherstep(edge0: float, edge1: float, x: float) -> float:
        """Even smoother interpolation"""
        t = max(0, min(1, (x - edge0) / (edge1 - edge0)))
        return t * t * t * (t * (t * 6 - 15) + 10)


class MathUtils:
    """General mathematical utilities"""
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def map_range(value: float, in_min: float, in_max: float, 
                 out_min: float, out_max: float) -> float:
        """Map value from one range to another"""
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def wrap_angle(angle: float) -> float:
        """Wrap angle to [-π, π] range"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians"""
        return degrees * math.pi / 180
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convert radians to degrees"""
        return radians * 180 / math.pi
    
    @staticmethod
    def is_power_of_two(n: int) -> bool:
        """Check if number is power of two"""
        return n > 0 and (n & (n - 1)) == 0
    
    @staticmethod
    def next_power_of_two(n: int) -> int:
        """Get next power of two"""
        power = 1
        while power < n:
            power *= 2
        return power
    
    @staticmethod
    def fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calculate greatest common divisor"""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calculate least common multiple"""
        return abs(a * b) // MathUtils.gcd(a, b)


# Commonly used constants
class Constants:
    PI = math.pi
    TWO_PI = 2 * math.pi
    HALF_PI = math.pi / 2
    E = math.e
    GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
    SQRT_2 = math.sqrt(2)
    SQRT_3 = math.sqrt(3)
    
    # Color constants
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
