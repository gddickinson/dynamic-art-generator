#!/usr/bin/env python3
"""
Musical Ecosystem Plugin for Dynamic Art Generator
A living predator-prey ecosystem that dances to music!

Features:
- Flocking boids that can reproduce and age
- Hungry predator that hunts to music
- Audio-driven reproduction and predation rates
- Survival of the fittest with musical beats
- Beautiful trails and life/death visual effects

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


class Vector2D:
    """2D Vector class for physics"""
    
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        if scalar != 0:
            return Vector2D(self.x / scalar, self.y / scalar)
        return Vector2D(0, 0)
    
    def add(self, other):
        self.x += other.x
        self.y += other.y
    
    def sub(self, other):
        self.x -= other.x
        self.y -= other.y
    
    def mult(self, scalar):
        self.x *= scalar
        self.y *= scalar
    
    def div(self, scalar):
        if scalar != 0:
            self.x /= scalar
            self.y /= scalar
    
    def mag(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        m = self.mag()
        if m > 0:
            self.div(m)
    
    def limit(self, max_val):
        if self.mag() > max_val:
            self.normalize()
            self.mult(max_val)
    
    def heading(self):
        return math.atan2(self.y, self.x)
    
    def copy(self):
        return Vector2D(self.x, self.y)
    
    @staticmethod
    def dist(v1, v2):
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def sub_static(v1, v2):
        return Vector2D(v1.x - v2.x, v1.y - v2.y)


class Boid:
    """Prey boid with flocking, fleeing, aging, and reproduction"""
    
    def __init__(self, x, y):
        self.acceleration = Vector2D(0, 0)
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = Vector2D(math.cos(angle), math.sin(angle))
        self.location = Vector2D(x, y)
        
        # Physical properties
        self.r = 3.0
        self.maxspeed = 3.0
        self.maxforce = 0.08
        
        # Life properties
        self.age = 0.0
        self.max_age = random.uniform(15, 25)  # Die of old age eventually
        self.reproduction_age = random.uniform(3, 5)  # Can reproduce when mature
        self.energy = 1.0
        self.is_alive = True
        
        # Visual properties
        self.trail = []
        self.max_trail_length = 12
        self.color_hue = random.uniform(60, 120)  # Green-ish (prey colors)
        self.birth_flash = 0.0  # Flash effect when born
        
        # Behavior weights
        self.separation_weight = 1.8
        self.alignment_weight = 1.2
        self.cohesion_weight = 1.0
        self.flee_weight = 4.0  # Strong fear response!
        
        # Audio response
        self.panic_level = 0.0
        self.reproduction_urge = 0.0
        self.last_reproduction = 0
    
    def update(self, dt: float, all_boids: List['Boid'], predators: List['Predator'], 
               audio_features: dict, bounds: Tuple[int, int]) -> List['Boid']:
        """Update boid and return any offspring"""
        offspring = []
        
        if not self.is_alive:
            return offspring
        
        # Age and energy
        self.age += dt
        self.energy -= 0.02 * dt  # Gradual energy loss
        
        # Die if too old or no energy
        if self.age > self.max_age or self.energy <= 0:
            self.is_alive = False
            return offspring
        
        # Update behaviors
        self.flock_and_flee(all_boids, predators, audio_features)
        self.update_physics()
        self.wrap_around(bounds)
        self.update_audio_response(audio_features)
        self.update_trail()
        
        # Reproduction check
        if self.can_reproduce(audio_features):
            baby = self.reproduce()
            if baby:
                offspring.append(baby)
        
        # Decay effects
        self.birth_flash *= 0.95
        self.panic_level *= 0.92
        
        return offspring
    
    def flock_and_flee(self, all_boids: List['Boid'], predators: List['Predator'], audio_features: dict):
        """Combined flocking and predator avoidance"""
        # Standard flocking behaviors
        sep = self.separate(all_boids)
        ali = self.align(all_boids)
        coh = self.cohesion(all_boids)
        
        # Predator avoidance - MOST IMPORTANT!
        flee = self.flee_from_predators(predators)
        
        # Audio can make them more scattered (bass) or more grouped (treble)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        bass_panic = freq_bands.get('bass', 0) * 2
        treble_calm = freq_bands.get('treble', 0)
        
        # Weight the forces
        sep.mult(self.separation_weight + bass_panic)
        ali.mult(self.alignment_weight + treble_calm * 0.5)
        coh.mult(self.cohesion_weight + treble_calm)
        flee.mult(self.flee_weight)
        
        # Apply forces
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)
        self.apply_force(flee)
        
        # Panic on beats - random evasive movement
        if audio_features.get('beat_detected', False):
            panic_force = Vector2D(
                random.uniform(-1, 1) * audio_features.get('amplitude', 0),
                random.uniform(-1, 1) * audio_features.get('amplitude', 0)
            )
            panic_force.mult(0.15)
            self.apply_force(panic_force)
    
    def flee_from_predators(self, predators: List['Predator']) -> Vector2D:
        """Flee from nearby predators"""
        steer = Vector2D(0, 0)
        flee_radius = 80  # Start fleeing when predator is this close
        
        for predator in predators:
            distance = Vector2D.dist(self.location, predator.location)
            
            if distance < flee_radius and distance > 0:
                # Flee direction (away from predator)
                flee_dir = Vector2D.sub_static(self.location, predator.location)
                flee_dir.normalize()
                
                # Stronger flee force when predator is closer
                flee_strength = (flee_radius - distance) / flee_radius
                flee_dir.mult(flee_strength * 2)
                
                steer.add(flee_dir)
                
                # Increase panic level
                self.panic_level = min(self.panic_level + flee_strength * 2, 3.0)
        
        if steer.mag() > 0:
            steer.normalize()
            steer.mult(self.maxspeed)
            steer.sub(self.velocity)
            steer.limit(self.maxforce * 2)  # Stronger force for fleeing
        
        return steer
    
    def can_reproduce(self, audio_features: dict) -> bool:
        """Check if boid can reproduce"""
        if (self.age < self.reproduction_age or 
            self.energy < 0.6 or 
            self.panic_level > 1.0 or  # Too scared to reproduce
            time.time() - self.last_reproduction < 2.0):  # Rate limit
            return False
        
        # Audio affects reproduction urge
        amplitude = audio_features.get('amplitude', 0)
        freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
        
        # Mid frequencies encourage reproduction (harmony = mating songs)
        mid_factor = freq_bands.get('mid', 0)
        self.reproduction_urge += mid_factor * 0.5
        
        # Beat detection can trigger reproduction
        if audio_features.get('beat_detected', False) and amplitude > 0.3:
            self.reproduction_urge += amplitude
        
        # Random chance based on accumulated urge
        return self.reproduction_urge > random.uniform(1.5, 2.5)
    
    def reproduce(self) -> 'Boid':
        """Create offspring"""
        # Reset reproduction state
        self.reproduction_urge = 0
        self.last_reproduction = time.time()
        self.energy -= 0.3  # Reproduction costs energy
        
        # Create baby near parent
        offset_x = random.uniform(-20, 20)
        offset_y = random.uniform(-20, 20)
        
        baby = Boid(self.location.x + offset_x, self.location.y + offset_y)
        baby.color_hue = self.color_hue + random.uniform(-20, 20)  # Inherit with variation
        baby.birth_flash = 2.0  # Birth glow effect
        
        return baby
    
    def separate(self, boids: List['Boid']) -> Vector2D:
        """Separation behavior"""
        desired_separation = 25.0
        steer = Vector2D(0, 0)
        count = 0
        
        for other in boids:
            if not other.is_alive or other is self:
                continue
            
            d = Vector2D.dist(self.location, other.location)
            if 0 < d < desired_separation:
                diff = Vector2D.sub_static(self.location, other.location)
                diff.normalize()
                diff.div(d)
                steer.add(diff)
                count += 1
        
        if count > 0:
            steer.div(count)
            if steer.mag() > 0:
                steer.normalize()
                steer.mult(self.maxspeed)
                steer.sub(self.velocity)
                steer.limit(self.maxforce)
        
        return steer
    
    def align(self, boids: List['Boid']) -> Vector2D:
        """Alignment behavior"""
        neighbor_dist = 50
        sum_vel = Vector2D(0, 0)
        count = 0
        
        for other in boids:
            if not other.is_alive or other is self:
                continue
            
            d = Vector2D.dist(self.location, other.location)
            if 0 < d < neighbor_dist:
                sum_vel.add(other.velocity)
                count += 1
        
        if count > 0:
            sum_vel.div(count)
            sum_vel.normalize()
            sum_vel.mult(self.maxspeed)
            steer = Vector2D.sub_static(sum_vel, self.velocity)
            steer.limit(self.maxforce)
            return steer
        
        return Vector2D(0, 0)
    
    def cohesion(self, boids: List['Boid']) -> Vector2D:
        """Cohesion behavior"""
        neighbor_dist = 50
        sum_pos = Vector2D(0, 0)
        count = 0
        
        for other in boids:
            if not other.is_alive or other is self:
                continue
            
            d = Vector2D.dist(self.location, other.location)
            if 0 < d < neighbor_dist:
                sum_pos.add(other.location)
                count += 1
        
        if count > 0:
            sum_pos.div(count)
            return self.seek(sum_pos)
        
        return Vector2D(0, 0)
    
    def seek(self, target: Vector2D) -> Vector2D:
        """Seek toward target"""
        desired = Vector2D.sub_static(target, self.location)
        desired.normalize()
        desired.mult(self.maxspeed)
        
        steer = Vector2D.sub_static(desired, self.velocity)
        steer.limit(self.maxforce)
        return steer
    
    def apply_force(self, force: Vector2D):
        """Apply force to acceleration"""
        self.acceleration.add(force)
    
    def update_physics(self):
        """Update velocity and position"""
        # Update velocity
        self.velocity.add(self.acceleration)
        # Limit speed (panic can make them faster)
        max_speed = self.maxspeed * (1 + self.panic_level * 0.5)
        self.velocity.limit(max_speed)
        # Update location
        self.location.add(self.velocity)
        # Reset acceleration
        self.acceleration.mult(0)
    
    def wrap_around(self, bounds: Tuple[int, int]):
        """Wrap around screen edges"""
        width, height = bounds
        
        if self.location.x < -self.r:
            self.location.x = width + self.r
        if self.location.y < -self.r:
            self.location.y = height + self.r
        if self.location.x > width + self.r:
            self.location.x = -self.r
        if self.location.y > height + self.r:
            self.location.y = -self.r
    
    def update_audio_response(self, audio_features: dict):
        """Update color and visual response to audio"""
        amplitude = audio_features.get('amplitude', 0)
        frequency = audio_features.get('dominant_frequency', 0)
        
        # Color shifts with frequency and age
        age_factor = self.age / self.max_age
        self.color_hue += frequency * 0.002 + amplitude * 10
        
        # Older boids get more blue/purple
        self.color_hue = (60 + age_factor * 60) % 360
    
    def update_trail(self):
        """Update visual trail"""
        self.trail.append((self.location.x, self.location.y, self.color_hue))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)


class Predator:
    """Hungry predator that hunts boids to music"""
    
    def __init__(self, x, y):
        self.location = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
        
        # Physical properties
        self.r = 8.0  # Bigger than boids
        self.maxspeed = 2.0  # Normally slower than panicked boids
        self.maxforce = 0.12
        
        # Predator properties
        self.energy = 50.0  # Starts with energy
        self.max_energy = 100.0
        self.hunger = 0.0  # Increases over time
        self.hunt_radius = 120.0  # How far it can sense prey
        self.kill_radius = 6.0  # How close to kill
        
        # Visual properties
        self.color_hue = random.uniform(0, 30)  # Red-ish (predator colors)
        self.trail = []
        self.max_trail_length = 20
        self.kill_flash = 0.0  # Flash when killing
        self.size_pulse = 0.0
        
        # Audio response
        self.hunt_intensity = 0.0
        self.beat_boost = 0.0
        
        # Hunting state
        self.target = None
        self.kills = 0
    
    def update(self, dt: float, boids: List[Boid], audio_features: dict, bounds: Tuple[int, int]) -> int:
        """Update predator and return number of kills"""
        kills_this_frame = 0
        
        # Lose energy over time (must hunt to survive)
        self.energy -= 8 * dt
        self.hunger += dt
        
        # Die if no energy
        if self.energy <= 0:
            self.energy = 0
            return 0
        
        # Hunt behavior
        self.hunt(boids, audio_features)
        
        # Check for kills
        kills_this_frame = self.check_for_kills(boids)
        
        # Update physics
        self.update_physics()
        self.wrap_around(bounds)
        self.update_audio_response(audio_features)
        self.update_trail()
        
        # Decay effects
        self.kill_flash *= 0.9
        self.beat_boost *= 0.95
        self.hunt_intensity *= 0.98
        
        return kills_this_frame
    
    def hunt(self, boids: List[Boid], audio_features: dict):
        """Hunt the nearest boid"""
        # Find closest living boid
        closest_boid = None
        closest_distance = float('inf')
        
        for boid in boids:
            if not boid.is_alive:
                continue
            
            distance = Vector2D.dist(self.location, boid.location)
            if distance < self.hunt_radius and distance < closest_distance:
                closest_distance = distance
                closest_boid = boid
        
        if closest_boid:
            self.target = closest_boid
            
            # Seek the target
            hunt_force = self.seek(closest_boid.location)
            
            # Audio makes predator more aggressive
            amplitude = audio_features.get('amplitude', 0)
            freq_bands = audio_features.get('frequency_bands', {'bass': 0, 'mid': 0, 'treble': 0})
            
            # Bass drives hunting intensity
            bass_factor = freq_bands.get('bass', 0)
            self.hunt_intensity += bass_factor * 2
            
            # Beat detection gives speed boost
            if audio_features.get('beat_detected', False):
                self.beat_boost = min(self.beat_boost + amplitude * 3, 5.0)
            
            # Scale hunt force by intensity and hunger
            intensity_multiplier = 1 + self.hunt_intensity * 0.5 + self.hunger * 0.3
            hunt_force.mult(intensity_multiplier)
            
            self.apply_force(hunt_force)
        else:
            # No target - patrol randomly with audio influence
            if random.random() < 0.01:  # Occasionally change direction
                random_force = Vector2D(
                    random.uniform(-1, 1),
                    random.uniform(-1, 1)
                )
                random_force.mult(0.05)
                self.apply_force(random_force)
    
    def check_for_kills(self, boids: List[Boid]) -> int:
        """Check if predator caught any boids"""
        kills = 0
        
        for boid in boids:
            if not boid.is_alive:
                continue
            
            distance = Vector2D.dist(self.location, boid.location)
            if distance < self.kill_radius:
                # KILL!
                boid.is_alive = False
                kills += 1
                self.kills += 1
                
                # Predator gains energy and satisfaction
                self.energy = min(self.energy + 25, self.max_energy)
                self.hunger = max(0, self.hunger - 1.5)
                
                # Visual effects
                self.kill_flash = 3.0
                self.size_pulse = 2.0
        
        return kills
    
    def seek(self, target: Vector2D) -> Vector2D:
        """Seek toward target with predator-specific behavior"""
        desired = Vector2D.sub_static(target, self.location)
        desired.normalize()
        
        # Speed up when close to prey
        distance = desired.mag()
        if distance < 30:
            speed = self.maxspeed * 2  # Sprint when close!
        else:
            speed = self.maxspeed
        
        # Audio boost
        speed *= (1 + self.beat_boost * 0.3)
        
        desired.mult(speed)
        
        steer = Vector2D.sub_static(desired, self.velocity)
        steer.limit(self.maxforce * (1 + self.hunt_intensity * 0.5))
        return steer
    
    def apply_force(self, force: Vector2D):
        """Apply force to acceleration"""
        self.acceleration.add(force)
    
    def update_physics(self):
        """Update velocity and position"""
        self.velocity.add(self.acceleration)
        max_speed = self.maxspeed * (1 + self.beat_boost * 0.4)
        self.velocity.limit(max_speed)
        self.location.add(self.velocity)
        self.acceleration.mult(0)
    
    def wrap_around(self, bounds: Tuple[int, int]):
        """Wrap around screen edges"""
        width, height = bounds
        
        if self.location.x < -self.r:
            self.location.x = width + self.r
        if self.location.y < -self.r:
            self.location.y = height + self.r
        if self.location.x > width + self.r:
            self.location.x = -self.r
        if self.location.y > height + self.r:
            self.location.y = -self.r
    
    def update_audio_response(self, audio_features: dict):
        """Update predator's audio response"""
        amplitude = audio_features.get('amplitude', 0)
        frequency = audio_features.get('dominant_frequency', 0)
        
        # Color shifts with hunting success and audio
        kill_factor = min(self.kills * 0.1, 1.0)
        self.color_hue = frequency * 0.003 + amplitude * 15 + kill_factor * 20
        self.color_hue %= 360
        
        # Size pulses with audio
        self.size_pulse += amplitude * 0.5
        self.size_pulse = min(self.size_pulse, 3.0)
        self.size_pulse *= 0.95
    
    def update_trail(self):
        """Update predator trail"""
        self.trail.append((self.location.x, self.location.y, self.color_hue))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)


class MusicalEcosystemPlugin(ArtPlugin):
    """
    Musical Ecosystem Plugin - Living predator-prey system
    
    A dynamic ecosystem where:
    - Boids flock, flee, age, and reproduce
    - Predators hunt to survive and gain energy
    - Music drives reproduction, predation, and panic
    - Survival of the fittest in a musical world
    """
    
    # Plugin identification
    PLUGIN_NAME = "Musical Ecosystem"
    PLUGIN_DESCRIPTION = "Living predator-prey ecosystem dancing to music"
    PLUGIN_VERSION = "1.0"
    PLUGIN_AUTHOR = "Claude Assistant"
    
    def __init__(self, surface_size: tuple):
        super().__init__(self.PLUGIN_NAME, surface_size)
        
        # Population parameters
        self.initial_boids = 40
        self.max_boids = 150
        self.num_predators = 2
        self.max_predators = 5
        
        # Ecosystem state
        self.boids = []
        self.predators = []
        self.total_births = 0
        self.total_deaths = 0
        
        # Visual settings
        self.show_trails = True
        self.show_hunt_radius = False
        self.trail_opacity = 0.7
        self.background_fade = 0.02
        
        # Audio responsiveness
        self.audio_sensitivity = 1.0
        self.reproduction_rate_multiplier = 1.0
        self.predator_aggression_multiplier = 1.0
        
        # Ecosystem balance
        self.auto_spawn_predators = True
        self.auto_spawn_boids = True
        self.min_population = 10
        
        # Store parameters for GUI
        self.parameters = {
            'initial_boids': self.initial_boids,
            'num_predators': self.num_predators,
            'audio_sensitivity': self.audio_sensitivity,
            'reproduction_rate_multiplier': self.reproduction_rate_multiplier,
            'predator_aggression_multiplier': self.predator_aggression_multiplier,
            'trail_opacity': self.trail_opacity,
            'show_trails': self.show_trails,
            'show_hunt_radius': self.show_hunt_radius,
            'auto_spawn_predators': self.auto_spawn_predators,
            'auto_spawn_boids': self.auto_spawn_boids
        }
        
        # Initialize ecosystem
        self.create_initial_ecosystem()
        
        # Statistics
        self.ecosystem_age = 0.0
        self.last_status_update = 0
    
    def create_initial_ecosystem(self):
        """Create the initial ecosystem"""
        self.boids.clear()
        self.predators.clear()
        
        # Create boids
        for _ in range(int(self.initial_boids)):
            x = random.uniform(50, self.surface_size[0] - 50)
            y = random.uniform(50, self.surface_size[1] - 50)
            boid = Boid(x, y)
            self.boids.append(boid)
        
        # Create predators
        for _ in range(int(self.num_predators)):
            x = random.uniform(100, self.surface_size[0] - 100)
            y = random.uniform(100, self.surface_size[1] - 100)
            predator = Predator(x, y)
            self.predators.append(predator)
        
        # Reset statistics
        self.total_births = 0
        self.total_deaths = 0
        self.ecosystem_age = 0.0
    
    def update(self, audio_features: dict, dt: float):
        """Update the entire ecosystem"""
        self.ecosystem_age += dt
        
        # Update all boids and collect offspring
        new_boids = []
        living_boids = []
        
        for boid in self.boids:
            if boid.is_alive:
                offspring = boid.update(dt, self.boids, self.predators, audio_features, self.surface_size)
                new_boids.extend(offspring)
                living_boids.append(boid)
            else:
                self.total_deaths += 1
        
        # Add new births
        if len(new_boids) > 0:
            # Apply reproduction rate multiplier
            reproduction_factor = self.reproduction_rate_multiplier * audio_features.get('amplitude', 0.5)
            for baby in new_boids:
                if random.random() < reproduction_factor and len(living_boids) < self.max_boids:
                    living_boids.append(baby)
                    self.total_births += 1
        
        self.boids = living_boids
        
        # Update predators
        living_predators = []
        total_kills = 0
        
        for predator in self.predators:
            kills = predator.update(dt, self.boids, audio_features, self.surface_size)
            total_kills += kills
            
            # Keep predator if it has energy or we want to maintain minimum
            if predator.energy > 0 or len(living_predators) < 1:
                living_predators.append(predator)
        
        self.predators = living_predators
        
        # Ecosystem management
        self.manage_ecosystem_balance(audio_features)
    
    def manage_ecosystem_balance(self, audio_features: dict):
        """Maintain ecosystem balance"""
        current_prey = len([b for b in self.boids if b.is_alive])
        current_predators = len(self.predators)
        
        # Auto-spawn boids if population too low
        if self.auto_spawn_boids and current_prey < self.min_population:
            for _ in range(self.min_population - current_prey):
                x = random.uniform(50, self.surface_size[0] - 50)
                y = random.uniform(50, self.surface_size[1] - 50)
                new_boid = Boid(x, y)
                new_boid.age = random.uniform(0, 2)  # Start with some age variation
                self.boids.append(new_boid)
        
        # Auto-spawn predators based on prey population and audio
        if self.auto_spawn_predators:
            ideal_predators = max(1, min(self.max_predators, current_prey // 20))
            amplitude = audio_features.get('amplitude', 0)
            
            # High amplitude (loud music) can spawn more predators
            if amplitude > 0.7 and random.random() < 0.01:
                ideal_predators += 1
            
            if current_predators < ideal_predators:
                x = random.uniform(100, self.surface_size[0] - 100)
                y = random.uniform(100, self.surface_size[1] - 100)
                new_predator = Predator(x, y)
                self.predators.append(new_predator)
    
    def render(self, surface: pygame.Surface):
        """Render the ecosystem"""
        # Draw trails
        if self.show_trails:
            self.render_trails(surface)
        
        # Draw hunt radius (optional)
        if self.show_hunt_radius:
            self.render_hunt_areas(surface)
        
        # Render boids
        self.render_boids(surface)
        
        # Render predators
        self.render_predators(surface)
        
        # Render ecosystem stats
        self.render_ecosystem_info(surface)
    
    def render_trails(self, surface: pygame.Surface):
        """Render trails for both boids and predators"""
        # Boid trails
        for boid in self.boids:
            if not boid.is_alive or len(boid.trail) < 2:
                continue
            
            for i in range(1, len(boid.trail)):
                fade_factor = i / len(boid.trail)
                alpha = max(0, min(255, int(fade_factor * self.trail_opacity * 255)))
                
                if alpha > 0:
                    x, y, hue = boid.trail[i]
                    trail_color = self.hsv_to_rgb(hue, 0.6, 0.8)
                    
                    trail_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                    trail_alpha_color = (*trail_color, alpha)
                    
                    try:
                        pygame.draw.circle(trail_surface, trail_alpha_color, (2, 2), 1)
                        surface.blit(trail_surface, (int(x) - 2, int(y) - 2))
                    except (ValueError, TypeError):
                        pass
        
        # Predator trails
        for predator in self.predators:
            if len(predator.trail) < 2:
                continue
            
            for i in range(1, len(predator.trail)):
                fade_factor = i / len(predator.trail)
                alpha = max(0, min(255, int(fade_factor * self.trail_opacity * 200)))
                
                if alpha > 0:
                    x, y, hue = predator.trail[i]
                    trail_color = self.hsv_to_rgb(hue, 0.8, 0.9)
                    
                    trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                    trail_alpha_color = (*trail_color, alpha)
                    
                    try:
                        pygame.draw.circle(trail_surface, trail_alpha_color, (3, 3), 2)
                        surface.blit(trail_surface, (int(x) - 3, int(y) - 3))
                    except (ValueError, TypeError):
                        pass
    
    def render_hunt_areas(self, surface: pygame.Surface):
        """Render predator hunt radius (debug)"""
        for predator in self.predators:
            pos = (int(predator.location.x), int(predator.location.y))
            radius = int(predator.hunt_radius)
            
            try:
                pygame.draw.circle(surface, (80, 0, 0), pos, radius, 1)
            except (ValueError, TypeError):
                pass
    
    def render_boids(self, surface: pygame.Surface):
        """Render all boids"""
        for boid in self.boids:
            if not boid.is_alive:
                continue
            
            x = int(boid.location.x)
            y = int(boid.location.y)
            
            # Boid color (changes with age and panic)
            age_factor = boid.age / boid.max_age
            panic_boost = min(0.3, boid.panic_level * 0.1)
            brightness = min(1.0, 0.8 + panic_boost + boid.birth_flash * 0.2)
            
            boid_color = self.hsv_to_rgb(boid.color_hue, 0.8, brightness)
            
            # Size (larger when panicked or newborn)
            size = max(1, boid.r * (1 + boid.panic_level * 0.2 + boid.birth_flash * 0.3))
            
            # Draw boid
            angle = boid.velocity.heading()
            self.draw_triangle(surface, x, y, angle, size, boid_color, boid.birth_flash)
    
    def render_predators(self, surface: pygame.Surface):
        """Render all predators"""
        for predator in self.predators:
            x = int(predator.location.x)
            y = int(predator.location.y)
            
            # Predator color (changes with kills and hunger)
            energy_factor = predator.energy / predator.max_energy
            hunger_factor = min(1.0, predator.hunger * 0.3)
            
            brightness = min(1.0, 0.7 + energy_factor * 0.3 + predator.kill_flash * 0.2)
            predator_color = self.hsv_to_rgb(predator.color_hue + hunger_factor * 30, 0.9, brightness)
            
            # Size (larger when killing or well-fed)
            size = predator.r * (1 + predator.size_pulse * 0.2 + energy_factor * 0.3)
            
            # Draw predator as larger triangle
            angle = predator.velocity.heading()
            self.draw_triangle(surface, x, y, angle, size, predator_color, predator.kill_flash)
            
            # Draw energy bar
            self.draw_energy_bar(surface, x, y - size - 8, predator.energy / predator.max_energy)
    
    def draw_triangle(self, surface: pygame.Surface, x: int, y: int, angle: float, 
                     size: float, color: Tuple[int, int, int], glow: float):
        """Draw a triangle (boid or predator)"""
        if size <= 0:
            return
        
        # Glow effect
        if glow > 0:
            glow_radius = max(1, int(size * 2 + glow * 4))
            glow_alpha = max(0, min(255, int(glow * 80)))
            
            if glow_alpha > 0:
                glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
                glow_color = (*color, glow_alpha)
                
                try:
                    pygame.draw.circle(glow_surface, glow_color,
                                     (glow_radius * 2, glow_radius * 2), glow_radius)
                    surface.blit(glow_surface, (x - glow_radius * 2, y - glow_radius * 2))
                except (ValueError, TypeError):
                    pass
        
        # Triangle points
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        front_x = x + cos_a * size * 2
        front_y = y + sin_a * size * 2
        
        back_left_x = x + math.cos(angle + 2.8) * size
        back_left_y = y + math.sin(angle + 2.8) * size
        
        back_right_x = x + math.cos(angle - 2.8) * size
        back_right_y = y + math.sin(angle - 2.8) * size
        
        points = [
            (int(front_x), int(front_y)),
            (int(back_left_x), int(back_left_y)),
            (int(back_right_x), int(back_right_y))
        ]
        
        try:
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 1)
        except (ValueError, TypeError):
            # Fallback
            try:
                pygame.draw.circle(surface, color, (x, y), max(1, int(size)))
            except (ValueError, TypeError):
                pass
    
    def draw_energy_bar(self, surface: pygame.Surface, x: int, y: int, energy_ratio: float):
        """Draw energy bar for predators"""
        bar_width = 20
        bar_height = 3
        
        # Background
        bg_rect = pygame.Rect(x - bar_width//2, y, bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect)
        
        # Energy fill
        fill_width = int(bar_width * energy_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(x - bar_width//2, y, fill_width, bar_height)
            
            # Color based on energy level
            if energy_ratio > 0.6:
                color = (0, 255, 0)  # Green
            elif energy_ratio > 0.3:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 0, 0)  # Red
            
            pygame.draw.rect(surface, color, fill_rect)
    
    def render_ecosystem_info(self, surface: pygame.Surface):
        """Render ecosystem statistics"""
        try:
            font = pygame.font.Font(None, 20)
            
            # Calculate statistics
            living_boids = len([b for b in self.boids if b.is_alive])
            avg_age = 0
            if living_boids > 0:
                avg_age = sum(b.age for b in self.boids if b.is_alive) / living_boids
            
            total_predator_energy = sum(p.energy for p in self.predators)
            total_predator_kills = sum(p.kills for p in self.predators)
            
            stats = [
                f"Prey: {living_boids}",
                f"Predators: {len(self.predators)}",
                f"Births: {self.total_births}",
                f"Deaths: {self.total_deaths}",
                f"Avg Age: {avg_age:.1f}",
                f"Predator Energy: {total_predator_energy:.0f}",
                f"Total Kills: {total_predator_kills}"
            ]
            
            for i, stat in enumerate(stats):
                text_surface = font.render(stat, True, (255, 255, 255))
                surface.blit(text_surface, (self.surface_size[0] - 150, 10 + i * 22))
        
        except:
            pass
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB"""
        h = h % 360.0
        s = max(0.0, min(1.0, float(s)))
        v = max(0.0, min(1.0, float(v)))
        
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
            max(0, min(255, int((r + m) * 255))),
            max(0, min(255, int((g + m) * 255))),
            max(0, min(255, int((b + m) * 255)))
        )
    
    def get_parameters(self) -> dict:
        """Return current parameter values for GUI controls"""
        return self.parameters.copy()
    
    def set_parameter(self, name: str, value):
        """Handle parameter changes from GUI"""
        if name in self.parameters:
            self.parameters[name] = value
            
            if hasattr(self, name):
                setattr(self, name, value)
            
            # Handle special parameter updates
            if name == 'num_predators':
                target_predators = max(1, min(5, int(value)))
                current_predators = len(self.predators)
                
                if target_predators > current_predators:
                    # Add predators
                    for _ in range(target_predators - current_predators):
                        x = random.uniform(100, self.surface_size[0] - 100)
                        y = random.uniform(100, self.surface_size[1] - 100)
                        new_predator = Predator(x, y)
                        self.predators.append(new_predator)
                elif target_predators < current_predators:
                    # Remove predators
                    self.predators = self.predators[:target_predators]
                
                self.num_predators = target_predators
                self.parameters[name] = target_predators
    
    def reset(self):
        """Reset the ecosystem"""
        self.create_initial_ecosystem()
        print(f"Reset {self.name} plugin - New ecosystem created!")
    
    def get_info(self) -> dict:
        """Get ecosystem information"""
        living_boids = len([b for b in self.boids if b.is_alive])
        return {
            'name': self.PLUGIN_NAME,
            'description': self.PLUGIN_DESCRIPTION,
            'version': self.PLUGIN_VERSION,
            'author': self.PLUGIN_AUTHOR,
            'ecosystem_age': self.ecosystem_age,
            'living_boids': living_boids,
            'predators': len(self.predators),
            'total_births': self.total_births,
            'total_deaths': self.total_deaths,
            'parameters': list(self.parameters.keys())
        }


# For standalone testing
if __name__ == "__main__":
    import pygame
    import math
    import time
    
    print("Testing Musical Ecosystem Plugin...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Musical Ecosystem - Predator vs Prey")
    clock = pygame.time.Clock()
    
    # Create plugin
    plugin = MusicalEcosystemPlugin((1000, 700))
    
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
                elif event.key == pygame.K_h:
                    plugin.show_hunt_radius = not plugin.show_hunt_radius
                elif event.key == pygame.K_t:
                    plugin.show_trails = not plugin.show_trails
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Add boid at mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_boid = Boid(mouse_x, mouse_y)
                plugin.boids.append(new_boid)
        
        # Simulate dramatic audio features
        fake_audio = {
            'amplitude': 0.5 + 0.4 * math.sin(current_time * 1.3),
            'beat_detected': (current_time % 2.0) < 0.2,
            'dominant_frequency': 440 + 400 * math.sin(current_time * 0.3),
            'frequency_bands': {
                'bass': 0.4 + 0.4 * math.sin(current_time * 0.5),  # Drives predator aggression
                'mid': 0.3 + 0.3 * math.sin(current_time * 0.8),   # Encourages reproduction
                'treble': 0.2 + 0.3 * math.sin(current_time * 1.2) # Calms the flock
            }
        }
        
        # Update ecosystem
        plugin.update(fake_audio, dt)
        
        # Render
        screen.fill((8, 12, 20))  # Dark ocean background
        plugin.render(screen)
        
        # Display controls
        try:
            font = pygame.font.Font(None, 24)
            controls = [
                "🎵 Musical Ecosystem - Living Predator-Prey System",
                "Click: Add Prey | SPACE: Reset | H: Hunt Radius | T: Trails"
            ]
            
            for i, line in enumerate(controls):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()
    print("Musical Ecosystem test completed")
