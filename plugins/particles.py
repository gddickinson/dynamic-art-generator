#!/usr/bin/env python3
"""
Particle System Plugin for Dynamic Art Generator
Creates dynamic sand/smoke-like particle effects inspired by 1100 AMIANGELIKA

Author: Claude Assistant
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


class Particle:
    """Individual particle with physics and rendering properties"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 life: float, color: Tuple[int, int, int], size: float = 2.0):
        """
        Initialize a particle
        
        Args:
            x, y: Initial position
            vx, vy: Initial velocity
            life: Particle lifetime in seconds
            color: RGB color tuple
            size: Particle size
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.initial_size = size
        
        # Additional properties
        self.mass = 1.0
        self.drag = 0.98
        self.bounce = 0.3
        self.rotation = random.uniform(0, 2 * math.pi)
        self.angular_velocity = random.uniform(-2, 2)
    
    def update(self, dt: float, forces: Tuple[float, float], bounds: Tuple[int, int]):
        """
        Update particle physics
        
        Args:
            dt: Time delta in seconds
            forces: (force_x, force_y) tuple
            bounds: (width, height) screen bounds
        """
        # Apply forces
        self.vx += forces[0] * dt / self.mass
        self.vy += forces[1] * dt / self.mass
        
        # Apply drag
        self.vx *= self.drag
        self.vy *= self.drag
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Update rotation
        self.rotation += self.angular_velocity * dt
        
        # Boundary collisions with bounce
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx) * self.bounce
        elif self.x > bounds[0]:
            self.x = bounds[0]
            self.vx = -abs(self.vx) * self.bounce
            
        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy) * self.bounce
        elif self.y > bounds[1]:
            self.y = bounds[1]
            self.vy = -abs(self.vy) * self.bounce
        
        # Update life
        self.life -= dt
        
        # Update size based on life (shrink over time)
        life_ratio = self.life / self.max_life
        self.size = self.initial_size * life_ratio
        
        # Update color alpha based on life
        alpha = max(0, min(255, int(life_ratio * 255)))
        if len(self.color) == 3:
            self.color = (*self.color, alpha)
        else:
            self.color = (*self.color[:3], alpha)
    
    def is_alive(self) -> bool:
        """Check if particle is still alive"""
        return self.life > 0 and self.size > 0.1
    
    def get_distance_to(self, x: float, y: float) -> float:
        """Get distance to a point"""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)


class ParticlePlugin(ArtPlugin):
    """
    Particle system plugin - creates sand/smoke-like effects
    
    This plugin generates dynamic particle systems that form and collapse
    around different shapes, responding to audio input. Inspired by the
    organic, flowing particle effects seen in works like 1100 AMIANGELIKA.
    """
    
    # Plugin identification
    PLUGIN_NAME = "Particles"
    PLUGIN_DESCRIPTION = "Dynamic particle systems that respond to audio"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Particle system properties
        self.particles = []
        self.max_particles = 1000
        self.spawn_rate = 50  # Particles per second
        self.spawn_timer = 0
        
        # Shape properties (particles spawn around these)
        self.shape_type = "circle"  # circle, square, triangle, line
        self.shape_center = (surface_size[0] / 2, surface_size[1] / 2)
        self.shape_size = 100
        self.shape_rotation = 0
        self.shape_velocity = [0, 0]  # Shape can move
        
        # Particle physics
        self.particle_life = 3.0      # Average particle lifetime
        self.particle_speed = 50      # Initial spawn speed
        self.gravity = 20             # Downward force
        self.wind = 0                 # Horizontal force
        self.turbulence = 10          # Random force strength
        self.attraction = 0           # Attraction to shape center
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_burst_strength = 0
        self.beat_decay = 0.9
        self.frequency_influence = 1.0
        
        # Visual properties
        self.color_hue = 0
        self.color_saturation = 0.7
        self.color_brightness = 0.9
        self.color_cycle_speed = 30
        self.particle_size_range = (1, 4)
        self.show_shape_outline = True
        
        # Advanced features
        self.particle_trails = False
        self.collision_response = True
        self.particle_interaction = False
        
        # Store parameters for GUI
        self.parameters = {
            'max_particles': self.max_particles,
            'spawn_rate': self.spawn_rate,
            'particle_life': self.particle_life,
            'particle_speed': self.particle_speed,
            'gravity': self.gravity,
            'wind': self.wind,
            'turbulence': self.turbulence,
            'attraction': self.attraction,
            'audio_sensitivity': self.audio_sensitivity,
            'shape_size': self.shape_size,
            'color_cycle_speed': self.color_cycle_speed,
            'color_saturation': self.color_saturation,
            'color_brightness': self.color_brightness,
            'show_shape_outline': self.show_shape_outline
        }
        
        # Internal state
        self._last_beat_time = 0
        self._shape_target = list(self.shape_center)
        self._emitter_points = []
    
    def update(self, audio_features: dict, dt: float):
        """
        Update particle system based on audio and time
        
        Args:
            audio_features: Dictionary containing audio analysis data
            dt: Time delta since last update in seconds
        """
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0.0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0.0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        current_time = time.time()
        
        # Handle beat detection
        if beat_detected and (current_time - self._last_beat_time) > 0.1:
            self.beat_burst_strength = min(self.beat_burst_strength + amplitude * 20, 10.0)
            self._last_beat_time = current_time
        else:
            self.beat_burst_strength *= self.beat_decay
        
        # Update color cycling
        self.color_hue = (self.color_hue + self.color_cycle_speed * dt) % 360
        
        # Add frequency influence to color
        if frequency > 0:
            self.color_hue = (self.color_hue + frequency * 0.01 * dt) % 360
        
        # Update shape based on audio
        self._update_shape(audio_features, dt)
        
        # Spawn new particles
        self._spawn_particles(audio_features, dt)
        
        # Update existing particles
        self._update_particles(audio_features, dt)
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def _update_shape(self, audio_features: dict, dt: float):
        """Update the shape that particles emanate from"""
        amplitude = audio_features.get('amplitude', 0.0)
        frequency = audio_features.get('dominant_frequency', 0.0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Shape size responds to amplitude
        base_size = self.shape_size
        audio_size_boost = amplitude * 100 * self.audio_sensitivity
        current_size = base_size + audio_size_boost
        
        # Shape movement based on audio
        # Low frequencies move the shape horizontally
        bass_movement = freq_bands.get('bass', 0) * 50
        # High frequencies move it vertically  
        treble_movement = freq_bands.get('treble', 0) * 30
        
        # Calculate new target position
        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2
        
        target_x = center_x + math.sin(time.time() * 2) * bass_movement
        target_y = center_y + math.cos(time.time() * 3) * treble_movement
        
        # Smooth movement towards target
        self._shape_target[0] += (target_x - self._shape_target[0]) * dt * 2
        self._shape_target[1] += (target_y - self._shape_target[1]) * dt * 2
        
        self.shape_center = tuple(self._shape_target)
        
        # Shape rotation based on frequency
        self.shape_rotation += frequency * 0.001 * dt + amplitude * 50 * dt
        
        # Update emitter points based on current shape
        self._update_emitter_points(current_size)
    
    def _update_emitter_points(self, size: float):
        """Update points where particles can spawn"""
        self._emitter_points.clear()
        
        if self.shape_type == "circle":
            # Points around circle perimeter
            num_points = max(8, int(size / 10))
            for i in range(num_points):
                angle = (2 * math.pi * i / num_points) + self.shape_rotation
                x = self.shape_center[0] + size * math.cos(angle)
                y = self.shape_center[1] + size * math.sin(angle)
                self._emitter_points.append((x, y))
        
        elif self.shape_type == "square":
            # Points around square perimeter
            half_size = size / 2
            sides = 4
            points_per_side = max(2, int(size / 20))
            
            for side in range(sides):
                for i in range(points_per_side):
                    t = i / points_per_side
                    
                    if side == 0:  # Top
                        x = self.shape_center[0] - half_size + t * size
                        y = self.shape_center[1] - half_size
                    elif side == 1:  # Right
                        x = self.shape_center[0] + half_size
                        y = self.shape_center[1] - half_size + t * size
                    elif side == 2:  # Bottom
                        x = self.shape_center[0] + half_size - t * size
                        y = self.shape_center[1] + half_size
                    else:  # Left
                        x = self.shape_center[0] - half_size
                        y = self.shape_center[1] + half_size - t * size
                    
                    self._emitter_points.append((x, y))
        
        else:  # Default to center point
            self._emitter_points.append(self.shape_center)
    
    def _spawn_particles(self, audio_features: dict, dt: float):
        """Spawn new particles based on audio and settings"""
        if len(self.particles) >= self.max_particles:
            return
        
        amplitude = audio_features.get('amplitude', 0.0)
        
        # Calculate spawn rate
        base_rate = self.spawn_rate
        audio_boost = amplitude * 100 * self.audio_sensitivity
        beat_boost = self.beat_burst_strength * 5
        
        effective_rate = base_rate + audio_boost + beat_boost
        
        self.spawn_timer += dt
        spawn_interval = 1.0 / max(1, effective_rate)
        
        particles_to_spawn = 0
        while self.spawn_timer >= spawn_interval and len(self.particles) < self.max_particles:
            particles_to_spawn += 1
            self.spawn_timer -= spawn_interval
            
            if particles_to_spawn > 50:  # Prevent lag spikes
                break
        
        # Spawn particles
        for _ in range(particles_to_spawn):
            self._spawn_single_particle(audio_features)
    
    def _spawn_single_particle(self, audio_features: dict):
        """Spawn a single particle"""
        amplitude = audio_features.get('amplitude', 0.0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Choose spawn position
        if self._emitter_points:
            spawn_point = random.choice(self._emitter_points)
            # Add some randomness
            x = spawn_point[0] + random.uniform(-10, 10)
            y = spawn_point[1] + random.uniform(-10, 10)
        else:
            x = self.shape_center[0] + random.uniform(-self.shape_size/2, self.shape_size/2)
            y = self.shape_center[1] + random.uniform(-self.shape_size/2, self.shape_size/2)
        
        # Calculate initial velocity
        speed_multiplier = 1.0 + amplitude * self.audio_sensitivity
        base_speed = self.particle_speed * speed_multiplier
        
        # Random direction with some bias
        angle = random.uniform(0, 2 * math.pi)
        
        # Bass frequencies tend to shoot particles outward
        bass_influence = freq_bands.get('bass', 0) * 2
        if bass_influence > 0.5:
            # Shoot away from center
            center_angle = math.atan2(y - self.shape_center[1], x - self.shape_center[0])
            angle = center_angle + random.uniform(-0.5, 0.5)
        
        vx = base_speed * math.cos(angle)
        vy = base_speed * math.sin(angle)
        
        # Add some upward bias for treble
        treble_influence = freq_bands.get('treble', 0)
        vy -= treble_influence * 30
        
        # Particle lifetime varies with audio
        life_multiplier = 1.0 + amplitude * 0.5
        life = self.particle_life * life_multiplier * random.uniform(0.5, 1.5)
        
        # Color based on current hue with some variation
        hue_variation = random.uniform(-30, 30)
        particle_hue = (self.color_hue + hue_variation) % 360
        
        # Frequency affects color saturation
        saturation = self.color_saturation + freq_bands.get('mid', 0) * 0.3
        saturation = max(0, min(1, saturation))
        
        color = self.hsv_to_rgb(particle_hue, saturation, self.color_brightness)
        
        # Particle size
        size_range = self.particle_size_range
        size = random.uniform(size_range[0], size_range[1])
        
        # Create and add particle
        particle = Particle(x, y, vx, vy, life, color, size)
        self.particles.append(particle)
    
    def _update_particles(self, audio_features: dict, dt: float):
        """Update all existing particles"""
        amplitude = audio_features.get('amplitude', 0.0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Calculate global forces
        force_x = self.wind
        force_y = self.gravity
        
        # Audio-influenced forces
        # Bass creates expanding force from center
        bass_force = freq_bands.get('bass', 0) * 100
        
        # Turbulence varies with amplitude
        turbulence_strength = self.turbulence * (1 + amplitude * 2)
        
        # Beat creates radial force
        beat_force = self.beat_burst_strength * 50
        
        for particle in self.particles:
            # Base forces
            total_force_x = force_x
            total_force_y = force_y
            
            # Turbulence (random force)
            total_force_x += random.uniform(-turbulence_strength, turbulence_strength)
            total_force_y += random.uniform(-turbulence_strength, turbulence_strength)
            
            # Distance and angle from shape center
            dx = particle.x - self.shape_center[0]
            dy = particle.y - self.shape_center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Normalize direction
                norm_dx = dx / distance
                norm_dy = dy / distance
                
                # Bass creates radial expansion
                if bass_force > 0:
                    total_force_x += norm_dx * bass_force
                    total_force_y += norm_dy * bass_force
                
                # Beat burst creates radial expansion
                if beat_force > 0:
                    total_force_x += norm_dx * beat_force
                    total_force_y += norm_dy * beat_force
                
                # Attraction to center (if enabled)
                if self.attraction > 0:
                    attraction_force = self.attraction * distance * 0.01
                    total_force_x -= norm_dx * attraction_force
                    total_force_y -= norm_dy * attraction_force
            
            # Update particle
            particle.update(dt, (total_force_x, total_force_y), self.surface_size)
    
    def render(self, surface: pygame.Surface):
        """Render particle system to surface"""
        # Draw shape outline (optional)
        if self.show_shape_outline:
            self._draw_shape_outline(surface)
        
        # Draw particles
        for particle in self.particles:
            self._draw_particle(surface, particle)
    
    def _draw_shape_outline(self, surface: pygame.Surface):
        """Draw the shape outline that particles emanate from"""
        outline_color = self.hsv_to_rgb(self.color_hue, 0.5, 0.5)
        center = (int(self.shape_center[0]), int(self.shape_center[1]))
        size = int(self.shape_size)
        
        try:
            if self.shape_type == "circle":
                pygame.draw.circle(surface, outline_color, center, size, 2)
            elif self.shape_type == "square":
                rect = pygame.Rect(center[0] - size, center[1] - size, size * 2, size * 2)
                pygame.draw.rect(surface, outline_color, rect, 2)
        except (ValueError, TypeError):
            pass  # Skip drawing if invalid parameters
    
    def _draw_particle(self, surface: pygame.Surface, particle: Particle):
        """Draw a single particle"""
        try:
            pos = (int(particle.x), int(particle.y))
            size = max(1, int(particle.size))
            
            if len(particle.color) == 4:  # Has alpha
                # Create temporary surface for alpha blending
                particle_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, particle.color, 
                                 (size * 2, size * 2), size)
                surface.blit(particle_surface, (pos[0] - size * 2, pos[1] - size * 2))
            else:
                # Direct drawing without alpha
                pygame.draw.circle(surface, particle.color[:3], pos, size)
                
        except (ValueError, TypeError, pygame.error):
            pass  # Skip drawing problematic particles
    
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
            if name == 'max_particles':
                self.max_particles = max(10, int(value))
                # Remove excess particles if limit was lowered
                while len(self.particles) > self.max_particles:
                    self.particles.pop(0)
            
            elif name == 'spawn_rate':
                self.spawn_rate = max(1, float(value))
            
            elif name == 'shape_size':
                self.shape_size = max(10, float(value))
                self._update_emitter_points(self.shape_size)
            
            elif name in ['color_saturation', 'color_brightness']:
                setattr(self, name, max(0, min(1, float(value))))
                self.parameters[name] = getattr(self, name)
    
    def reset(self):
        """Reset plugin to initial state"""
        # Clear all particles
        self.particles.clear()
        
        # Reset shape to center
        self.shape_center = (self.surface_size[0] / 2, self.surface_size[1] / 2)
        self._shape_target = list(self.shape_center)
        
        # Reset visual state
        self.color_hue = 0
        self.shape_rotation = 0
        self.beat_burst_strength = 0
        self.spawn_timer = 0
        
        # Update emitter points
        self._update_emitter_points(self.shape_size)
        
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
            'particle_count': len(self.particles),
            'shape_center': self.shape_center,
            'current_hue': self.color_hue
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Particle Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Particle Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = ParticlePlugin((800, 600))
    
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
                elif event.key == pygame.K_1:
                    plugin.shape_type = "circle"
                elif event.key == pygame.K_2:
                    plugin.shape_type = "square"
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.5 + 0.4 * math.sin(current_time * 2),
            'beat_detected': (current_time % 1.5) < 0.1,
            'dominant_frequency': 440 + 300 * math.sin(current_time * 0.3),
            'frequency_bands': {
                'bass': 0.4 + 0.3 * math.sin(current_time * 0.8),
                'mid': 0.3 + 0.2 * math.sin(current_time * 1.2),
                'treble': 0.2 + 0.3 * math.sin(current_time * 1.8)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((15, 15, 25))  # Dark background
        plugin.render(screen)
        
        # Display info
        font = pygame.font.Font(None, 24)
        info_lines = [
            f"Particles: {len(plugin.particles)}/{plugin.max_particles}",
            f"Shape: {plugin.shape_type} (1/2 to change)",
            "Press SPACE to reset"
        ]
        
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
    
    pygame.quit()
    print("Particle plugin test completed")
