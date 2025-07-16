#!/usr/bin/env python3
"""
Musical Flock Plugin for Dynamic Art Generator
Based on Craig Reynolds' Boids flocking algorithm with audio responsiveness

Features:
- Classic flocking behaviors (separation, alignment, cohesion)
- Audio-driven color changes and trail effects
- Beat detection influences flock behavior
- Frequency affects movement patterns
- Beautiful trails and glowing effects

Author: Claude Assistant (adapted from Daniel Shiffman's Processing version)
Version: 1.0
"""

import pygame
import numpy as np
import time
import math
import random
from typing import Dict, List, Tuple

# Import base plugin class
try:
    from plugins import ArtPlugin
except ImportError:
    # Fallback for standalone testing
    from abc import ABC, abstractmethod

    class ArtPlugin(ABC):
        def __init__(self, name: str, surface_size: tuple):
            self.name = name
            self.surface_size = surface_size
            self.is_active = False
            self.parameters = {}
            self.last_update = time.time()

        @abstractmethod
        def update(self, audio_features: dict, dt: float):
            pass

        @abstractmethod
        def render(self, surface: pygame.Surface):
            pass

        @abstractmethod
        def get_parameters(self) -> dict:
            pass

        @abstractmethod
        def set_parameter(self, name: str, value):
            pass

        def reset(self):
            pass


class Vector2D:
    """2D Vector class for boid physics"""

    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        if scalar != 0:
            return Vector2D(self.x / scalar, self.y / scalar)
        return Vector2D(0, 0)

    def add(self, other):
        """Add another vector to this one"""
        self.x += other.x
        self.y += other.y

    def sub(self, other):
        """Subtract another vector from this one"""
        self.x -= other.x
        self.y -= other.y

    def mult(self, scalar):
        """Multiply by scalar"""
        self.x *= scalar
        self.y *= scalar

    def div(self, scalar):
        """Divide by scalar"""
        if scalar != 0:
            self.x /= scalar
            self.y /= scalar

    def mag(self):
        """Get magnitude"""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        """Normalize to unit vector"""
        m = self.mag()
        if m > 0:
            self.div(m)

    def limit(self, max_val):
        """Limit magnitude to max_val"""
        if self.mag() > max_val:
            self.normalize()
            self.mult(max_val)

    def heading(self):
        """Get angle in radians"""
        return math.atan2(self.y, self.x)

    def copy(self):
        """Create a copy"""
        return Vector2D(self.x, self.y)

    @staticmethod
    def dist(v1, v2):
        """Distance between two vectors"""
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def sub_static(v1, v2):
        """Static subtraction"""
        return Vector2D(v1.x - v2.x, v1.y - v2.y)


class Boid:
    """Individual boid with flocking behaviors and audio responsiveness"""

    def __init__(self, x, y):
        self.acceleration = Vector2D(0, 0)
        self.angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2D(math.cos(self.angle), math.sin(self.angle))
        self.location = Vector2D(x, y)

        # Physical properties
        self.r = 3.0  # Size
        self.maxspeed = 2.5
        self.maxforce = 0.05

        # Visual properties
        self.trail = []
        self.max_trail_length = 15
        self.color_hue = random.uniform(0, 360)
        self.energy = 0.0  # Audio energy accumulator

        # Flocking behavior weights (can be modified by audio)
        self.separation_weight = 1.5
        self.alignment_weight = 1.0
        self.cohesion_weight = 1.0

        # Audio response properties
        self.beat_response = 0.0
        self.frequency_influence = 0.0

    def run(self, boids, audio_features, bounds):
        """Main update method"""
        self.flock(boids, audio_features)
        self.update()
        self.borders(bounds)
        self.update_audio_response(audio_features)
        self.update_trail()

    def update_audio_response(self, audio_features):
        """Update audio-driven properties"""
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})

        # Accumulate energy
        self.energy += amplitude * 10
        self.energy *= 0.95  # Decay

        # Beat response
        if beat_detected:
            self.beat_response = min(self.beat_response + amplitude * 5, 3.0)
        else:
            self.beat_response *= 0.9

        # Frequency influence on color
        self.frequency_influence = frequency * 0.001
        self.color_hue += self.frequency_influence + amplitude * 20
        self.color_hue %= 360

        # Audio affects flocking behavior
        # Bass increases separation (more spread out)
        bass_factor = freq_bands.get('bass', 0)
        self.separation_weight = 1.5 + bass_factor * 2

        # Treble increases alignment (more synchronized)
        treble_factor = freq_bands.get('treble', 0)
        self.alignment_weight = 1.0 + treble_factor * 1.5

        # Mid frequencies affect cohesion
        mid_factor = freq_bands.get('mid', 0)
        self.cohesion_weight = 1.0 + mid_factor * 1.2

        # Beats temporarily increase max speed
        if self.beat_response > 0:
            self.maxspeed = 2.5 + self.beat_response * 1.5
        else:
            self.maxspeed = 2.5

    def update_trail(self):
        """Update visual trail"""
        self.trail.append((self.location.x, self.location.y, self.color_hue))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def apply_force(self, force):
        """Apply force to acceleration"""
        self.acceleration.add(force)

    def flock(self, boids, audio_features):
        """Apply flocking behaviors"""
        sep = self.separate(boids)    # Separation
        ali = self.align(boids)       # Alignment
        coh = self.cohesion(boids)    # Cohesion

        # Weight the forces (modified by audio)
        sep.mult(self.separation_weight)
        ali.mult(self.alignment_weight)
        coh.mult(self.cohesion_weight)

        # Apply forces
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)

        # Add audio-driven forces
        amplitude = audio_features.get('amplitude', 0)

        # Random force on high amplitude
        if amplitude > 0.5:
            random_force = Vector2D(
                random.uniform(-1, 1) * amplitude,
                random.uniform(-1, 1) * amplitude
            )
            random_force.mult(0.02)
            self.apply_force(random_force)

    def update(self):
        """Update position and velocity"""
        # Update velocity
        self.velocity.add(self.acceleration)
        # Limit speed
        self.velocity.limit(self.maxspeed)
        # Update location
        self.location.add(self.velocity)
        # Reset acceleration
        self.acceleration.mult(0)

    def seek(self, target):
        """Seek towards target location"""
        desired = Vector2D.sub_static(target, self.location)
        desired.normalize()
        desired.mult(self.maxspeed)

        steer = Vector2D.sub_static(desired, self.velocity)
        steer.limit(self.maxforce)
        return steer

    def separate(self, boids):
        """Separation: steer to avoid crowding local flockmates"""
        desired_separation = 25.0
        steer = Vector2D(0, 0)
        count = 0

        for other in boids:
            d = Vector2D.dist(self.location, other.location)
            if 0 < d < desired_separation:
                diff = Vector2D.sub_static(self.location, other.location)
                diff.normalize()
                diff.div(d)  # Weight by distance
                steer.add(diff)
                count += 1

        if count > 0:
            steer.div(count)
            if steer.mag() > 0:
                steer.normalize()
                steer.mult(self.maxspeed)
                steer.sub(self.velocity)
                steer.limit(self.maxforce)

        return steer

    def align(self, boids):
        """Alignment: steer towards average heading of neighbors"""
        neighbor_dist = 50
        sum_vel = Vector2D(0, 0)
        count = 0

        for other in boids:
            d = Vector2D.dist(self.location, other.location)
            if 0 < d < neighbor_dist:
                sum_vel.add(other.velocity)
                count += 1

        if count > 0:
            sum_vel.div(count)
            sum_vel.normalize()
            sum_vel.mult(self.maxspeed)
            steer = Vector2D.sub_static(sum_vel, self.velocity)
            steer.limit(self.maxforce)
            return steer

        return Vector2D(0, 0)

    def cohesion(self, boids):
        """Cohesion: steer to move toward average position of neighbors"""
        neighbor_dist = 50
        sum_pos = Vector2D(0, 0)
        count = 0

        for other in boids:
            d = Vector2D.dist(self.location, other.location)
            if 0 < d < neighbor_dist:
                sum_pos.add(other.location)
                count += 1

        if count > 0:
            sum_pos.div(count)
            return self.seek(sum_pos)

        return Vector2D(0, 0)

    def borders(self, bounds):
        """Wrap around screen edges"""
        width, height = bounds

        if self.location.x < -self.r:
            self.location.x = width + self.r
        if self.location.y < -self.r:
            self.location.y = height + self.r
        if self.location.x > width + self.r:
            self.location.x = -self.r
        if self.location.y > height + self.r:
            self.location.y = -self.r


class MusicalFlockPlugin(ArtPlugin):
    """
    Musical Flock Plugin - Craig Reynolds' Boids with Audio Response

    Creates a flock of boids (bird-like entities) that exhibit emergent flocking
    behavior while responding to audio input. The classic three rules of flocking
    (separation, alignment, cohesion) are dynamically modified by audio features.

    Audio Response:
    - Bass frequencies increase separation (spread out)
    - Treble frequencies increase alignment (synchronization)
    - Mid frequencies affect cohesion (clustering)
    - Beat detection increases movement speed
    - Amplitude affects colors and adds random forces
    """

    # Plugin identification
    PLUGIN_NAME = "Musical Flock"
    PLUGIN_DESCRIPTION = "Flocking boids that dance to music"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant (adapted from Craig Reynolds/Daniel Shiffman)"

    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)

        # Flock properties
        self.boids = []
        self.num_boids = 60
        self.max_boids = 200

        # Visual properties
        self.show_trails = True
        self.show_boid_bodies = True
        self.trail_opacity = 0.6
        self.boid_size_multiplier = 1.0

        # Color system
        self.base_hue = 200  # Start with blue
        self.hue_spread = 60  # How much color varies across flock
        self.color_cycle_speed = 30

        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_spawn_threshold = 0.7  # Amplitude needed to spawn new boids
        self.frequency_color_influence = 1.0

        # Flocking behavior parameters
        self.neighbor_radius = 50
        self.separation_radius = 25
        self.max_speed = 2.5
        self.max_force = 0.05

        # Effects
        self.enable_beat_spawning = True
        self.enable_audio_forces = True
        self.enable_color_cycling = True

        # Store parameters for GUI
        self.parameters = {
            'num_boids': self.num_boids,
            'audio_sensitivity': self.audio_sensitivity,
            'neighbor_radius': self.neighbor_radius,
            'separation_radius': self.separation_radius,
            'max_speed': self.max_speed,
            'trail_opacity': self.trail_opacity,
            'boid_size_multiplier': self.boid_size_multiplier,
            'color_cycle_speed': self.color_cycle_speed,
            'hue_spread': self.hue_spread,
            'show_trails': self.show_trails,
            'enable_beat_spawning': self.enable_beat_spawning,
            'enable_audio_forces': self.enable_audio_forces
        }

        # Initialize flock
        self.create_initial_flock()

        # Animation state
        self.time_offset = 0
        self.last_beat_spawn = 0

    def create_initial_flock(self):
        """Create initial flock of boids"""
        self.boids.clear()

        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2

        for i in range(int(self.num_boids)):
            # Start boids in center with some spread
            x = center_x + random.uniform(-50, 50)
            y = center_y + random.uniform(-50, 50)

            # Ensure they're within bounds
            x = max(50, min(self.surface_size[0] - 50, x))
            y = max(50, min(self.surface_size[1] - 50, y))

            boid = Boid(x, y)

            # Set individual color variation
            boid.color_hue = self.base_hue + random.uniform(-self.hue_spread/2, self.hue_spread/2)
            boid.color_hue %= 360

            self.boids.append(boid)

    def update(self, audio_features: dict, dt: float):
        """Update the flock simulation"""
        self.time_offset += dt

        # Extract audio features
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)

        # Update base color
        if self.enable_color_cycling:
            self.base_hue += self.color_cycle_speed * dt
            self.base_hue %= 360

        # Beat spawning
        if (self.enable_beat_spawning and beat_detected and
            amplitude > self.beat_spawn_threshold and
            len(self.boids) < self.max_boids and
            time.time() - self.last_beat_spawn > 0.5):  # Rate limit

            self.spawn_boid_at_random_location()
            self.last_beat_spawn = time.time()

        # Update all boids
        for boid in self.boids:
            # Scale audio features
            scaled_audio = {
                'amplitude': amplitude * self.audio_sensitivity,
                'beat_detected': beat_detected,
                'dominant_frequency': frequency * self.frequency_color_influence,
                'frequency_bands': audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
            }

            boid.run(self.boids, scaled_audio, self.surface_size)

    def spawn_boid_at_random_location(self):
        """Spawn a new boid at a random edge location"""
        # Spawn from random edge
        edge = random.randint(0, 3)

        if edge == 0:  # Top
            x = random.uniform(0, self.surface_size[0])
            y = 0
        elif edge == 1:  # Right
            x = self.surface_size[0]
            y = random.uniform(0, self.surface_size[1])
        elif edge == 2:  # Bottom
            x = random.uniform(0, self.surface_size[0])
            y = self.surface_size[1]
        else:  # Left
            x = 0
            y = random.uniform(0, self.surface_size[1])

        boid = Boid(x, y)
        boid.color_hue = self.base_hue + random.uniform(-self.hue_spread/2, self.hue_spread/2)
        boid.color_hue %= 360

        # Give it initial velocity towards center
        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2
        angle = math.atan2(center_y - y, center_x - x)
        speed = random.uniform(1, 3)
        boid.velocity = Vector2D(math.cos(angle) * speed, math.sin(angle) * speed)

        self.boids.append(boid)

    def render(self, surface: pygame.Surface):
        """Render the flock"""
        # Draw trails first (behind boids)
        if self.show_trails:
            self.render_trails(surface)

        # Draw boids
        if self.show_boid_bodies:
            self.render_boids(surface)

    def render_trails(self, surface: pygame.Surface):
        """Render boid trails"""
        for boid in self.boids:
            if len(boid.trail) < 2:
                continue

            for i in range(1, len(boid.trail)):
                # Calculate trail fade
                fade_factor = i / len(boid.trail)
                alpha = max(0, min(255, int(fade_factor * self.trail_opacity * 255)))

                if alpha > 0:
                    # Get trail segment info
                    x, y, hue = boid.trail[i]

                    # Trail color
                    trail_color = self.hsv_to_rgb(hue, 0.7, 0.8)

                    # Ensure color is valid
                    if len(trail_color) >= 3:
                        safe_trail_color = (
                            max(0, min(255, int(trail_color[0]))),
                            max(0, min(255, int(trail_color[1]))),
                            max(0, min(255, int(trail_color[2])))
                        )
                    else:
                        safe_trail_color = (255, 255, 255)

                    # Draw trail point
                    trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    trail_alpha_color = (*safe_trail_color, alpha)

                    try:
                        pygame.draw.circle(trail_surface, trail_alpha_color, (3, 3), 2)
                        surface.blit(trail_surface, (int(x) - 3, int(y) - 3))
                    except (ValueError, TypeError):
                        pass

    def render_boids(self, surface: pygame.Surface):
        """Render individual boids"""
        for boid in self.boids:
            # Boid position
            x = int(boid.location.x)
            y = int(boid.location.y)

            # Boid color (influenced by audio energy)
            energy_boost = min(0.3, boid.energy * 0.1)
            brightness = min(1.0, 0.9 + energy_boost)  # Clamp to 1.0
            saturation = min(1.0, 0.8 + boid.beat_response * 0.2)  # Clamp to 1.0

            boid_color = self.hsv_to_rgb(boid.color_hue, saturation, brightness)

            # Ensure color is valid (3 integers 0-255)
            if len(boid_color) >= 3:
                boid_color = (
                    max(0, min(255, int(boid_color[0]))),
                    max(0, min(255, int(boid_color[1]))),
                    max(0, min(255, int(boid_color[2])))
                )
            else:
                boid_color = (255, 255, 255)  # Fallback white

            # Calculate boid orientation
            angle = boid.velocity.heading()

            # Boid size (affected by beat response and settings)
            size = max(1, boid.r * self.boid_size_multiplier * (1 + boid.beat_response * 0.3))

            # Draw boid as triangle pointing in direction of movement
            self.draw_boid_triangle(surface, x, y, angle, size, boid_color, boid.beat_response)

    def draw_boid_triangle(self, surface: pygame.Surface, x: int, y: int,
                          angle: float, size: float, color: Tuple[int, int, int],
                          glow_intensity: float):
        """Draw a boid as a triangle with optional glow"""
        # Validate inputs
        if size <= 0:
            return

        # Ensure color is valid
        if not isinstance(color, (tuple, list)) or len(color) < 3:
            color = (255, 255, 255)

        # Clamp color values
        safe_color = (
            max(0, min(255, int(color[0]))),
            max(0, min(255, int(color[1]))),
            max(0, min(255, int(color[2])))
        )

        # Calculate triangle points
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Triangle vertices (pointing in direction of movement)
        front_x = x + cos_a * size * 2
        front_y = y + sin_a * size * 2

        back_left_x = x + math.cos(angle + 2.8) * size
        back_left_y = y + math.sin(angle + 2.8) * size

        back_right_x = x + math.cos(angle - 2.8) * size
        back_right_y = y + math.sin(angle - 2.8) * size

        points = [
            (int(front_x), int(front_y)),
            (int(back_left_x), int(back_left_y)),
            (int(back_right_x), int(back_right_y))
        ]

        # Draw glow effect on beat response
        if glow_intensity > 0:
            glow_radius = max(1, int(size * 2 + glow_intensity * 5))
            glow_alpha = max(0, min(255, int(glow_intensity * 50)))

            if glow_alpha > 0 and glow_radius > 0:
                glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
                glow_color = (*safe_color, glow_alpha)

                try:
                    pygame.draw.circle(glow_surface, glow_color,
                                     (glow_radius * 2, glow_radius * 2), glow_radius)
                    surface.blit(glow_surface, (x - glow_radius * 2, y - glow_radius * 2))
                except (ValueError, TypeError):
                    pass

        # Draw main triangle
        try:
            pygame.draw.polygon(surface, safe_color, points)
            # Add white outline for visibility
            pygame.draw.polygon(surface, (255, 255, 255), points, 1)
        except (ValueError, TypeError):
            # Fallback: draw as circle
            try:
                pygame.draw.circle(surface, safe_color, (x, y), max(1, int(size)))
            except (ValueError, TypeError):
                # Ultimate fallback: draw white circle
                pygame.draw.circle(surface, (255, 255, 255), (x, y), max(1, int(size)))

    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB color space"""
        # Clamp input values to valid ranges
        h = h % 360.0
        s = max(0.0, min(1.0, float(s)))
        v = max(0.0, min(1.0, float(v)))

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

        # Ensure output is valid integers in range 0-255
        return (
            max(0, min(255, int((r + m) * 255))),
            max(0, min(255, int((g + m) * 255))),
            max(0, min(255, int((b + m) * 255)))
        )

    def get_parameters(self) -> dict:
        """Return current parameter values for GUI controls"""
        return self.parameters.copy()

    def set_parameter(self, name: str, value):
        """Handle parameter changes from GUI"""
        if name in self.parameters:
            self.parameters[name] = value

            # Update corresponding instance variables
            if hasattr(self, name):
                setattr(self, name, value)

            # Handle special cases
            if name == 'num_boids':
                new_count = max(5, min(200, int(value)))
                current_count = len(self.boids)

                if new_count > current_count:
                    # Add more boids
                    for _ in range(new_count - current_count):
                        x = random.uniform(50, self.surface_size[0] - 50)
                        y = random.uniform(50, self.surface_size[1] - 50)
                        boid = Boid(x, y)
                        boid.color_hue = self.base_hue + random.uniform(-self.hue_spread/2, self.hue_spread/2)
                        self.boids.append(boid)

                elif new_count < current_count:
                    # Remove boids
                    self.boids = self.boids[:new_count]

                self.num_boids = new_count
                self.parameters[name] = new_count

            elif name in ['trail_opacity', 'boid_size_multiplier']:
                setattr(self, name, max(0.1, min(2.0, float(value))))
                self.parameters[name] = getattr(self, name)

            elif name == 'hue_spread':
                self.hue_spread = max(0, min(180, float(value)))
                self.parameters[name] = self.hue_spread

    def reset(self):
        """Reset plugin to initial state"""
        # Reset flock
        self.create_initial_flock()

        # Reset visual state
        self.base_hue = 200
        self.time_offset = 0
        self.last_beat_spawn = 0

        print(f"Reset {self.name} plugin")

    def get_info(self) -> dict:
        """Get plugin information"""
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'boid_count': len(self.boids),
            'max_boids': self.max_boids
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time

    print("Testing Musical Flock Plugin...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Musical Flock Plugin Test")
    clock = pygame.time.Clock()

    # Create plugin
    plugin = MusicalFlockPlugin((800, 600))

    # Test loop
    running = True
    start_time = time.time()

    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS
        current_time = time.time() - start_time

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    plugin.reset()
                elif event.key == pygame.K_UP:
                    plugin.set_parameter('num_boids', min(200, plugin.num_boids + 5))
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('num_boids', max(5, plugin.num_boids - 5))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Add boid at mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_boid = Boid(mouse_x, mouse_y)
                new_boid.color_hue = plugin.base_hue + random.uniform(-30, 30)
                plugin.boids.append(new_boid)

        # Simulate audio features
        fake_audio = {
            'amplitude': 0.4 + 0.4 * math.sin(current_time * 1.2),
            'beat_detected': (current_time % 2.5) < 0.15,
            'dominant_frequency': 440 + 200 * math.sin(current_time * 0.4),
            'frequency_bands': {
                'bass': 0.3 + 0.3 * math.sin(current_time * 0.6),
                'mid': 0.4 + 0.2 * math.sin(current_time * 0.9),
                'treble': 0.2 + 0.4 * math.sin(current_time * 1.4)
            }
        }

        # Update plugin
        plugin.update(fake_audio, dt)

        # Render
        screen.fill((15, 15, 30))  # Dark blue background
        plugin.render(screen)

        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Musical Flock - Boids: {len(plugin.boids)}",
                f"Click: Add boid | UP/DOWN: ±5 boids",
                "SPACE: Reset"
            ]

            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass

        pygame.display.flip()

    pygame.quit()
    print("Musical Flock plugin test completed")
