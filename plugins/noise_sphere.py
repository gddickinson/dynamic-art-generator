#!/usr/bin/env python3
"""
Noise Sphere Plugin for Dynamic Art Generator
Creates a mesmerizing 3D hairy sphere with flowing Perlin noise animation

Based on the original Processing concept but enhanced for audio responsiveness
Author: Claude Assistant  
Version: 1.0 - Organic Flowing Edition
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


class NoiseGenerator:
    """Simple Perlin-like noise generator"""
    
    def __init__(self, octaves=4, persistence=0.5):
        self.octaves = octaves
        self.persistence = persistence
        
    def noise(self, x, y=0, z=0):
        """Generate noise value at given coordinates"""
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        
        for _ in range(self.octaves):
            value += amplitude * self._simple_noise(x * frequency, y * frequency, z * frequency)
            amplitude *= self.persistence
            frequency *= 2.0
        
        return value
    
    def _simple_noise(self, x, y, z):
        """Simple noise function"""
        # Use sin/cos for smooth noise-like behavior
        return (math.sin(x * 1.5 + math.cos(y * 2.3)) * 
                math.cos(y * 1.7 + math.sin(z * 1.9)) * 
                math.sin(z * 2.1 + math.cos(x * 1.3))) * 0.5


class Hair:
    """A single hair strand on the noise sphere"""
    
    def __init__(self, radius: float, noise_gen: NoiseGenerator):
        self.noise_gen = noise_gen
        
        # Spherical coordinates
        self.z = random.uniform(-radius, radius)
        self.phi = random.uniform(0, 2 * math.pi)
        self.theta = math.asin(self.z / radius) if radius > 0 else 0
        
        # Hair properties
        self.length_multiplier = random.uniform(1.15, 1.2)
        self.base_length = self.length_multiplier
        self.thickness = random.uniform(0.5, 2.0)
        
        # Animation properties
        self.noise_offset_phi = random.uniform(0, 1000)
        self.noise_offset_theta = random.uniform(0, 1000)
        self.color_offset = random.uniform(0, 360)
        
        # Audio response
        self.energy = 0.0
        self.beat_response = 0.0
        
    def update(self, radius: float, time_factor: float, audio_features: dict, dt: float):
        """Update hair position and properties based on noise and audio"""
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update energy and beat response
        self.energy += amplitude * 5 * dt
        self.energy *= 0.95  # Decay
        
        if beat_detected:
            self.beat_response = min(self.beat_response + amplitude * 3, 2.0)
        else:
            self.beat_response *= 0.9
        
        # Calculate noise-driven offsets
        noise_time = time_factor * 0.0005
        
        # Use noise to create organic movement
        off_phi = (self.noise_gen.noise(noise_time, math.sin(self.phi) + self.noise_offset_phi) - 0.5) * 0.3
        off_theta = (self.noise_gen.noise(noise_time * 0.7, math.sin(self.z) * 0.01 + self.noise_offset_theta) - 0.5) * 0.3
        
        # Add audio influence to the noise
        bass_influence = freq_bands.get('bass', 0) * 0.5
        treble_influence = freq_bands.get('treble', 0) * 0.3
        
        off_phi += bass_influence * math.sin(time_factor * 0.01)
        off_theta += treble_influence * math.cos(time_factor * 0.007)
        
        # Calculate new spherical coordinates
        self.theta_current = self.theta + off_theta
        self.phi_current = self.phi + off_phi
        
        # Calculate base position on sphere
        self.base_x = radius * math.cos(self.theta) * math.cos(self.phi)
        self.base_y = radius * math.cos(self.theta) * math.sin(self.phi)
        self.base_z = radius * math.sin(self.theta)
        
        # Calculate hair tip position with noise and audio influence
        hair_radius = radius * self.length_multiplier
        
        # Add energy and beat effects to hair length
        energy_length = hair_radius * (1 + self.energy * 0.2 + self.beat_response * 0.3)
        
        self.tip_x = energy_length * math.cos(self.theta_current) * math.cos(self.phi_current)
        self.tip_y = energy_length * math.cos(self.theta_current) * math.sin(self.phi_current)
        self.tip_z = energy_length * math.sin(self.theta_current)
        
        # Update color
        freq_color_shift = frequency * 0.1 if frequency > 0 else 0
        self.color_offset += freq_color_shift * dt
        self.color_offset %= 360


class NoiseSpherePlugin(ArtPlugin):
    """
    Noise Sphere Plugin - Creates a mesmerizing 3D hairy sphere
    
    This plugin generates thousands of "hair" strands emanating from a sphere,
    each moving organically based on Perlin noise and responding to audio.
    The 3D sphere can be rotated and viewed from different angles.
    """
    
    # Plugin identification
    PLUGIN_NAME = "Noise Sphere"
    PLUGIN_DESCRIPTION = "3D hairy sphere with organic Perlin noise movement"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Sphere properties
        self.radius = min(surface_size) / 3.5
        self.hair_count = 8000  # Start with fewer for performance
        self.hairs = []
        
        # 3D rotation
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_speed = 1.0
        self.auto_rotate = True
        
        # Noise system
        self.noise_gen = NoiseGenerator(octaves=3, persistence=0.5)
        self.noise_detail = 3
        self.noise_speed = 1.0
        
        # Visual properties
        self.background_color = (5, 5, 15)
        self.sphere_color = (0, 0, 0)
        self.hair_base_color = (0, 0, 0)
        self.hair_tip_color = (200, 200, 200)
        self.show_sphere = True
        self.hair_alpha = 150
        
        # Color system
        self.base_hue = 180
        self.hue_shift_speed = 30
        self.color_variance = 60
        self.rainbow_mode = True
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_sensitivity = 2.0
        self.frequency_response = 1.0
        
        # Animation
        self.time_factor = 0
        
        # Store parameters for GUI
        self.parameters = {
            'hair_count': self.hair_count,
            'radius': self.radius,
            'audio_sensitivity': self.audio_sensitivity,
            'beat_sensitivity': self.beat_sensitivity,
            'frequency_response': self.frequency_response,
            'noise_speed': self.noise_speed,
            'rotation_speed': self.rotation_speed,
            'auto_rotate': self.auto_rotate,
            'show_sphere': self.show_sphere,
            'rainbow_mode': self.rainbow_mode,
            'hair_alpha': self.hair_alpha,
            'hue_shift_speed': self.hue_shift_speed
        }
        
        # Create the hairs
        self.create_hairs()
    
    def create_hairs(self):
        """Create all the hair strands"""
        self.hairs.clear()
        
        for _ in range(int(self.hair_count)):
            hair = Hair(self.radius, self.noise_gen)
            self.hairs.append(hair)
        
        print(f"Created {len(self.hairs)} hairs on sphere")
    
    def update(self, audio_features: dict, dt: float):
        """Update the noise sphere animation"""
        self.time_factor += dt * 1000  # Convert to milliseconds like original
        
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Scale audio features
        scaled_audio = {
            'amplitude': amplitude * self.audio_sensitivity,
            'beat_detected': beat_detected,
            'dominant_frequency': frequency * self.frequency_response,
            'frequency_bands': {
                'bass': freq_bands.get('bass', 0),
                'mid': freq_bands.get('mid', 0),
                'treble': freq_bands.get('treble', 0)
            }
        }
        
        # Update rotation
        if self.auto_rotate:
            rotation_speed = self.rotation_speed * (1 + amplitude * 0.5)
            self.rotation_y += rotation_speed * dt * 0.5
            self.rotation_x += rotation_speed * dt * 0.3
        
        # Update color system
        if self.rainbow_mode:
            self.base_hue += self.hue_shift_speed * dt
            self.base_hue %= 360
            
            # Add frequency influence
            if frequency > 0:
                self.base_hue += frequency * 0.01 * dt
                self.base_hue %= 360
        
        # Update each hair
        current_radius = self.radius * (1 + amplitude * 0.2)  # Sphere breathes with audio
        
        for hair in self.hairs:
            hair.update(current_radius, self.time_factor * self.noise_speed, scaled_audio, dt)
    
    def render(self, surface: pygame.Surface):
        """Render the noise sphere"""
        # Clear background
        surface.fill(self.background_color)
        
        # Calculate projection center
        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2
        
        # Draw the central sphere (optional)
        if self.show_sphere:
            sphere_radius = max(3, int(self.radius * 0.8))
            pygame.draw.circle(surface, self.sphere_color, 
                             (int(center_x), int(center_y)), sphere_radius)
        
        # Draw all the hairs
        self.render_hairs(surface, center_x, center_y)
    
    def render_hairs(self, surface: pygame.Surface, center_x: float, center_y: float):
        """Render all hair strands with 3D projection"""
        # Sort hairs by z-depth for proper rendering order
        hairs_with_depth = []
        
        for hair in self.hairs:
            # Apply 3D rotation
            rotated_base = self.rotate_3d(hair.base_x, hair.base_y, hair.base_z)
            rotated_tip = self.rotate_3d(hair.tip_x, hair.tip_y, hair.tip_z)
            
            # Project to 2D
            base_2d = self.project_to_2d(rotated_base, center_x, center_y)
            tip_2d = self.project_to_2d(rotated_tip, center_x, center_y)
            
            # Store with depth for sorting
            depth = rotated_tip[2]  # Use tip z for depth
            hairs_with_depth.append((depth, hair, base_2d, tip_2d, rotated_base, rotated_tip))
        
        # Sort by depth (back to front)
        hairs_with_depth.sort(key=lambda x: x[0])
        
        # Render hairs
        for depth, hair, base_2d, tip_2d, rotated_base, rotated_tip in hairs_with_depth:
            self.render_single_hair(surface, hair, base_2d, tip_2d, depth)
    
    def render_single_hair(self, surface: pygame.Surface, hair: Hair, 
                          base_2d: Tuple[int, int], tip_2d: Tuple[int, int], depth: float):
        """Render a single hair strand"""
        # Calculate color based on depth and audio response
        if self.rainbow_mode:
            # Rainbow coloring
            hue = (self.base_hue + hair.color_offset + depth * 0.5) % 360
            hair_color = self.hsv_to_rgb(hue, 0.8, 0.9)
        else:
            # Depth-based grayscale
            depth_factor = max(0, min(1, (depth + self.radius) / (2 * self.radius)))
            gray_value = int(50 + depth_factor * 150 + hair.energy * 50)
            hair_color = (gray_value, gray_value, gray_value)
        
        # Add energy glow
        if hair.beat_response > 0.1:
            # Brighten color on beat
            hair_color = tuple(min(255, int(c * (1 + hair.beat_response * 0.5))) for c in hair_color)
        
        # Calculate line thickness
        thickness = max(1, int(hair.thickness + hair.energy * 0.5))
        
        # Draw the hair as a line
        try:
            # Check if points are within reasonable bounds
            if (0 <= base_2d[0] <= self.surface_size[0] and 
                0 <= base_2d[1] <= self.surface_size[1] and
                0 <= tip_2d[0] <= self.surface_size[0] * 2 and  # Allow some overflow
                0 <= tip_2d[1] <= self.surface_size[1] * 2):
                
                if self.hair_alpha < 255:
                    # Draw with alpha
                    hair_surface = pygame.Surface((abs(tip_2d[0] - base_2d[0]) + thickness * 2,
                                                  abs(tip_2d[1] - base_2d[1]) + thickness * 2), 
                                                 pygame.SRCALPHA)
                    
                    alpha_color = (*hair_color, self.hair_alpha)
                    
                    rel_base = (thickness, thickness)
                    rel_tip = (tip_2d[0] - base_2d[0] + thickness, tip_2d[1] - base_2d[1] + thickness)
                    
                    pygame.draw.line(hair_surface, alpha_color, rel_base, rel_tip, thickness)
                    surface.blit(hair_surface, (min(base_2d[0], tip_2d[0]) - thickness,
                                               min(base_2d[1], tip_2d[1]) - thickness))
                else:
                    # Direct drawing
                    pygame.draw.line(surface, hair_color, base_2d, tip_2d, thickness)
        
        except (ValueError, TypeError, OverflowError):
            # Skip problematic hairs
            pass
    
    def rotate_3d(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Apply 3D rotation to a point"""
        # Rotate around X axis
        cos_x = math.cos(self.rotation_x)
        sin_x = math.sin(self.rotation_x)
        
        y_rot = y * cos_x - z * sin_x
        z_rot = y * sin_x + z * cos_x
        y, z = y_rot, z_rot
        
        # Rotate around Y axis
        cos_y = math.cos(self.rotation_y)
        sin_y = math.sin(self.rotation_y)
        
        x_rot = x * cos_y + z * sin_y
        z_rot = -x * sin_y + z * cos_y
        x, z = x_rot, z_rot
        
        return (x, y, z)
    
    def project_to_2d(self, point_3d: Tuple[float, float, float], 
                     center_x: float, center_y: float) -> Tuple[int, int]:
        """Project 3D point to 2D screen coordinates"""
        x, y, z = point_3d
        
        # Simple orthographic projection (you could add perspective here)
        screen_x = center_x + x
        screen_y = center_y + y
        
        return (int(screen_x), int(screen_y))
    
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
            if name == 'hair_count':
                new_count = max(100, min(20000, int(value)))
                if new_count != len(self.hairs):
                    self.hair_count = new_count
                    self.create_hairs()
                    self.parameters[name] = new_count
            
            elif name == 'radius':
                self.radius = max(50, min(min(self.surface_size) / 2, float(value)))
                self.parameters[name] = self.radius
                # Recreate hairs with new radius
                self.create_hairs()
            
            elif name in ['audio_sensitivity', 'beat_sensitivity', 'frequency_response']:
                setattr(self, name, max(0, min(5, float(value))))
                self.parameters[name] = getattr(self, name)
            
            elif name == 'hair_alpha':
                self.hair_alpha = max(10, min(255, int(value)))
                self.parameters[name] = self.hair_alpha
    
    def reset(self):
        """Reset plugin to initial state"""
        # Reset rotation
        self.rotation_x = 0
        self.rotation_y = 0
        
        # Reset animation
        self.time_factor = 0
        self.base_hue = 180
        
        # Reset all hair states
        for hair in self.hairs:
            hair.energy = 0
            hair.beat_response = 0
        
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
            'hair_count': len(self.hairs),
            'radius': self.radius,
            'rotation_x': self.rotation_x,
            'rotation_y': self.rotation_y
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Noise Sphere Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Noise Sphere Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = NoiseSpherePlugin((800, 600))
    
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
                elif event.key == pygame.K_r:
                    plugin.set_parameter('rainbow_mode', not plugin.rainbow_mode)
                elif event.key == pygame.K_a:
                    plugin.set_parameter('auto_rotate', not plugin.auto_rotate)
                elif event.key == pygame.K_UP:
                    new_count = min(15000, plugin.hair_count + 500)
                    plugin.set_parameter('hair_count', new_count)
                elif event.key == pygame.K_DOWN:
                    new_count = max(500, plugin.hair_count - 500)
                    plugin.set_parameter('hair_count', new_count)
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.7 + 0.3 * math.sin(current_time * 1.2),
            'beat_detected': (current_time % 1.8) < 0.15,
            'dominant_frequency': 440 + 400 * math.sin(current_time * 0.4),
            'frequency_bands': {
                'bass': 0.6 + 0.4 * math.sin(current_time * 0.6),
                'mid': 0.5 + 0.3 * math.sin(current_time * 0.9),
                'treble': 0.4 + 0.4 * math.sin(current_time * 1.4)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        plugin.render(screen)
        
        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Noise Sphere - Hairs: {len(plugin.hairs)}",
                f"R: Rainbow Mode ({'ON' if plugin.rainbow_mode else 'OFF'})",
                f"A: Auto Rotate ({'ON' if plugin.auto_rotate else 'OFF'})",
                "UP/DOWN: Change hair count, SPACE: Reset"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Noise Sphere plugin test completed")
