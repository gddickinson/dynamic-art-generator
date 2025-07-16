#!/usr/bin/env python3
"""
Bio-Mechanical Garden Plugin for Dynamic Art Generator
Where cyberpunk technology merges with organic plant growth
A living ecosystem of mechanical vines, gear-flowers, and data-sap

Author: Claude Assistant
Version: 1.0 - Cyber-Organic Fusion
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


class BioMechVine:
    """A growing vine that's part organic, part mechanical"""
    
    def __init__(self, x: float, y: float, vine_type: str = "basic"):
        self.segments = [(x, y)]
        self.growth_direction = random.uniform(-math.pi/4, math.pi/4) - math.pi/2  # Generally upward
        self.growth_speed = random.uniform(15, 30)
        self.max_length = random.randint(8, 25)
        self.thickness = random.uniform(2, 6)
        self.vine_type = vine_type  # basic, cable, neural, fiber_optic
        
        # Mechanical properties
        self.gears = []
        self.joints = []
        self.data_flow = []
        self.energy_level = 0
        
        # Organic properties
        self.bio_luminescence = 0
        self.growth_energy = 1.0
        self.nutrients = 1.0
        
        # Visual properties
        self.color_hue = random.uniform(0, 360)
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        
        # Create initial mechanical components
        self.add_gear_joint(x, y)
    
    def add_gear_joint(self, x: float, y: float):
        """Add a mechanical gear joint"""
        gear = {
            'x': x,
            'y': y,
            'size': random.uniform(5, 12),
            'rotation': 0,
            'speed': random.uniform(0.5, 2.0),
            'type': random.choice(['gear', 'servo', 'connector'])
        }
        self.gears.append(gear)
        
        joint = {
            'x': x,
            'y': y,
            'angle': self.growth_direction,
            'flexibility': random.uniform(0.1, 0.3)
        }
        self.joints.append(joint)
    
    def update(self, dt: float, audio_features: dict, bounds: Tuple[int, int]):
        """Update vine growth and mechanical components"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Audio affects growth energy
        self.growth_energy += freq_bands.get('mid', 0) * dt * 2
        self.growth_energy = min(2.0, self.growth_energy)
        
        # Beat affects bio-luminescence
        if beat:
            self.bio_luminescence = min(self.bio_luminescence + amplitude * 3, 2.0)
        else:
            self.bio_luminescence *= 0.95
        
        # Energy affects mechanical activity
        self.energy_level = amplitude + freq_bands.get('treble', 0)
        
        # Grow if we have energy and haven't reached max length
        if len(self.segments) < self.max_length and self.growth_energy > 0.5:
            growth_rate = self.growth_speed * self.growth_energy * dt
            
            if random.random() < growth_rate * 0.1:  # Growth probability
                last_x, last_y = self.segments[-1]
                
                # Add some randomness to growth direction
                direction_change = random.uniform(-0.3, 0.3)
                self.growth_direction += direction_change
                
                # Audio affects growth direction
                if frequency > 0:
                    freq_influence = math.sin(frequency * 0.01) * 0.2
                    self.growth_direction += freq_influence
                
                # Calculate new segment position
                new_x = last_x + math.cos(self.growth_direction) * 10
                new_y = last_y + math.sin(self.growth_direction) * 10
                
                # Boundary checking
                if 10 < new_x < bounds[0] - 10 and 10 < new_y < bounds[1] - 10:
                    self.segments.append((new_x, new_y))
                    
                    # Add mechanical components at intervals
                    if len(self.segments) % 3 == 0:
                        self.add_gear_joint(new_x, new_y)
                    
                    # Add data flow
                    if self.vine_type in ['neural', 'fiber_optic']:
                        self.add_data_packet(0)
        
        # Update mechanical components
        for gear in self.gears:
            gear['rotation'] += gear['speed'] * self.energy_level * dt * 100
            gear['rotation'] %= 360
        
        # Update data flow
        for packet in self.data_flow[:]:
            packet['position'] += packet['speed'] * dt
            if packet['position'] > len(self.segments) - 1:
                self.data_flow.remove(packet)
        
        # Color cycling
        self.color_hue += frequency * 0.001 * dt + dt * 10
        self.color_hue %= 360
        
        # Pulse phase
        self.pulse_phase += dt * 3 + amplitude * 5
    
    def add_data_packet(self, start_position: float):
        """Add a data packet that flows along the vine"""
        packet = {
            'position': start_position,
            'speed': random.uniform(2, 5),
            'size': random.uniform(2, 4),
            'color': random.uniform(0, 360),
            'intensity': random.uniform(0.5, 1.0)
        }
        self.data_flow.append(packet)
    
    def get_segment_color(self, segment_index: int) -> Tuple[int, int, int]:
        """Get color for a specific segment"""
        base_color = self.hsv_to_rgb(self.color_hue, 0.7, 0.8)
        
        # Bio-luminescence affects brightness
        bio_factor = 1 + self.bio_luminescence * 0.5
        
        # Mechanical segments are more metallic
        if segment_index % 3 == 0:  # Gear joints
            metallic_factor = 0.5
            enhanced_color = tuple(int(c * bio_factor * metallic_factor + 128 * (1 - metallic_factor)) 
                                 for c in base_color)
        else:
            enhanced_color = tuple(min(255, int(c * bio_factor)) for c in base_color)
        
        return enhanced_color
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
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


class GearFlower:
    """A mechanical flower that blooms and closes"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.bloom_state = 0  # 0 = closed, 1 = fully bloomed
        self.target_bloom = 0
        self.petal_count = random.randint(5, 8)
        self.center_size = random.uniform(8, 15)
        self.petal_length = random.uniform(15, 25)
        
        # Mechanical properties
        self.gear_rotation = 0
        self.gear_speed = random.uniform(0.5, 1.5)
        self.servo_angle = 0
        
        # Organic properties
        self.bio_pulse = 0
        self.nectar_level = 0
        
        # Visual
        self.hue = random.uniform(0, 360)
        self.bloom_timer = random.uniform(0, 5)  # Autonomous blooming
    
    def update(self, dt: float, audio_features: dict):
        """Update flower blooming and mechanical animation"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Audio controls blooming
        audio_bloom_trigger = freq_bands.get('mid', 0) + amplitude * 0.5
        
        # Autonomous blooming cycle
        self.bloom_timer += dt
        autonomous_bloom = 0.5 + 0.5 * math.sin(self.bloom_timer * 0.3)
        
        # Combine audio and autonomous blooming
        self.target_bloom = max(audio_bloom_trigger, autonomous_bloom * 0.3)
        
        # Smooth bloom transition
        bloom_speed = 2.0
        if self.target_bloom > self.bloom_state:
            self.bloom_state += bloom_speed * dt
        else:
            self.bloom_state -= bloom_speed * dt * 0.5
        
        self.bloom_state = max(0, min(1, self.bloom_state))
        
        # Update mechanical components
        self.gear_rotation += self.gear_speed * dt * 50
        self.gear_rotation %= 360
        
        # Servo movement
        self.servo_angle = math.sin(time.time() * 2) * 45 * self.bloom_state
        
        # Bio-pulse from beats
        if beat:
            self.bio_pulse = min(self.bio_pulse + amplitude * 2, 1.5)
        else:
            self.bio_pulse *= 0.9
        
        # Nectar production
        self.nectar_level = freq_bands.get('bass', 0) * self.bloom_state
        
        # Color evolution
        self.hue += dt * 20
        self.hue %= 360


class BioMechGardenPlugin(ArtPlugin):
    """
    Bio-Mechanical Garden Plugin - Where nature meets cyberpunk
    
    Creates a living ecosystem featuring:
    - Growing mechanical vines with gear joints
    - Blooming gear-flowers that open and close
    - Data packets flowing through neural pathways
    - Bio-luminescent pulsing effects
    - Organic growth patterns with mechanical precision
    - Cyberpunk aesthetics merged with natural forms
    """
    
    # Plugin identification
    PLUGIN_NAME = "Bio-Mechanical Garden"
    PLUGIN_DESCRIPTION = "Cyberpunk technology merging with organic plant growth"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Garden components
        self.vines = []
        self.flowers = []
        self.data_streams = []
        self.nutrient_pools = []
        
        # Garden parameters
        self.max_vines = 12
        self.max_flowers = 8
        self.vine_types = ["basic", "cable", "neural", "fiber_optic"]
        
        # Visual theme
        self.background_color = (15, 25, 15)  # Dark green
        self.soil_color = (40, 30, 20)        # Rich brown
        self.metal_color = (120, 120, 130)    # Metallic gray
        self.bio_glow_color = (0, 255, 100)   # Bright green
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.growth_threshold = 0.3
        self.bloom_sensitivity = 1.2
        self.data_flow_rate = 1.0
        
        # Garden state
        self.ecosystem_energy = 0.5
        self.nutrient_level = 1.0
        self.data_network_activity = 0
        
        # Effects
        self.enable_bio_glow = True
        self.enable_data_flow = True
        self.enable_particle_effects = True
        self.enable_servo_animation = True
        
        # Store parameters for GUI
        self.parameters = {
            'max_vines': self.max_vines,
            'max_flowers': self.max_flowers,
            'audio_sensitivity': self.audio_sensitivity,
            'growth_threshold': self.growth_threshold,
            'bloom_sensitivity': self.bloom_sensitivity,
            'data_flow_rate': self.data_flow_rate,
            'enable_bio_glow': self.enable_bio_glow,
            'enable_data_flow': self.enable_data_flow,
            'enable_particle_effects': self.enable_particle_effects,
            'enable_servo_animation': self.enable_servo_animation
        }
        
        # Initialize garden
        self.plant_initial_seeds()
        
        # Animation state
        self.time_offset = 0
        self.last_growth_time = 0
    
    def plant_initial_seeds(self):
        """Plant initial seeds for vines and flowers"""
        # Create initial vines from bottom of screen
        for i in range(3):  # Start with fewer vines
            x = random.uniform(50, self.surface_size[0] - 50)
            y = self.surface_size[1] - 30  # Near bottom
            vine_type = random.choice(self.vine_types)
            vine = BioMechVine(x, y, vine_type)
            self.vines.append(vine)
        
        # Create initial flowers
        for i in range(2):
            x = random.uniform(100, self.surface_size[0] - 100)
            y = random.uniform(200, self.surface_size[1] - 100)
            flower = GearFlower(x, y)
            self.flowers.append(flower)
    
    def update(self, audio_features: dict, dt: float):
        """Update the bio-mechanical garden"""
        self.time_offset += dt
        
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0) * self.audio_sensitivity
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update ecosystem energy
        energy_input = freq_bands.get('bass', 0) + amplitude * 0.5
        self.ecosystem_energy += (energy_input - self.ecosystem_energy) * dt * 2
        
        # Update data network activity
        self.data_network_activity = freq_bands.get('treble', 0) * self.data_flow_rate
        
        # Spawn new vines based on audio
        if (len(self.vines) < self.max_vines and 
            amplitude > self.growth_threshold and 
            self.time_offset - self.last_growth_time > 2.0):
            
            self.spawn_new_vine()
            self.last_growth_time = self.time_offset
        
        # Spawn new flowers
        if len(self.flowers) < self.max_flowers and beat_detected and amplitude > 0.5:
            self.spawn_new_flower()
        
        # Update vines
        for vine in self.vines:
            vine.update(dt, audio_features, self.surface_size)
            
            # Add data flow to neural vines
            if (self.enable_data_flow and 
                vine.vine_type in ['neural', 'fiber_optic'] and 
                self.data_network_activity > 0.3 and 
                random.random() < self.data_network_activity * dt):
                vine.add_data_packet(0)
        
        # Update flowers
        for flower in self.flowers:
            # Scale bloom sensitivity
            scaled_audio = {
                **audio_features,
                'frequency_bands': {
                    k: v * self.bloom_sensitivity for k, v in freq_bands.items()
                }
            }
            flower.update(dt, scaled_audio)
        
        # Clean up old/small vines
        self.vines = [vine for vine in self.vines if len(vine.segments) > 2]
    
    def spawn_new_vine(self):
        """Spawn a new vine at a random location"""
        # Prefer spawning near existing vines (clustering)
        if self.vines and random.random() < 0.7:
            parent_vine = random.choice(self.vines)
            if parent_vine.segments:
                parent_x, parent_y = parent_vine.segments[-1]
                x = parent_x + random.uniform(-50, 50)
                y = parent_y + random.uniform(-20, 20)
        else:
            x = random.uniform(50, self.surface_size[0] - 50)
            y = random.uniform(self.surface_size[1] - 100, self.surface_size[1] - 30)
        
        # Ensure within bounds
        x = max(50, min(self.surface_size[0] - 50, x))
        y = max(50, min(self.surface_size[1] - 30, y))
        
        vine_type = random.choice(self.vine_types)
        vine = BioMechVine(x, y, vine_type)
        self.vines.append(vine)
    
    def spawn_new_flower(self):
        """Spawn a new flower at a random location"""
        # Prefer spawning near vine tips
        if self.vines:
            vine = random.choice(self.vines)
            if vine.segments:
                vine_x, vine_y = vine.segments[-1]
                x = vine_x + random.uniform(-30, 30)
                y = vine_y + random.uniform(-30, 30)
            else:
                x = random.uniform(100, self.surface_size[0] - 100)
                y = random.uniform(200, self.surface_size[1] - 100)
        else:
            x = random.uniform(100, self.surface_size[0] - 100)
            y = random.uniform(200, self.surface_size[1] - 100)
        
        # Ensure within bounds
        x = max(100, min(self.surface_size[0] - 100, x))
        y = max(100, min(self.surface_size[1] - 100, y))
        
        flower = GearFlower(x, y)
        self.flowers.append(flower)
    
    def render(self, surface: pygame.Surface):
        """Render the bio-mechanical garden"""
        # Background
        surface.fill(self.background_color)
        
        # Render soil layer at bottom
        soil_height = 40
        soil_rect = pygame.Rect(0, self.surface_size[1] - soil_height, 
                               self.surface_size[0], soil_height)
        pygame.draw.rect(surface, self.soil_color, soil_rect)
        
        # Render vines
        self.render_vines(surface)
        
        # Render flowers
        self.render_flowers(surface)
        
        # Render data network effects
        if self.enable_data_flow:
            self.render_data_network(surface)
    
    def render_vines(self, surface: pygame.Surface):
        """Render bio-mechanical vines"""
        for vine in self.vines:
            if len(vine.segments) < 2:
                continue
            
            # Draw vine segments
            for i in range(1, len(vine.segments)):
                start_pos = (int(vine.segments[i-1][0]), int(vine.segments[i-1][1]))
                end_pos = (int(vine.segments[i][0]), int(vine.segments[i][1]))
                
                # Get segment color
                color = vine.get_segment_color(i)
                
                # Draw main vine body
                thickness = max(1, int(vine.thickness))
                try:
                    pygame.draw.line(surface, color, start_pos, end_pos, thickness)
                except:
                    pass
                
                # Bio-luminescent glow
                if self.enable_bio_glow and vine.bio_luminescence > 0.1:
                    glow_alpha = int(vine.bio_luminescence * 100)
                    glow_color = (*self.bio_glow_color, glow_alpha)
                    
                    # Create glow effect
                    glow_surface = pygame.Surface((thickness * 4, thickness * 4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, glow_color, 
                                     (thickness * 2, thickness * 2), thickness * 2)
                    
                    surface.blit(glow_surface, (end_pos[0] - thickness * 2, 
                                              end_pos[1] - thickness * 2))
            
            # Draw mechanical components (gears and joints)
            for gear in vine.gears:
                self.render_gear(surface, gear, vine.energy_level)
            
            # Draw data flow
            if vine.vine_type in ['neural', 'fiber_optic']:
                for packet in vine.data_flow:
                    self.render_data_packet(surface, vine, packet)
    
    def render_gear(self, surface: pygame.Surface, gear: dict, energy_level: float):
        """Render a mechanical gear"""
        pos = (int(gear['x']), int(gear['y']))
        size = int(gear['size'])
        
        # Gear color based on energy
        base_brightness = 120 + int(energy_level * 100)
        gear_color = (base_brightness, base_brightness, base_brightness + 20)
        
        try:
            # Draw gear body
            pygame.draw.circle(surface, gear_color, pos, size)
            
            # Draw gear teeth
            teeth_count = 8
            for i in range(teeth_count):
                angle = gear['rotation'] + (360 / teeth_count) * i
                tooth_angle = math.radians(angle)
                
                inner_x = pos[0] + (size - 2) * math.cos(tooth_angle)
                inner_y = pos[1] + (size - 2) * math.sin(tooth_angle)
                outer_x = pos[0] + (size + 2) * math.cos(tooth_angle)
                outer_y = pos[1] + (size + 2) * math.sin(tooth_angle)
                
                pygame.draw.line(surface, gear_color, 
                               (int(inner_x), int(inner_y)), 
                               (int(outer_x), int(outer_y)), 2)
            
            # Center hub
            hub_color = tuple(min(255, c + 30) for c in gear_color)
            pygame.draw.circle(surface, hub_color, pos, max(1, size // 3))
        
        except:
            pass
    
    def render_data_packet(self, surface: pygame.Surface, vine: BioMechVine, packet: dict):
        """Render a data packet flowing along a vine"""
        if packet['position'] >= len(vine.segments) - 1:
            return
        
        # Interpolate position along vine
        segment_index = int(packet['position'])
        segment_progress = packet['position'] - segment_index
        
        if segment_index + 1 < len(vine.segments):
            start_seg = vine.segments[segment_index]
            end_seg = vine.segments[segment_index + 1]
            
            x = start_seg[0] + (end_seg[0] - start_seg[0]) * segment_progress
            y = start_seg[1] + (end_seg[1] - start_seg[1]) * segment_progress
            
            # Data packet color
            packet_hue = packet['color']
            packet_color = self.hsv_to_rgb(packet_hue, 0.9, 1.0)
            
            # Draw packet
            pos = (int(x), int(y))
            size = max(1, int(packet['size']))
            
            try:
                pygame.draw.circle(surface, packet_color, pos, size)
                
                # Glow effect
                glow_color = (*packet_color, int(packet['intensity'] * 150))
                glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (size * 2, size * 2), size * 2)
                surface.blit(glow_surface, (pos[0] - size * 2, pos[1] - size * 2))
            
            except:
                pass
    
    def render_flowers(self, surface: pygame.Surface):
        """Render mechanical flowers"""
        for flower in self.flowers:
            pos = (int(flower.x), int(flower.y))
            
            # Draw petals
            for i in range(flower.petal_count):
                petal_angle = (360 / flower.petal_count) * i + flower.servo_angle
                petal_rad = math.radians(petal_angle)
                
                # Petal extends based on bloom state
                petal_length = flower.petal_length * flower.bloom_state
                
                petal_end_x = flower.x + petal_length * math.cos(petal_rad)
                petal_end_y = flower.y + petal_length * math.sin(petal_rad)
                
                # Petal color
                petal_color = self.hsv_to_rgb(flower.hue, 0.8, 0.9)
                
                # Bio-pulse affects petal brightness
                pulse_factor = 1 + flower.bio_pulse * 0.3
                enhanced_color = tuple(min(255, int(c * pulse_factor)) for c in petal_color)
                
                try:
                    # Draw petal as line with thickness
                    thickness = max(1, int(3 * flower.bloom_state))
                    pygame.draw.line(surface, enhanced_color, pos, 
                                   (int(petal_end_x), int(petal_end_y)), thickness)
                    
                    # Petal tip (gear-like)
                    tip_size = max(1, int(2 * flower.bloom_state))
                    pygame.draw.circle(surface, self.metal_color, 
                                     (int(petal_end_x), int(petal_end_y)), tip_size)
                
                except:
                    pass
            
            # Draw flower center (main gear)
            center_size = int(flower.center_size)
            center_color = self.hsv_to_rgb(flower.hue, 0.6, 0.7)
            
            try:
                pygame.draw.circle(surface, center_color, pos, center_size)
                
                # Center gear details
                gear_center = {
                    'x': flower.x,
                    'y': flower.y,
                    'size': center_size,
                    'rotation': flower.gear_rotation,
                    'type': 'gear'
                }
                self.render_gear(surface, gear_center, flower.bio_pulse)
            
            except:
                pass
    
    def render_data_network(self, surface: pygame.Surface):
        """Render data network connections between components"""
        if self.data_network_activity < 0.2:
            return
        
        # Draw connections between nearby flowers and vine tips
        components = []
        
        # Add flower positions
        for flower in self.flowers:
            components.append((flower.x, flower.y, 'flower'))
        
        # Add vine tip positions
        for vine in self.vines:
            if vine.segments and vine.vine_type in ['neural', 'fiber_optic']:
                tip_x, tip_y = vine.segments[-1]
                components.append((tip_x, tip_y, 'vine'))
        
        # Draw connections
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                distance = math.sqrt((comp1[0] - comp2[0])**2 + (comp1[1] - comp2[1])**2)
                
                if distance < 100:  # Only connect nearby components
                    connection_strength = 1 - (distance / 100)
                    alpha = int(connection_strength * self.data_network_activity * 100)
                    
                    if alpha > 10:
                        connection_color = (*self.bio_glow_color, alpha)
                        
                        # Draw connection line
                        try:
                            line_surface = pygame.Surface((int(distance) + 20, 20), pygame.SRCALPHA)
                            pygame.draw.line(line_surface, connection_color, 
                                           (10, 10), (int(distance) + 10, 10), 1)
                            
                            # Rotate and position the line
                            angle = math.atan2(comp2[1] - comp1[1], comp2[0] - comp1[0])
                            rotated_surface = pygame.transform.rotate(line_surface, 
                                                                    -math.degrees(angle))
                            
                            surface.blit(rotated_surface, 
                                       (comp1[0] - 10, comp1[1] - 10))
                        
                        except:
                            pass
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
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
            if name == 'max_vines':
                self.max_vines = max(2, min(30, int(value)))
                self.parameters[name] = self.max_vines
            
            elif name == 'max_flowers':
                self.max_flowers = max(1, min(20, int(value)))
                self.parameters[name] = self.max_flowers
    
    def reset(self):
        """Reset plugin to initial state"""
        # Clear all garden components
        self.vines.clear()
        self.flowers.clear()
        self.data_streams.clear()
        
        # Reset state
        self.ecosystem_energy = 0.5
        self.data_network_activity = 0
        self.time_offset = 0
        self.last_growth_time = 0
        
        # Plant new seeds
        self.plant_initial_seeds()
        
        print(f"Reset {self.name} plugin")
    
    def get_info(self) -> dict:
        """Get plugin information"""
        total_segments = sum(len(vine.segments) for vine in self.vines)
        bloomed_flowers = sum(1 for flower in self.flowers if flower.bloom_state > 0.5)
        
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'vine_count': len(self.vines),
            'flower_count': len(self.flowers),
            'total_vine_segments': total_segments,
            'bloomed_flowers': bloomed_flowers,
            'ecosystem_energy': f"{self.ecosystem_energy:.2f}",
            'data_network_activity': f"{self.data_network_activity:.2f}"
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Bio-Mechanical Garden Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Bio-Mechanical Garden Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = BioMechGardenPlugin((800, 600))
    
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
                    plugin.set_parameter('max_vines', plugin.max_vines + 1)
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('max_vines', max(2, plugin.max_vines - 1))
        
        # Simulate organic growth audio
        fake_audio = {
            'amplitude': 0.5 + 0.3 * math.sin(current_time * 1.5),
            'beat_detected': (current_time % 2.5) < 0.2,  # Slower organic rhythm
            'dominant_frequency': 220 + 180 * math.sin(current_time * 0.6),  # Lower, earthier tones
            'frequency_bands': {
                'bass': 0.4 + 0.3 * math.sin(current_time * 0.8),   # Growth energy
                'mid': 0.5 + 0.4 * math.sin(current_time * 1.2),    # Bio-luminescence
                'treble': 0.3 + 0.2 * math.sin(current_time * 1.8)  # Data flow
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
                f"Bio-Mechanical Garden - Vines: {len(plugin.vines)} | Flowers: {len(plugin.flowers)}",
                f"Ecosystem Energy: {plugin.ecosystem_energy:.2f} | Data Activity: {plugin.data_network_activity:.2f}",
                "UP/DOWN: Vine count | SPACE: Reset"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (200, 255, 200))  # Light green text
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Bio-Mechanical Garden plugin test completed")
