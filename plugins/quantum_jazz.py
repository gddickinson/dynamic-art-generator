#!/usr/bin/env python3
"""
Quantum Jazz Plugin for Dynamic Art Generator
Where quantum physics meets jazz improvisation - uncertainty becomes art
Probability waves, quantum entanglement, and jazz-like spontaneous creation

Author: Claude Assistant
Version: 1.0 - Quantum Improvisation Edition
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


def generate_wave_function(size):
    """
    Generates an array of random complex numbers representing a wave function.

    Parameters:
    - size: int, the number of complex numbers to generate.

    Returns:
    - np.ndarray: An array of random complex numbers.
    """

    # Generate random complex numbers using np.random.random
    # To create complex numbers, we can combine real and imaginary parts
    real_part = np.random.random(size)
    imaginary_part = np.random.random(size)

    # Combine to form complex numbers
    wave_function = real_part + 1j * imaginary_part

    return wave_function

class QuantumParticle:
    """A quantum particle that exists in superposition until observed"""

    def __init__(self, x: float, y: float, energy_level: int = 1):
        # Position and momentum (Heisenberg uncertainty)
        self.x = x
        self.y = y
        self.momentum_x = random.uniform(-50, 50)
        self.momentum_y = random.uniform(-50, 50)

        # Quantum properties
        self.energy_level = energy_level
        self.wave_function = generate_wave_function(size=10)  # Probability amplitude
        self.coherence = 1.0  # How quantum vs classical
        self.observed = False
        self.collapse_timer = 0

        # Jazz improvisation properties
        self.improvisation_factor = random.uniform(0.3, 1.0)
        self.rhythm_sync = random.uniform(0, 1)
        self.jazz_phrase_position = 0
        self.spontaneity = random.uniform(0.5, 1.5)

        # Visual properties
        self.trail = []
        self.uncertainty_cloud = []
        self.color_phase = random.uniform(0, 2 * math.pi)
        self.size = 3 + energy_level * 2

        # Entanglement
        self.entangled_partner = None
        self.entanglement_strength = 0

    def update(self, dt: float, audio_features: dict, other_particles: List['QuantumParticle']):
        """Update quantum state and jazz improvisation"""
        amplitude = audio_features.get('amplitude', 0)
        beat = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})

        # Beat causes wave function collapse (observation)
        if beat and not self.observed:
            self.observe_particle(amplitude)

        # Quantum decoherence over time
        if self.observed:
            self.collapse_timer += dt
            self.coherence = max(0, 1 - self.collapse_timer * 0.5)

            if self.coherence <= 0:
                self.reset_quantum_state()

        # Jazz improvisation affects movement
        jazz_influence = self.improvisation_factor * amplitude

        # Frequency affects energy level transitions
        if frequency > 0:
            new_energy = 1 + int(frequency * 0.01) % 5
            if new_energy != self.energy_level:
                self.energy_level = new_energy
                self.emit_photon()  # Energy transition

        # Update position based on quantum vs classical behavior
        if self.observed:
            # Classical motion when observed
            self.update_classical_motion(dt, jazz_influence)
        else:
            # Quantum superposition when unobserved
            self.update_quantum_motion(dt, jazz_influence, freq_bands)

        # Jazz rhythm synchronization
        self.jazz_phrase_position += dt * (1 + jazz_influence)
        rhythm_factor = math.sin(self.jazz_phrase_position * 2 * math.pi)

        # Spontaneous direction changes (jazz improvisation)
        if random.random() < self.spontaneity * dt * 0.5:
            self.improvise_movement()

        # Update uncertainty cloud
        self.update_uncertainty_cloud(dt)

        # Check for entanglement with other particles
        self.check_entanglement(other_particles)

        # Update visual trail
        self.trail.append((self.x, self.y, time.time()))
        self.trail = [point for point in self.trail if time.time() - point[2] < 2.0]

        # Update color phase
        self.color_phase += dt * 3 + amplitude * 5

    def observe_particle(self, intensity: float):
        """Collapse wave function through observation (measurement)"""
        self.observed = True
        self.collapse_timer = 0

        # Position becomes definite
        uncertainty_reduction = intensity
        position_spread = 20 * (1 - uncertainty_reduction)

        self.x += random.uniform(-position_spread, position_spread)
        self.y += random.uniform(-position_spread, position_spread)

        # Momentum becomes more uncertain (Heisenberg principle)
        momentum_increase = intensity * 30
        self.momentum_x += random.uniform(-momentum_increase, momentum_increase)
        self.momentum_y += random.uniform(-momentum_increase, momentum_increase)

    def reset_quantum_state(self):
        """Return to quantum superposition"""
        self.observed = False
        self.coherence = 1.0
        self.collapse_timer = 0

        # Regenerate wave function
        self.wave_function = generate_wave_function(size=10)

    def update_classical_motion(self, dt: float, jazz_influence: float):
        """Update motion when particle is observed (classical)"""
        # Simple momentum-based motion with jazz influence
        self.x += self.momentum_x * dt * (1 + jazz_influence * 0.5)
        self.y += self.momentum_y * dt * (1 + jazz_influence * 0.5)

        # Friction
        self.momentum_x *= 0.99
        self.momentum_y *= 0.99

    def update_quantum_motion(self, dt: float, jazz_influence: float, freq_bands: dict):
        """Update motion in superposition (quantum)"""
        # Wave-like motion based on wave function
        wave_amplitude = 30 + jazz_influence * 20

        # Multiple wave components create complex motion
        for i, amplitude in enumerate(self.wave_function):
            wave_freq = (i + 1) * 0.5
            wave_phase = time.time() * wave_freq + self.color_phase

            self.x += np.real(amplitude) * wave_amplitude * math.sin(wave_phase) * dt
            self.y += np.imag(amplitude) * wave_amplitude * math.cos(wave_phase) * dt

        # Bass frequencies create lower energy orbital motion
        bass_orbit = freq_bands.get('bass', 0) * 40
        orbit_freq = 0.5 + freq_bands.get('mid', 0)

        self.x += bass_orbit * math.sin(time.time() * orbit_freq) * dt
        self.y += bass_orbit * math.cos(time.time() * orbit_freq * 1.3) * dt

    def improvise_movement(self):
        """Spontaneous direction change (jazz improvisation)"""
        # Random walk with bias towards center
        center_x = 400  # Assume screen center
        center_y = 300

        # Bias towards center (like jazz returning to key center)
        bias_x = (center_x - self.x) * 0.1
        bias_y = (center_y - self.y) * 0.1

        # Random improvisation
        improv_x = random.uniform(-30, 30)
        improv_y = random.uniform(-30, 30)

        self.momentum_x += bias_x + improv_x * self.improvisation_factor
        self.momentum_y += bias_y + improv_y * self.improvisation_factor

    def update_uncertainty_cloud(self, dt: float):
        """Update Heisenberg uncertainty visualization"""
        # Uncertainty is larger when unobserved
        if self.observed:
            uncertainty_size = 5 + self.collapse_timer * 10
        else:
            uncertainty_size = 15 + self.coherence * 20

        # Create cloud points around particle
        self.uncertainty_cloud = []
        cloud_density = max(3, int(uncertainty_size / 3))

        for _ in range(cloud_density):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, uncertainty_size)

            cloud_x = self.x + distance * math.cos(angle)
            cloud_y = self.y + distance * math.sin(angle)

            self.uncertainty_cloud.append((cloud_x, cloud_y))

    def check_entanglement(self, other_particles: List['QuantumParticle']):
        """Check for quantum entanglement with nearby particles"""
        if self.entangled_partner:
            # Maintain existing entanglement
            distance = math.sqrt((self.x - self.entangled_partner.x)**2 +
                               (self.y - self.entangled_partner.y)**2)

            # Entanglement weakens with distance
            self.entanglement_strength = max(0, 1 - distance / 100)

            if self.entanglement_strength < 0.1:
                self.break_entanglement()
        else:
            # Look for new entanglement
            for other in other_particles:
                if other is self or other.entangled_partner:
                    continue

                distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

                if distance < 50 and random.random() < 0.01:  # Low probability
                    self.create_entanglement(other)
                    break

    def create_entanglement(self, other: 'QuantumParticle'):
        """Create quantum entanglement with another particle"""
        self.entangled_partner = other
        other.entangled_partner = self
        self.entanglement_strength = 1.0
        other.entanglement_strength = 1.0

    def break_entanglement(self):
        """Break quantum entanglement"""
        if self.entangled_partner:
            self.entangled_partner.entangled_partner = None
            self.entangled_partner.entanglement_strength = 0

        self.entangled_partner = None
        self.entanglement_strength = 0

    def emit_photon(self):
        """Emit a photon during energy level transition"""
        # This creates a visual effect handled by the main plugin
        pass

    def get_color(self) -> Tuple[int, int, int]:
        """Get particle color based on quantum state and jazz mood"""
        # Base color from energy level (like electron orbitals)
        base_hues = [240, 200, 280, 320, 60]  # Blue, cyan, purple, magenta, yellow
        base_hue = base_hues[self.energy_level - 1] if self.energy_level <= 5 else 240

        # Jazz mood affects color
        jazz_hue_shift = math.sin(self.jazz_phrase_position) * 30
        final_hue = (base_hue + jazz_hue_shift + math.degrees(self.color_phase)) % 360

        # Quantum coherence affects saturation
        saturation = 0.7 + self.coherence * 0.3

        # Observation affects brightness
        brightness = 0.6 + (0.4 if self.observed else 0.2)

        return self.hsv_to_rgb(final_hue, saturation, brightness)

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


class ProbabilityWave:
    """A quantum probability wave that propagates through space"""

    def __init__(self, x: float, y: float, wavelength: float, amplitude: float):
        self.origin_x = x
        self.origin_y = y
        self.wavelength = wavelength
        self.amplitude = amplitude
        self.phase = 0
        self.radius = 0
        self.max_radius = 200
        self.decay_rate = 0.5

        # Jazz properties
        self.rhythm_pattern = random.choice([1, 1.5, 2, 0.75])  # Different time signatures
        self.improvisation_phase = random.uniform(0, 2 * math.pi)

    def update(self, dt: float, audio_features: dict):
        """Update wave propagation"""
        amplitude = audio_features.get('amplitude', 0)
        frequency = audio_features.get('dominant_frequency', 0)

        # Wave propagates outward
        self.radius += 60 * dt * (1 + amplitude * 0.5)

        # Phase advances
        self.phase += dt * self.rhythm_pattern * 5

        # Jazz improvisation affects wavelength
        freq_factor = 1 + frequency * 0.001
        self.wavelength *= freq_factor ** (dt * 0.1)

        # Amplitude decays
        self.amplitude *= (1 - self.decay_rate * dt)

    def is_alive(self) -> bool:
        return self.radius < self.max_radius and self.amplitude > 0.01

    def get_amplitude_at(self, x: float, y: float) -> float:
        """Get wave amplitude at a given position"""
        distance = math.sqrt((x - self.origin_x)**2 + (y - self.origin_y)**2)

        if distance == 0:
            return self.amplitude

        # Wave equation with distance-based decay
        wave_value = self.amplitude * math.sin(2 * math.pi * distance / self.wavelength + self.phase)
        decay_factor = 1 / (1 + distance * 0.01)

        return wave_value * decay_factor


class QuantumJazzPlugin(ArtPlugin):
    """
    Quantum Jazz Plugin - Where physics meets improvisation

    Features:
    - Quantum particles in superposition that collapse on observation (beats)
    - Heisenberg uncertainty principle visualization
    - Quantum entanglement between particles
    - Probability waves propagating through space
    - Jazz-like improvisation in particle movement
    - Energy level transitions creating photon emission
    - Wave-particle duality representation
    - Spontaneous creation and annihilation events
    """

    # Plugin identification
    PLUGIN_NAME = "Quantum Jazz"
    PLUGIN_DESCRIPTION = "Quantum physics meets jazz improvisation"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"

    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)

        # Quantum system
        self.particles = []
        self.probability_waves = []
        self.photons = []
        self.entanglement_pairs = []

        # System parameters
        self.max_particles = 15
        self.particle_creation_rate = 0.3
        self.wave_creation_rate = 0.2
        self.quantum_coherence_time = 5.0

        # Jazz parameters
        self.improvisation_intensity = 0.7
        self.rhythm_complexity = 1.0
        self.harmonic_progression = 0
        self.jazz_tempo = 120  # BPM

        # Visual theme (jazz club + quantum lab)
        self.background_color = (15, 15, 30)     # Deep space blue
        self.jazz_gold = (255, 215, 0)           # Gold accents
        self.quantum_blue = (100, 150, 255)      # Quantum blue
        self.uncertainty_gray = (80, 80, 120)    # Uncertainty cloud
        self.entanglement_red = (255, 100, 100)  # Entanglement connections

        # Audio responsiveness
        self.audio_sensitivity = 1.2
        self.beat_observation_strength = 2.0
        self.frequency_quantum_coupling = 1.5

        # Effects toggles
        self.show_uncertainty = True
        self.show_probability_waves = True
        self.show_entanglement = True
        self.show_particle_trails = True
        self.enable_jazz_improvisation = True

        # Store parameters for GUI
        self.parameters = {
            'max_particles': self.max_particles,
            'particle_creation_rate': self.particle_creation_rate,
            'improvisation_intensity': self.improvisation_intensity,
            'rhythm_complexity': self.rhythm_complexity,
            'audio_sensitivity': self.audio_sensitivity,
            'beat_observation_strength': self.beat_observation_strength,
            'quantum_coherence_time': self.quantum_coherence_time,
            'show_uncertainty': self.show_uncertainty,
            'show_probability_waves': self.show_probability_waves,
            'show_entanglement': self.show_entanglement,
            'show_particle_trails': self.show_particle_trails,
            'enable_jazz_improvisation': self.enable_jazz_improvisation
        }

        # Initialize quantum jazz ensemble
        self.create_initial_particles()

        # Animation state
        self.time_offset = 0
        self.last_creation_time = 0
        self.quantum_field_energy = 0

    def create_initial_particles(self):
        """Create initial quantum particles"""
        for i in range(3):  # Start with few particles
            x = random.uniform(100, self.surface_size[0] - 100)
            y = random.uniform(100, self.surface_size[1] - 100)
            energy_level = random.randint(1, 3)

            particle = QuantumParticle(x, y, energy_level)
            self.particles.append(particle)

    def update(self, audio_features: dict, dt: float):
        """Update the quantum jazz system"""
        self.time_offset += dt

        # Extract audio features
        amplitude = audio_features.get('amplitude', 0) * self.audio_sensitivity
        beat_detected = audio_features.get('beat_detected', False)
        frequency = audio_features.get('dominant_frequency', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})

        # Update quantum field energy
        field_energy_input = freq_bands.get('bass', 0) + amplitude * 0.5
        self.quantum_field_energy += (field_energy_input - self.quantum_field_energy) * dt * 3

        # Jazz harmony progression
        self.harmonic_progression += dt * (self.jazz_tempo / 60) * self.rhythm_complexity

        # Create new particles (pair production from vacuum fluctuations)
        if (len(self.particles) < self.max_particles and
            self.quantum_field_energy > 0.5 and
            self.time_offset - self.last_creation_time > (1 / self.particle_creation_rate)):

            self.create_particle_pair()
            self.last_creation_time = self.time_offset

        # Create probability waves on certain beats
        if beat_detected and self.show_probability_waves:
            self.create_probability_wave(amplitude, frequency)

        # Update particles
        for particle in self.particles[:]:
            # Apply jazz improvisation scaling
            if self.enable_jazz_improvisation:
                particle.improvisation_factor = self.improvisation_intensity

            particle.update(dt, audio_features, self.particles)

            # Remove particles that have drifted too far (annihilation)
            if (particle.x < -50 or particle.x > self.surface_size[0] + 50 or
                particle.y < -50 or particle.y > self.surface_size[1] + 50):
                self.particles.remove(particle)

        # Update probability waves
        for wave in self.probability_waves[:]:
            wave.update(dt, audio_features)
            if not wave.is_alive():
                self.probability_waves.remove(wave)

        # Quantum interference effects
        self.update_quantum_interference()

    def create_particle_pair(self):
        """Create a particle-antiparticle pair"""
        # Random position for pair creation
        x = random.uniform(100, self.surface_size[0] - 100)
        y = random.uniform(100, self.surface_size[1] - 100)

        # Create particle and antiparticle with opposite properties
        energy_level = random.randint(1, 4)

        particle = QuantumParticle(x - 10, y, energy_level)
        antiparticle = QuantumParticle(x + 10, y, energy_level)

        # Opposite momentum for conservation
        momentum = 30
        angle = random.uniform(0, 2 * math.pi)

        particle.momentum_x = momentum * math.cos(angle)
        particle.momentum_y = momentum * math.sin(angle)
        antiparticle.momentum_x = -particle.momentum_x
        antiparticle.momentum_y = -particle.momentum_y

        # Different jazz characteristics
        particle.improvisation_factor = random.uniform(0.3, 1.0)
        antiparticle.improvisation_factor = 1.0 - particle.improvisation_factor

        self.particles.extend([particle, antiparticle])

    def create_probability_wave(self, amplitude: float, frequency: float):
        """Create a probability wave from audio"""
        # Random source position
        x = random.uniform(0, self.surface_size[0])
        y = random.uniform(0, self.surface_size[1])

        # Wave properties from audio
        wavelength = 50 + frequency * 0.1
        wave_amplitude = amplitude * 0.5

        wave = ProbabilityWave(x, y, wavelength, wave_amplitude)
        self.probability_waves.append(wave)

    def update_quantum_interference(self):
        """Update quantum interference patterns between waves"""
        # This creates complex interference patterns when multiple waves overlap
        # The visualization happens in the render method
        pass

    def render(self, surface: pygame.Surface):
        """Render the quantum jazz visualization"""
        # Background
        surface.fill(self.background_color)

        # Render probability waves
        if self.show_probability_waves:
            self.render_probability_waves(surface)

        # Render uncertainty clouds
        if self.show_uncertainty:
            self.render_uncertainty_clouds(surface)

        # Render particle trails
        if self.show_particle_trails:
            self.render_particle_trails(surface)

        # Render entanglement connections
        if self.show_entanglement:
            self.render_entanglement(surface)

        # Render particles
        self.render_particles(surface)

        # Render quantum field visualization
        self.render_quantum_field(surface)

    def render_probability_waves(self, surface: pygame.Surface):
        """Render quantum probability waves"""
        for wave in self.probability_waves:
            if wave.amplitude < 0.05:
                continue

            # Draw concentric circles representing wave fronts
            num_rings = 5
            for i in range(num_rings):
                ring_radius = wave.radius - i * (wave.wavelength / 2)
                if ring_radius > 0:
                    alpha = int(wave.amplitude * 100 * (1 - i / num_rings))
                    if alpha > 5:
                        wave_color = (*self.quantum_blue, alpha)

                        # Create surface for alpha blending
                        ring_surface = pygame.Surface((ring_radius * 4, ring_radius * 4), pygame.SRCALPHA)
                        try:
                            pygame.draw.circle(ring_surface, wave_color,
                                             (ring_radius * 2, ring_radius * 2),
                                             int(ring_radius), 2)
                            surface.blit(ring_surface,
                                       (wave.origin_x - ring_radius * 2,
                                        wave.origin_y - ring_radius * 2))
                        except:
                            pass

    def render_uncertainty_clouds(self, surface: pygame.Surface):
        """Render Heisenberg uncertainty clouds"""
        for particle in self.particles:
            if not particle.uncertainty_cloud:
                continue

            # Uncertainty opacity based on quantum coherence
            base_alpha = int(particle.coherence * 60)
            if base_alpha < 5:
                continue

            cloud_color = (*self.uncertainty_gray, base_alpha)

            for cloud_x, cloud_y in particle.uncertainty_cloud:
                pos = (int(cloud_x), int(cloud_y))

                try:
                    # Small uncertainty dot
                    uncertainty_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(uncertainty_surface, cloud_color, (3, 3), 2)
                    surface.blit(uncertainty_surface, (pos[0] - 3, pos[1] - 3))
                except:
                    pass

    def render_particle_trails(self, surface: pygame.Surface):
        """Render particle movement trails"""
        for particle in self.particles:
            if len(particle.trail) < 2:
                continue

            # Draw trail with fading
            for i in range(1, len(particle.trail)):
                age = time.time() - particle.trail[i][2]
                alpha = max(0, int(255 * (1 - age / 2.0)))

                if alpha > 10:
                    trail_color = particle.get_color()
                    faded_color = (*trail_color, alpha)

                    start_pos = (int(particle.trail[i-1][0]), int(particle.trail[i-1][1]))
                    end_pos = (int(particle.trail[i][0]), int(particle.trail[i][1]))

                    try:
                        # Draw trail line
                        trail_surface = pygame.Surface((abs(end_pos[0] - start_pos[0]) + 10,
                                                       abs(end_pos[1] - start_pos[1]) + 10),
                                                      pygame.SRCALPHA)

                        rel_start = (5, 5)
                        rel_end = (end_pos[0] - start_pos[0] + 5, end_pos[1] - start_pos[1] + 5)

                        pygame.draw.line(trail_surface, faded_color, rel_start, rel_end, 1)
                        surface.blit(trail_surface,
                                   (min(start_pos[0], end_pos[0]) - 5,
                                    min(start_pos[1], end_pos[1]) - 5))
                    except:
                        pass

    def render_entanglement(self, surface: pygame.Surface):
        """Render quantum entanglement connections"""
        for particle in self.particles:
            if particle.entangled_partner and particle.entanglement_strength > 0.1:
                # Draw entanglement connection
                start_pos = (int(particle.x), int(particle.y))
                end_pos = (int(particle.entangled_partner.x), int(particle.entangled_partner.y))

                alpha = int(particle.entanglement_strength * 150)
                entangle_color = (*self.entanglement_red, alpha)

                try:
                    # Wavy entanglement line (quantum correlation)
                    distance = math.sqrt((end_pos[0] - start_pos[0])**2 +
                                       (end_pos[1] - start_pos[1])**2)

                    if distance > 0:
                        # Create wavy line
                        num_segments = max(5, int(distance / 20))
                        points = []

                        for i in range(num_segments + 1):
                            t = i / num_segments
                            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t

                            # Add wave to the line
                            perpendicular_offset = math.sin(t * math.pi * 4 + time.time() * 5) * 10
                            angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])

                            wave_x = x + perpendicular_offset * math.sin(angle + math.pi/2)
                            wave_y = y + perpendicular_offset * math.cos(angle + math.pi/2)

                            points.append((int(wave_x), int(wave_y)))

                        # Draw the wavy line
                        if len(points) > 1:
                            entangle_surface = pygame.Surface((int(distance) + 40, 40), pygame.SRCALPHA)
                            # Simple line for now (complex curves are harder to implement)
                            pygame.draw.line(entangle_surface, entangle_color,
                                           (10, 20), (int(distance) + 10, 20), 2)

                            surface.blit(entangle_surface,
                                       (min(start_pos[0], end_pos[0]) - 20,
                                        min(start_pos[1], end_pos[1]) - 20))

                except:
                    pass

    def render_particles(self, surface: pygame.Surface):
        """Render quantum particles"""
        for particle in self.particles:
            pos = (int(particle.x), int(particle.y))
            color = particle.get_color()
            size = int(particle.size)

            try:
                # Particle core
                pygame.draw.circle(surface, color, pos, size)

                # Energy level rings
                for level in range(particle.energy_level):
                    ring_radius = size + level * 3
                    ring_alpha = max(20, 100 - level * 20)
                    ring_color = (*color, ring_alpha)

                    ring_surface = pygame.Surface((ring_radius * 4, ring_radius * 4), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surface, ring_color,
                                     (ring_radius * 2, ring_radius * 2), ring_radius, 1)
                    surface.blit(ring_surface,
                               (pos[0] - ring_radius * 2, pos[1] - ring_radius * 2))

                # Observation state indicator
                if particle.observed:
                    # Classical particle (solid)
                    pygame.draw.circle(surface, (255, 255, 255), pos, size + 2, 1)
                else:
                    # Quantum particle (fuzzy)
                    for i in range(3):
                        fuzz_radius = size + i
                        fuzz_alpha = 50 - i * 15
                        fuzz_color = (*color, fuzz_alpha)

                        fuzz_surface = pygame.Surface((fuzz_radius * 4, fuzz_radius * 4), pygame.SRCALPHA)
                        pygame.draw.circle(fuzz_surface, fuzz_color,
                                         (fuzz_radius * 2, fuzz_radius * 2), fuzz_radius)
                        surface.blit(fuzz_surface,
                                   (pos[0] - fuzz_radius * 2, pos[1] - fuzz_radius * 2))

            except:
                pass

    def render_quantum_field(self, surface: pygame.Surface):
        """Render background quantum field energy"""
        if self.quantum_field_energy < 0.1:
            return

        # Grid pattern representing quantum field fluctuations
        grid_spacing = 40
        field_alpha = int(self.quantum_field_energy * 30)

        if field_alpha > 5:
            field_color = (*self.jazz_gold, field_alpha)

            # Vertical lines
            for x in range(0, self.surface_size[0], grid_spacing):
                field_surface = pygame.Surface((2, self.surface_size[1]), pygame.SRCALPHA)
                pygame.draw.line(field_surface, field_color, (1, 0), (1, self.surface_size[1]), 1)
                surface.blit(field_surface, (x, 0))

            # Horizontal lines
            for y in range(0, self.surface_size[1], grid_spacing):
                field_surface = pygame.Surface((self.surface_size[0], 2), pygame.SRCALPHA)
                pygame.draw.line(field_surface, field_color, (0, 1), (self.surface_size[0], 1), 1)
                surface.blit(field_surface, (0, y))

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
                self.max_particles = max(3, min(50, int(value)))
                self.parameters[name] = self.max_particles

            elif name in ['improvisation_intensity', 'rhythm_complexity']:
                setattr(self, name, max(0.1, min(2.0, float(value))))
                self.parameters[name] = getattr(self, name)

    def reset(self):
        """Reset plugin to initial state"""
        # Clear all quantum effects
        self.particles.clear()
        self.probability_waves.clear()
        self.photons.clear()
        self.entanglement_pairs.clear()

        # Reset state
        self.time_offset = 0
        self.last_creation_time = 0
        self.quantum_field_energy = 0
        self.harmonic_progression = 0

        # Create new initial particles
        self.create_initial_particles()

        print(f"Reset {self.name} plugin")

    def get_info(self) -> dict:
        """Get plugin information"""
        observed_particles = sum(1 for p in self.particles if p.observed)
        entangled_particles = sum(1 for p in self.particles if p.entangled_partner)

        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'parameters': list(self.parameters.keys()),
            'surface_size': self.surface_size,
            'particle_count': len(self.particles),
            'observed_particles': observed_particles,
            'quantum_particles': len(self.particles) - observed_particles,
            'entangled_particles': entangled_particles,
            'probability_waves': len(self.probability_waves),
            'quantum_field_energy': f"{self.quantum_field_energy:.2f}",
            'harmonic_progression': f"{self.harmonic_progression:.1f}"
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time

    print("Testing Quantum Jazz Plugin...")

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Quantum Jazz Plugin Test")
    clock = pygame.time.Clock()

    # Create plugin
    plugin = QuantumJazzPlugin((800, 600))

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
                    plugin.set_parameter('max_particles', plugin.max_particles + 1)
                elif event.key == pygame.K_DOWN:
                    plugin.set_parameter('max_particles', max(3, plugin.max_particles - 1))

        # Simulate jazz-like audio (syncopated, complex)
        fake_audio = {
            'amplitude': 0.6 + 0.3 * math.sin(current_time * 1.7),
            'beat_detected': (current_time % 1.3) < 0.12,  # Syncopated jazz rhythm
            'dominant_frequency': 440 + 220 * math.sin(current_time * 0.7),  # Jazz harmonies
            'frequency_bands': {
                'bass': 0.5 + 0.3 * math.sin(current_time * 0.9),    # Walking bass
                'mid': 0.4 + 0.4 * math.sin(current_time * 1.4),     # Piano/horns
                'treble': 0.3 + 0.3 * math.sin(current_time * 2.1)   # Cymbals/high notes
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
                f"Quantum Jazz - Particles: {len(plugin.particles)} | Waves: {len(plugin.probability_waves)}",
                f"Field Energy: {plugin.quantum_field_energy:.2f} | Harmony: {plugin.harmonic_progression:.1f}",
                "UP/DOWN: Particles | SPACE: Reset"
            ]

            for i, line in enumerate(info_lines):
                text_surface = font.render(line, True, (255, 215, 0))  # Jazz gold text
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass

        pygame.display.flip()

    pygame.quit()
    print("Quantum Jazz plugin test completed")
