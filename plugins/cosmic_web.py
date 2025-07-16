#!/usr/bin/env python3
"""
Cosmic Web Plugin for Dynamic Art Generator
Creates a mesmerizing network of fluid orbs, gravitational connections, and particle streams

Author: Claude Assistant
Version: 1.0 - Delightfully Strange Edition
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


class CosmicOrb:
    """A fluid, gravitationally-influenced orb in the cosmic web"""

    def __init__(self, x: float, y: float, mass: float = 1.0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(-20, 20)
        self.mass = mass
        self.base_radius = 10 + mass * 5
        self.radius = self.base_radius
        self.energy = 0.0  # Audio energy accumulator
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.color_shift = random.uniform(0, 360)

        # Fluid properties
        self.fluidity = 0.3
        self.surface_tension = 0.1
        self.ripples = []

        # Trail for cosmic effect
        self.trail = []
        self.max_trail_length = 20

        # Connection strength to other orbs
        self.connections = {}

        # Particle emission
        self.particle_timer = 0
        self.particles = []

    def update(self, dt: float, other_orbs: List['CosmicOrb'], audio_features: dict, bounds: Tuple[int, int]):
        """Update orb physics and audio response"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})

        # Audio energy accumulation
        self.energy += amplitude * 10 * dt
        self.energy *= 0.95  # Decay

        # Beat response
        if beat:
            self.energy += amplitude * 20
            self.create_ripple()

        # Gravitational forces from other orbs
        force_x, force_y = 0, 0

        for other in other_orbs:
            if other is self:
                continue

            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                # Gravitational attraction (but not too strong)
                force_magnitude = (self.mass * other.mass) / (distance*distance + 100)
                force_magnitude *= 0.5  # Reduce strength

                force_x += force_magnitude * (dx / distance)
                force_y += force_magnitude * (dy / distance)

                # Store connection strength for rendering
                connection_strength = min(1.0, 200 / distance)
                if connection_strength > 0.1:
                    self.connections[id(other)] = connection_strength

        # Audio forces
        # Bass creates outward expansion
        bass_force = freq_bands.get('bass', 0) * 50
        if bass_force > 0:
            center_x = bounds[0] / 2
            center_y = bounds[1] / 2
            dx_center = self.x - center_x
            dy_center = self.y - center_y
            dist_center = math.sqrt(dx_center*dx_center + dy_center*dy_center)

            if dist_center > 0:
                force_x += bass_force * (dx_center / dist_center)
                force_y += bass_force * (dy_center / dist_center)

        # Treble creates swirling motion
        treble_force = freq_bands.get('treble', 0) * 30
        if treble_force > 0:
            force_x += treble_force * math.sin(time.time() * frequency * 0.01)
            force_y += treble_force * math.cos(time.time() * frequency * 0.01)

        # Apply forces
        self.vx += force_x * dt
        self.vy += force_y * dt

        # Damping
        self.vx *= 0.98
        self.vy *= 0.98

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Boundary behavior - bounce with energy loss
        margin = self.radius
        if self.x < margin or self.x > bounds[0] - margin:
            self.vx *= -0.8
            self.x = max(margin, min(bounds[0] - margin, self.x))
            self.create_ripple()

        if self.y < margin or self.y > bounds[1] - margin:
            self.vy *= -0.8
            self.y = max(margin, min(bounds[1] - margin, self.y))
            self.create_ripple()

        # Update radius based on energy and audio
        pulse_factor = 1 + 0.3 * math.sin(self.pulse_phase + time.time() * 3)
        energy_factor = 1 + self.energy * 0.1
        audio_factor = 1 + amplitude * 0.5

        self.radius = self.base_radius * pulse_factor * energy_factor * audio_factor

        # Update color shift
        self.color_shift += frequency * 0.001 * dt + amplitude * 50 * dt
        self.color_shift %= 360

        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Update ripples
        self.update_ripples(dt)

        # Emit particles on high energy
        if self.energy > 5:
            self.particle_timer += dt
            if self.particle_timer > 0.1:  # Emit every 0.1 seconds
                self.emit_particle()
                self.particle_timer = 0

        # Update particles
        self.update_particles(dt, bounds)

    def create_ripple(self):
        """Create a ripple effect on the orb surface"""
        self.ripples.append({
            'time': 0,
            'max_time': 1.0,
            'intensity': self.energy * 0.1
        })

    def update_ripples(self, dt: float):
        """Update ripple animations"""
        for ripple in self.ripples[:]:
            ripple['time'] += dt
            if ripple['time'] > ripple['max_time']:
                self.ripples.remove(ripple)

    def emit_particle(self):
        """Emit a cosmic particle"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(20, 50)

        particle = {
            'x': self.x + math.cos(angle) * self.radius,
            'y': self.y + math.sin(angle) * self.radius,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': random.uniform(1, 3),
            'max_life': 3,
            'color': self.color_shift
        }

        self.particles.append(particle)

    def update_particles(self, dt: float, bounds: Tuple[int, int]):
        """Update emitted particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt

            # Fade velocity
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98

            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def get_connections(self) -> Dict:
        """Get current connections to other orbs"""
        return self.connections.copy()


class CosmicWebPlugin(ArtPlugin):
    """
    Cosmic Web Plugin - Creates a living galaxy of interconnected orbs

    This plugin generates a mesmerizing cosmic network where:
    - Fluid orbs respond to gravitational forces
    - Connections form between nearby orbs
    - Audio drives pulsing, color changes, and particle emission
    - Bass creates expansion, treble creates swirling motion
    - Beat detection triggers ripples and energy bursts
    """

    # Plugin identification
    PLUGIN_NAME = "Cosmic Web"
    PLUGIN_DESCRIPTION = "Gravitational orbs forming a living cosmic network"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"

    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)

        # Cosmic orbs
        self.orbs = []
        self.num_orbs = 8
        self.orb_mass_range = (0.5, 2.0)

        # Visual properties
        self.background_stars = []
        self.star_count = 100
        self.connection_opacity = 0.7
        self.trail_fade = 0.3

        # Color system
        self.base_hue = 240  # Start with blue
        self.hue_shift_speed = 20
        self.color_variance = 60

        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_amplification = 3.0
        self.frequency_color_influence = 1.0

        # Effects
        self.enable_trails = True
        self.enable_particles = True
        self.enable_connections = True
        self.enable_ripples = True
        self.enable_stars = True

        # Cosmic forces
        self.gravity_strength = 1.0
        self.expansion_force = 0.5
        self.swirl_force = 0.3

        # Store parameters for GUI
        self.parameters = {
            'num_orbs': self.num_orbs,
            'audio_sensitivity': self.audio_sensitivity,
            'beat_amplification': self.beat_amplification,
            'gravity_strength': self.gravity_strength,
            'expansion_force': self.expansion_force,
            'swirl_force': self.swirl_force,
            'connection_opacity': self.connection_opacity,
            'hue_shift_speed': self.hue_shift_speed,
            'color_variance': self.color_variance,
            'enable_trails': self.enable_trails,
            'enable_particles': self.enable_particles,
            'enable_connections': self.enable_connections,
            'enable_stars': self.enable_stars
        }

        # Initialize the cosmic web
        self.create_orbs()
        self.create_background_stars()

        # Animation state
        self.time_offset = 0

    def create_orbs(self):
        """Create the initial set of cosmic orbs"""
        self.orbs.clear()

        for i in range(int(self.num_orbs)):
            # Position orbs in a loose cluster
            cluster_center_x = self.surface_size[0] / 2
            cluster_center_y = self.surface_size[1] / 2
            cluster_radius = min(self.surface_size) * 0.3

            angle = (2 * math.pi * i / self.num_orbs) + random.uniform(-0.5, 0.5)
            distance = random.uniform(0.3, 1.0) * cluster_radius

            x = cluster_center_x + distance * math.cos(angle)
            y = cluster_center_y + distance * math.sin(angle)

            mass = random.uniform(self.orb_mass_range[0], self.orb_mass_range[1])

            orb = CosmicOrb(x, y, mass)
            self.orbs.append(orb)

    def create_background_stars(self):
        """Create twinkling background stars"""
        self.background_stars.clear()

        for _ in range(self.star_count):
            star = {
                'x': random.uniform(0, self.surface_size[0]),
                'y': random.uniform(0, self.surface_size[1]),
                'brightness': random.uniform(0.1, 1.0),
                'twinkle_phase': random.uniform(0, 2 * math.pi),
                'twinkle_speed': random.uniform(1, 3)
            }
            self.background_stars.append(star)

    def update(self, audio_features: dict, dt: float):
        """Update the cosmic web simulation"""
        self.time_offset += dt

        # Extract audio features
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})

        # Update color system
        self.base_hue += self.hue_shift_speed * dt
        self.base_hue %= 360

        # Add frequency influence to colors
        if frequency > 0:
            self.base_hue += frequency * 0.01 * self.frequency_color_influence * dt
            self.base_hue %= 360

        # Update each orb
        for orb in self.orbs:
            # Scale audio features by sensitivity
            scaled_audio = {
                'amplitude': amplitude * self.audio_sensitivity,
                'beat_detected': beat_detected,
                'dominant_frequency': frequency,
                'frequency_bands': {
                    'bass': freq_bands.get('bass', 0) * self.expansion_force,
                    'mid': freq_bands.get('mid', 0),
                    'treble': freq_bands.get('treble', 0) * self.swirl_force
                }
            }

            orb.update(dt, self.orbs, scaled_audio, self.surface_size)

        # Update background stars
        if self.enable_stars:
            for star in self.background_stars:
                star['twinkle_phase'] += star['twinkle_speed'] * dt

    def render(self, surface: pygame.Surface):
        """Render the cosmic web"""
        # Draw background stars
        if self.enable_stars:
            self.render_background_stars(surface)

        # Draw connections between orbs
        if self.enable_connections:
            self.render_connections(surface)

        # Draw orb trails
        if self.enable_trails:
            self.render_trails(surface)

        # Draw orbs themselves
        self.render_orbs(surface)

        # Draw particles
        if self.enable_particles:
            self.render_particles(surface)

    def render_background_stars(self, surface: pygame.Surface):
        """Render twinkling background stars"""
        for star in self.background_stars:
            # Calculate twinkling brightness
            twinkle = 0.5 + 0.5 * math.sin(star['twinkle_phase'])
            brightness = star['brightness'] * twinkle

            # Star color (pale blue-white)
            color_value = int(brightness * 255)
            color = (color_value, color_value, min(255, int(color_value * 1.2)))

            # Draw star as small circle
            pos = (int(star['x']), int(star['y']))
            pygame.draw.circle(surface, color, pos, 1)

    def render_connections(self, surface: pygame.Surface):
        """Render glowing connections between orbs"""
        for i, orb1 in enumerate(self.orbs):
            connections = orb1.get_connections()

            for other_id, strength in connections.items():
                # Find the other orb
                orb2 = None
                for orb in self.orbs:
                    if id(orb) == other_id:
                        orb2 = orb
                        break

                if orb2 is None:
                    continue

                # Calculate connection color
                avg_hue = (orb1.color_shift + orb2.color_shift) / 2
                connection_color = self.hsv_to_rgb(avg_hue, 0.8, 0.9)

                # Calculate alpha based on strength and opacity setting
                alpha = max(0, min(255, int(strength * self.connection_opacity * 255)))

                # Draw connection line with glow effect
                start_pos = (int(orb1.x), int(orb1.y))
                end_pos = (int(orb2.x), int(orb2.y))

                # Create surface for alpha blending
                width = abs(end_pos[0] - start_pos[0]) + 20
                height = abs(end_pos[1] - start_pos[1]) + 20

                if width > 0 and height > 0:
                    line_surface = pygame.Surface((width, height), pygame.SRCALPHA)

                    # Draw multiple lines for glow effect
                    for thickness in [5, 3, 1]:
                        line_alpha = max(0, min(255, alpha // (thickness + 1)))
                        line_color = (*connection_color, line_alpha)

                        rel_start = (10, 10)
                        rel_end = (end_pos[0] - start_pos[0] + 10, end_pos[1] - start_pos[1] + 10)

                        try:
                            pygame.draw.line(line_surface, line_color, rel_start, rel_end, thickness)
                        except (ValueError, TypeError):
                            # Skip this line if there's a drawing error
                            pass

                    # Blit to main surface
                    surface.blit(line_surface, (min(start_pos[0], end_pos[0]) - 10,
                                               min(start_pos[1], end_pos[1]) - 10))

    def render_trails(self, surface: pygame.Surface):
        """Render cosmic trails behind orbs"""
        for orb in self.orbs:
            if len(orb.trail) < 2:
                continue

            for i in range(1, len(orb.trail)):
                # Calculate trail fade
                fade_factor = i / len(orb.trail)
                alpha = max(0, min(255, int(fade_factor * self.trail_fade * 255)))

                # Trail color
                trail_hue = (orb.color_shift + i * 10) % 360
                trail_color = self.hsv_to_rgb(trail_hue, 0.6, 0.7)

                # Draw trail segment
                end_pos = (int(orb.trail[i][0]), int(orb.trail[i][1]))

                # Create small surface for alpha
                if alpha > 0:
                    trail_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
                    trail_alpha_color = (*trail_color, alpha)
                    try:
                        pygame.draw.circle(trail_surface, trail_alpha_color, (5, 5), 3)
                        surface.blit(trail_surface, (end_pos[0] - 5, end_pos[1] - 5))
                    except (ValueError, TypeError):
                        # Skip this trail segment if there's a drawing error
                        pass

    def render_orbs(self, surface: pygame.Surface):
        """Render the cosmic orbs with all their effects"""
        for orb in self.orbs:
            # Main orb color
            orb_hue = (self.base_hue + orb.color_shift) % 360
            orb_color = self.hsv_to_rgb(orb_hue, 0.8, 0.9)

            # Draw orb with glow effect
            pos = (int(orb.x), int(orb.y))
            radius = int(orb.radius)

            # Outer glow
            glow_radius = radius + 10
            glow_color = self.hsv_to_rgb(orb_hue, 0.6, 0.5)

            if glow_radius > 0:
                glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)

                for r in range(glow_radius, 0, -2):
                    alpha = max(0, min(255, int(100 * (r / glow_radius) * 0.3)))
                    if alpha > 0:
                        try:
                            glow_alpha_color = (*glow_color, alpha)
                            pygame.draw.circle(glow_surface, glow_alpha_color,
                                             (glow_radius * 2, glow_radius * 2), r)
                        except (ValueError, TypeError):
                            # Skip this glow ring if there's a drawing error
                            pass

                surface.blit(glow_surface, (pos[0] - glow_radius * 2, pos[1] - glow_radius * 2))

            # Main orb body
            pygame.draw.circle(surface, orb_color, pos, radius)

            # Energy core
            core_radius = max(2, radius // 3)
            core_color = self.hsv_to_rgb(orb_hue, 1.0, 1.0)
            pygame.draw.circle(surface, core_color, pos, core_radius)

            # Ripple effects
            if self.enable_ripples:
                for ripple in orb.ripples:
                    ripple_progress = ripple['time'] / ripple['max_time']
                    ripple_radius = radius + ripple_progress * 30
                    ripple_alpha = int((1 - ripple_progress) * ripple['intensity'] * 255)

                    if ripple_alpha > 0 and ripple_radius > 0:
                        # Ensure we use only RGB components for the base color
                        base_rgb = orb_color[:3] if len(orb_color) >= 3 else orb_color
                        ripple_color = (*base_rgb, max(0, min(255, ripple_alpha)))

                        ripple_surface = pygame.Surface((int(ripple_radius * 4), int(ripple_radius * 4)),
                                                       pygame.SRCALPHA)
                        try:
                            pygame.draw.circle(ripple_surface, ripple_color,
                                             (int(ripple_radius * 2), int(ripple_radius * 2)),
                                             int(ripple_radius), 2)
                            surface.blit(ripple_surface,
                                       (pos[0] - int(ripple_radius * 2), pos[1] - int(ripple_radius * 2)))
                        except (ValueError, TypeError):
                            # Skip this ripple if there's a drawing error
                            pass

    def render_particles(self, surface: pygame.Surface):
        """Render cosmic particles emitted by orbs"""
        for orb in self.orbs:
            for particle in orb.particles:
                # Particle fade based on life
                life_ratio = particle['life'] / particle['max_life']
                alpha = max(0, min(255, int(life_ratio * 255)))

                # Particle color
                particle_hue = (particle['color'] + self.time_offset * 50) % 360
                particle_color = self.hsv_to_rgb(particle_hue, 0.9, 1.0)

                # Draw particle
                pos = (int(particle['x']), int(particle['y']))

                if alpha > 0:
                    particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    particle_alpha_color = (*particle_color, alpha)
                    try:
                        pygame.draw.circle(particle_surface, particle_alpha_color, (3, 3), 2)
                        surface.blit(particle_surface, (pos[0] - 3, pos[1] - 3))
                    except (ValueError, TypeError):
                        # Skip this particle if there's a drawing error
                        pass

    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
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
            if name == 'num_orbs':
                new_count = max(2, min(20, int(value)))
                if new_count != len(self.orbs):
                    self.num_orbs = new_count
                    self.create_orbs()
                    self.parameters[name] = new_count

            elif name in ['connection_opacity', 'trail_fade']:
                setattr(self, name, max(0, min(1, float(value))))
                self.parameters[name] = getattr(self, name)

            elif name == 'color_variance':
                self.color_variance = max(0, min(180, float(value)))
                self.parameters[name] = self.color_variance

    def reset(self):
        """Reset plugin to initial state"""
        # Reset orbs
        self.create_orbs()

        # Reset visual state
        self.base_hue = 240
        self.time_offset = 0

        # Clear all orb states
        for orb in self.orbs:
            orb.energy = 0
            orb.ripples.clear()
            orb.particles.clear()
            orb.trail.clear()
            orb.connections.clear()

        print(f"Reset {self.name} plugin")

    def get_info(self) -> dict:
        """Get plugin information"""
        total_particles = sum(len(orb.particles) for orb in self.orbs)
        total_connections = sum(len(orb.connections) for orb in self.orbs)

        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'orb_count': len(self.orbs),
            'particle_count': total_particles,
            'connection_count': total_connections // 2,  # Each connection counted twice
            'background_stars': len(self.background_stars)
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time

    print("Testing Cosmic Web Plugin...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Cosmic Web Plugin Test")
    clock = pygame.time.Clock()

    # Create plugin
    plugin = CosmicWebPlugin((800, 600))

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
                    plugin.set_parameter('num_orbs', plugin.num_orbs + 1)
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('num_orbs', max(2, plugin.num_orbs - 1))

        # Simulate audio features
        fake_audio = {
            'amplitude': 0.6 + 0.4 * math.sin(current_time * 1.5),
            'beat_detected': (current_time % 2.0) < 0.2,
            'dominant_frequency': 440 + 300 * math.sin(current_time * 0.3),
            'frequency_bands': {
                'bass': 0.5 + 0.3 * math.sin(current_time * 0.7),
                'mid': 0.4 + 0.2 * math.sin(current_time * 1.1),
                'treble': 0.3 + 0.4 * math.sin(current_time * 1.7)
            }
        }

        # Update plugin
        plugin.update(fake_audio, dt)

        # Render
        screen.fill((5, 5, 20))  # Deep space background
        plugin.render(screen)

        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Cosmic Web - Orbs: {len(plugin.orbs)}",
                f"UP/DOWN: Change orb count",
                "SPACE: Reset"
            ]

            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass

        pygame.display.flip()

    pygame.quit()
    print("Cosmic Web plugin test completed")
