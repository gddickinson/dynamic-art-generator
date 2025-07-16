#!/usr/bin/env python3
"""
Particle Fountain Plugin for Dynamic Art Generator
High-performance particle system inspired by Daniel Shiffman's particle code

Author: Claude Assistant  
Version: 1.0 - Processing-Inspired Edition
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
    """2D Vector class for particle physics"""
    
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)
    
    def add(self, other):
        """Add another vector to this vector"""
        if isinstance(other, Vector2D):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other
            self.y += other
    
    def mult(self, scalar):
        """Multiply this vector by a scalar"""
        self.x *= scalar
        self.y *= scalar
    
    def copy(self):
        """Create a copy of this vector"""
        return Vector2D(self.x, self.y)
    
    def magnitude(self):
        """Calculate the magnitude of this vector"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        """Normalize this vector to unit length"""
        mag = self.magnitude()
        if mag > 0:
            self.x /= mag
            self.y /= mag
    
    def limit(self, max_val):
        """Limit the magnitude of this vector"""
        if self.magnitude() > max_val:
            self.normalize()
            self.mult(max_val)
    
    @staticmethod
    def random():
        """Create a random unit vector"""
        angle = random.uniform(0, 2 * math.pi)
        return Vector2D(math.cos(angle), math.sin(angle))
    
    @staticmethod
    def from_angle(angle, magnitude=1):
        """Create a vector from angle and magnitude"""
        return Vector2D(math.cos(angle) * magnitude, math.sin(angle) * magnitude)


class FountainParticle:
    """Individual particle in the fountain system"""
    
    def __init__(self, emitter_x, emitter_y):
        # Physics properties
        self.position = Vector2D(emitter_x, emitter_y)
        self.velocity = Vector2D()
        self.acceleration = Vector2D()
        self.gravity = Vector2D(0, 0.15)  # Downward gravity
        
        # Visual properties
        self.lifespan = 255.0
        self.max_lifespan = 255.0
        self.size = random.uniform(2, 8)
        self.initial_size = self.size
        
        # Color properties
        self.hue = random.uniform(0, 360)
        self.saturation = random.uniform(0.6, 1.0)
        self.brightness = random.uniform(0.7, 1.0)
        
        # Initialize with random velocity
        self.rebirth(emitter_x, emitter_y)
    
    def rebirth(self, x, y):
        """Respawn the particle at the emitter location"""
        # Set new position
        self.position.x = x + random.uniform(-10, 10)
        self.position.y = y + random.uniform(-5, 5)
        
        # Random velocity in a cone upward
        angle = random.uniform(-math.pi * 0.3, -math.pi * 0.7)  # Upward cone
        speed = random.uniform(1, 6)
        
        self.velocity = Vector2D.from_angle(angle, speed)
        
        # Add some horizontal spread
        self.velocity.x += random.uniform(-2, 2)
        
        # Reset lifespan
        self.lifespan = self.max_lifespan
        self.size = self.initial_size
        
        # Randomize color
        self.hue = random.uniform(0, 360)
    
    def update(self, audio_features: dict):
        """Update particle physics and properties"""
        amplitude = audio_features.get('amplitude', 0)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Apply forces
        self.acceleration = self.gravity.copy()
        
        # Audio influences
        # Bass adds upward lift
        bass_force = freq_bands.get('bass', 0) * 0.3
        self.acceleration.y -= bass_force
        
        # Treble adds horizontal turbulence
        treble_force = freq_bands.get('treble', 0) * 0.2
        self.acceleration.x += random.uniform(-treble_force, treble_force)
        
        # Mid frequencies affect color
        mid_influence = freq_bands.get('mid', 0)
        self.hue += mid_influence * 100
        
        # Update velocity and position
        self.velocity.add(self.acceleration)
        
        # Limit velocity to prevent particles from going too fast
        self.velocity.limit(12)
        
        # Update position
        self.position.add(self.velocity)
        
        # Decrease lifespan
        decay_rate = 1.5 + amplitude * 2  # Audio makes particles decay faster/slower
        self.lifespan -= decay_rate
        
        # Size changes with lifespan
        life_ratio = self.lifespan / self.max_lifespan
        self.size = self.initial_size * (0.5 + 0.5 * life_ratio)
        
        # Color shifting
        self.hue += frequency * 0.01
        self.hue = self.hue % 360
    
    def is_dead(self):
        """Check if particle should be respawned"""
        return self.lifespan <= 0
    
    def get_alpha(self):
        """Calculate current alpha based on lifespan"""
        life_ratio = self.lifespan / self.max_lifespan
        return max(0, min(255, int(life_ratio * 255)))


class ParticleFountainPlugin(ArtPlugin):
    """
    Particle Fountain Plugin - High-performance particle system
    
    Based on Daniel Shiffman's particle system code, this creates a fountain
    of thousands of particles that:
    - Emit from an audio-controlled point
    - Fall under gravity with physics
    - Fade over their lifespan and respawn
    - Respond to audio frequency bands
    - Create mesmerizing flowing patterns
    """
    
    # Plugin identification
    PLUGIN_NAME = "Particle Fountain"
    PLUGIN_DESCRIPTION = "High-performance fountain of thousands of particles"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Particle system properties
        self.particles = []
        self.num_particles = 5000  # Start with 5000, can be adjusted
        self.max_particles = 10000
        
        # Emitter properties
        self.emitter_x = surface_size[0] / 2
        self.emitter_y = surface_size[1] / 2
        self.emitter_target_x = self.emitter_x
        self.emitter_target_y = self.emitter_y
        self.emitter_smoothing = 0.1
        
        # Physics properties
        self.gravity_strength = 1.0
        self.wind_force = 0.0
        self.turbulence = 0.1
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.bass_lift = 1.0
        self.treble_spread = 1.0
        self.frequency_color_influence = 1.0
        
        # Visual properties
        self.particle_size_range = (2, 8)
        self.color_mode = "rainbow"  # rainbow, mono, frequency
        self.base_hue = 200  # Blue
        self.fade_trails = True
        self.glow_effect = True
        
        # Performance options
        self.use_batch_rendering = True
        self.render_quality = "high"  # low, medium, high
        
        # Store parameters for GUI
        self.parameters = {
            'num_particles': self.num_particles,
            'audio_sensitivity': self.audio_sensitivity,
            'gravity_strength': self.gravity_strength,
            'wind_force': self.wind_force,
            'turbulence': self.turbulence,
            'bass_lift': self.bass_lift,
            'treble_spread': self.treble_spread,
            'base_hue': self.base_hue,
            'glow_effect': self.glow_effect,
            'fade_trails': self.fade_trails
        }
        
        # Initialize particles
        self.create_particles()
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 60
    
    def create_particles(self):
        """Initialize the particle system"""
        self.particles.clear()
        
        for _ in range(int(self.num_particles)):
            particle = FountainParticle(self.emitter_x, self.emitter_y)
            # Stagger initial lifespans for smooth startup
            particle.lifespan = random.uniform(0, 255)
            self.particles.append(particle)
    
    def update_emitter_position(self, audio_features: dict):
        """Update emitter position based on audio"""
        amplitude = audio_features.get('amplitude', 0)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Audio-driven emitter movement
        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2
        
        # Create movement based on audio
        movement_range = 150 * self.audio_sensitivity
        
        # Bass moves horizontally
        bass_offset_x = freq_bands.get('bass', 0) * movement_range * math.sin(time.time() * 2)
        
        # Mid frequencies move vertically
        mid_offset_y = freq_bands.get('mid', 0) * movement_range * 0.5 * math.cos(time.time() * 1.5)
        
        # Treble adds circular motion
        treble_influence = freq_bands.get('treble', 0) * 50
        treble_offset_x = treble_influence * math.cos(time.time() * 4)
        treble_offset_y = treble_influence * math.sin(time.time() * 4)
        
        # Frequency-based position
        freq_influence = (frequency / 1000.0) if frequency > 0 else 0
        freq_offset_x = freq_influence * 100 * math.sin(time.time() * 3)
        
        # Calculate target position
        self.emitter_target_x = center_x + bass_offset_x + treble_offset_x + freq_offset_x
        self.emitter_target_y = center_y + mid_offset_y + treble_offset_y
        
        # Keep within bounds
        margin = 50
        self.emitter_target_x = max(margin, min(self.surface_size[0] - margin, self.emitter_target_x))
        self.emitter_target_y = max(margin, min(self.surface_size[1] - margin, self.emitter_target_y))
        
        # Smooth movement
        self.emitter_x += (self.emitter_target_x - self.emitter_x) * self.emitter_smoothing
        self.emitter_y += (self.emitter_target_y - self.emitter_y) * self.emitter_smoothing
    
    def update(self, audio_features: dict, dt: float):
        """Update the particle fountain"""
        # Update emitter position
        self.update_emitter_position(audio_features)
        
        # Scale audio features
        scaled_audio = {
            'amplitude': audio_features.get('amplitude', 0) * self.audio_sensitivity,
            'beat_detected': audio_features.get('beat_detected', False),
            'dominant_frequency': audio_features.get('dominant_frequency', 0),
            'frequency_bands': {
                'bass': audio_features.get('frequency_bands', {}).get('bass', 0) * self.bass_lift,
                'mid': audio_features.get('frequency_bands', {}).get('mid', 0),
                'treble': audio_features.get('frequency_bands', {}).get('treble', 0) * self.treble_spread
            }
        }
        
        # Update all particles
        for particle in self.particles:
            if particle.is_dead():
                # Respawn particle at emitter
                particle.rebirth(self.emitter_x, self.emitter_y)
            else:
                # Update existing particle
                particle.update(scaled_audio)
        
        # Update performance tracking
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time > 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def render(self, surface: pygame.Surface):
        """Render the particle fountain"""
        if self.use_batch_rendering:
            self.render_batched(surface)
        else:
            self.render_individual(surface)
        
        # Draw emitter indicator
        self.render_emitter(surface)
    
    def render_batched(self, surface: pygame.Surface):
        """High-performance batched rendering"""
        # Group particles by alpha ranges for efficient rendering
        alpha_groups = {
            'high': [],    # Alpha > 200
            'medium': [],  # Alpha 100-200
            'low': []      # Alpha < 100
        }
        
        for particle in self.particles:
            if particle.is_dead():
                continue
            
            alpha = particle.get_alpha()
            pos = (int(particle.position.x), int(particle.position.y))
            size = max(1, int(particle.size))
            
            # Skip particles outside screen bounds
            if (pos[0] < -size or pos[0] > self.surface_size[0] + size or
                pos[1] < -size or pos[1] > self.surface_size[1] + size):
                continue
            
            # Calculate color
            color = self.calculate_particle_color(particle)
            
            # Group by alpha for batched rendering
            if alpha > 200:
                alpha_groups['high'].append((pos, size, color, alpha))
            elif alpha > 100:
                alpha_groups['medium'].append((pos, size, color, alpha))
            else:
                alpha_groups['low'].append((pos, size, color, alpha))
        
        # Render each group
        for group_name, particles in alpha_groups.items():
            if not particles:
                continue
            
            # Adjust rendering quality based on group
            if group_name == 'high':
                self.render_particle_group(surface, particles, quality='high')
            elif group_name == 'medium':
                self.render_particle_group(surface, particles, quality='medium')
            else:
                self.render_particle_group(surface, particles, quality='low')
    
    def render_particle_group(self, surface: pygame.Surface, particles: List, quality: str):
        """Render a group of particles with specified quality"""
        for pos, size, color, alpha in particles:
            if quality == 'high' and self.glow_effect:
                # High quality with glow
                self.render_particle_with_glow(surface, pos, size, color, alpha)
            elif quality == 'medium':
                # Medium quality with alpha
                self.render_particle_with_alpha(surface, pos, size, color, alpha)
            else:
                # Low quality, direct drawing
                pygame.draw.circle(surface, color[:3], pos, size)
    
    def render_particle_with_glow(self, surface: pygame.Surface, pos: Tuple[int, int], 
                                size: int, color: Tuple[int, int, int], alpha: int):
        """Render particle with glow effect"""
        # Create glow surface
        glow_size = size * 3
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Draw multiple circles for glow effect
        for r in range(glow_size, 0, -2):
            glow_alpha = int((alpha / 255) * (r / glow_size) * 50)
            if glow_alpha > 0:
                glow_color = (*color, glow_alpha)
                try:
                    pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), r)
                except (ValueError, TypeError):
                    pass
        
        # Draw main particle
        main_color = (*color, alpha)
        try:
            pygame.draw.circle(glow_surface, main_color, (glow_size, glow_size), size)
        except (ValueError, TypeError):
            pass
        
        # Blit to main surface
        surface.blit(glow_surface, (pos[0] - glow_size, pos[1] - glow_size))
    
    def render_particle_with_alpha(self, surface: pygame.Surface, pos: Tuple[int, int],
                                 size: int, color: Tuple[int, int, int], alpha: int):
        """Render particle with alpha blending"""
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        particle_color = (*color, alpha)
        
        try:
            pygame.draw.circle(particle_surface, particle_color, (size, size), size)
            surface.blit(particle_surface, (pos[0] - size, pos[1] - size))
        except (ValueError, TypeError):
            # Fallback to direct drawing
            pygame.draw.circle(surface, color, pos, size)
    
    def render_individual(self, surface: pygame.Surface):
        """Simple individual particle rendering"""
        for particle in self.particles:
            if particle.is_dead():
                continue
            
            pos = (int(particle.position.x), int(particle.position.y))
            size = max(1, int(particle.size))
            alpha = particle.get_alpha()
            
            if alpha > 0:
                color = self.calculate_particle_color(particle)
                
                if self.glow_effect:
                    self.render_particle_with_glow(surface, pos, size, color, alpha)
                else:
                    pygame.draw.circle(surface, color, pos, size)
    
    def render_emitter(self, surface: pygame.Surface):
        """Draw the emitter indicator"""
        emitter_pos = (int(self.emitter_x), int(self.emitter_y))
        
        # Pulsing emitter indicator
        pulse = 0.5 + 0.5 * math.sin(time.time() * 5)
        radius = int(8 + pulse * 5)
        
        # Emitter color
        emitter_color = self.hsv_to_rgb(self.base_hue, 1.0, 1.0)
        
        # Draw emitter with glow
        glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        
        for r in range(radius * 2, 0, -2):
            alpha = int(100 * (r / (radius * 2)))
            glow_color = (*emitter_color, alpha)
            try:
                pygame.draw.circle(glow_surface, glow_color, (radius * 2, radius * 2), r)
            except (ValueError, TypeError):
                pass
        
        surface.blit(glow_surface, (emitter_pos[0] - radius * 2, emitter_pos[1] - radius * 2))
    
    def calculate_particle_color(self, particle: FountainParticle) -> Tuple[int, int, int]:
        """Calculate particle color based on current color mode"""
        if self.color_mode == "rainbow":
            return self.hsv_to_rgb(particle.hue, particle.saturation, particle.brightness)
        elif self.color_mode == "mono":
            return self.hsv_to_rgb(self.base_hue, particle.saturation, particle.brightness)
        elif self.color_mode == "frequency":
            # Color based on position (frequency-like)
            hue = (self.base_hue + particle.position.y * 0.5) % 360
            return self.hsv_to_rgb(hue, particle.saturation, particle.brightness)
        else:
            return self.hsv_to_rgb(particle.hue, particle.saturation, particle.brightness)
    
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
            if name == 'num_particles':
                new_count = max(100, min(self.max_particles, int(value)))
                if new_count != len(self.particles):
                    self.num_particles = new_count
                    self.create_particles()
                    self.parameters[name] = new_count
            
            elif name == 'base_hue':
                self.base_hue = float(value) % 360
                self.parameters[name] = self.base_hue
            
            # Update gravity for all particles
            elif name == 'gravity_strength':
                for particle in self.particles:
                    particle.gravity.y = 0.15 * self.gravity_strength
    
    def reset(self):
        """Reset plugin to initial state"""
        # Reset emitter position
        self.emitter_x = self.surface_size[0] / 2
        self.emitter_y = self.surface_size[1] / 2
        self.emitter_target_x = self.emitter_x
        self.emitter_target_y = self.emitter_y
        
        # Reset all particles
        self.create_particles()
        
        print(f"Reset {self.name} plugin")
    
    def get_info(self) -> dict:
        """Get plugin information"""
        alive_particles = sum(1 for p in self.particles if not p.is_dead())
        
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'total_particles': len(self.particles),
            'alive_particles': alive_particles,
            'emitter_position': (int(self.emitter_x), int(self.emitter_y)),
            'current_fps': self.current_fps
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Particle Fountain Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Particle Fountain Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = ParticleFountainPlugin((800, 600))
    
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
                    plugin.set_parameter('num_particles', min(10000, plugin.num_particles + 500))
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('num_particles', max(100, plugin.num_particles - 500))
                elif event.key == pygame.K_g:
                    plugin.glow_effect = not plugin.glow_effect
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.7 + 0.3 * math.sin(current_time * 1.5),
            'beat_detected': (current_time % 1.8) < 0.15,
            'dominant_frequency': 440 + 400 * math.sin(current_time * 0.4),
            'frequency_bands': {
                'bass': 0.6 + 0.4 * math.sin(current_time * 0.8),
                'mid': 0.5 + 0.3 * math.sin(current_time * 1.2),
                'treble': 0.4 + 0.4 * math.sin(current_time * 1.6)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((5, 5, 15))  # Dark background
        plugin.render(screen)
        
        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Particles: {len(plugin.particles)} FPS: {plugin.current_fps}",
                f"UP/DOWN: Change count, G: Toggle glow",
                "SPACE: Reset"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Particle Fountain plugin test completed")
