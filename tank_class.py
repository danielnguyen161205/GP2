import pygame
import math

class Tank:
    PLAYER1_KEYS = {
        'forward': pygame.K_w,
        'backward': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
        'turret_left': pygame.K_q,
        'turret_right': pygame.K_e,
    }
    
    PLAYER2_KEYS = {
        'forward': pygame.K_UP,
        'backward': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'turret_left': pygame.K_COMMA,
        'turret_right': pygame.K_PERIOD,
    }
    
    def __init__(self, x, y, player_number=1, speed=5):
        self.x = x
        self.y = y
        self.player_number = player_number
        self.speed = speed
        self.angle = 0  # Tank body angle
        self.turret_angle = 0  # Independent turret angle
        self.velocity_x = 0
        self.velocity_y = 0
        self.image = None
        self.rect = None
        
        # Health and scoring system
        self.max_health = 3
        self.health = self.max_health
        self.kills = 0
        
        self.original_sprite_path = "./assets/tankBlue.png" if player_number==1 else "./assets/tankRed.png"
        self.load_sprite(self.original_sprite_path)
        
        # Load turret/barrel sprite
        self.barrel_sprite_path = "./assets/barrelBlue.png" if player_number==1 else "./assets/barrelRed.png"
        self.load_barrel_sprite(self.barrel_sprite_path)
        
        self.keys = self.PLAYER1_KEYS if player_number == 1 else self.PLAYER2_KEYS

        self.last_shot_time = 0
        self.shoot_cooldown = 1000  # shoot Cooldown
        self.bullet_img = "./assets/bulletBlue.png" if player_number == 1 else "./assets/bulletRed.png"
    
    def load_sprite(self, sprite_path):
        try:
            self.original_image = pygame.image.load(sprite_path).convert_alpha()
            self.image = self.original_image.copy()
            self.rect = self.image.get_rect(center=(self.x, self.y))
        except FileNotFoundError:
            print(f"Error: Sprite file not found at {sprite_path}")
    
    def load_barrel_sprite(self, barrel_path):
        try:
            barrel_temp = pygame.image.load(barrel_path).convert_alpha()
            # Scale barrel to 50% of original size for better proportion
            barrel_width = int(barrel_temp.get_width() * 0.5)
            barrel_height = int(barrel_temp.get_height() * 0.5)
            self.original_barrel = pygame.transform.scale(barrel_temp, (barrel_width, barrel_height))
            self.barrel_length = barrel_height  # Store actual barrel length for bullet spawn
            self.barrel_image = self.original_barrel.copy()
            self.barrel_rect = self.barrel_image.get_rect(center=(self.x, self.y))
            # Initial rotation to set proper pivot
            self.rotate_barrel()
        except FileNotFoundError:
            print(f"Error: Barrel sprite not found at {barrel_path}")
            raise
        except pygame.error as e:
            print(f"Error: Could not load sprite: {e}")
            raise
    
    def _calculate_velocity(self):
        angle_rad = math.radians(self.angle+90) #add 90 as the tank face up when it first appear
        self.velocity_x = self.speed * math.cos(angle_rad)
        self.velocity_y = self.speed * math.sin(angle_rad) * -1 # Multiply by -1 as inverted Pygame's y-axis
    
    def handle_input(self):
        keys_pressed = pygame.key.get_pressed()
        body_angle_changed = False
        turret_angle_changed = False

        # Tank body rotation
        if keys_pressed[self.keys['left']]:
            self.angle += 5
            body_angle_changed = True
        if keys_pressed[self.keys['right']]:
            self.angle -= 5
            body_angle_changed = True
        
        if body_angle_changed:
            self.angle = self.angle % 360
            self.rotate_sprite()    # Only rotate body when tank changes angle
        
        # Independent turret rotation
        if keys_pressed[self.keys['turret_left']]:
            self.turret_angle += 3
            turret_angle_changed = True
        if keys_pressed[self.keys['turret_right']]:
            self.turret_angle -= 3
            turret_angle_changed = True
        
        if turret_angle_changed:
            self.turret_angle = self.turret_angle % 360
            self.rotate_barrel()    # Rotate turret independently

        if keys_pressed[self.keys['forward']]:
            self._calculate_velocity()
        elif keys_pressed[self.keys['backward']]:
            self._calculate_velocity()
            self.velocity_x *= -1
            self.velocity_y *= -1
        else:
            self.velocity_x = 0
            self.velocity_y = 0
    
    def update(self, walls=None):
        self.handle_input()
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        if self.rect:
            self.rect.centerx = new_x
            self.rect.centery = new_y
            if not self.check_collision(walls):
                self.x = new_x
                self.y = new_y
            else:
                self.rect.centerx = self.x
                self.rect.centery = self.y
        else:
            self.x = new_x
            self.y = new_y
    
    def check_collision(self, walls):
        if not walls or not self.rect:
            return False
        return self.rect.collidelist(walls) != -1
    
    def rotate_sprite(self):
        if self.original_image:
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
    
    def rotate_barrel(self):
        if self.original_barrel:
            self.barrel_image = pygame.transform.rotate(self.original_barrel, self.turret_angle)
            # Keep pivot point at tank center instead of barrel center
            # The pivot is at the bottom-center of the barrel (where it connects to tank)
            self.barrel_rect = self.barrel_image.get_rect()
            # Offset to position barrel so its base (pivot) is at tank center
            pivot_offset_y = self.original_barrel.get_height() // 3  # Adjust pivot point
            angle_rad = math.radians(self.turret_angle + 90)
            offset_x = -pivot_offset_y * math.cos(angle_rad)
            offset_y = pivot_offset_y * math.sin(angle_rad)
            self.barrel_rect.center = (self.x + offset_x, self.y + offset_y)
    
    def draw(self, surface):
        if self.image and self.rect:
            # Draw tank body
            surface.blit(self.image, self.rect)
            
            # Draw turret/barrel on top of tank body
            if self.barrel_image and self.barrel_rect:
                # Update barrel position to follow tank
                self.rotate_barrel()  # This updates barrel_rect position
                surface.blit(self.barrel_image, self.barrel_rect)
            
            # Draw health bar above tank
            self.draw_health_bar(surface)
    
    def get_position(self):
        return (self.x, self.y)
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
        if self.rect:
            self.rect.center = (x, y)
    
    def get_angle(self):
        return self.angle
    
    def set_angle(self, angle):
        self.angle = angle % 360
    
    def take_damage(self, damage=1):
        """Reduce tank health by damage amount"""
        self.health -= damage
        return self.health <= 0  # Return True if tank is dead
    
    def reset_health(self):
        """Reset tank health to maximum"""
        self.health = self.max_health
    
    def draw_health_bar(self, surface):
        """Draw health bar above the tank"""
        bar_width = 50
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 40  # Position above tank
        
        # Background (empty health)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect)
        pygame.draw.rect(surface, (200, 200, 200), bg_rect, 1)
        
        # Foreground (current health)
        health_width = int((self.health / self.max_health) * bar_width)
        if self.health > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            # Color based on player
            color = (100, 150, 255) if self.player_number == 1 else (255, 100, 100)
            pygame.draw.rect(surface, color, health_rect)

    def shoot(self):
        from bullet_class import Bullet # Import class đạn

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            
            # Shoot from turret angle instead of body angle
            # Đạn bắn ngược hướng, nên spawn ở đầu gốc của barrel (phía gần tank)
            tip_distance = self.barrel_length * 0.15  # Distance from tank center to barrel base
            angle_rad = math.radians(self.turret_angle + 90)
            spawn_x = self.x + tip_distance * math.cos(angle_rad)
            spawn_y = self.y - tip_distance * math.sin(angle_rad) # Pygame Y ngược
            
            # Reverse bullet direction by adding 180 degrees
            bullet_angle = (self.turret_angle + 180) % 360
            return Bullet(spawn_x, spawn_y, bullet_angle, self.bullet_img, self.player_number)
        return None