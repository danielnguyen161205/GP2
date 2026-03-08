import pygame
import random

class PowerUp:
    """Class for power-up items that spawn on the map"""
    
    TYPES = {
        'health': {
            'color': (255, 50, 50),      # Red
            'icon_color': (255, 255, 255),
            'symbol': '+',
            'duration': 0,  # Instant effect
        },
        'speed': {
            'color': (50, 200, 255),     # Cyan
            'icon_color': (255, 255, 255),
            'symbol': '»',
            'duration': 5000,  # 5 seconds in milliseconds
        }
    }
    
    def __init__(self, x, y, powerup_type='health'):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.size = 30
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.active = True
        
        # Visual effects
        self.pulse = 0
        self.rotation = 0
        
        # Get type properties
        self.properties = self.TYPES.get(powerup_type, self.TYPES['health'])
    
    def update(self):
        """Update powerup animations"""
        self.pulse += 0.1
        self.rotation += 2
        if self.rotation >= 360:
            self.rotation = 0
    
    def draw(self, surface):
        """Draw the powerup with visual effects"""
        if not self.active:
            return
        
        # Pulsing effect
        pulse_size = int(self.size + abs(pygame.math.Vector2(0, 5).rotate(self.pulse * 50).y))
        
        # Draw outer glow
        glow_surface = pygame.Surface((pulse_size + 10, pulse_size + 10), pygame.SRCALPHA)
        glow_color = (*self.properties['color'], 100)
        pygame.draw.circle(glow_surface, glow_color, 
                          (pulse_size//2 + 5, pulse_size//2 + 5), pulse_size//2 + 5)
        surface.blit(glow_surface, (self.x - pulse_size//2 - 5, self.y - pulse_size//2 - 5))
        
        # Draw main circle
        pygame.draw.circle(surface, self.properties['color'], (int(self.x), int(self.y)), pulse_size//2)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), pulse_size//2, 2)
        
        # Draw icon/symbol
        font = pygame.font.SysFont(None, 32)
        text = font.render(self.properties['symbol'], True, self.properties['icon_color'])
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text, text_rect)
    
    def collect(self, tank):
        """Apply powerup effect to tank"""
        self.active = False
        
        if self.type == 'health':
            # Restore 1 health point
            if tank.health < tank.max_health:
                tank.health += 1
                return True
        elif self.type == 'speed':
            # Apply speed boost
            tank.apply_speed_boost(self.properties['duration'])
            return True
        
        return False

class SpeedBoost:
    """Tracks speed boost effect on a tank"""
    def __init__(self, duration):
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.boost_multiplier = 1.5
    
    def is_active(self):
        return pygame.time.get_ticks() - self.start_time < self.duration
    
    def get_remaining_time(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, self.duration - elapsed)
        return remaining / 1000  # Convert to seconds
