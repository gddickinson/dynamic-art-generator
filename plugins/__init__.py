#!/usr/bin/env python3
"""
Dynamic Art Generator - Plugins Package
Plugin discovery and management system

Author: Claude Assistant
Version: 1.0
"""

import os
import importlib
import inspect
from typing import List, Dict, Type
from abc import ABC, abstractmethod

# Base plugin class (can be imported from here)
class ArtPlugin(ABC):
    """Base class for all art plugins"""
    
    def __init__(self, name: str, surface_size: tuple):
        self.name = name
        self.surface_size = surface_size
        self.is_active = False
        self.parameters = {}
        self.last_update = 0
    
    @abstractmethod
    def update(self, audio_features: dict, dt: float):
        """Update the plugin state based on audio and time"""
        pass
    
    @abstractmethod
    def render(self, surface):
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
        pass


class PluginManager:
    """Manages plugin discovery and loading"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_classes = {}
        self.plugin_directory = os.path.dirname(__file__)
    
    def discover_plugins(self) -> Dict[str, Type[ArtPlugin]]:
        """Discover all available plugin classes"""
        self.plugin_classes.clear()
        
        # Get all Python files in the plugins directory
        for filename in os.listdir(self.plugin_directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                
                try:
                    # Import the module
                    module = importlib.import_module(f'plugins.{module_name}')
                    
                    # Look for plugin classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, ArtPlugin) and 
                            obj != ArtPlugin):
                            
                            plugin_name = getattr(obj, 'PLUGIN_NAME', name)
                            self.plugin_classes[plugin_name] = obj
                            print(f"Discovered plugin: {plugin_name}")
                
                except Exception as e:
                    print(f"Error loading plugin {module_name}: {e}")
        
        return self.plugin_classes
    
    def create_plugin(self, plugin_name: str, surface_size: tuple) -> ArtPlugin:
        """Create an instance of a plugin"""
        if plugin_name in self.plugin_classes:
            try:
                return self.plugin_classes[plugin_name](surface_size)
            except Exception as e:
                print(f"Error creating plugin {plugin_name}: {e}")
                return None
        else:
            print(f"Plugin {plugin_name} not found")
            return None
    
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugin names"""
        return list(self.plugin_classes.keys())
    
    def reload_plugins(self):
        """Reload all plugins (for development)"""
        # Clear import cache for plugin modules
        import sys
        modules_to_remove = []
        for module_name in sys.modules:
            if module_name.startswith('plugins.') and module_name != 'plugins':
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
        
        # Rediscover plugins
        self.discover_plugins()


# Global plugin manager instance
plugin_manager = PluginManager()

def get_available_plugins():
    """Get available plugins (convenience function)"""
    plugin_manager.discover_plugins()
    return plugin_manager.get_available_plugins()

def create_plugin(plugin_name: str, surface_size: tuple):
    """Create a plugin instance (convenience function)"""
    return plugin_manager.create_plugin(plugin_name, surface_size)

# Auto-discover plugins when module is imported
plugin_manager.discover_plugins()
