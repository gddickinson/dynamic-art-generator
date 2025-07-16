#!/usr/bin/env python3
"""
Rehoboam Plugin for Dynamic Art Generator
Creates Westworld-inspired circular AI visualization with prediction pathways and data streams

Author: Claude Assistant  
Version: 1.0 - Digital Oracle Edition
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


class DataNode:
    """A node in the Rehoboam network representing a data point or decision"""
    
    def __init__(self, angle: float, radius: float, ring_index: int):
        self.angle = angle
        self.radius = radius
        self.ring_index = ring_index
        self.x = 0
        self.y = 0
        self.active = False
        self.activation_level = 0.0
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.connections = []
        self.data_value = random.uniform(0, 100)
        self.prediction_confidence = random.uniform(0.3, 0.95)
        
        # Visual properties
        self.base_size = 3 + ring_index * 0.5
        self.current_size = self.base_size
        self.glow_intensity = 0.0
        
        # Animation
        self.breathing_offset = random.uniform(0, 2 * math.pi)
        
    def update_position(self, center_x: float, center_y: float):
        """Update node position based on center and polar coordinates"""
        self.x = center_x + self.radius * math.cos(self.angle)
        self.y = center_y + self.radius * math.sin(self.angle)
    
    def update(self, dt: float, audio_features: dict):
        """Update node state and animations"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        
        # Update pulse phase
        self.pulse_phase += dt * 3
        
        # Breathing animation
        self.breathing_offset += dt * 2
        breathing_factor = 1 + 0.1 * math.sin(self.breathing_offset)
        
        # Audio response
        audio_boost = 1 + amplitude * 0.3
        
        # Beat response
        if beat and random.random() < 0.3:
            self.activation_level = min(1.0, self.activation_level + 0.5)
            self.active = True
        
        # Decay activation
        self.activation_level *= 0.95
        if self.activation_level < 0.1:
            self.active = False
        
        # Update visual properties
        self.current_size = self.base_size * breathing_factor * audio_boost
        self.glow_intensity = self.activation_level


class DataStream:
    """A flowing data stream between nodes"""
    
    def __init__(self, start_node: DataNode, end_node: DataNode):
        self.start_node = start_node
        self.end_node = end_node
        self.particles = []
        self.stream_active = False
        self.flow_speed = random.uniform(50, 100)
        self.particle_spawn_timer = 0
        self.stream_strength = random.uniform(0.3, 1.0)
        
    def spawn_particle(self):
        """Spawn a data particle"""
        particle = {
            'progress': 0.0,
            'speed': self.flow_speed,
            'life': 1.0,
            'size': random.uniform(1, 3),
            'brightness': random.uniform(0.5, 1.0)
        }
        self.particles.append(particle)
    
    def update(self, dt: float, audio_features: dict):
        """Update data stream"""
        amplitude = audio_features.get('amplitude', 0)
        
        # Activate stream based on node states and audio
        self.stream_active = (self.start_node.active or self.end_node.active or 
                             amplitude > 0.2 or random.random() < 0.1)
        
        # Spawn particles
        if self.stream_active:
            self.particle_spawn_timer += dt
            spawn_interval = 0.3 / (1 + amplitude * 2)
            
            if self.particle_spawn_timer > spawn_interval:
                self.spawn_particle()
                self.particle_spawn_timer = 0
        
        # Update particles
        for particle in self.particles[:]:
            particle['progress'] += particle['speed'] * dt / 100
            particle['life'] -= dt
            
            if particle['progress'] >= 1.0 or particle['life'] <= 0:
                self.particles.remove(particle)
                
                # Activate end node when particle arrives
                if particle['progress'] >= 1.0:
                    self.end_node.activation_level = min(1.0, self.end_node.activation_level + 0.3)
                    self.end_node.active = True


class PredictionPathway:
    """A branching prediction pathway showing possible futures"""
    
    def __init__(self, origin_node: DataNode, direction: float, length: float):
        self.origin_node = origin_node
        self.direction = direction
        self.length = length
        self.confidence = random.uniform(0.2, 0.9)
        self.active = False
        self.growth_progress = 0.0
        self.branch_points = []
        self.probability_text = f"{self.confidence:.1%}"
        
        # Generate branch points
        for i in range(random.randint(1, 4)):
            progress = random.uniform(0.3, 0.9)
            branch_angle = direction + random.uniform(-0.5, 0.5)
            branch_length = length * random.uniform(0.3, 0.7)
            self.branch_points.append({
                'progress': progress,
                'angle': branch_angle,
                'length': branch_length,
                'active': False
            })
    
    def update(self, dt: float, audio_features: dict):
        """Update prediction pathway"""
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        
        # Activate on beats or high frequency
        if beat or frequency > 800:
            if random.random() < 0.4:
                self.active = True
                self.growth_progress = 0.0
        
        # Grow pathway
        if self.active:
            self.growth_progress += dt * 2
            
            # Activate branches as we grow
            for branch in self.branch_points:
                if self.growth_progress > branch['progress'] and not branch['active']:
                    branch['active'] = True
            
            # Deactivate when fully grown
            if self.growth_progress > 1.2:
                self.active = False
                self.growth_progress = 0.0
                for branch in self.branch_points:
                    branch['active'] = False


class RehoboamPlugin(ArtPlugin):
    """
    Rehoboam Plugin - Creates Westworld-inspired AI visualization
    
    Features:
    - Concentric rings of interconnected nodes
    - Flowing data streams between nodes  
    - Branching prediction pathways
    - Real-time data visualization
    - Clean geometric sci-fi aesthetic
    - Audio-responsive network activity
    """
    
    # Plugin identification
    PLUGIN_NAME = "Rehoboam"
    PLUGIN_DESCRIPTION = "Westworld-inspired AI network visualization"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Network structure
        self.rings = []
        self.num_rings = 6
        self.nodes_per_ring = [8, 12, 16, 20, 24, 28]
        self.ring_spacing = 40
        self.base_radius = 60
        
        # Network components
        self.all_nodes = []
        self.data_streams = []
        self.prediction_pathways = []
        
        # Visual properties
        self.center_x = surface_size[0] / 2
        self.center_y = surface_size[1] / 2
        self.primary_color = (0, 150, 255)  # Rehoboam blue
        self.secondary_color = (255, 255, 255)  # White
        self.accent_color = (255, 100, 100)  # Red for alerts
        self.background_color = (5, 10, 20)  # Dark blue-black
        
        # Animation state
        self.global_pulse = 0
        self.network_breathing = 0
        self.reorganization_timer = 0
        self.alert_mode = False
        self.alert_intensity = 0.0
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_response_strength = 1.5
        self.frequency_color_shift = 0.3
        
        # System parameters
        self.network_activity_level = 0.5
        self.prediction_frequency = 0.3
        self.data_flow_speed = 1.0
        self.geometric_precision = 1.0
        
        # Store parameters for GUI
        self.parameters = {
            'num_rings': self.num_rings,
            'audio_sensitivity': self.audio_sensitivity,
            'beat_response_strength': self.beat_response_strength,
            'network_activity_level': self.network_activity_level,
            'prediction_frequency': self.prediction_frequency,
            'data_flow_speed': self.data_flow_speed,
            'frequency_color_shift': self.frequency_color_shift,
            'geometric_precision': self.geometric_precision
        }
        
        # Initialize the network
        self.build_network()
        
        # Font for data display (if available)
        self.font = None
        try:
            pygame.font.init()
            self.font = pygame.font.Font(None, 16)
        except:
            pass
    
    def build_network(self):
        """Build the Rehoboam network structure"""
        self.all_nodes.clear()
        self.data_streams.clear()
        self.prediction_pathways.clear()
        
        # Create concentric rings of nodes
        for ring_idx in range(int(self.num_rings)):
            ring_nodes = []
            node_count = self.nodes_per_ring[ring_idx] if ring_idx < len(self.nodes_per_ring) else 20
            radius = self.base_radius + ring_idx * self.ring_spacing
            
            for node_idx in range(node_count):
                angle = (2 * math.pi * node_idx / node_count) + ring_idx * 0.1
                node = DataNode(angle, radius, ring_idx)
                node.update_position(self.center_x, self.center_y)
                ring_nodes.append(node)
                self.all_nodes.append(node)
            
            self.rings.append(ring_nodes)
        
        # Create data streams between nodes
        self.create_data_streams()
        
        # Create prediction pathways
        self.create_prediction_pathways()
    
    def create_data_streams(self):
        """Create data streams connecting nodes"""
        # Connect adjacent nodes in same ring
        for ring in self.rings:
            for i, node in enumerate(ring):
                next_node = ring[(i + 1) % len(ring)]
                if random.random() < 0.7:  # 70% connection chance
                    stream = DataStream(node, next_node)
                    self.data_streams.append(stream)
        
        # Connect between rings
        for ring_idx in range(len(self.rings) - 1):
            inner_ring = self.rings[ring_idx]
            outer_ring = self.rings[ring_idx + 1]
            
            for inner_node in inner_ring:
                # Find closest nodes in outer ring
                closest_nodes = sorted(outer_ring, 
                                     key=lambda n: abs(n.angle - inner_node.angle))[:3]
                
                for outer_node in closest_nodes:
                    if random.random() < 0.4:  # 40% connection chance
                        stream = DataStream(inner_node, outer_node)
                        self.data_streams.append(stream)
        
        # Random long-distance connections
        for _ in range(20):
            node1 = random.choice(self.all_nodes)
            node2 = random.choice(self.all_nodes)
            if node1 != node2 and random.random() < 0.1:
                stream = DataStream(node1, node2)
                self.data_streams.append(stream)
    
    def create_prediction_pathways(self):
        """Create branching prediction pathways"""
        for node in self.all_nodes:
            if random.random() < 0.3:  # 30% of nodes have pathways
                direction = node.angle + random.uniform(-0.3, 0.3)
                length = random.uniform(50, 150)
                pathway = PredictionPathway(node, direction, length)
                self.prediction_pathways.append(pathway)
    
    def update(self, audio_features: dict, dt: float):
        """Update the Rehoboam network"""
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Scale audio by sensitivity
        scaled_amplitude = amplitude * self.audio_sensitivity
        
        # Update global animations
        self.global_pulse += dt * 4
        self.network_breathing += dt * 1.5
        
        # Beat response
        if beat_detected:
            # Trigger network reorganization
            if random.random() < 0.3:
                self.trigger_reorganization()
            
            # Activate random nodes
            for _ in range(int(self.beat_response_strength * 5)):
                node = random.choice(self.all_nodes)
                node.activation_level = min(1.0, node.activation_level + scaled_amplitude)
                node.active = True
        
        # Frequency-based color shifts
        if frequency > 1000:
            self.alert_mode = True
            self.alert_intensity = min(1.0, frequency / 2000)
        else:
            self.alert_mode = False
            self.alert_intensity *= 0.9
        
        # Update network breathing based on bass
        bass_influence = freq_bands.get('bass', 0)
        self.network_breathing_amplitude = 0.05 + bass_influence * 0.1
        
        # Update all nodes
        for node in self.all_nodes:
            node.update(dt, audio_features)
            
            # Apply network breathing
            breathing_factor = 1 + self.network_breathing_amplitude * math.sin(self.network_breathing)
            node.radius = (self.base_radius + node.ring_index * self.ring_spacing) * breathing_factor
            node.update_position(self.center_x, self.center_y)
        
        # Update data streams
        for stream in self.data_streams:
            stream.update(dt, audio_features)
        
        # Update prediction pathways
        for pathway in self.prediction_pathways:
            pathway.update(dt, audio_features)
        
        # Periodic reorganization
        self.reorganization_timer += dt
        if self.reorganization_timer > 10 + random.uniform(-2, 2):
            self.trigger_reorganization()
            self.reorganization_timer = 0
    
    def trigger_reorganization(self):
        """Trigger a network reorganization event"""
        # Randomly rotate some rings
        for ring in self.rings:
            if random.random() < 0.5:
                rotation = random.uniform(-0.2, 0.2)
                for node in ring:
                    node.angle += rotation
        
        # Activate some pathways
        for pathway in self.prediction_pathways:
            if random.random() < 0.4:
                pathway.active = True
                pathway.growth_progress = 0.0
    
    def render(self, surface: pygame.Surface):
        """Render the Rehoboam visualization"""
        # Draw ring structures
        self.render_rings(surface)
        
        # Draw data streams
        self.render_data_streams(surface)
        
        # Draw prediction pathways
        self.render_prediction_pathways(surface)
        
        # Draw nodes
        self.render_nodes(surface)
        
        # Draw central core
        self.render_core(surface)
        
        # Draw data overlays
        self.render_data_overlay(surface)
    
    def render_rings(self, surface: pygame.Surface):
        """Render the concentric ring structure"""
        for ring_idx, ring in enumerate(self.rings):
            if not ring:
                continue
            
            # Calculate ring radius
            avg_radius = ring[0].radius
            
            # Ring color based on alert mode
            if self.alert_mode:
                ring_color = self.blend_colors(self.primary_color, self.accent_color, self.alert_intensity)
            else:
                ring_color = self.primary_color
            
            # Fade outer rings
            alpha = max(50, 150 - ring_idx * 20)
            ring_color = (*ring_color, alpha)
            
            # Draw ring
            ring_surface = pygame.Surface((avg_radius * 4, avg_radius * 4), pygame.SRCALPHA)
            try:
                pygame.draw.circle(ring_surface, ring_color, 
                                 (avg_radius * 2, avg_radius * 2), 
                                 int(avg_radius), 1)
                surface.blit(ring_surface, 
                           (self.center_x - avg_radius * 2, self.center_y - avg_radius * 2))
            except (ValueError, TypeError):
                pass
    
    def render_data_streams(self, surface: pygame.Surface):
        """Render flowing data streams"""
        for stream in self.data_streams:
            if not stream.stream_active and not stream.particles:
                continue
            
            # Draw connection line
            start_pos = (int(stream.start_node.x), int(stream.start_node.y))
            end_pos = (int(stream.end_node.x), int(stream.end_node.y))
            
            # Line color based on stream strength
            alpha = int(stream.stream_strength * 100)
            line_color = (*self.primary_color, alpha)
            
            try:
                pygame.draw.line(surface, self.primary_color[:3], start_pos, end_pos, 1)
            except:
                pass
            
            # Draw flowing particles
            for particle in stream.particles:
                # Calculate particle position
                progress = particle['progress']
                x = stream.start_node.x + progress * (stream.end_node.x - stream.start_node.x)
                y = stream.start_node.y + progress * (stream.end_node.y - stream.start_node.y)
                
                # Particle color and size
                brightness = particle['brightness'] * particle['life']
                particle_color = self.brighten_color(self.primary_color, brightness)
                particle_size = max(1, int(particle['size']))
                
                # Draw particle
                pos = (int(x), int(y))
                try:
                    pygame.draw.circle(surface, particle_color, pos, particle_size)
                except:
                    pass
    
    def render_prediction_pathways(self, surface: pygame.Surface):
        """Render branching prediction pathways"""
        for pathway in self.prediction_pathways:
            if not pathway.active:
                continue
            
            # Main pathway
            start_x = pathway.origin_node.x
            start_y = pathway.origin_node.y
            
            pathway_length = pathway.length * min(1.0, pathway.growth_progress)
            end_x = start_x + pathway_length * math.cos(pathway.direction)
            end_y = start_y + pathway_length * math.sin(pathway.direction)
            
            # Pathway color based on confidence
            confidence_color = self.blend_colors(self.accent_color, self.secondary_color, 
                                               pathway.confidence)
            
            try:
                pygame.draw.line(surface, confidence_color, 
                               (int(start_x), int(start_y)), 
                               (int(end_x), int(end_y)), 2)
            except:
                pass
            
            # Draw branches
            for branch in pathway.branch_points:
                if not branch['active'] or pathway.growth_progress < branch['progress']:
                    continue
                
                branch_start_progress = branch['progress']
                branch_start_x = start_x + branch_start_progress * pathway.length * math.cos(pathway.direction)
                branch_start_y = start_y + branch_start_progress * pathway.length * math.sin(pathway.direction)
                
                branch_end_x = branch_start_x + branch['length'] * math.cos(branch['angle'])
                branch_end_y = branch_start_y + branch['length'] * math.sin(branch['angle'])
                
                try:
                    pygame.draw.line(surface, confidence_color, 
                                   (int(branch_start_x), int(branch_start_y)), 
                                   (int(branch_end_x), int(branch_end_y)), 1)
                except:
                    pass
    
    def render_nodes(self, surface: pygame.Surface):
        """Render network nodes"""
        for node in self.all_nodes:
            pos = (int(node.x), int(node.y))
            
            # Node color based on activation
            if node.active:
                node_color = self.brighten_color(self.primary_color, 1 + node.activation_level)
            else:
                node_color = self.primary_color
            
            # Alert mode override
            if self.alert_mode and random.random() < self.alert_intensity:
                node_color = self.accent_color
            
            # Draw node glow
            if node.glow_intensity > 0:
                glow_radius = int(node.current_size + node.glow_intensity * 10)
                glow_color = (*node_color, int(node.glow_intensity * 100))
                
                glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
                try:
                    pygame.draw.circle(glow_surface, glow_color, 
                                     (glow_radius * 2, glow_radius * 2), glow_radius)
                    surface.blit(glow_surface, (pos[0] - glow_radius * 2, pos[1] - glow_radius * 2))
                except:
                    pass
            
            # Draw node
            node_size = max(1, int(node.current_size))
            try:
                pygame.draw.circle(surface, node_color, pos, node_size)
                
                # Inner core for active nodes
                if node.active:
                    core_size = max(1, node_size // 2)
                    pygame.draw.circle(surface, self.secondary_color, pos, core_size)
            except:
                pass
    
    def render_core(self, surface: pygame.Surface):
        """Render the central Rehoboam core"""
        center_pos = (int(self.center_x), int(self.center_y))
        
        # Pulsing core
        pulse_factor = 1 + 0.3 * math.sin(self.global_pulse)
        core_radius = int(15 * pulse_factor)
        
        # Core color
        if self.alert_mode:
            core_color = self.blend_colors(self.primary_color, self.accent_color, self.alert_intensity)
        else:
            core_color = self.primary_color
        
        # Draw core with glow
        glow_radius = core_radius + 10
        glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
        
        # Outer glow
        for r in range(glow_radius, core_radius, -2):
            alpha = int(150 * (r - core_radius) / (glow_radius - core_radius) * 0.3)
            glow_color = (*core_color, alpha)
            try:
                pygame.draw.circle(glow_surface, glow_color, 
                                 (glow_radius * 2, glow_radius * 2), r)
            except:
                pass
        
        surface.blit(glow_surface, (center_pos[0] - glow_radius * 2, center_pos[1] - glow_radius * 2))
        
        # Main core
        try:
            pygame.draw.circle(surface, core_color, center_pos, core_radius)
            pygame.draw.circle(surface, self.secondary_color, center_pos, core_radius // 2)
        except:
            pass
    
    def render_data_overlay(self, surface: pygame.Surface):
        """Render data overlays and text"""
        if not self.font:
            return
        
        # System status
        status_texts = [
            f"NETWORK ACTIVITY: {self.network_activity_level:.1%}",
            f"PREDICTION CONFIDENCE: {random.uniform(0.7, 0.95):.1%}",
            f"DATA STREAMS: {len([s for s in self.data_streams if s.stream_active])}",
            f"ALERT LEVEL: {'HIGH' if self.alert_mode else 'NORMAL'}"
        ]
        
        for i, text in enumerate(status_texts):
            color = self.accent_color if self.alert_mode and i == 3 else self.secondary_color
            try:
                text_surface = self.font.render(text, True, color)
                surface.blit(text_surface, (10, 10 + i * 20))
            except:
                pass
    
    def blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float) -> Tuple[int, int, int]:
        """Blend two colors"""
        factor = max(0, min(1, factor))
        return (
            int(color1[0] * (1 - factor) + color2[0] * factor),
            int(color1[1] * (1 - factor) + color2[1] * factor),
            int(color1[2] * (1 - factor) + color2[2] * factor)
        )
    
    def brighten_color(self, color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Brighten a color"""
        factor = max(1, factor)
        return (
            min(255, int(color[0] * factor)),
            min(255, int(color[1] * factor)),
            min(255, int(color[2] * factor))
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
            if name == 'num_rings':
                new_rings = max(3, min(8, int(value)))
                if new_rings != len(self.rings):
                    self.num_rings = new_rings
                    self.build_network()
                    self.parameters[name] = new_rings
    
    def reset(self):
        """Reset plugin to initial state"""
        # Rebuild network
        self.build_network()
        
        # Reset animation state
        self.global_pulse = 0
        self.network_breathing = 0
        self.reorganization_timer = 0
        self.alert_mode = False
        self.alert_intensity = 0.0
        
        # Reset all nodes
        for node in self.all_nodes:
            node.active = False
            node.activation_level = 0.0
            node.glow_intensity = 0.0
        
        print(f"Reset {self.name} plugin")
    
    def get_info(self) -> dict:
        """Get plugin information"""
        active_nodes = len([n for n in self.all_nodes if n.active])
        active_streams = len([s for s in self.data_streams if s.stream_active])
        active_pathways = len([p for p in self.prediction_pathways if p.active])
        
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'total_nodes': len(self.all_nodes),
            'active_nodes': active_nodes,
            'data_streams': active_streams,
            'prediction_pathways': active_pathways,
            'alert_mode': self.alert_mode
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Rehoboam Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Rehoboam Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = RehoboamPlugin((1000, 800))
    
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
                    plugin.trigger_reorganization()
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.4 + 0.4 * math.sin(current_time * 1.2),
            'beat_detected': (current_time % 2.5) < 0.15,
            'dominant_frequency': 600 + 400 * math.sin(current_time * 0.4),
            'frequency_bands': {
                'bass': 0.3 + 0.3 * math.sin(current_time * 0.6),
                'mid': 0.4 + 0.2 * math.sin(current_time),
                'treble': 0.2 + 0.4 * math.sin(current_time * 1.8)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((5, 10, 20))  # Dark background
        plugin.render(screen)
        
        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                "REHOBOAM NETWORK VISUALIZATION",
                "SPACE: Reset | R: Reorganize",
                f"Nodes: {len(plugin.all_nodes)} | Streams: {len(plugin.data_streams)}"
            ]
            
            for i, line in enumerate(info_lines):
                color = (0, 150, 255) if i == 0 else (255, 255, 255)
                text_surface = font.render(line, True, color)
                screen.blit(text_surface, (10, screen.get_height() - 80 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Rehoboam plugin test completed")
