#!/usr/bin/env python3
"""
CarrotOS Theme Engine - System-wide theme management
Supports: Dark/Light themes, custom icons, color schemes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import shutil
import os

@dataclass
class ColorScheme:
    """Color scheme definition"""
    name: str
    primary: str
    secondary: str
    accent: str
    foreground: str
    background: str
    success: str
    warning: str
    error: str

@dataclass
class Theme:
    """Theme definition"""
    name: str
    variant: str  # "light" or "dark"
    colors: ColorScheme
    fonts: Dict[str, str]
    icons: str  # icon theme name
    description: str

class ThemeManager:
    """Manage system themes"""
    
    THEMES_DIR = Path("/usr/share/carrot/themes")
    ICONS_DIR = Path("/usr/share/carrot/icons")
    CONFIG_FILE = Path("/etc/carrot-desktop/themes.conf")
    USER_THEME_DIR = Path.home() / ".config" / "carrot" / "themes"
    
    # Default themes
    DEFAULT_THEMES = {
        'carrot-light': {
            'variant': 'light',
            'colors': {
                'primary': '#ffffff',
                'secondary': '#f5f5f5',
                'accent': '#ff8c00',
                'foreground': '#000000',
                'background': '#ffffff',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
            },
            'fonts': {
                'default': 'Sans 10',
                'monospace': 'Monospace 10',
                'title': 'Sans Bold 14',
            },
            'icons': 'carrot-icons-light',
            'description': 'Light theme with orange accent',
        },
        'carrot-dark': {
            'variant': 'dark',
            'colors': {
                'primary': '#1e1e2e',
                'secondary': '#2a2a3e',
                'accent': '#ff8c00',
                'foreground': '#ffffff',
                'background': '#1e1e2e',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
            },
            'fonts': {
                'default': 'Sans 10',
                'monospace': 'Monospace 10',
                'title': 'Sans Bold 14',
            },
            'icons': 'carrot-icons-dark',
            'description': 'Dark theme with orange accent',
        },
        'carrot-system': {
            'variant': 'auto',
            'colors': {
                'primary': '#ffffff',
                'secondary': '#f5f5f5',
                'accent': '#ff8c00',
                'foreground': '#000000',
                'background': '#ffffff',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
            },
            'fonts': {
                'default': 'Sans 10',
                'monospace': 'Monospace 10',
                'title': 'Sans Bold 14',
            },
            'icons': 'carrot-icons-system',
            'description': 'System-dependent theme',
        },
    }
    
    # Icon themes
    ICON_THEMES = {
        'carrot-icons-light': {
            'description': 'Light icon theme',
            'inherits': 'Adwaita',
            'directories': ['actions', 'apps', 'categories', 'devices', 'mimetypes', 'places', 'status'],
        },
        'carrot-icons-dark': {
            'description': 'Dark icon theme',
            'inherits': 'Adwaita-dark',
            'directories': ['actions', 'apps', 'categories', 'devices', 'mimetypes', 'places', 'status'],
        },
        'carrot-icons-system': {
            'description': 'System icon theme',
            'inherits': 'Adwaita',
            'directories': ['actions', 'apps', 'categories', 'devices', 'mimetypes', 'places', 'status'],
        },
    }
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[str] = None
        self.icon_themes: Dict[str, Dict] = ICON_THEMES.copy()
        self.load_themes()
        self.load_config()
    
    def ensure_directories(self):
        """Create required directories"""
        for d in [self.THEMES_DIR, self.ICONS_DIR, self.USER_THEME_DIR]:
            d.mkdir(parents=True, exist_ok=True)
    
    def load_themes(self):
        """Load all available themes"""
        self.ensure_directories()
        
        # Load built-in themes
        for theme_name, theme_data in self.DEFAULT_THEMES.items():
            colors = ColorScheme(
                name=theme_name,
                **theme_data['colors']
            )
            
            theme = Theme(
                name=theme_name,
                variant=theme_data['variant'],
                colors=colors,
                fonts=theme_data['fonts'],
                icons=theme_data['icons'],
                description=theme_data['description'],
            )
            
            self.themes[theme_name] = theme
        
        # Load user themes
        if self.USER_THEME_DIR.exists():
            for theme_file in self.USER_THEME_DIR.glob('*.json'):
                try:
                    theme_data = json.loads(theme_file.read_text())
                    colors = ColorScheme(
                        name=theme_data['name'],
                        **theme_data['colors']
                    )
                    
                    theme = Theme(
                        name=theme_data['name'],
                        variant=theme_data.get('variant', 'dark'),
                        colors=colors,
                        fonts=theme_data.get('fonts', {}),
                        icons=theme_data.get('icons', 'carrot-icons-dark'),
                        description=theme_data.get('description', ''),
                    )
                    
                    self.themes[theme_data['name']] = theme
                except Exception as e:
                    print(f"Error loading theme {theme_file}: {e}")
    
    def load_config(self):
        """Load theme configuration"""
        if self.CONFIG_FILE.exists():
            try:
                config = json.loads(self.CONFIG_FILE.read_text())
                self.current_theme = config.get('current_theme', 'carrot-dark')
            except:
                self.current_theme = 'carrot-dark'
        else:
            self.current_theme = 'carrot-dark'
    
    def save_config(self):
        """Save theme configuration"""
        config = {
            'current_theme': self.current_theme,
            'timestamp': str(__import__('datetime').datetime.now()),
        }
        
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.CONFIG_FILE.write_text(json.dumps(config, indent=2))
    
    def set_theme(self, theme_name: str) -> bool:
        """Set active theme"""
        if theme_name not in self.themes:
            print(f"Theme not found: {theme_name}")
            return False
        
        self.current_theme = theme_name
        self.save_config()
        
        # Apply theme globally
        self.apply_theme(theme_name)
        
        print(f"Theme changed to: {theme_name}")
        return True
    
    def apply_theme(self, theme_name: str):
        """Apply theme to system"""
        theme = self.themes.get(theme_name)
        if not theme:
            return
        
        # Write GTK+ theme files
        self.apply_gtk_theme(theme)
        
        # Update icon theme
        self.apply_icon_theme(theme.icons)
        
        # Update Qt theme (if available)
        self.apply_qt_theme(theme)
    
    def apply_gtk_theme(self, theme: Theme):
        """Apply GTK+ theme settings"""
        # Create GTK settings file
        settings_dir = Path.home() / ".config" / "gtk-3.0"
        settings_dir.mkdir(parents=True, exist_ok=True)
        
        settings_content = f"""
[Settings]
gtk-theme-name={self.current_theme}
gtk-icon-theme-name={theme.icons}
gtk-font-name={theme.fonts.get('default', 'Sans 10')}
gtk-application-prefer-dark-theme={'true' if theme.variant == 'dark' else 'false'}
gtk-cursor-theme-name=default
gtk-cursor-theme-size=24
gtk-toolbar-style=GTK_TOOLBAR_BOTH_HORIZ
gtk-toolbar-icon-size=GTK_ICON_SIZE_LARGE_TOOLBAR
gtk-button-images=true
gtk-menu-images=true
gtk-enable-event-sounds=false
gtk-enable-input-feedback-sounds=false
"""
        
        settings_file = settings_dir / "settings.ini"
        settings_file.write_text(settings_content)
    
    def apply_icon_theme(self, icon_theme: str):
        """Apply icon theme"""
        # Create icon theme index
        icons_dir = self.ICONS_DIR / icon_theme
        icons_dir.mkdir(parents=True, exist_ok=True)
        
        index_content = f"""[Icon Theme]
Name={icon_theme}
Comment=CarrotOS icon theme
Inherits=Adwaita
Example=folder

Directories=actions,apps,categories,devices,mimetypes,places,status

[actions]
Size=16
Type=Fixed

[apps]
Size=32
Type=Scalable

[categories]
Size=32
Type=Scalable

[devices]
Size=32
Type=Scalable

[mimetypes]
Size=32
Type=Scalable

[places]
Size=32
Type=Scalable

[status]
Size=16
Type=Fixed
"""
        
        index_file = icons_dir / "index.theme"
        index_file.write_text(index_content)
    
    def apply_qt_theme(self, theme: Theme):
        """Apply Qt theme settings"""
        qt_config_dir = Path.home() / ".config" / "qt5ct"
        qt_config_dir.mkdir(parents=True, exist_ok=True)
        
        dark_mode = theme.variant == 'dark'
        
        qt_content = f"""[General]
style=Fusion
palette_scheme={"dark" if dark_mode else "light"}
"""
        
        qt_file = qt_config_dir / "qt5ct.conf"
        qt_file.write_text(qt_content)
    
    def create_custom_theme(self, name: str, variant: str, 
                           colors: Dict[str, str], icons: str) -> bool:
        """Create custom theme"""
        try:
            color_scheme = ColorScheme(
                name=name,
                primary=colors.get('primary', '#ffffff'),
                secondary=colors.get('secondary', '#f5f5f5'),
                accent=colors.get('accent', '#ff8c00'),
                foreground=colors.get('foreground', '#000000'),
                background=colors.get('background', '#ffffff'),
                success=colors.get('success', '#4caf50'),
                warning=colors.get('warning', '#ff9800'),
                error=colors.get('error', '#f44336'),
            )
            
            theme = Theme(
                name=name,
                variant=variant,
                colors=color_scheme,
                fonts=self.DEFAULT_THEMES['carrot-dark']['fonts'],
                icons=icons,
                description=f"Custom {variant} theme",
            )
            
            # Save theme
            theme_file = self.USER_THEME_DIR / f"{name}.json"
            theme_data = {
                'name': name,
                'variant': variant,
                'colors': asdict(color_scheme),
                'fonts': theme.fonts,
                'icons': icons,
                'description': theme.description,
            }
            
            theme_file.write_text(json.dumps(theme_data, indent=2))
            
            self.themes[name] = theme
            print(f"Theme created: {name}")
            return True
        
        except Exception as e:
            print(f"Error creating theme: {e}")
            return False
    
    def delete_theme(self, theme_name: str) -> bool:
        """Delete custom theme"""
        try:
            theme_file = self.USER_THEME_DIR / f"{theme_name}.json"
            
            if theme_file.exists():
                theme_file.unlink()
            
            if theme_name in self.themes:
                del self.themes[theme_name]
            
            print(f"Theme deleted: {theme_name}")
            return True
        except Exception as e:
            print(f"Error deleting theme: {e}")
            return False
    
    def export_theme(self, theme_name: str, export_path: Path) -> bool:
        """Export theme to file"""
        try:
            theme = self.themes.get(theme_name)
            if not theme:
                return False
            
            theme_data = {
                'name': theme.name,
                'variant': theme.variant,
                'colors': asdict(theme.colors),
                'fonts': theme.fonts,
                'icons': theme.icons,
                'description': theme.description,
            }
            
            export_path.write_text(json.dumps(theme_data, indent=2))
            print(f"Theme exported to: {export_path}")
            return True
        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, import_path: Path) -> bool:
        """Import theme from file"""
        try:
            if not import_path.exists():
                print(f"Theme file not found: {import_path}")
                return False
            
            theme_data = json.loads(import_path.read_text())
            
            # Save to user themes
            save_path = self.USER_THEME_DIR / import_path.name
            shutil.copy(import_path, save_path)
            
            # Reload themes
            self.load_themes()
            
            print(f"Theme imported: {theme_data.get('name', 'Unknown')}")
            return True
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(name)
    
    def get_all_themes(self) -> List[str]:
        """Get all available themes"""
        return list(self.themes.keys())
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get current active theme"""
        if self.current_theme:
            return self.themes.get(self.current_theme)
        return None

def main():
    """Test theme manager"""
    manager = ThemeManager()
    
    print(f"Available themes: {manager.get_all_themes()}")
    print(f"Current theme: {manager.current_theme}")
    
    # Set dark theme
    manager.set_theme('carrot-dark')
    
    # Create custom theme
    custom_colors = {
        'primary': '#2c3e50',
        'secondary': '#34495e',
        'accent': '#3498db',
        'foreground': '#ecf0f1',
        'background': '#2c3e50',
    }
    
    manager.create_custom_theme('my-blue', 'dark', custom_colors, 'carrot-icons-dark')

if __name__ == '__main__':
    main()
