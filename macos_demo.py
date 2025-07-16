#!/usr/bin/env python3
'''
Simple Demo - macOS Compatible
Run both plugins in sequence without GUI issues
'''

import pygame
import time
import math

def run_demo():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dynamic Art Generator - macOS Demo")
    clock = pygame.time.Clock()
    
    # Try to import plugins
    try:
        from plugins.pendulum_plugin import PendulumPlugin
        from plugins.particles_plugin import ParticlePlugin
        plugins = [
            PendulumPlugin((800, 600)),
            ParticlePlugin((800, 600))
        ]
        current_plugin = 0
    except ImportError as e:
        print(f"Could not import plugins: {e}")
        return
    
    print("🎨 Demo Controls:")
    print("   SPACE: Switch between plugins")
    print("   R: Reset current plugin")
    print("   ESC: Exit")
    
    start_time = time.time()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    current_plugin = (current_plugin + 1) % len(plugins)
                    print(f"Switched to: {plugins[current_plugin].name}")
                elif event.key == pygame.K_r:
                    plugins[current_plugin].reset()
        
        # Simulate audio
        fake_audio = {
            'amplitude': 0.5 + 0.3 * math.sin(current_time * 2),
            'beat_detected': (current_time % 1.2) < 0.1,
            'dominant_frequency': 440 + 200 * math.sin(current_time * 0.5),
            'frequency_bands': {
                'bass': 0.3 + 0.2 * math.sin(current_time),
                'mid': 0.4 + 0.3 * math.sin(current_time * 1.5),
                'treble': 0.2 + 0.1 * math.sin(current_time * 2)
            }
        }
        
        # Update and render
        screen.fill((20, 20, 30))
        
        plugin = plugins[current_plugin]
        plugin.update(fake_audio, dt)
        plugin.render(screen)
        
        # Show info
        try:
            font = pygame.font.Font(None, 24)
            info = f"{plugin.name} Plugin - Press SPACE to switch"
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 10))
        except:
            pass
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    run_demo()
