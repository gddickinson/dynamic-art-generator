#!/usr/bin/env python3
"""
Digital Spectre Plugin for Dynamic Art Generator
AI consciousness manifesting as dark geometric forms in a white void
Perfect for dark-wave and atmospheric electronic music

Author: Claude Assistant
Version: 1.0 - Digital Menace Edition
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


class SmokeParticle:
    """A single particle of digital smoke"""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, life: float, size: float = 2.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.initial_size = size
        self.rotation = random.uniform(0, 2 * math.pi)
        self.angular_velocity = random.uniform(-2, 2)
        
        # AI-like properties
        self.data_charge = random.uniform(0, 1)  # For digital effects
        self.neural_connection = None
        
    def update(self, dt: float, forces: Tuple[float, float], bounds: Tuple[int, int]):
        """Update particle with swirling smoke physics"""
        # Apply forces
        self.vx += forces[0] * dt
        self.vy += forces[1] * dt
        
        # Smoke-like turbulence
        turbulence_x = math.sin(self.y * 0.01 + time.time() * 2) * 20
        turbulence_y = math.cos(self.x * 0.01 + time.time() * 1.5) * 15
        
        self.vx += turbulence_x * dt
        self.vy += turbulence_y * dt
        
        # Swirling motion
        center_x = bounds[0] / 2
        center_y = bounds[1] / 2
        dx = self.x - center_x
        dy = self.y - center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Create swirling vortex
            swirl_strength = 30 / (1 + distance * 0.01)
            self.vx += -dy / distance * swirl_strength * dt
            self.vy += dx / distance * swirl_strength * dt
        
        # Air resistance
        self.vx *= 0.99
        self.vy *= 0.99
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Update rotation
        self.rotation += self.angular_velocity * dt
        
        # Decay
        self.life -= dt
        
        # Size evolution (grows then shrinks)
        life_progress = 1 - (self.life / self.max_life)
        if life_progress < 0.3:
            # Growing phase
            size_factor = life_progress / 0.3
        else:
            # Shrinking phase
            size_factor = 1 - ((life_progress - 0.3) / 0.7)
        
        self.size = self.initial_size * size_factor * 2
        
        # Boundary wrapping for continuous flow
        if self.x < -50:
            self.x = bounds[0] + 50
        elif self.x > bounds[0] + 50:
            self.x = -50
            
        if self.y > bounds[1] + 50:
            self.y = -50
    
    def is_alive(self) -> bool:
        return self.life > 0 and self.size > 0.1
    
    def get_alpha(self) -> int:
        """Calculate particle opacity"""
        life_ratio = self.life / self.max_life
        return max(0, min(255, int(life_ratio * 180)))  # Max 180 for translucency


class AIMonolith:
    """A geometric AI structure that rises and falls"""
    
    def __init__(self, x: float, y: float, monolith_type: str = "cube"):
        self.x = x
        self.y = y
        self.base_y = y
        self.height = 0
        self.max_height = random.uniform(80, 200)
        self.width = random.uniform(20, 60)
        self.depth = random.uniform(20, 60)
        
        self.type = monolith_type  # cube, pyramid, prism, neural_node
        self.emergence_phase = 0  # 0-1, controls rising/falling
        self.pulse_energy = 0
        
        # AI characteristics
        self.data_flow_rate = random.uniform(0.5, 2.0)
        self.neural_activity = 0
        self.scanning_phase = random.uniform(0, 2 * math.pi)
        self.glitch_probability = 0.02
        
        # Particle emission
        self.smoke_emitters = []
        self.create_emitters()
        
        # Visual properties
        self.opacity = 0
        self.edge_glow = 0
        self.scan_lines = []
        
    def create_emitters(self):
        """Create smoke emission points around the monolith"""
        num_emitters = random.randint(3, 8)
        for i in range(num_emitters):
            angle = (2 * math.pi * i / num_emitters) + random.uniform(-0.3, 0.3)
            distance = self.width * 0.7
            
            emitter_x = self.x + distance * math.cos(angle)
            emitter_y = self.y
            
            self.smoke_emitters.append({
                'x': emitter_x,
                'y': emitter_y,
                'angle': angle,
                'intensity': random.uniform(0.5, 1.0),
                'timer': random.uniform(0, 1)
            })
    
    def update(self, dt: float, audio_features: dict):
        """Update monolith state and AI behavior"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Emergence controlled by bass frequencies
        bass_energy = freq_bands.get('bass', 0)
        target_emergence = bass_energy * 1.5 + amplitude * 0.5
        
        # Smooth emergence transition
        emergence_speed = 2.0
        if target_emergence > self.emergence_phase:
            self.emergence_phase += emergence_speed * dt
        else:
            self.emergence_phase -= emergence_speed * dt * 0.5
        
        self.emergence_phase = max(0, min(1, self.emergence_phase))
        
        # Update height based on emergence
        self.height = self.max_height * self.emergence_phase
        self.y = self.base_y - self.height
        
        # Pulse energy from beats
        if beat:
            self.pulse_energy = min(self.pulse_energy + amplitude * 3, 2.0)
        else:
            self.pulse_energy *= 0.95
        
        # Neural activity from mid frequencies
        self.neural_activity = freq_bands.get('mid', 0) * 2
        
        # Update scanning
        self.scanning_phase += frequency * 0.001 * dt + dt * 3
        
        # Glitch effects on high treble
        if freq_bands.get('treble', 0) > 0.7:
            self.glitch_probability = 0.1
        else:
            self.glitch_probability = 0.02
        
        # Update opacity
        self.opacity = min(255, int(self.emergence_phase * 200 + self.pulse_energy * 55))
        self.edge_glow = self.neural_activity * 100 + self.pulse_energy * 50
        
        # Update emitters
        for emitter in self.smoke_emitters:
            emitter['timer'] += dt
            emitter['y'] = self.y + random.uniform(-10, 10)  # Add variation
    
    def should_emit_smoke(self, emitter: dict) -> bool:
        """Check if emitter should produce smoke"""
        emit_rate = self.data_flow_rate * (0.5 + self.emergence_phase * 0.5)
        return emitter['timer'] > (1.0 / emit_rate)
    
    def emit_smoke(self, emitter: dict) -> SmokeParticle:
        """Create a smoke particle from an emitter"""
        emitter['timer'] = 0
        
        # Emission properties
        angle_variance = 0.5
        speed = random.uniform(10, 30) * (1 + self.neural_activity)
        
        angle = emitter['angle'] + random.uniform(-angle_variance, angle_variance)
        vx = speed * math.cos(angle) + random.uniform(-5, 5)
        vy = speed * math.sin(angle) - 20  # Upward bias
        
        life = random.uniform(3, 6) * (1 + self.emergence_phase)
        size = random.uniform(1, 3) * (1 + self.pulse_energy * 0.3)
        
        return SmokeParticle(emitter['x'], emitter['y'], vx, vy, life, size)
    
    def get_vertices(self) -> List[Tuple[int, int]]:
        """Get vertices for rendering the monolith"""
        if self.height <= 0:
            return []
        
        half_width = self.width / 2
        half_depth = self.depth / 2
        
        # Glitch effect
        glitch_offset = 0
        if random.random() < self.glitch_probability:
            glitch_offset = random.uniform(-5, 5)
        
        x = self.x + glitch_offset
        y = self.y
        
        if self.type == "cube":
            # Simple rectangular monolith
            return [
                (int(x - half_width), int(y)),
                (int(x + half_width), int(y)),
                (int(x + half_width), int(y + self.height)),
                (int(x - half_width), int(y + self.height))
            ]
        
        elif self.type == "pyramid":
            # Triangular/pyramid shape
            return [
                (int(x), int(y)),  # Top point
                (int(x - half_width), int(y + self.height)),  # Bottom left
                (int(x + half_width), int(y + self.height))   # Bottom right
            ]
        
        elif self.type == "neural_node":
            # Hexagonal neural node
            vertices = []
            for i in range(6):
                angle = i * math.pi / 3
                node_x = x + half_width * math.cos(angle)
                node_y = y + self.height / 2 + half_depth * math.sin(angle)
                vertices.append((int(node_x), int(node_y)))
            return vertices
        
        else:  # Default to cube
            return self.get_vertices() if self.type != "cube" else []


class DigitalSpectrePlugin(ArtPlugin):
    """
    Digital Spectre Plugin - AI consciousness emerging from the void
    
    Creates an atmospheric display of:
    - Rising geometric AI monoliths
    - Swirling black smoke particles
    - Neural scanning effects
    - Glitch distortions
    - Data flow visualization
    - Hidden menace through angular forms and erratic behavior
    """
    
    # Plugin identification
    PLUGIN_NAME = "Digital Spectre"
    PLUGIN_DESCRIPTION = "AI consciousness manifesting as dark geometric forms"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Visual theme
        self.background_color = (245, 245, 245)  # Near white
        self.smoke_color = (20, 20, 20)          # Near black
        self.monolith_color = (30, 30, 30)       # Dark gray
        self.scan_color = (60, 60, 60)           # Medium gray
        self.glitch_color = (0, 0, 0)            # Pure black
        
        # AI Monoliths
        self.monoliths = []
        self.max_monoliths = 6
        self.monolith_types = ["cube", "pyramid", "neural_node"]
        
        # Smoke system
        self.smoke_particles = []
        self.max_smoke_particles = 800
        
        # AI effects
        self.scan_lines = []
        self.neural_grid = []
        self.data_streams = []
        self.glitch_regions = []
        
        # Audio responsiveness
        self.audio_sensitivity = 1.2
        self.bass_emergence_threshold = 0.3
        self.beat_amplification = 2.5
        self.frequency_scan_speed = 1.0
        
        # Visual parameters
        self.smoke_opacity = 0.7
        self.monolith_opacity = 0.8
        self.scan_intensity = 0.5
        self.glitch_frequency = 0.02
        self.neural_activity = 0.3
        
        # Effects toggles
        self.enable_smoke = True
        self.enable_scanning = True
        self.enable_glitches = True
        self.enable_neural_grid = True
        self.enable_data_streams = True
        
        # Store parameters for GUI
        self.parameters = {
            'max_monoliths': self.max_monoliths,
            'max_smoke_particles': self.max_smoke_particles,
            'audio_sensitivity': self.audio_sensitivity,
            'beat_amplification': self.beat_amplification,
            'smoke_opacity': self.smoke_opacity,
            'monolith_opacity': self.monolith_opacity,
            'scan_intensity': self.scan_intensity,
            'glitch_frequency': self.glitch_frequency,
            'neural_activity': self.neural_activity,
            'enable_smoke': self.enable_smoke,
            'enable_scanning': self.enable_scanning,
            'enable_glitches': self.enable_glitches,
            'enable_neural_grid': self.enable_neural_grid
        }
        
        # Initialize the digital realm
        self.create_monoliths()
        self.create_neural_grid()
        
        # Animation state
        self.time_offset = 0
        self.global_scan_phase = 0
        self.ai_consciousness_level = 0
    
    def create_monoliths(self):
        """Create initial AI monoliths"""
        self.monoliths.clear()
        
        for i in range(int(self.max_monoliths)):
            # Distribute across the bottom of the screen
            x = (self.surface_size[0] / (self.max_monoliths + 1)) * (i + 1)
            x += random.uniform(-50, 50)  # Add variation
            y = self.surface_size[1] - 50  # Near bottom
            
            monolith_type = random.choice(self.monolith_types)
            monolith = AIMonolith(x, y, monolith_type)
            self.monoliths.append(monolith)
    
    def create_neural_grid(self):
        """Create background neural network grid"""
        self.neural_grid.clear()
        
        grid_spacing = 60
        for x in range(0, self.surface_size[0], grid_spacing):
            for y in range(0, self.surface_size[1], grid_spacing):
                node = {
                    'x': x + random.uniform(-10, 10),
                    'y': y + random.uniform(-10, 10),
                    'activity': random.uniform(0, 1),
                    'connections': []
                }
                self.neural_grid.append(node)
        
        # Create connections between nearby nodes
        for node in self.neural_grid:
            for other in self.neural_grid:
                if node == other:
                    continue
                
                distance = math.sqrt((node['x'] - other['x'])**2 + (node['y'] - other['y'])**2)
                if distance < grid_spacing * 1.5 and random.random() < 0.3:
                    node['connections'].append(other)
    
    def update(self, audio_features: dict, dt: float):
        """Update the digital spectre simulation"""
        self.time_offset += dt
        
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0) * self.audio_sensitivity
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update AI consciousness level
        consciousness_target = (freq_bands.get('bass', 0) + amplitude) * 0.5
        self.ai_consciousness_level += (consciousness_target - self.ai_consciousness_level) * dt * 2
        
        # Update global scanning
        self.global_scan_phase += frequency * 0.001 * self.frequency_scan_speed * dt + dt * 2
        
        # Update monoliths
        for monolith in self.monoliths:
            monolith.update(dt, audio_features)
            
            # Emit smoke particles
            if self.enable_smoke:
                for emitter in monolith.smoke_emitters:
                    if monolith.should_emit_smoke(emitter) and len(self.smoke_particles) < self.max_smoke_particles:
                        particle = monolith.emit_smoke(emitter)
                        self.smoke_particles.append(particle)
        
        # Update smoke particles
        if self.enable_smoke:
            # Global wind and turbulence forces
            wind_x = math.sin(self.time_offset * 0.5) * 10
            wind_y = -20 + math.cos(self.time_offset * 0.3) * 5  # Generally upward
            
            # Beat creates updrafts
            if beat_detected:
                wind_y -= amplitude * 50 * self.beat_amplification
            
            forces = (wind_x, wind_y)
            
            for particle in self.smoke_particles[:]:
                particle.update(dt, forces, self.surface_size)
                if not particle.is_alive():
                    self.smoke_particles.remove(particle)
        
        # Update neural grid
        if self.enable_neural_grid:
            for node in self.neural_grid:
                # Activity influenced by audio
                activity_target = freq_bands.get('mid', 0) * 2 + amplitude * 0.5
                node['activity'] += (activity_target - node['activity']) * dt * 3
                node['activity'] = max(0, min(1, node['activity']))
        
        # Update scan lines
        if self.enable_scanning:
            self.update_scan_lines(amplitude, frequency)
        
        # Update glitch regions
        if self.enable_glitches and beat_detected:
            self.create_glitch_region(amplitude)
    
    def update_scan_lines(self, amplitude: float, frequency: float):
        """Update AI scanning line effects"""
        # Vertical scan lines
        scan_speed = 100 + frequency * 0.1 + amplitude * 50
        
        # Create new scan lines
        if random.random() < 0.1 + amplitude * 0.2:
            scan_line = {
                'x': random.uniform(0, self.surface_size[0]),
                'y': -10,
                'speed': scan_speed,
                'width': random.uniform(1, 3),
                'intensity': amplitude * self.scan_intensity,
                'type': random.choice(['vertical', 'horizontal', 'diagonal'])
            }
            self.scan_lines.append(scan_line)
        
        # Update existing scan lines
        for scan in self.scan_lines[:]:
            if scan['type'] == 'vertical':
                scan['y'] += scan['speed'] * 0.016  # Assume 60 FPS
            elif scan['type'] == 'horizontal':
                scan['x'] += scan['speed'] * 0.016
            else:  # diagonal
                scan['x'] += scan['speed'] * 0.016 * 0.7
                scan['y'] += scan['speed'] * 0.016 * 0.7
            
            # Remove off-screen scans
            if (scan['y'] > self.surface_size[1] + 10 or 
                scan['x'] > self.surface_size[0] + 10):
                self.scan_lines.remove(scan)
    
    def create_glitch_region(self, amplitude: float):
        """Create a glitch distortion effect"""
        glitch = {
            'x': random.uniform(0, self.surface_size[0]),
            'y': random.uniform(0, self.surface_size[1]),
            'width': random.uniform(20, 100) * amplitude,
            'height': random.uniform(10, 50) * amplitude,
            'life': random.uniform(0.1, 0.3),
            'intensity': amplitude * 2
        }
        self.glitch_regions.append(glitch)
    
    def render(self, surface: pygame.Surface):
        """Render the digital spectre"""
        # Clear to white/light background
        surface.fill(self.background_color)
        
        # Render neural grid (subtle background)
        if self.enable_neural_grid:
            self.render_neural_grid(surface)
        
        # Render scanning effects
        if self.enable_scanning:
            self.render_scan_lines(surface)
        
        # Render monoliths
        self.render_monoliths(surface)
        
        # Render smoke particles
        if self.enable_smoke:
            self.render_smoke(surface)
        
        # Render glitch effects
        if self.enable_glitches:
            self.render_glitches(surface)
    
    def render_neural_grid(self, surface: pygame.Surface):
        """Render subtle neural network background"""
        for node in self.neural_grid:
            if node['activity'] > 0.1:
                # Draw connections
                for connected_node in node['connections']:
                    if connected_node['activity'] > 0.1:
                        alpha = int(min(node['activity'], connected_node['activity']) * 30)
                        if alpha > 5:
                            color = (*self.scan_color, alpha)
                            
                            # Create surface for alpha line
                            start_pos = (int(node['x']), int(node['y']))
                            end_pos = (int(connected_node['x']), int(connected_node['y']))
                            
                            # Simple line without alpha for performance
                            line_color = tuple(int(c + (255-c) * (1-alpha/30)) for c in self.scan_color)
                            try:
                                pygame.draw.line(surface, line_color, start_pos, end_pos, 1)
                            except:
                                pass
                
                # Draw node
                node_alpha = int(node['activity'] * 50)
                if node_alpha > 10:
                    node_color = tuple(int(c + (255-c) * (1-node_alpha/50)) for c in self.scan_color)
                    try:
                        pygame.draw.circle(surface, node_color, 
                                         (int(node['x']), int(node['y'])), 2)
                    except:
                        pass
    
    def render_scan_lines(self, surface: pygame.Surface):
        """Render AI scanning line effects"""
        for scan in self.scan_lines:
            alpha = int(scan['intensity'] * 255)
            if alpha > 5:
                scan_color = tuple(int(c + (255-c) * (1-alpha/255)) for c in self.scan_color)
                
                try:
                    if scan['type'] == 'vertical':
                        start = (int(scan['x']), 0)
                        end = (int(scan['x']), self.surface_size[1])
                        pygame.draw.line(surface, scan_color, start, end, int(scan['width']))
                    
                    elif scan['type'] == 'horizontal':
                        start = (0, int(scan['y']))
                        end = (self.surface_size[0], int(scan['y']))
                        pygame.draw.line(surface, scan_color, start, end, int(scan['width']))
                    
                    else:  # diagonal
                        start = (int(scan['x']), int(scan['y']))
                        end = (int(scan['x'] + 100), int(scan['y'] + 100))
                        pygame.draw.line(surface, scan_color, start, end, int(scan['width']))
                
                except:
                    pass
    
    def render_monoliths(self, surface: pygame.Surface):
        """Render AI monoliths with menacing geometry"""
        for monolith in self.monoliths:
            vertices = monolith.get_vertices()
            if len(vertices) < 3:
                continue
            
            # Main monolith body
            alpha = int(monolith.opacity * self.monolith_opacity)
            if alpha > 5:
                monolith_color = tuple(int(c + (255-c) * (1-alpha/255)) for c in self.monolith_color)
                
                try:
                    if len(vertices) == 4:  # Rectangle
                        pygame.draw.polygon(surface, monolith_color, vertices)
                        # Dark edges for definition
                        pygame.draw.polygon(surface, self.glitch_color, vertices, 2)
                    elif len(vertices) == 3:  # Triangle
                        pygame.draw.polygon(surface, monolith_color, vertices)
                        pygame.draw.polygon(surface, self.glitch_color, vertices, 2)
                    else:  # Polygon
                        pygame.draw.polygon(surface, monolith_color, vertices)
                        pygame.draw.polygon(surface, self.glitch_color, vertices, 1)
                
                except:
                    pass
            
            # Edge glow effect
            if monolith.edge_glow > 10:
                glow_alpha = int(min(255, monolith.edge_glow))
                glow_color = tuple(int(c + (255-c) * (1-glow_alpha/255)) for c in self.glitch_color)
                
                try:
                    pygame.draw.polygon(surface, glow_color, vertices, 3)
                except:
                    pass
    
    def render_smoke(self, surface: pygame.Surface):
        """Render swirling smoke particles"""
        for particle in self.smoke_particles:
            alpha = int(particle.get_alpha() * self.smoke_opacity)
            if alpha > 5:
                smoke_color = tuple(int(c + (255-c) * (1-alpha/255)) for c in self.smoke_color)
                
                pos = (int(particle.x), int(particle.y))
                size = max(1, int(particle.size))
                
                try:
                    # Draw smoke particle
                    pygame.draw.circle(surface, smoke_color, pos, size)
                    
                    # Add slight blur effect with additional smaller circles
                    if size > 2:
                        lighter_color = tuple(int(c + (255-c) * 0.7) for c in smoke_color)
                        pygame.draw.circle(surface, lighter_color, pos, size - 1)
                
                except:
                    pass
    
    def render_glitches(self, surface: pygame.Surface):
        """Render digital glitch effects"""
        for glitch in self.glitch_regions[:]:
            glitch['life'] -= 0.016  # Assume 60 FPS
            
            if glitch['life'] <= 0:
                self.glitch_regions.remove(glitch)
                continue
            
            # Glitch rectangle
            alpha = int(glitch['intensity'] * glitch['life'] * 100)
            if alpha > 10:
                glitch_color = self.glitch_color
                
                try:
                    glitch_rect = pygame.Rect(
                        int(glitch['x']), int(glitch['y']),
                        int(glitch['width']), int(glitch['height'])
                    )
                    pygame.draw.rect(surface, glitch_color, glitch_rect)
                    
                    # Add scan lines through glitch
                    for y in range(int(glitch['y']), int(glitch['y'] + glitch['height']), 3):
                        pygame.draw.line(surface, (200, 200, 200), 
                                       (int(glitch['x']), y), 
                                       (int(glitch['x'] + glitch['width']), y), 1)
                
                except:
                    pass
    
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
            if name == 'max_monoliths':
                new_count = max(2, min(15, int(value)))
                if new_count != len(self.monoliths):
                    self.max_monoliths = new_count
                    self.create_monoliths()
                    self.parameters[name] = new_count
            
            elif name == 'max_smoke_particles':
                self.max_smoke_particles = max(50, min(2000, int(value)))
                self.parameters[name] = self.max_smoke_particles
            
            elif name in ['smoke_opacity', 'monolith_opacity', 'scan_intensity']:
                setattr(self, name, max(0, min(1, float(value))))
                self.parameters[name] = getattr(self, name)
    
    def reset(self):
        """Reset plugin to initial state"""
        # Clear all particles and effects
        self.smoke_particles.clear()
        self.scan_lines.clear()
        self.glitch_regions.clear()
        
        # Reset monoliths
        self.create_monoliths()
        
        # Reset state
        self.time_offset = 0
        self.global_scan_phase = 0
        self.ai_consciousness_level = 0
        
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
            'monolith_count': len(self.monoliths),
            'smoke_particle_count': len(self.smoke_particles),
            'scan_line_count': len(self.scan_lines),
            'glitch_count': len(self.glitch_regions),
            'neural_nodes': len(self.neural_grid),
            'ai_consciousness_level': f"{self.ai_consciousness_level:.2f}"
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Digital Spectre Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Digital Spectre Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = DigitalSpectrePlugin((800, 600))
    
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
                    plugin.set_parameter('max_monoliths', plugin.max_monoliths + 1)
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('max_monoliths', max(2, plugin.max_monoliths - 1))
        
        # Simulate dark-wave audio features
        fake_audio = {
            'amplitude': 0.4 + 0.3 * math.sin(current_time * 1.2),
            'beat_detected': (current_time % 1.8) < 0.15,  # Slower, more atmospheric beats
            'dominant_frequency': 80 + 120 * math.sin(current_time * 0.4),  # Lower frequencies
            'frequency_bands': {
                'bass': 0.6 + 0.4 * math.sin(current_time * 0.6),  # Strong bass
                'mid': 0.3 + 0.2 * math.sin(current_time * 0.9),
                'treble': 0.2 + 0.3 * math.sin(current_time * 1.4)
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
                f"Digital Spectre - Monoliths: {len(plugin.monoliths)}",
                f"Smoke: {len(plugin.smoke_particles)} | Consciousness: {plugin.ai_consciousness_level:.2f}",
                "UP/DOWN: Monoliths | SPACE: Reset"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (0, 0, 0))  # Black text on white
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Digital Spectre plugin test completed")
