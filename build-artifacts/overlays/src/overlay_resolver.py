#!/usr/bin/env python3
"""
CarrotOS Overlay Resolver
Builds and manages the overlay filesystem stack
"""

import json
import yaml
import sys
from pathlib import Path
from typing import List, Dict

class OverlayLayer:
    """Represents a single overlay layer"""
    
    def __init__(self, name: str, path: str, readonly: bool = False):
        self.name = name
        self.path = path
        self.readonly = readonly
        
    def __dict__(self):
        return {
            'name': self.name,
            'path': self.path,
            'readonly': self.readonly
        }

class OverlayStack:
    """Manages the complete overlay stack"""
    
    def __init__(self):
        self.layers: List[OverlayLayer] = []
        
    def add_layer(self, layer: OverlayLayer):
        """Add layer to stack (order matters)"""
        self.layers.append(layer)
        
    def load_manifest(self, manifest_path: str):
        """Load overlay manifest file"""
        with open(manifest_path, 'r') as f:
            config = yaml.safe_load(f)
            
        if not config:
            print("Error: Invalid manifest file", file=sys.stderr)
            return False
            
        for layer_config in config.get('layers', []):
            layer = OverlayLayer(
                layer_config['name'],
                layer_config['path'],
                layer_config.get('readonly', False)
            )
            self.add_layer(layer)
            
        return True
        
    def resolve_stack(self) -> List[str]:
        """Return layer paths in mounting order (bottom to top)"""
        return [layer.path for layer in self.layers]
        
    def print_stack(self):
        """Print current stack for debugging"""
        print("[overlay] Resolved stack:")
        for i, layer in enumerate(self.layers):
            access = "RO" if layer.readonly else "RW"
            print(f"  [{i}] {layer.name} ({access}): {layer.path}")


def main():
    overlay_manifest = Path("/etc/carrot/overlays.yaml")
    
    if len(sys.argv) > 1:
        overlay_manifest = Path(sys.argv[1])
    
    if not overlay_manifest.exists():
        print(f"Error: Manifest not found: {overlay_manifest}", file=sys.stderr)
        return 1
        
    stack = OverlayStack()
    if not stack.load_manifest(str(overlay_manifest)):
        return 1
        
    stack.print_stack()
    print(f"[overlay] Stack ready with {len(stack.layers)} layers")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
