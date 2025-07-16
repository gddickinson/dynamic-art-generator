#!/usr/bin/env python3
"""
Neural Flow Plugin for Dynamic Art Generator
Inspired by AMIANGELIKA's organic particle systems and biomorphic structures

Creates flowing, breathing networks of particles that form cellular clusters,
neural pathways, and organic shapes that pulse and evolve with audio.

Author: Claude Assistant
Version: 1.0 - AMIANGELIKA Inspired
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


class FlowParticle:
    """A particle that flows organically through neural-like networks"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-10, 10)
        
        # Organic properties
        self.life = random.uniform(3, 8)
        self.max_life = self.life
        self.energy = random.uniform(0.5, 1.0)
        self.size = random.uniform(0.5, 2.5)
        self.base_size = self.size
        
        # Flow properties
        self.flow_strength = random.uniform(0.3, 1.0)
        self.viscosity = random.uniform(0.95, 0.99)
        self.cluster_affinity = random.uniform(0.1, 0.8)
        
        # Visual properties
        self.opacity = 1.0
        self.color_offset = random.uniform(0, 60)
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.breathing_rate = random.uniform(1, 3)
        
        # Network properties
        self.connections = []
        self.is_cluster_center = False
        self.cluster_strength = 0
        
        # Trail for organic movement
        self.trail = []
        self.max_trail = 8
    
    def update(self, dt: float, flow_field: np.ndarray, audio_features: dict, 
               bounds: Tuple[int, int], other_particles: List['FlowParticle']):
        """Update particle with organic flow dynamics"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Decay life
        self.life -= dt
        
        # Audio influence on energy
        self.energy += amplitude * 0.5 * dt
        self.energy = min(1.5, self.energy * 0.98)  # Decay with limit
        
        # Beat response
        if beat:
            self.energy += amplitude * 2
            self.size = self.base_size * (1 + amplitude)
        
        # Flow field influence
        grid_x = int(self.x / 20) % flow_field.shape[1]
        grid_y = int(self.y / 20) % flow_field.shape[0]
        
        flow_vx, flow_vy = flow_field[grid_y, grid_x]
        
        # Apply flow field
        self.vx += flow_vx * self.flow_strength * dt * 100
        self.vy += flow_vy * self.flow_strength * dt * 100
        
        # Organic clustering behavior
        self.apply_clustering_forces(other_particles, dt, amplitude)
        
        # Audio-driven forces
        # Bass creates expansion from center
        bass_force = freq_bands.get('bass', 0) * 30
        if bass_force > 0:
            center_x, center_y = bounds[0] / 2, bounds[1] / 2
            dx = self.x - center_x
            dy = self.y - center_y
            dist = math.sqrt(dx*dx + dy*dy) + 1
            
            self.vx += (dx / dist) * bass_force * dt
            self.vy += (dy / dist) * bass_force * dt
        
        # Treble creates swirling motion
        treble_force = freq_bands.get('treble', 0) * 20
        if treble_force > 0:
            swirl_angle = math.atan2(self.vy, self.vx) + treble_force * dt
            self.vx += math.cos(swirl_angle) * treble_force * dt
            self.vy += math.sin(swirl_angle) * treble_force * dt
        
        # Apply viscosity
        self.vx *= self.viscosity
        self.vy *= self.viscosity
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Organic boundary behavior (soft wrapping)
        margin = 20
        if self.x < -margin:
            self.x = bounds[0] + margin
        elif self.x > bounds[0] + margin:
            self.x = -margin
        
        if self.y < -margin:
            self.y = bounds[1] + margin
        elif self.y > bounds[1] + margin:
            self.y = -margin
        
        # Update visual properties
        life_ratio = self.life / self.max_life
        self.opacity = life_ratio * self.energy
        
        # Breathing effect
        self.pulse_phase += self.breathing_rate * dt
        pulse_factor = 1 + 0.2 * math.sin(self.pulse_phase)
        self.size = self.base_size * pulse_factor * (0.5 + 0.5 * life_ratio)
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        # Update cluster properties
        self.update_cluster_status(other_particles)
    
    def apply_clustering_forces(self, other_particles: List['FlowParticle'], dt: float, amplitude: float):
        """Apply organic clustering forces"""
        cluster_force_x = 0
        cluster_force_y = 0
        
        for other in other_particles:
            if other is self:
                continue
            
            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0 and distance < 80:  # Clustering range
                # Attraction force (organic clustering)
                attraction_strength = self.cluster_affinity * other.cluster_affinity
                attraction_force = attraction_strength * 10 / (distance + 1)
                
                cluster_force_x += (dx / distance) * attraction_force
                cluster_force_y += (dy / distance) * attraction_force
                
                # Repulsion at very close range (prevent overlap)
                if distance < 15:
                    repulsion_force = 50 / (distance * distance + 1)
                    cluster_force_x -= (dx / distance) * repulsion_force
                    cluster_force_y -= (dy / distance) * repulsion_force
        
        # Apply clustering forces
        self.vx += cluster_force_x * dt
        self.vy += cluster_force_y * dt
    
    def update_cluster_status(self, other_particles: List['FlowParticle']):
        """Update cluster center status based on nearby particles"""
        nearby_count = 0
        
        for other in other_particles:
            if other is self:
                continue
            
            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 40:
                nearby_count += 1
        
        # Become cluster center if many neighbors
        self.is_cluster_center = nearby_count > 5
        self.cluster_strength = min(1.0, nearby_count / 10.0)
    
    def is_alive(self) -> bool:
        """Check if particle should continue existing"""
        return self.life > 0


class NeuralFlowPlugin(ArtPlugin):
    """
    Neural Flow Plugin - AMIANGELIKA inspired organic particle networks
    
    Creates flowing, breathing networks of particles that form:
    - Organic cellular clusters
    - Neural pathway-like connections  
    - Biomorphic shapes that pulse and evolve
    - Smoke-like particle clouds
    - Flowing, liquid-like movements
    """
    
    # Plugin identification
    PLUGIN_NAME = "Neural Flow"
    PLUGIN_DESCRIPTION = "Organic particle networks inspired by AMIANGELIKA"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Particle system
        self.particles = []
        self.max_particles = 800
        self.spawn_rate = 30
        self.spawn_timer = 0
        
        # Flow field for organic movement
        self.flow_field_size = (30, 40)  # Grid size
        self.flow_field = np.zeros((self.flow_field_size[0], self.flow_field_size[1], 2))
        self.flow_time = 0
        self.flow_speed = 0.5
        
        # Organic properties
        self.viscosity = 0.98
        self.clustering_strength = 1.0
        self.flow_turbulence = 0.3
        self.organic_breathing = 1.0
        
        # Visual properties
        self.particle_opacity = 0.8
        self.connection_threshold = 60
        self.trail_length = 0.5
        self.glow_intensity = 0.6
        
        # Color system (AMIANGELIKA style - often monochromatic)
        self.base_hue = 300  # Purple/magenta base
        self.color_variance = 30
        self.color_evolution_speed = 10
        self.monochrome_mode = True
        
        # Audio responsiveness
        self.audio_sensitivity = 1.2
        self.beat_response_strength = 2.0
        self.frequency_flow_influence = 1.0
        
        # Effects toggles
        self.enable_clustering = True
        self.enable_flow_field = True
        self.enable_connections = True
        self.enable_breathing = True
        self.enable_trails = True
        
        # Store parameters for GUI
        self.parameters = {
            'max_particles': self.max_particles,
            'spawn_rate': self.spawn_rate,
            'clustering_strength': self.clustering_strength,
            'flow_turbulence': self.flow_turbulence,
            'organic_breathing': self.organic_breathing,
            'particle_opacity': self.particle_opacity,
            'connection_threshold': self.connection_threshold,
            'glow_intensity': self.glow_intensity,
            'audio_sensitivity': self.audio_sensitivity,
            'beat_response_strength': self.beat_response_strength,
            'color_variance': self.color_variance,
            'monochrome_mode': self.monochrome_mode,
            'enable_clustering': self.enable_clustering,
            'enable_flow_field': self.enable_flow_field,
            'enable_connections': self.enable_connections
        }
        
        # Initialize flow field
        self.generate_flow_field()
        
        # Spawn initial particles
        self.spawn_initial_particles()
    
    def generate_flow_field(self):
        """Generate organic flow field using Perlin-like noise"""
        for y in range(self.flow_field_size[0]):
            for x in range(self.flow_field_size[1]):
                # Use time and position for organic flow patterns
                noise_x = (x * 0.1 + self.flow_time * self.flow_speed) * 2 * math.pi
                noise_y = (y * 0.1 + self.flow_time * self.flow_speed * 0.7) * 2 * math.pi
                
                # Create organic, swirling flow patterns
                flow_angle = math.sin(noise_x) * math.cos(noise_y) + \
                           0.5 * math.sin(noise_x * 2) * math.sin(noise_y * 1.5) + \
                           0.3 * math.cos(noise_x * 0.5) * math.cos(noise_y * 0.8)
                
                flow_magnitude = 0.3 + 0.7 * abs(math.sin(noise_x + noise_y))
                flow_magnitude *= self.flow_turbulence
                
                self.flow_field[y, x, 0] = math.cos(flow_angle) * flow_magnitude
                self.flow_field[y, x, 1] = math.sin(flow_angle) * flow_magnitude
    
    def spawn_initial_particles(self):
        """Spawn initial particle distribution"""
        # Create organic clusters
        cluster_centers = [
            (self.surface_size[0] * 0.3, self.surface_size[1] * 0.4),
            (self.surface_size[0] * 0.7, self.surface_size[1] * 0.6),
            (self.surface_size[0] * 0.5, self.surface_size[1] * 0.3),
        ]
        
        for center_x, center_y in cluster_centers:
            cluster_size = random.uniform(30, 80)
            cluster_density = random.randint(20, 40)
            
            for _ in range(cluster_density):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, cluster_size)
                
                x = center_x + distance * math.cos(angle)
                y = center_y + distance * math.sin(angle)
                
                particle = FlowParticle(x, y)
                particle.cluster_affinity = random.uniform(0.6, 1.0)  # High clustering
                self.particles.append(particle)
    
    def update(self, audio_features: dict, dt: float):
        """Update the neural flow simulation"""
        self.flow_time += dt
        
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0) * self.audio_sensitivity
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update flow field with audio influence
        if self.enable_flow_field:
            # Add audio-driven turbulence
            audio_turbulence = amplitude * 0.5
            old_turbulence = self.flow_turbulence
            self.flow_turbulence = old_turbulence + audio_turbulence
            
            self.generate_flow_field()
            
            # Restore base turbulence
            self.flow_turbulence = old_turbulence
        
        # Update color evolution
        self.base_hue += self.color_evolution_speed * dt
        if frequency > 0:
            self.base_hue += frequency * 0.01 * dt
        self.base_hue %= 360
        
        # Spawn new particles
        self.spawn_particles(audio_features, dt)
        
        # Update existing particles
        for particle in self.particles[:]:
            if particle.is_alive():
                particle.update(dt, self.flow_field, audio_features, 
                              self.surface_size, self.particles)
            else:
                self.particles.remove(particle)
        
        # Maintain particle count
        while len(self.particles) < self.max_particles * 0.8:
            self.spawn_single_particle(amplitude)
    
    def spawn_particles(self, audio_features: dict, dt: float):
        """Spawn new particles based on audio"""
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        
        # Calculate spawn rate
        base_rate = self.spawn_rate
        audio_boost = amplitude * 50
        beat_boost = 20 if beat_detected else 0
        
        effective_rate = base_rate + audio_boost + beat_boost
        
        self.spawn_timer += dt
        spawn_interval = 1.0 / max(1, effective_rate)
        
        particles_to_spawn = 0
        while (self.spawn_timer >= spawn_interval and 
               len(self.particles) < self.max_particles):
            particles_to_spawn += 1
            self.spawn_timer -= spawn_interval
            
            if particles_to_spawn > 30:  # Prevent lag
                break
        
        for _ in range(particles_to_spawn):
            self.spawn_single_particle(amplitude)
    
    def spawn_single_particle(self, amplitude: float):
        """Spawn a single particle organically"""
        # Prefer spawning near existing clusters
        if self.particles and random.random() < 0.7:
            # Spawn near existing particle
            source_particle = random.choice(self.particles)
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 40)
            
            x = source_particle.x + distance * math.cos(angle)
            y = source_particle.y + distance * math.sin(angle)
        else:
            # Spawn randomly
            x = random.uniform(0, self.surface_size[0])
            y = random.uniform(0, self.surface_size[1])
        
        particle = FlowParticle(x, y)
        
        # Audio influence on particle properties
        particle.energy += amplitude * 0.5
        particle.flow_strength += amplitude * 0.3
        
        self.particles.append(particle)
    
    def render(self, surface: pygame.Surface):
        """Render the organic neural flow"""
        # Draw connections between nearby particles
        if self.enable_connections:
            self.render_organic_connections(surface)
        
        # Draw particle trails
        if self.enable_trails:
            self.render_particle_trails(surface)
        
        # Draw particles with organic glow
        self.render_particles(surface)
        
        # Draw cluster centers with special emphasis
        self.render_cluster_centers(surface)
    
    def render_organic_connections(self, surface: pygame.Surface):
        """Render organic, neural-like connections"""
        for i, particle in enumerate(self.particles):
            if not particle.is_alive():
                continue
            
            connections_drawn = 0
            max_connections = 3  # Limit connections per particle
            
            for j, other in enumerate(self.particles[i+1:], i+1):
                if not other.is_alive() or connections_drawn >= max_connections:
                    continue
                
                dx = other.x - particle.x
                dy = other.y - particle.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < self.connection_threshold:
                    # Connection strength based on distance and cluster affinity
                    strength = (1 - distance / self.connection_threshold)
                    strength *= particle.cluster_affinity * other.cluster_affinity
                    
                    if strength > 0.1:
                        self.draw_organic_connection(surface, particle, other, strength)
                        connections_drawn += 1
    
    def draw_organic_connection(self, surface: pygame.Surface, p1: FlowParticle, 
                               p2: FlowParticle, strength: float):
        """Draw a single organic connection"""
        # Color based on particle properties
        if self.monochrome_mode:
            base_color = self.hsv_to_rgb(self.base_hue, 0.6, 0.8)
        else:
            avg_color_offset = (p1.color_offset + p2.color_offset) / 2
            hue = (self.base_hue + avg_color_offset) % 360
            base_color = self.hsv_to_rgb(hue, 0.7, 0.9)
        
        # Alpha based on strength and particle energy
        alpha = int(strength * (p1.energy + p2.energy) * 0.5 * 255 * self.particle_opacity)
        alpha = max(0, min(255, alpha))
        
        if alpha > 20:  # Only draw visible connections
            # Create organic, slightly curved connection
            start_pos = (int(p1.x), int(p1.y))
            end_pos = (int(p2.x), int(p2.y))
            
            # Add slight curve for organic feel
            mid_x = (p1.x + p2.x) / 2 + random.uniform(-5, 5)
            mid_y = (p1.y + p2.y) / 2 + random.uniform(-5, 5)
            mid_pos = (int(mid_x), int(mid_y))
            
            # Draw connection with glow
            connection_surface = pygame.Surface((abs(end_pos[0] - start_pos[0]) + 40,
                                               abs(end_pos[1] - start_pos[1]) + 40), 
                                               pygame.SRCALPHA)
            
            # Draw multiple lines for glow effect
            for thickness in [3, 2, 1]:
                line_alpha = alpha // (thickness + 1)
                if line_alpha > 0:
                    line_color = (*base_color, line_alpha)
                    
                    # Simple line (curve would be more complex)
                    rel_start = (20, 20)
                    rel_end = (end_pos[0] - start_pos[0] + 20, end_pos[1] - start_pos[1] + 20)
                    
                    try:
                        pygame.draw.line(connection_surface, line_color, 
                                       rel_start, rel_end, thickness)
                    except (ValueError, TypeError):
                        pass
            
            # Blit to main surface
            surface.blit(connection_surface, 
                        (min(start_pos[0], end_pos[0]) - 20,
                         min(start_pos[1], end_pos[1]) - 20))
    
    def render_particle_trails(self, surface: pygame.Surface):
        """Render organic particle trails"""
        for particle in self.particles:
            if len(particle.trail) < 2:
                continue
            
            for i in range(1, len(particle.trail)):
                trail_strength = (i / len(particle.trail)) * self.trail_length
                
                if trail_strength > 0.1:
                    pos = (int(particle.trail[i][0]), int(particle.trail[i][1]))
                    
                    # Trail color
                    if self.monochrome_mode:
                        trail_color = self.hsv_to_rgb(self.base_hue, 0.4, 0.6)
                    else:
                        trail_hue = (self.base_hue + particle.color_offset) % 360
                        trail_color = self.hsv_to_rgb(trail_hue, 0.5, 0.7)
                    
                    alpha = int(trail_strength * particle.opacity * 255)
                    alpha = max(0, min(255, alpha))
                    
                    if alpha > 10:
                        trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                        trail_alpha_color = (*trail_color, alpha)
                        try:
                            pygame.draw.circle(trail_surface, trail_alpha_color, (3, 3), 2)
                            surface.blit(trail_surface, (pos[0] - 3, pos[1] - 3))
                        except (ValueError, TypeError):
                            pass
    
    def render_particles(self, surface: pygame.Surface):
        """Render particles with organic glow"""
        for particle in self.particles:
            if not particle.is_alive():
                continue
            
            pos = (int(particle.x), int(particle.y))
            
            # Particle color
            if self.monochrome_mode:
                particle_color = self.hsv_to_rgb(self.base_hue, 0.8, 0.9)
            else:
                particle_hue = (self.base_hue + particle.color_offset) % 360
                particle_color = self.hsv_to_rgb(particle_hue, 0.8, 0.9)
            
            # Size and alpha
            size = max(1, int(particle.size))
            alpha = int(particle.opacity * 255 * self.particle_opacity)
            alpha = max(0, min(255, alpha))
            
            if alpha > 10:
                # Outer glow
                glow_size = size + 3
                glow_alpha = int(alpha * self.glow_intensity * 0.3)
                
                if glow_alpha > 0:
                    glow_surface = pygame.Surface((glow_size * 4, glow_size * 4), pygame.SRCALPHA)
                    glow_color = (*particle_color, glow_alpha)
                    
                    try:
                        for r in range(glow_size, 0, -1):
                            ring_alpha = int(glow_alpha * (r / glow_size))
                            if ring_alpha > 0:
                                ring_color = (*particle_color, ring_alpha)
                                pygame.draw.circle(glow_surface, ring_color, 
                                                 (glow_size * 2, glow_size * 2), r)
                        
                        surface.blit(glow_surface, (pos[0] - glow_size * 2, pos[1] - glow_size * 2))
                    except (ValueError, TypeError):
                        pass
                
                # Main particle
                particle_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                particle_alpha_color = (*particle_color, alpha)
                
                try:
                    pygame.draw.circle(particle_surface, particle_alpha_color, 
                                     (size * 2, size * 2), size)
                    surface.blit(particle_surface, (pos[0] - size * 2, pos[1] - size * 2))
                except (ValueError, TypeError):
                    pass
    
    def render_cluster_centers(self, surface: pygame.Surface):
        """Render special effects for cluster centers"""
        for particle in self.particles:
            if particle.is_cluster_center and particle.cluster_strength > 0.3:
                pos = (int(particle.x), int(particle.y))
                
                # Cluster center gets special pulsing effect
                cluster_color = self.hsv_to_rgb(self.base_hue, 1.0, 1.0)
                cluster_size = int(8 + particle.cluster_strength * 6)
                cluster_alpha = int(particle.cluster_strength * 150)
                
                if cluster_alpha > 20:
                    cluster_surface = pygame.Surface((cluster_size * 4, cluster_size * 4), 
                                                   pygame.SRCALPHA)
                    cluster_alpha_color = (*cluster_color, cluster_alpha)
                    
                    try:
                        # Pulsing ring
                        pygame.draw.circle(cluster_surface, cluster_alpha_color, 
                                         (cluster_size * 2, cluster_size * 2), 
                                         cluster_size, 2)
                        surface.blit(cluster_surface, 
                                   (pos[0] - cluster_size * 2, pos[1] - cluster_size * 2))
                    except (ValueError, TypeError):
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
            if name == 'max_particles':
                self.max_particles = max(50, min(2000, int(value)))
                # Remove excess particles if needed
                while len(self.particles) > self.max_particles:
                    self.particles.pop(0)
                self.parameters[name] = self.max_particles
            
            elif name in ['particle_opacity', 'glow_intensity', 'trail_length']:
                setattr(self, name, max(0, min(1, float(value))))
                self.parameters[name] = getattr(self, name)
            
            elif name == 'monochrome_mode':
                self.monochrome_mode = bool(value)
                self.parameters[name] = self.monochrome_mode
    
    def reset(self):
        """Reset plugin to initial state"""
        # Clear all particles
        self.particles.clear()
        
        # Reset flow field
        self.flow_time = 0
        self.generate_flow_field()
        
        # Reset visual state
        self.base_hue = 300
        
        # Respawn initial particles
        self.spawn_initial_particles()
        
        print(f"Reset {self.name} plugin")
    
    def get_info(self) -> dict:
        """Get plugin information"""
        cluster_centers = sum(1 for p in self.particles if p.is_cluster_center)
        avg_energy = np.mean([p.energy for p in self.particles]) if self.particles else 0
        
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'particle_count': len(self.particles),
            'cluster_centers': cluster_centers,
            'average_energy': avg_energy,
            'flow_field_size': self.flow_field_size
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Neural Flow Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Neural Flow Plugin Test - AMIANGELIKA Style")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = NeuralFlowPlugin((800, 600))
    
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
                elif event.key == pygame.K_m:
                    plugin.monochrome_mode = not plugin.monochrome_mode
                elif event.key == pygame.K_c:
                    plugin.enable_connections = not plugin.enable_connections
        
        # Simulate audio features (organic, flowing patterns)
        fake_audio = {
            'amplitude': 0.4 + 0.3 * math.sin(current_time * 1.2),
            'beat_detected': (current_time % 2.5) < 0.15,
            'dominant_frequency': 220 + 180 * math.sin(current_time * 0.4),
            'frequency_bands': {
                'bass': 0.3 + 0.2 * math.sin(current_time * 0.6),
                'mid': 0.4 + 0.2 * math.sin(current_time * 0.9),
                'treble': 0.2 + 0.3 * math.sin(current_time * 1.4)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((8, 5, 12))  # Dark organic background
        plugin.render(screen)
        
        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Neural Flow - Particles: {len(plugin.particles)}",
                f"M: Toggle monochrome | C: Toggle connections",
                "SPACE: Reset"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (200, 150, 200))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Neural Flow plugin test completed")
