#!/usr/bin/env python3
"""
Dynamic Art Generator - Main Application (Updated with Canvas Fixes)
A plugin-based audiovisual art generation system

Author: Claude Assistant
Version: 1.1 - Canvas Display Fixed
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pygame
import numpy as np
import threading
import time
import sys
import traceback
from typing import Dict, List, Optional, Callable
import json
import os
from abc import ABC, abstractmethod

# Audio processing imports
try:
    import pyaudio
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio libraries not available. Install with: pip install pyaudio librosa")

# Import utilities
try:
    from utils.audio_utils import AudioAnalyzer, DrumMachine, AudioSmoother
    from utils.math_utils import Vector2D, ColorUtils, GeometryUtils
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("Utilities not available - using basic implementations")

# PIL import for canvas conversion
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - canvas display will be limited")

class AudioProcessor:
    """Handles real-time audio input and analysis"""

    def __init__(self, sample_rate=44100, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_data = np.zeros(chunk_size)
        self.beat_detected = False
        self.amplitude = 0.0
        self.frequency = 0.0

        if AUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
                self.setup_stream()
            except Exception as e:
                print(f"Audio setup failed: {e}")
                self.audio = None

    def setup_stream(self):
        """Initialize audio stream"""
        if not self.audio:
            return

        try:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
        except Exception as e:
            print(f"Stream setup failed: {e}")
            self.stream = None

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Process incoming audio data"""
        try:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            self.audio_data = audio_data

            # Calculate amplitude
            self.amplitude = np.sqrt(np.mean(audio_data**2))

            # Simple beat detection (amplitude threshold)
            self.beat_detected = self.amplitude > 0.1

            # Frequency analysis (simplified)
            if len(audio_data) > 0:
                fft = np.fft.rfft(audio_data)
                freqs = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)
                peak_freq_idx = np.argmax(np.abs(fft))
                self.frequency = freqs[peak_freq_idx]

        except Exception as e:
            print(f"Audio processing error: {e}")

        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        """Start audio recording"""
        if self.stream:
            self.stream.start_stream()
            self.is_recording = True

    def stop_recording(self):
        """Stop audio recording"""
        if self.stream:
            self.stream.stop_stream()
            self.is_recording = False

    def get_audio_features(self):
        """Get current audio features"""
        return {
            'amplitude': self.amplitude,
            'frequency': self.frequency,
            'beat_detected': self.beat_detected,
            'raw_data': self.audio_data.copy()
        }

    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()


class ArtPlugin(ABC):
    """Base class for all art plugins"""

    def __init__(self, name: str, surface_size: tuple):
        self.name = name
        self.surface_size = surface_size
        self.surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        self.is_active = False
        self.parameters = {}
        self.last_update = time.time()

    @abstractmethod
    def update(self, audio_features: dict, dt: float):
        """Update the plugin state based on audio and time"""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        """Render the plugin to the given surface"""
        pass

    @abstractmethod
    def get_parameters(self) -> dict:
        """Return configurable parameters"""
        pass

    @abstractmethod
    def set_parameter(self, name: str, value):
        """Set a parameter value"""
        pass

    def reset(self):
        """Reset plugin state"""
        self.surface.fill((0, 0, 0, 0))


class PendulumPlugin(ArtPlugin):
    """Pendulum art plugin - creates paint-can-like effects"""

    def __init__(self, surface_size: tuple):
        super().__init__("Pendulum", surface_size)

        # Physics parameters
        self.x = surface_size[0] / 2
        self.y = surface_size[1] / 2
        self.vx = 0
        self.vy = 0

        # Pendulum properties
        self.length = 200
        self.gravity = 9.81
        self.damping = 0.999
        self.ellipse_a = 150  # Semi-major axis
        self.ellipse_b = 100  # Semi-minor axis

        # Visual properties
        self.trail_points = []
        self.max_trail_length = 500
        self.color_hue = 0
        self.line_width = 2

        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_impulse = 0

        self.parameters = {
            'gravity': self.gravity,
            'damping': self.damping,
            'ellipse_a': self.ellipse_a,
            'ellipse_b': self.ellipse_b,
            'audio_sensitivity': self.audio_sensitivity,
            'trail_length': self.max_trail_length,
            'line_width': self.line_width
        }

    def update(self, audio_features: dict, dt: float):
        """Update pendulum physics and audio response"""
        # Audio influence
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)

        if beat:
            self.beat_impulse = min(self.beat_impulse + amplitude * 10, 5.0)

        # Pendulum physics with elliptical constraint
        center_x = self.surface_size[0] / 2
        center_y = self.surface_size[1] / 2

        # Calculate forces
        dx = self.x - center_x
        dy = self.y - center_y

        # Elliptical restoring force
        force_x = -dx * (self.gravity / self.ellipse_a)
        force_y = -dy * (self.gravity / self.ellipse_b)

        # Add audio influence
        force_x += np.sin(time.time() * 2) * amplitude * self.audio_sensitivity
        force_y += np.cos(time.time() * 3) * amplitude * self.audio_sensitivity

        # Beat impulse
        if self.beat_impulse > 0:
            force_x += np.random.uniform(-1, 1) * self.beat_impulse
            force_y += np.random.uniform(-1, 1) * self.beat_impulse
            self.beat_impulse *= 0.9

        # Update velocity and position
        self.vx += force_x * dt
        self.vy += force_y * dt

        # Apply damping
        self.vx *= self.damping
        self.vy *= self.damping

        # Update position
        self.x += self.vx * dt * 100
        self.y += self.vy * dt * 100

        # Keep within bounds
        self.x = max(50, min(self.surface_size[0] - 50, self.x))
        self.y = max(50, min(self.surface_size[1] - 50, self.y))

        # Add to trail
        self.trail_points.append((int(self.x), int(self.y)))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)

        # Update color
        self.color_hue = (self.color_hue + amplitude * 50) % 360

    def render(self, surface: pygame.Surface):
        """Render pendulum trail"""
        if len(self.trail_points) < 2:
            return

        # Draw trail with fading effect
        for i in range(1, len(self.trail_points)):
            alpha = (i / len(self.trail_points)) * 255
            progress = i / len(self.trail_points)

            # HSV to RGB conversion for color cycling
            hue = (self.color_hue + progress * 60) % 360
            color = self.hsv_to_rgb(hue, 0.8, 0.9)

            # Draw line segment
            if i > 0:
                try:
                    pygame.draw.line(surface, color,
                                   self.trail_points[i-1],
                                   self.trail_points[i],
                                   max(1, int(self.line_width * (alpha / 255))))
                except:
                    pass

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
        h = h / 360.0
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c

        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    def get_parameters(self) -> dict:
        return self.parameters

    def set_parameter(self, name: str, value):
        if name in self.parameters:
            self.parameters[name] = value
            setattr(self, name, value)

    def reset(self):
        super().reset()
        self.trail_points.clear()
        self.x = self.surface_size[0] / 2
        self.y = self.surface_size[1] / 2
        self.vx = 0
        self.vy = 0


class ParticleSystem:
    """Individual particle for the particle plugin"""

    def __init__(self, x, y, vx, vy, life, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = np.random.uniform(1, 3)

    def update(self, dt, forces):
        """Update particle physics"""
        # Apply forces
        self.vx += forces[0] * dt
        self.vy += forces[1] * dt

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Decay
        self.life -= dt

        # Fade alpha based on life
        alpha = max(0, self.life / self.max_life)
        self.color = (*self.color[:3], int(alpha * 255))

    def is_alive(self):
        return self.life > 0


class ParticlePlugin(ArtPlugin):
    """Particle system plugin - creates sand/smoke-like effects"""

    def __init__(self, surface_size: tuple):
        super().__init__("Particles", surface_size)

        self.particles = []
        self.max_particles = 1000
        self.spawn_rate = 50
        self.spawn_timer = 0

        # Shape properties
        self.shape_type = "circle"  # circle, square, triangle
        self.shape_center = (surface_size[0] / 2, surface_size[1] / 2)
        self.shape_size = 100
        self.shape_rotation = 0

        # Particle properties
        self.particle_life = 3.0
        self.particle_speed = 50
        self.gravity = 20
        self.wind = 0

        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.beat_burst = 0

        # Color cycling
        self.color_hue = 0
        self.color_cycle_speed = 30

        self.parameters = {
            'max_particles': self.max_particles,
            'spawn_rate': self.spawn_rate,
            'particle_life': self.particle_life,
            'particle_speed': self.particle_speed,
            'gravity': self.gravity,
            'wind': self.wind,
            'audio_sensitivity': self.audio_sensitivity,
            'shape_size': self.shape_size,
            'color_cycle_speed': self.color_cycle_speed
        }

    def update(self, audio_features: dict, dt: float):
        """Update particle system"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('frequency', 0)

        # Update color
        self.color_hue = (self.color_hue + self.color_cycle_speed * dt) % 360

        # Beat response
        if beat:
            self.beat_burst = min(self.beat_burst + amplitude * 20, 10.0)

        # Shape morphing based on frequency
        self.shape_size = 100 + frequency * 0.1
        self.shape_rotation += amplitude * 100 * dt

        # Update shape center (moves with audio)
        center_x = self.surface_size[0] / 2 + np.sin(time.time() * 2) * amplitude * 50
        center_y = self.surface_size[1] / 2 + np.cos(time.time() * 3) * amplitude * 50
        self.shape_center = (center_x, center_y)

        # Spawn new particles
        self.spawn_timer += dt
        spawn_interval = 1.0 / (self.spawn_rate + amplitude * 100)

        if self.spawn_timer >= spawn_interval and len(self.particles) < self.max_particles:
            self.spawn_timer = 0

            # Spawn burst on beat
            spawn_count = 1
            if self.beat_burst > 0:
                spawn_count = int(self.beat_burst)
                self.beat_burst *= 0.8

            for _ in range(spawn_count):
                self.spawn_particle()

        # Update existing particles
        forces = self.calculate_forces(amplitude)

        for particle in self.particles[:]:
            particle.update(dt, forces)

            # Remove dead particles
            if not particle.is_alive():
                self.particles.remove(particle)

    def spawn_particle(self):
        """Spawn a new particle around the shape"""
        # Generate position around shape
        angle = np.random.uniform(0, 2 * np.pi)
        radius = np.random.uniform(0, self.shape_size)

        x = self.shape_center[0] + radius * np.cos(angle)
        y = self.shape_center[1] + radius * np.sin(angle)

        # Generate velocity
        vx = np.random.uniform(-self.particle_speed, self.particle_speed)
        vy = np.random.uniform(-self.particle_speed, self.particle_speed)

        # Generate color
        hue = (self.color_hue + np.random.uniform(-30, 30)) % 360
        color = self.hsv_to_rgb(hue, 0.7, 0.9)

        # Create particle
        particle = ParticleSystem(x, y, vx, vy, self.particle_life, color)
        self.particles.append(particle)

    def calculate_forces(self, amplitude):
        """Calculate forces affecting particles"""
        # Gravity
        force_x = self.wind + np.sin(time.time()) * amplitude * 10
        force_y = self.gravity + amplitude * 50

        return (force_x, force_y)

    def render(self, surface: pygame.Surface):
        """Render particle system"""
        # Draw shape outline
        self.draw_shape(surface)

        # Draw particles
        for particle in self.particles:
            if particle.is_alive():
                pos = (int(particle.x), int(particle.y))
                size = max(1, int(particle.size))

                # Draw particle with alpha
                if len(particle.color) == 4:
                    temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surface, particle.color, (size, size), size)
                    surface.blit(temp_surface, (pos[0] - size, pos[1] - size))
                else:
                    pygame.draw.circle(surface, particle.color, pos, size)

    def draw_shape(self, surface):
        """Draw the shape that particles emanate from"""
        center = (int(self.shape_center[0]), int(self.shape_center[1]))
        size = int(self.shape_size)

        # Shape outline color
        outline_color = self.hsv_to_rgb(self.color_hue, 0.5, 0.5)

        if self.shape_type == "circle":
            pygame.draw.circle(surface, outline_color, center, size, 2)
        elif self.shape_type == "square":
            rect = pygame.Rect(center[0] - size, center[1] - size, size * 2, size * 2)
            pygame.draw.rect(surface, outline_color, rect, 2)

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
        h = h / 360.0
        c = v * s
        x = c * (1 - abs((h / 60.0) % 2 - 1))
        m = v - c

        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

    def get_parameters(self) -> dict:
        return self.parameters

    def set_parameter(self, name: str, value):
        if name in self.parameters:
            self.parameters[name] = value
            setattr(self, name, value)

    def reset(self):
        super().reset()
        self.particles.clear()


class DynamicArtGenerator:
    """Main application class"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dynamic Art Generator")
        self.root.geometry("1200x800")

        # Core components
        self.audio_processor = AudioProcessor()
        self.plugins = {}
        self.current_plugin = None
        self.is_running = False

        # Pygame setup
        pygame.init()
        self.canvas_size = (800, 600)
        self.pygame_surface = pygame.Surface(self.canvas_size)

        # GUI setup
        self.setup_gui()
        self.setup_plugins()

        # Message console
        self.log_message("Dynamic Art Generator initialized")
        self.log_message(f"Audio available: {AUDIO_AVAILABLE}")
        self.log_message(f"PIL available: {PIL_AVAILABLE}")

        # Start main loop
        self.update_loop()

    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - controls
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        # Plugin selection
        ttk.Label(left_frame, text="Art Plugin:").pack(pady=(0, 5))
        self.plugin_var = tk.StringVar()
        self.plugin_combo = ttk.Combobox(left_frame, textvariable=self.plugin_var,
                                        state="readonly", width=25)
        self.plugin_combo.pack(pady=(0, 10))
        self.plugin_combo.bind('<<ComboboxSelected>>', self.on_plugin_change)

        # Control buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_button = ttk.Button(button_frame, text="Start",
                                      command=self.start_generation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_button = ttk.Button(button_frame, text="Stop",
                                     command=self.stop_generation)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))

        self.reset_button = ttk.Button(button_frame, text="Reset",
                                      command=self.reset_plugin)
        self.reset_button.pack(side=tk.LEFT)

        # Audio controls
        audio_frame = ttk.LabelFrame(left_frame, text="Audio Settings")
        audio_frame.pack(fill=tk.X, pady=(0, 10))

        self.audio_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(audio_frame, text="Enable Audio Input",
                       variable=self.audio_enabled).pack(anchor=tk.W)

        # Plugin parameters (will be populated dynamically)
        self.params_frame = ttk.LabelFrame(left_frame, text="Plugin Parameters")
        self.params_frame.pack(fill=tk.X, pady=(0, 10))

        # Message console
        console_frame = ttk.LabelFrame(left_frame, text="Console")
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = scrolledtext.ScrolledText(console_frame, height=10, width=35)
        self.console_text.pack(fill=tk.BOTH, expand=True)

        # Right panel - display
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas for pygame surface
        self.canvas = tk.Canvas(right_frame, width=self.canvas_size[0],
                               height=self.canvas_size[1], bg='black')
        self.canvas.pack(expand=True)

        # Store reference to prevent garbage collection
        self.photo = None

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(right_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_plugins(self):
        """Initialize available plugins"""
        # Try to import plugins from the plugins directory
        try:
            # Look for plugin files in the plugins directory
            import os
            import importlib.util
            plugins_dir = "plugins"

            if os.path.exists(plugins_dir):
                # Check for the actual plugin files
                plugin_files = [f for f in os.listdir(plugins_dir)
                              if f.endswith('.py') and not f.startswith('__')]

                for plugin_file in plugin_files:
                    plugin_module_name = plugin_file[:-3]  # Remove .py extension

                    try:
                        # Import the plugin module dynamically
                        spec = importlib.util.spec_from_file_location(
                            plugin_module_name,
                            os.path.join(plugins_dir, plugin_file)
                        )
                        plugin_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(plugin_module)

                        # Look for plugin classes in the module
                        for attr_name in dir(plugin_module):
                            attr = getattr(plugin_module, attr_name)

                            # Check if it's a plugin class
                            if (hasattr(attr, '__bases__') and
                                any('ArtPlugin' in str(base) for base in attr.__bases__) and
                                attr_name != 'ArtPlugin'):

                                # Create plugin instance
                                plugin_instance = attr(self.canvas_size)
                                plugin_name = getattr(plugin_instance, 'name', attr_name)

                                self.plugins[plugin_name] = plugin_instance
                                print(f"✅ Loaded {plugin_name} plugin")
                                break
                        else:
                            print(f"⚠️ No valid plugin class found in {plugin_file}")

                    except Exception as e:
                        print(f"⚠️ Could not load plugin {plugin_file}: {e}")
                        import traceback
                        traceback.print_exc()

        except Exception as e:
            print(f"⚠️ Plugin loading error: {e}")

        # Fallback: create basic plugins if imports failed
        if not self.plugins:
            print("Creating fallback plugins...")
            self.plugins['Pendulum'] = PendulumPlugin(self.canvas_size)
            self.plugins['Particles'] = ParticlePlugin(self.canvas_size)

        # Populate plugin combo
        plugin_names = list(self.plugins.keys())
        self.plugin_combo['values'] = plugin_names
        if plugin_names:
            self.plugin_combo.set(plugin_names[0])
            self.current_plugin = self.plugins[plugin_names[0]]
            self.update_parameter_controls()

    def update_parameter_controls(self):
        """Update parameter controls for current plugin"""
        # Clear existing controls
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        if not self.current_plugin:
            return

        # Create controls for each parameter
        params = self.current_plugin.get_parameters()
        self.param_vars = {}

        for param_name, param_value in params.items():
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill=tk.X, pady=2)

            label = ttk.Label(frame, text=param_name.replace('_', ' ').title())
            label.pack(side=tk.LEFT)

            # Create appropriate control based on parameter type
            if isinstance(param_value, bool):
                var = tk.BooleanVar(value=param_value)
                control = ttk.Checkbutton(frame, variable=var)
            elif isinstance(param_value, (int, float)):
                var = tk.DoubleVar(value=param_value)
                control = ttk.Scale(frame, from_=0, to=param_value*2,
                                   variable=var, orient=tk.HORIZONTAL)
            else:
                var = tk.StringVar(value=str(param_value))
                control = ttk.Entry(frame, textvariable=var, width=10)

            control.pack(side=tk.RIGHT)
            self.param_vars[param_name] = var

            # Bind change event
            var.trace('w', lambda *args, name=param_name: self.on_parameter_change(name))

    def on_parameter_change(self, param_name):
        """Handle parameter changes"""
        if self.current_plugin and param_name in self.param_vars:
            value = self.param_vars[param_name].get()
            self.current_plugin.set_parameter(param_name, value)

    def on_plugin_change(self, event):
        """Handle plugin selection change"""
        plugin_name = self.plugin_var.get()
        if plugin_name in self.plugins:
            self.current_plugin = self.plugins[plugin_name]
            self.update_parameter_controls()
            self.log_message(f"Switched to {plugin_name} plugin")

    def start_generation(self):
        """Start the art generation"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            if self.audio_enabled.get() and self.audio_processor:
                self.audio_processor.start_recording()

            self.status_var.set("Generating...")
            self.log_message("Art generation started")

    def stop_generation(self):
        """Stop the art generation"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            if self.audio_processor:
                self.audio_processor.stop_recording()

            self.status_var.set("Stopped")
            self.log_message("Art generation stopped")

    def reset_plugin(self):
        """Reset the current plugin"""
        if self.current_plugin:
            self.current_plugin.reset()
            self.log_message(f"Reset {self.current_plugin.name} plugin")

    def log_message(self, message):
        """Add message to console"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.console_text.insert(tk.END, full_message)
        self.console_text.see(tk.END)

    def update_loop(self):
        """Main update loop"""
        try:
            if self.is_running and self.current_plugin:
                # Get audio features
                audio_features = {'amplitude': 0, 'frequency': 0, 'beat_detected': False}
                if self.audio_processor and self.audio_enabled.get():
                    audio_features = self.audio_processor.get_audio_features()

                # Update plugin
                dt = 1.0 / 60.0  # 60 FPS
                self.current_plugin.update(audio_features, dt)

                # Render
                self.pygame_surface.fill((0, 0, 0))
                self.current_plugin.render(self.pygame_surface)

                # Convert pygame surface to tkinter
                self.update_canvas()

                # Update status
                self.status_var.set(f"Running - Amplitude: {audio_features['amplitude']:.3f}")

        except Exception as e:
            self.log_message(f"Error in update loop: {str(e)}")
            traceback.print_exc()

        # Schedule next update
        self.root.after(16, self.update_loop)  # ~60 FPS

    def update_canvas(self):
        """Update the tkinter canvas with pygame surface"""
        try:
            if PIL_AVAILABLE:
                # Convert pygame surface to numpy array
                pygame_image = pygame.surfarray.array3d(self.pygame_surface)
                # Pygame uses (width, height, channels), PIL expects (height, width, channels)
                pygame_image = pygame_image.swapaxes(0, 1)

                # Convert to PIL Image
                pil_image = Image.fromarray(pygame_image)

                # Convert to PhotoImage for tkinter
                self.photo = ImageTk.PhotoImage(pil_image)

                # Update canvas
                self.canvas.delete("all")
                self.canvas.create_image(
                    self.canvas_size[0]//2,
                    self.canvas_size[1]//2,
                    image=self.photo
                )
            else:
                # Fallback without PIL
                self.canvas.delete("all")
                self.canvas.create_text(400, 300, text="Art Generation Active\n(PIL not available)",
                                       fill="white", font=("Arial", 16), justify=tk.CENTER)

                # Show plugin info
                if self.current_plugin:
                    plugin_info = f"Plugin: {self.current_plugin.name}"
                    if hasattr(self.current_plugin, 'trail_points'):
                        plugin_info += f"\nTrail Points: {len(self.current_plugin.trail_points)}"
                    elif hasattr(self.current_plugin, 'particles'):
                        plugin_info += f"\nParticles: {len(self.current_plugin.particles)}"

                    self.canvas.create_text(400, 350, text=plugin_info,
                                           fill="yellow", font=("Arial", 12))

        except Exception as e:
            # Enhanced fallback with error info
            self.canvas.delete("all")
            self.canvas.create_text(400, 280, text="Art Generation Active",
                                   fill="white", font=("Arial", 18))

            error_text = f"Display Error: {str(e)[:40]}..."
            self.canvas.create_text(400, 320, text=error_text,
                                   fill="orange", font=("Arial", 10))

            # Show what's happening
            if self.current_plugin:
                plugin_info = f"Plugin: {self.current_plugin.name}"
                if hasattr(self.current_plugin, 'trail_points'):
                    plugin_info += f"\nTrail Points: {len(self.current_plugin.trail_points)}"
                elif hasattr(self.current_plugin, 'particles'):
                    plugin_info += f"\nParticles: {len(self.current_plugin.particles)}"

                self.canvas.create_text(400, 360, text=plugin_info,
                                       fill="lightblue", font=("Arial", 12))

                self.canvas.create_text(400, 400, text="Try: pip install --upgrade Pillow",
                                       fill="lightgreen", font=("Arial", 10))

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Clean shutdown"""
        self.is_running = False
        if self.audio_processor:
            self.audio_processor.cleanup()
        pygame.quit()
        self.root.destroy()


if __name__ == "__main__":
    try:
        app = DynamicArtGenerator()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        traceback.print_exc()
