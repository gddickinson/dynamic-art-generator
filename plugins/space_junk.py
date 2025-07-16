#!/usr/bin/env python3
"""
Space Junk Plugin for Dynamic Art Generator
3D rotating cubes in space with audio responsiveness

Adapted from Ira Greenberg's "Space Junk" Processing sketch
Author: Claude Assistant
Version: 1.0 - 3D Audio Responsive Edition
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


class Vector3D:
    """3D vector class for 3D transformations"""
    
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def rotate_x(self, angle):
        """Rotate around X axis"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        y = self.y * cos_a - self.z * sin_a
        z = self.y * sin_a + self.z * cos_a
        return Vector3D(self.x, y, z)
    
    def rotate_y(self, angle):
        """Rotate around Y axis"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a + self.z * sin_a
        z = -self.x * sin_a + self.z * cos_a
        return Vector3D(x, self.y, z)
    
    def rotate_z(self, angle):
        """Rotate around Z axis"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        return Vector3D(x, y, self.z)
    
    def project(self, screen_width, screen_height, fov=500):
        """Project 3D point to 2D screen coordinates"""
        if self.z == 0:
            self.z = 0.001  # Avoid division by zero
        
        # Perspective projection
        factor = fov / (fov + self.z)
        x2d = self.x * factor + screen_width / 2
        y2d = self.y * factor + screen_height / 2
        
        return (int(x2d), int(y2d)), factor


class Cube3D:
    """3D Cube with audio-responsive properties"""
    
    def __init__(self, w, h, d, x, y, z):
        self.size = Vector3D(w, h, d)
        self.position = Vector3D(x, y, z)
        self.rotation = Vector3D(0, 0, 0)
        self.rotation_speed = Vector3D(
            random.uniform(0.5, 2.0),
            random.uniform(0.5, 2.0), 
            random.uniform(0.5, 2.0)
        )
        
        # Audio response properties
        self.audio_scale = 1.0
        self.color_shift = random.uniform(0, 360)
        self.energy = 0.0
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        
        # Create the 8 vertices of the cube
        self.vertices = [
            Vector3D(-w/2, -h/2, -d/2),  # Front bottom left
            Vector3D( w/2, -h/2, -d/2),  # Front bottom right
            Vector3D( w/2,  h/2, -d/2),  # Front top right
            Vector3D(-w/2,  h/2, -d/2),  # Front top left
            Vector3D(-w/2, -h/2,  d/2),  # Back bottom left
            Vector3D( w/2, -h/2,  d/2),  # Back bottom right
            Vector3D( w/2,  h/2,  d/2),  # Back top right
            Vector3D(-w/2,  h/2,  d/2),  # Back top left
        ]
        
        # Define the 6 faces of the cube (indices into vertices array)
        self.faces = [
            [0, 1, 2, 3],  # Front face
            [5, 4, 7, 6],  # Back face
            [4, 0, 3, 7],  # Left face
            [1, 5, 6, 2],  # Right face
            [3, 2, 6, 7],  # Top face
            [4, 5, 1, 0],  # Bottom face
        ]
        
        # Face colors (will be modified by lighting)
        self.base_colors = [
            (255, 100, 100),  # Front - Red
            (100, 255, 100),  # Back - Green
            (100, 100, 255),  # Left - Blue
            (255, 255, 100),  # Right - Yellow
            (255, 100, 255),  # Top - Magenta
            (100, 255, 255),  # Bottom - Cyan
        ]
    
    def update(self, dt, audio_features, global_rotation):
        """Update cube rotation and audio response"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update energy for audio response
        self.energy += amplitude * 10 * dt
        self.energy *= 0.95  # Decay
        
        # Beat response
        if beat:
            self.energy += amplitude * 20
            # Add random impulse to rotation
            self.rotation_speed.x += random.uniform(-1, 1) * amplitude
            self.rotation_speed.y += random.uniform(-1, 1) * amplitude
            self.rotation_speed.z += random.uniform(-1, 1) * amplitude
        
        # Audio-responsive rotation speed
        speed_multiplier = 1 + amplitude * 2 + self.energy * 0.1
        
        # Update individual cube rotation
        self.rotation.x += self.rotation_speed.x * dt * speed_multiplier
        self.rotation.y += self.rotation_speed.y * dt * speed_multiplier
        self.rotation.z += self.rotation_speed.z * dt * speed_multiplier
        
        # Audio-responsive scaling
        bass_scale = 1 + freq_bands.get('bass', 0) * 0.5
        pulse_scale = 1 + 0.2 * math.sin(self.pulse_phase + time.time() * 5)
        self.audio_scale = bass_scale * pulse_scale
        
        # Color shifting based on frequency
        if frequency > 0:
            self.color_shift += frequency * 0.01 * dt
        self.color_shift += amplitude * 100 * dt
        self.color_shift %= 360
        
        # Damping for rotation speed
        self.rotation_speed.x *= 0.99
        self.rotation_speed.y *= 0.99
        self.rotation_speed.z *= 0.99
    
    def get_transformed_vertices(self, global_rotation):
        """Get vertices transformed by rotations and position"""
        transformed = []
        
        for vertex in self.vertices:
            # Apply cube scaling
            scaled = Vector3D(
                vertex.x * self.audio_scale,
                vertex.y * self.audio_scale,
                vertex.z * self.audio_scale
            )
            
            # Apply individual cube rotation
            rotated = scaled.rotate_x(self.rotation.x)
            rotated = rotated.rotate_y(self.rotation.y)
            rotated = rotated.rotate_z(self.rotation.z)
            
            # Apply global scene rotation
            rotated = rotated.rotate_x(global_rotation.x)
            rotated = rotated.rotate_y(global_rotation.y)
            
            # Translate to cube position
            final = Vector3D(
                rotated.x + self.position.x,
                rotated.y + self.position.y,
                rotated.z + self.position.z
            )
            
            transformed.append(final)
        
        return transformed
    
    def get_face_color(self, face_index, lighting, audio_features):
        """Calculate face color based on lighting and audio"""
        base_color = self.base_colors[face_index]
        
        # Apply audio color shift
        h = (self.color_shift + face_index * 60) % 360
        audio_color = self.hsv_to_rgb(h, 0.8, 0.9)
        
        # Blend base color with audio color
        blend_factor = 0.7
        final_color = (
            int(base_color[0] * (1 - blend_factor) + audio_color[0] * blend_factor),
            int(base_color[1] * (1 - blend_factor) + audio_color[1] * blend_factor),
            int(base_color[2] * (1 - blend_factor) + audio_color[2] * blend_factor)
        )
        
        # Apply lighting (simple brightness modification)
        brightness = max(0.3, min(1.5, lighting + self.energy * 0.1))
        final_color = (
            min(255, int(final_color[0] * brightness)),
            min(255, int(final_color[1] * brightness)),
            min(255, int(final_color[2] * brightness))
        )
        
        return final_color
    
    def hsv_to_rgb(self, h, s, v):
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
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


class SpaceJunkPlugin(ArtPlugin):
    """
    Space Junk Plugin - 3D rotating cubes in space
    
    Creates a field of rotating 3D cubes that respond to audio input.
    Based on Ira Greenberg's classic "Space Junk" Processing sketch,
    adapted for pygame with audio responsiveness.
    """
    
    # Plugin identification
    PLUGIN_NAME = "Space Junk"
    PLUGIN_DESCRIPTION = "3D rotating cubes floating in audio-responsive space"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant (adapted from Ira Greenberg)"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # 3D scene properties
        self.cubes = []
        self.cube_count = 150
        self.global_rotation = Vector3D(0, 0, 0)
        self.zoom = -200
        self.fov = 500
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.rotation_speed = 1.0
        self.zoom_sensitivity = 1.0
        self.beat_zoom_boost = 0
        
        # Lighting simulation
        self.ambient_light = 0.7
        self.light_positions = [
            Vector3D(65, 60, 100),
            Vector3D(-65, -60, -150)
        ]
        self.light_colors = [
            (51, 102, 255),   # Blue light
            (200, 40, 60)     # Red light
        ]
        
        # Visual effects
        self.enable_depth_sorting = True
        self.enable_lighting = True
        self.enable_trails = False
        self.trail_alpha = 0.1
        
        # Performance settings
        self.cube_size_range = (5, 15)
        self.position_range = 140
        
        # Store parameters for GUI
        self.parameters = {
            'cube_count': self.cube_count,
            'audio_sensitivity': self.audio_sensitivity,
            'rotation_speed': self.rotation_speed,
            'zoom_sensitivity': self.zoom_sensitivity,
            'ambient_light': self.ambient_light,
            'enable_depth_sorting': self.enable_depth_sorting,
            'enable_lighting': self.enable_lighting,
            'enable_trails': self.enable_trails,
            'position_range': self.position_range
        }
        
        # Initialize cubes
        self.create_cubes()
        
        # Animation state
        self.time_offset = 0
        self.last_surface = None
    
    def create_cubes(self):
        """Create the initial set of cubes"""
        self.cubes.clear()
        
        for _ in range(int(self.cube_count)):
            # Random cube size
            size = random.uniform(self.cube_size_range[0], self.cube_size_range[1])
            w = random.uniform(size * 0.8, size * 1.2)
            h = random.uniform(size * 0.8, size * 1.2)
            d = random.uniform(size * 0.8, size * 1.2)
            
            # Random position in 3D space
            x = random.uniform(-self.position_range, self.position_range)
            y = random.uniform(-self.position_range, self.position_range)
            z = random.uniform(-self.position_range, self.position_range)
            
            cube = Cube3D(w, h, d, x, y, z)
            self.cubes.append(cube)
    
    def update(self, audio_features: dict, dt: float):
        """Update the 3D scene"""
        self.time_offset += dt
        
        # Extract audio features
        amplitude = audio_features.get('amplitude', 0)
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Update global rotation
        base_rotation_speed = self.rotation_speed * 20 * dt  # degrees per frame
        audio_rotation_boost = amplitude * self.audio_sensitivity * 50 * dt
        
        # Different axes respond to different frequency bands
        self.global_rotation.y += base_rotation_speed + freq_bands.get('bass', 0) * 30 * dt
        self.global_rotation.x += base_rotation_speed * 0.7 + freq_bands.get('treble', 0) * 20 * dt
        
        # Beat response for zoom
        if beat_detected:
            self.beat_zoom_boost = amplitude * 100 * self.zoom_sensitivity
        else:
            self.beat_zoom_boost *= 0.9
        
        # Update zoom based on audio (like mouse control in original)
        target_zoom = -200 + amplitude * 200 * self.zoom_sensitivity + self.beat_zoom_boost
        self.zoom += (target_zoom - self.zoom) * dt * 2
        
        # Update individual cubes
        for cube in self.cubes:
            cube.update(dt, audio_features, self.global_rotation)
        
        # Spawn new cubes on strong beats (keeping count constant)
        if beat_detected and amplitude > 0.5:
            # Replace a random cube with a new one
            if self.cubes:
                idx = random.randint(0, len(self.cubes) - 1)
                size = random.uniform(self.cube_size_range[0], self.cube_size_range[1])
                w = random.uniform(size * 0.8, size * 1.2)
                h = random.uniform(size * 0.8, size * 1.2)
                d = random.uniform(size * 0.8, size * 1.2)
                
                x = random.uniform(-self.position_range, self.position_range)
                y = random.uniform(-self.position_range, self.position_range)
                z = random.uniform(-self.position_range, self.position_range)
                
                self.cubes[idx] = Cube3D(w, h, d, x, y, z)
    
    def render(self, surface: pygame.Surface):
        """Render the 3D scene"""
        # Apply trail effect if enabled
        if self.enable_trails and self.last_surface:
            # Create a faded version of the last frame
            trail_surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)
            trail_surface.fill((0, 0, 0, int(255 * self.trail_alpha)))
            surface.blit(self.last_surface, (0, 0))
            surface.blit(trail_surface, (0, 0))
        
        # Prepare for 3D rendering
        cube_data = []
        
        # Transform all cubes and calculate depth
        for cube in self.cubes:
            transformed_vertices = cube.get_transformed_vertices(self.global_rotation)
            
            # Apply zoom (translate in Z)
            for vertex in transformed_vertices:
                vertex.z += self.zoom
            
            # Calculate average Z for depth sorting
            avg_z = sum(v.z for v in transformed_vertices) / len(transformed_vertices)
            
            cube_data.append((cube, transformed_vertices, avg_z))
        
        # Sort by depth (back to front) for proper rendering
        if self.enable_depth_sorting:
            cube_data.sort(key=lambda x: x[2], reverse=True)
        
        # Render each cube
        for cube, vertices, avg_z in cube_data:
            self.render_cube(surface, cube, vertices)
        
        # Store this frame for trails
        if self.enable_trails:
            self.last_surface = surface.copy()
    
    def render_cube(self, surface, cube, vertices):
        """Render a single cube"""
        # Project 3D vertices to 2D screen coordinates
        projected_vertices = []
        visible = True
        
        for vertex in vertices:
            try:
                (x2d, y2d), scale_factor = vertex.project(
                    self.surface_size[0], 
                    self.surface_size[1], 
                    self.fov
                )
                
                # Check if vertex is on screen
                if (0 <= x2d <= self.surface_size[0] and 
                    0 <= y2d <= self.surface_size[1]):
                    projected_vertices.append((x2d, y2d))
                else:
                    projected_vertices.append((x2d, y2d))  # Keep for partial visibility
            except:
                visible = False
                break
        
        if not visible or len(projected_vertices) != 8:
            return
        
        # Calculate lighting (simplified)
        lighting = self.ambient_light
        if self.enable_lighting:
            # Simple distance-based lighting
            distance = abs(vertices[0].z)
            lighting += max(0, 1.0 - distance / 500)
        
        # Render faces (only visible ones)
        face_depths = []
        
        for face_idx, face_indices in enumerate(cube.faces):
            # Get face vertices
            face_verts_3d = [vertices[i] for i in face_indices]
            face_verts_2d = [projected_vertices[i] for i in face_indices]
            
            # Calculate face depth (average Z)
            face_z = sum(v.z for v in face_verts_3d) / len(face_verts_3d)
            
            # Simple backface culling (check if face is facing away)
            # This is a simplified version - just use Z coordinate
            if face_z > -50:  # Face is reasonably close
                face_depths.append((face_idx, face_verts_2d, face_z))
        
        # Sort faces by depth (back to front)
        face_depths.sort(key=lambda x: x[2], reverse=True)
        
        # Draw faces
        for face_idx, face_verts_2d, face_z in face_depths:
            try:
                # Get face color
                face_color = cube.get_face_color(face_idx, lighting, {
                    'amplitude': 0,  # Will be passed in properly in actual use
                    'frequency_bands': {'bass': 0, 'mid': 0, 'treble': 0}
                })
                
                # Draw face as polygon
                if len(face_verts_2d) >= 3:
                    pygame.draw.polygon(surface, face_color, face_verts_2d)
                    
                    # Optional: draw wireframe
                    if cube.energy > 5:  # High energy = wireframe
                        pygame.draw.polygon(surface, (255, 255, 255), face_verts_2d, 1)
                        
            except Exception as e:
                # Skip problematic faces
                continue
    
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
            if name == 'cube_count':
                new_count = max(10, min(500, int(value)))
                if new_count != len(self.cubes):
                    self.cube_count = new_count
                    self.create_cubes()
                    self.parameters[name] = new_count
            
            elif name == 'position_range':
                self.position_range = max(50, min(300, float(value)))
                self.parameters[name] = self.position_range
            
            elif name == 'ambient_light':
                self.ambient_light = max(0, min(2, float(value)))
                self.parameters[name] = self.ambient_light
    
    def reset(self):
        """Reset plugin to initial state"""
        # Reset rotation
        self.global_rotation = Vector3D(0, 0, 0)
        self.zoom = -200
        self.beat_zoom_boost = 0
        
        # Recreate cubes
        self.create_cubes()
        
        # Reset animation state
        self.time_offset = 0
        self.last_surface = None
        
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
            'cube_count': len(self.cubes),
            'current_zoom': self.zoom,
            'global_rotation': f"({self.global_rotation.x:.1f}, {self.global_rotation.y:.1f})"
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Space Junk Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Space Junk Plugin Test")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = SpaceJunkPlugin((800, 600))
    
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
                    plugin.set_parameter('cube_count', min(500, plugin.cube_count + 10))
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('cube_count', max(10, plugin.cube_count - 10))
                elif event.key == pygame.K_t:
                    plugin.set_parameter('enable_trails', not plugin.enable_trails)
        
        # Simulate audio features
        fake_audio = {
            'amplitude': 0.4 + 0.3 * math.sin(current_time * 1.5),
            'beat_detected': (current_time % 2.5) < 0.2,
            'dominant_frequency': 440 + 200 * math.sin(current_time * 0.4),
            'frequency_bands': {
                'bass': 0.6 + 0.4 * math.sin(current_time * 0.8),
                'mid': 0.3 + 0.2 * math.sin(current_time * 1.2),
                'treble': 0.2 + 0.3 * math.sin(current_time * 1.6)
            }
        }
        
        # Update plugin
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((0, 0, 0))  # Space background
        plugin.render(screen)
        
        # Display info
        try:
            font = pygame.font.Font(None, 24)
            info_lines = [
                f"Space Junk - Cubes: {len(plugin.cubes)}",
                f"UP/DOWN: Change cube count",
                f"T: Toggle trails ({plugin.enable_trails})",
                "SPACE: Reset"
            ]
            
            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Space Junk plugin test completed")
