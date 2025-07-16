#!/usr/bin/env python3
"""
Plugin Template for Dynamic Art Generator
Copy this file to create your own custom art plugins

Author: Your Name
Version: 1.0
"""

import pygame
import numpy as np
import time
import math
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod

# Import the base plugin class (adjust path as needed)
try:
    from main import ArtPlugin
except ImportError:
    # If running standalone, define a minimal base class
    class ArtPlugin(ABC):
        def __init__(self, name: str, surface_size: tuple):
            self.name = name
            self.surface_size = surface_size
            self.surface = pygame.Surface(surface_size, pygame.SRCALPHA)
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
            self.surface.fill((0, 0, 0, 0))


class MyCustomPlugin(ArtPlugin):
    """
    Custom Plugin Template
    
    Replace this with your own creative implementation!
    This example creates a simple spiral pattern that responds to audio.
    """
    
    def __init__(self, surface_size: tuple):
        super().__init__("MyCustomPlugin", surface_size)
        
        # Initialize your plugin's state variables here
        self.spiral_points = []
        self.spiral_angle = 0
        self.spiral_radius = 0
        self.center_x = surface_size[0] / 2
        self.center_y = surface_size[1] / 2
        
        # Plugin parameters (these will appear as controls in the GUI)
        self.spiral_speed = 2.0
        self.radius_growth = 0.5
        self.max_radius = 200
        self.color_hue = 0
        self.color_saturation = 0.8
        self.color_brightness = 0.9
        self.trail_length = 200
        self.audio_sensitivity = 1.0
        self.line_width = 2
        
        # Beat response
        self.beat_pulse = 0
        self.beat_decay = 0.95
        
        # Store parameters for GUI
        self.parameters = {
            'spiral_speed': self.spiral_speed,
            'radius_growth': self.radius_growth,
            'max_radius': self.max_radius,
            'color_saturation': self.color_saturation,
            'color_brightness': self.color_brightness,
            'trail_length': self.trail_length,
            'audio_sensitivity': self.audio_sensitivity,
            'line_width': self.line_width
        }
    
    def update(self, audio_features: dict, dt: float):
        """
        Update your plugin's state based on audio features and elapsed time
        
        Available audio features:
        - amplitude: Peak amplitude (0-1)
        - rms: RMS energy (0-1)
        - dominant_frequency: Dominant frequency in Hz
        - beat_detected: Boolean indicating if beat was detected
        - frequency_bands: Dict with 'bass', 'mid', 'treble' energy levels
        """
        
        # Get audio features
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        dominant_freq = audio_features.get('dominant_frequency', 0)
        
        # Update spiral based on audio
        # Speed varies with amplitude
        current_speed = self.spiral_speed * (1 + amplitude * self.audio_sensitivity)
        self.spiral_angle += current_speed * dt
        
        # Radius grows and resets
        self.spiral_radius += self.radius_growth * (1 + amplitude * 2) * dt * 10
        if self.spiral_radius > self.max_radius:
            self.spiral_radius = 0
        
        # Beat response
        if beat_detected:
            self.beat_pulse = min(self.beat_pulse + amplitude * 5, 3.0)
        else:
            self.beat_pulse *= self.beat_decay
        
        # Calculate new spiral point
        pulse_radius = self.spiral_radius + self.beat_pulse * 20
        x = self.center_x + pulse_radius * math.cos(self.spiral_angle)
        y = self.center_y + pulse_radius * math.sin(self.spiral_angle)
        
        # Color changes with frequency
        self.color_hue = (self.color_hue + dominant_freq * 0.001) % 360
        
        # Add point to spiral
        self.spiral_points.append((int(x), int(y), self.color_hue))
        
        # Limit trail length
        if len(self.spiral_points) > self.trail_length:
            self.spiral_points.pop(0)
    
    def render(self, surface: pygame.Surface):
        """
        Render your plugin to the given surface
        Use pygame drawing functions to create your art
        """
        
        if len(self.spiral_points) < 2:
            return
        
        # Draw spiral trail
        for i in range(1, len(self.spiral_points)):
            # Calculate alpha based on position in trail
            alpha = (i / len(self.spiral_points)) * 255
            
            # Get color
            prev_point = self.spiral_points[i-1]
            curr_point = self.spiral_points[i]
            
            # Use HSV color that changes along the trail
            hue = curr_point[2]
            color = self.hsv_to_rgb(hue, self.color_saturation, self.color_brightness)
            
            # Draw line segment
            try:
                # Create temporary surface for alpha blending
                temp_surface = pygame.Surface((abs(curr_point[0] - prev_point[0]) + 10,
                                             abs(curr_point[1] - prev_point[1]) + 10), 
                                            pygame.SRCALPHA)
                
                # Draw line on temp surface
                start_pos = (5, 5)
                end_pos = (curr_point[0] - prev_point[0] + 5, curr_point[1] - prev_point[1] + 5)
                
                # Draw with varying width based on beat
                width = max(1, int(self.line_width + self.beat_pulse))
                
                pygame.draw.line(temp_surface, (*color, int(alpha)), 
                               start_pos, end_pos, width)
                
                # Blit to main surface
                surface.blit(temp_surface, (min(prev_point[0], curr_point[0]) - 5,
                                          min(prev_point[1], curr_point[1]) - 5))
                
            except Exception as e:
                # Fallback to simple line drawing
                pygame.draw.line(surface, color, 
                               (prev_point[0], prev_point[1]), 
                               (curr_point[0], curr_point[1]), 
                               max(1, int(self.line_width)))
        
        # Draw center dot
        center_color = self.hsv_to_rgb(self.color_hue, 1.0, 1.0)
        center_size = max(3, int(5 + self.beat_pulse * 2))
        pygame.draw.circle(surface, center_color, 
                         (int(self.center_x), int(self.center_y)), center_size)
    
    def get_parameters(self) -> dict:
        """Return current parameter values for GUI controls"""
        return self.parameters
    
    def set_parameter(self, name: str, value):
        """Handle parameter changes from GUI"""
        if name in self.parameters:
            self.parameters[name] = value
            # Update corresponding instance variables
            setattr(self, name, value)
            
            # Handle special cases
            if name == 'trail_length':
                # Trim spiral points if trail got shorter
                if len(self.spiral_points) > int(value):
                    self.spiral_points = self.spiral_points[-int(value):]
    
    def reset(self):
        """Reset plugin to initial state"""
        super().reset()
        self.spiral_points.clear()
        self.spiral_angle = 0
        self.spiral_radius = 0
        self.color_hue = 0
        self.beat_pulse = 0
    
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
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


class WaveformPlugin(ArtPlugin):
    """
    Another example plugin that creates waveform visualizations
    """
    
    def __init__(self, surface_size: tuple):
        super().__init__("Waveform", surface_size)
        
        self.waveform_data = []
        self.frequency_bars = []
        self.wave_color = (0, 255, 255)  # Cyan
        self.background_alpha = 20
        
        # Parameters
        self.wave_height = 100
        self.wave_speed = 1.0
        self.frequency_sensitivity = 1.0
        self.color_cycle_speed = 1.0
        self.show_frequency_bars = True
        
        self.parameters = {
            'wave_height': self.wave_height,
            'wave_speed': self.wave_speed,
            'frequency_sensitivity': self.frequency_sensitivity,
            'color_cycle_speed': self.color_cycle_speed,
            'show_frequency_bars': self.show_frequency_bars
        }
        
        self.time_offset = 0
        self.hue_offset = 0
    
    def update(self, audio_features: dict, dt: float):
        """Update waveform based on audio"""
        amplitude = audio_features.get('amplitude', 0)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update time for animation
        self.time_offset += dt * self.wave_speed
        self.hue_offset += dt * self.color_cycle_speed * 50
        
        # Update waveform data
        width = self.surface_size[0]
        self.waveform_data = []
        
        for x in range(0, width, 4):  # Sample every 4 pixels for performance
            # Create sine wave with audio influence
            base_wave = math.sin((x * 0.01 + self.time_offset) * 2 * math.pi)
            audio_wave = math.sin((x * 0.005 + frequency * 0.001) * 2 * math.pi)
            
            # Combine waves with audio amplitude
            combined_wave = base_wave * 0.5 + audio_wave * 0.3 * amplitude
            
            # Scale by wave height
            y_offset = combined_wave * self.wave_height * (1 + amplitude)
            
            self.waveform_data.append((x, y_offset))
        
        # Update frequency bars
        if self.show_frequency_bars:
            self.frequency_bars = [
                ('Bass', freq_bands['bass'], (255, 0, 0)),
                ('Mid', freq_bands['mid'], (0, 255, 0)),
                ('Treble', freq_bands['treble'], (0, 0, 255))
            ]
    
    def render(self, surface: pygame.Surface):
        """Render waveform visualization"""
        center_y = self.surface_size[1] / 2
        
        # Draw waveform
        if len(self.waveform_data) > 1:
            for i in range(1, len(self.waveform_data)):
                x1, y1 = self.waveform_data[i-1]
                x2, y2 = self.waveform_data[i]
                
                # Calculate color based on position
                hue = (self.hue_offset + x1 * 0.5) % 360
                color = self.hsv_to_rgb(hue, 0.8, 0.9)
                
                # Draw line
                pygame.draw.line(surface, color,
                               (x1, center_y + y1),
                               (x2, center_y + y2), 2)
        
        # Draw frequency bars
        if self.show_frequency_bars and self.frequency_bars:
            bar_width = 50
            bar_spacing = 70
            bar_x = 50
            
            for i, (label, value, color) in enumerate(self.frequency_bars):
                bar_height = value * 200 * self.frequency_sensitivity
                bar_y = self.surface_size[1] - 50 - bar_height
                
                # Draw bar
                pygame.draw.rect(surface, color,
                               (bar_x + i * bar_spacing, bar_y, bar_width, bar_height))
                
                # Draw label (simplified)
                pygame.draw.rect(surface, (255, 255, 255),
                               (bar_x + i * bar_spacing, self.surface_size[1] - 30, 
                                bar_width, 20))
    
    def get_parameters(self) -> dict:
        return self.parameters
    
    def set_parameter(self, name: str, value):
        if name in self.parameters:
            self.parameters[name] = value
            setattr(self, name, value)
    
    def reset(self):
        super().reset()
        self.waveform_data.clear()
        self.frequency_bars.clear()
        self.time_offset = 0
        self.hue_offset = 0
    
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
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


# Plugin registration function
def get_available_plugins():
    """
    Return a list of plugin classes available in this module
    This function should be called by the main application to discover plugins
    """
    return [MyCustomPlugin, WaveformPlugin]


# Test function
def test_plugin():
    """Test the plugin standalone"""
    pygame.init()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin instance
    plugin = MyCustomPlugin((800, 600))
    
    # Simulate audio features
    running = True
    time_counter = 0
    
    while running:
        dt = clock.tick(60) / 1000.0  # 60 FPS
        time_counter += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.5 + 0.3 * math.sin(time_counter * 2),
            'beat_detected': (time_counter % 1.0) < 0.1,
            'dominant_frequency': 440 + 200 * math.sin(time_counter * 0.5),
            'frequency_bands': {
                'bass': 0.3 + 0.2 * math.sin(time_counter),
                'mid': 0.4 + 0.3 * math.sin(time_counter * 1.5),
                'treble': 0.2 + 0.1 * math.sin(time_counter * 2)
            }
        }
        
        # Update and render plugin
        plugin.update(fake_audio, dt)
        
        screen.fill((0, 0, 0))
        plugin.render(screen)
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    """Run plugin test when executed directly"""
    print("Testing plugin...")
    test_plugin()
