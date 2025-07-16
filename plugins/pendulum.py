#!/usr/bin/env python3
"""
Pendulum Art Plugin for Dynamic Art Generator
Creates paint-can-like elliptical pendulum trails

Author: Claude Assistant
Version: 1.0
"""

import pygame
import numpy as np
import time
import math
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


class PendulumPlugin(ArtPlugin):
    """
    Pendulum art plugin - creates paint-can-like effects
    
    This plugin simulates a pendulum following an elliptical orbit,
    similar to the art created by a paint can swinging over a canvas
    while leaking paint. The motion responds to audio input with
    gravity, damping, and audio-driven forces.
    """
    
    # Plugin identification
    PLUGIN_NAME = "Pendulum"
    PLUGIN_DESCRIPTION = "Elliptical pendulum trails that respond to audio"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Initialize pendulum position at center
        self.x = surface_size[0] / 2
        self.y = surface_size[1] / 2
        self.vx = 0  # X velocity
        self.vy = 0  # Y velocity
        
        # Physics parameters
        self.gravity = 9.81           # Gravitational constant
        self.damping = 0.999          # Velocity damping factor
        self.length = 200             # Pendulum length (unused in elliptical version)
        self.ellipse_a = 150          # Semi-major axis of ellipse
        self.ellipse_b = 100          # Semi-minor axis of ellipse
        
        # Visual properties
        self.trail_points = []        # List of (x, y) trail points
        self.max_trail_length = 500   # Maximum number of trail points
        self.color_hue = 0            # Current color hue (0-360)
        self.line_width = 2           # Trail line width
        self.color_saturation = 0.8   # Color saturation
        self.color_brightness = 0.9   # Color brightness
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0  # How much audio affects motion
        self.beat_impulse = 0         # Current beat impulse strength
        self.beat_decay = 0.9         # How quickly beat impulse decays
        
        # Animation properties
        self.color_cycle_speed = 1.0  # How fast colors cycle
        self.motion_smoothing = 0.1   # Motion smoothing factor
        
        # Store parameters for GUI controls
        self.parameters = {
            'gravity': self.gravity,
            'damping': self.damping,
            'ellipse_a': self.ellipse_a,
            'ellipse_b': self.ellipse_b,
            'audio_sensitivity': self.audio_sensitivity,
            'trail_length': self.max_trail_length,
            'line_width': self.line_width,
            'color_cycle_speed': self.color_cycle_speed,
            'color_saturation': self.color_saturation,
            'color_brightness': self.color_brightness
        }
        
        # Internal state
        self._last_beat_time = 0
        self._force_accumulator = np.array([0.0, 0.0])
    
    def update(self, audio_features: dict, dt: float):
        """
        Update pendulum physics and audio response
        
        Args:
            audio_features: Dictionary containing audio analysis data
            dt: Time delta since last update in seconds
        """
        # Extract audio features with defaults
        amplitude = audio_features.get('amplitude', 0.0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0.0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Handle beat detection
        current_time = time.time()
        if beat_detected and (current_time - self._last_beat_time) > 0.1:
            self.beat_impulse = min(self.beat_impulse + amplitude * 10, 5.0)
            self._last_beat_time = current_time
        
        # Calculate elliptical center
        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2
        
        # Calculate displacement from center
        dx = self.x - center_x
        dy = self.y - center_y
        
        # Elliptical restoring force (Hooke's law for ellipse)
        # Force is proportional to displacement, but scaled by ellipse dimensions
        force_x = -dx * (self.gravity / self.ellipse_a) if self.ellipse_a > 0 else 0
        force_y = -dy * (self.gravity / self.ellipse_b) if self.ellipse_b > 0 else 0
        
        # Add audio-driven forces
        # Frequency-based oscillation
        time_factor = current_time * 2 * math.pi
        freq_influence = max(0.001, frequency * 0.001)  # Prevent division by zero
        
        force_x += (math.sin(time_factor * freq_influence) * 
                   amplitude * self.audio_sensitivity * 50)
        force_y += (math.cos(time_factor * freq_influence * 1.5) * 
                   amplitude * self.audio_sensitivity * 50)
        
        # Bass response (low frequency energy adds circular motion)
        bass_energy = freq_bands.get('bass', 0)
        force_x += math.cos(time_factor * 0.5) * bass_energy * self.audio_sensitivity * 30
        force_y += math.sin(time_factor * 0.5) * bass_energy * self.audio_sensitivity * 30
        
        # Beat impulse (random force on beats)
        if self.beat_impulse > 0:
            impulse_angle = np.random.uniform(0, 2 * math.pi)
            impulse_strength = self.beat_impulse * 20
            force_x += math.cos(impulse_angle) * impulse_strength
            force_y += math.sin(impulse_angle) * impulse_strength
            self.beat_impulse *= self.beat_decay
        
        # Apply forces to velocity (Euler integration)
        self.vx += force_x * dt
        self.vy += force_y * dt
        
        # Apply damping to velocity
        self.vx *= self.damping
        self.vy *= self.damping
        
        # Update position
        self.x += self.vx * dt * 100  # Scale factor for reasonable motion
        self.y += self.vy * dt * 100
        
        # Keep pendulum within reasonable bounds (soft boundaries)
        margin = 50
        if self.x < margin:
            self.x = margin
            self.vx = abs(self.vx) * 0.8  # Bounce with energy loss
        elif self.x > self.surface_size[0] - margin:
            self.x = self.surface_size[0] - margin
            self.vx = -abs(self.vx) * 0.8
            
        if self.y < margin:
            self.y = margin
            self.vy = abs(self.vy) * 0.8
        elif self.y > self.surface_size[1] - margin:
            self.y = self.surface_size[1] - margin
            self.vy = -abs(self.vy) * 0.8
        
        # Add current position to trail
        self.trail_points.append((int(self.x), int(self.y)))
        
        # Limit trail length
        while len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
        # Update color based on audio and time
        # Base color cycling
        self.color_hue += self.color_cycle_speed * dt * 30
        
        # Audio influence on color
        self.color_hue += amplitude * 50 * self.audio_sensitivity * dt
        
        # Frequency influence on color
        if frequency > 0:
            self.color_hue += frequency * 0.01 * dt
        
        # Keep hue in valid range
        self.color_hue = self.color_hue % 360
    
    def render(self, surface: pygame.Surface):
        """
        Render pendulum trail to the surface
        
        Args:
            surface: Pygame surface to draw on
        """
        if len(self.trail_points) < 2:
            return
        
        # Draw trail with fading effect and color variation
        for i in range(1, len(self.trail_points)):
            # Calculate alpha based on position in trail (newer = more opaque)
            alpha = (i / len(self.trail_points)) * 255
            
            # Calculate color progression along trail
            progress = i / len(self.trail_points)
            
            # Vary hue slightly along the trail for rainbow effect
            current_hue = (self.color_hue + progress * 60) % 360
            
            # Convert HSV to RGB
            color = self.hsv_to_rgb(current_hue, self.color_saturation, self.color_brightness)
            
            # Get line segment points
            prev_point = self.trail_points[i-1]
            curr_point = self.trail_points[i]
            
            # Calculate line width based on position and beat impulse
            width_multiplier = 1.0 + (progress * 0.5) + (self.beat_impulse * 0.3)
            current_width = max(1, int(self.line_width * width_multiplier))
            
            try:
                # Draw line segment with alpha blending
                if alpha >= 255:
                    # Fully opaque - use direct drawing
                    pygame.draw.line(surface, color, prev_point, curr_point, current_width)
                else:
                    # Semi-transparent - use temporary surface for alpha
                    line_surface = pygame.Surface((
                        abs(curr_point[0] - prev_point[0]) + current_width * 2,
                        abs(curr_point[1] - prev_point[1]) + current_width * 2
                    ), pygame.SRCALPHA)
                    
                    # Calculate relative positions on temporary surface
                    offset_x = min(prev_point[0], curr_point[0]) - current_width
                    offset_y = min(prev_point[1], curr_point[1]) - current_width
                    
                    rel_prev = (prev_point[0] - offset_x, prev_point[1] - offset_y)
                    rel_curr = (curr_point[0] - offset_x, curr_point[1] - offset_y)
                    
                    # Draw line with alpha
                    pygame.draw.line(line_surface, (*color, int(alpha)), 
                                   rel_prev, rel_curr, current_width)
                    
                    # Blit to main surface
                    surface.blit(line_surface, (offset_x, offset_y))
                    
            except (ValueError, TypeError):
                # Fallback to simple line drawing if alpha blending fails
                try:
                    pygame.draw.line(surface, color, prev_point, curr_point, current_width)
                except:
                    pass  # Skip this line if drawing fails
        
        # Draw current pendulum position as a glowing dot
        if self.trail_points:
            current_pos = self.trail_points[-1]
            center_color = self.hsv_to_rgb(self.color_hue, 1.0, 1.0)
            
            # Pulsing size based on beat impulse
            base_radius = 3
            pulse_radius = int(base_radius + self.beat_impulse * 2)
            
            # Draw multiple circles for glow effect
            for radius in range(pulse_radius, 0, -1):
                alpha = int(255 * (radius / pulse_radius) * 0.7)
                glow_color = (*center_color, alpha)
                
                # Create small surface for glow circle
                glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (radius * 2, radius * 2), radius)
                
                surface.blit(glow_surface, 
                           (current_pos[0] - radius * 2, current_pos[1] - radius * 2))
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """
        Convert HSV color values to RGB
        
        Args:
            h: Hue (0-360)
            s: Saturation (0-1)
            v: Value/Brightness (0-1)
            
        Returns:
            RGB tuple (r, g, b) with values 0-255
        """
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
        """
        Handle parameter changes from GUI
        
        Args:
            name: Parameter name
            value: New parameter value
        """
        if name in self.parameters:
            self.parameters[name] = value
            
            # Update corresponding instance variables
            if hasattr(self, name):
                setattr(self, name, value)
            
            # Handle special cases
            if name == 'trail_length':
                self.max_trail_length = int(value)
                # Trim trail if it got shorter
                while len(self.trail_points) > self.max_trail_length:
                    self.trail_points.pop(0)
            
            elif name in ['ellipse_a', 'ellipse_b']:
                # Ensure ellipse dimensions are positive
                setattr(self, name, max(10, float(value)))
                self.parameters[name] = getattr(self, name)
            
            elif name == 'line_width':
                self.line_width = max(1, int(value))
                self.parameters[name] = self.line_width
    
    def reset(self):
        """Reset plugin to initial state"""
        # Clear trail
        self.trail_points.clear()
        
        # Reset position to center
        self.x = self.surface_size[0] / 2
        self.y = self.surface_size[1] / 2
        
        # Reset velocities
        self.vx = 0
        self.vy = 0
        
        # Reset visual state
        self.color_hue = 0
        self.beat_impulse = 0
        self._force_accumulator = np.array([0.0, 0.0])
        
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
            'trail_points': len(self.trail_points),
            'current_hue': self.color_hue
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Pendulum Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pendulum Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = PendulumPlugin((800, 600))
    
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
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.5 + 0.3 * math.sin(current_time * 2),
            'beat_detected': (current_time % 1.0) < 0.1,
            'dominant_frequency': 440 + 200 * math.sin(current_time * 0.5),
            'frequency_bands': {
                'bass': 0.3 + 0.2 * math.sin(current_time),
                'mid': 0.4 + 0.3 * math.sin(current_time * 1.5),
                'treble': 0.2 + 0.1 * math.sin(current_time * 2)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((10, 10, 20))  # Dark background
        plugin.render(screen)
        
        # Display info
        font = pygame.font.Font(None, 24)
        info_text = f"Pendulum Test - Press SPACE to reset"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("Pendulum plugin test completed")
