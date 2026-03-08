import pygame
import sys
import random
from tank_class import Tank
from level_map import LEVEL_MAP, LEVEL_MAPS
from button import Button
from particle import Particle
from powerup import PowerUp

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # <--- KHỞI TẠO HỆ THỐNG ÂM THANH

        self.TILE_SIZE = 50
        self.HUD_HEIGHT = 80  # Reserve space for HUD at top
        
        self.LEVEL_MAP = LEVEL_MAP
        self.current_map_index = 0  # Track current map
        
        self.map_width = len(self.LEVEL_MAP[0]) * self.TILE_SIZE
        self.map_height = len(self.LEVEL_MAP) * self.TILE_SIZE
        
        self.world_surface = pygame.Surface((self.map_width, self.map_height))
        
        MIN_WIDTH, MIN_HEIGHT = 800, 600
        self.WIDTH = max(self.map_width, MIN_WIDTH)
        # Add HUD_HEIGHT to total height to ensure space for HUD
        self.HEIGHT = max(self.map_height + self.HUD_HEIGHT, MIN_HEIGHT)

        self.offset_x = (self.WIDTH - self.map_width) // 2
        # Offset map below HUD
        self.offset_y = max(self.HUD_HEIGHT, (self.HEIGHT - self.map_height) // 2)

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Tank Battle")
        self.clock = pygame.time.Clock()

        # --- TẢI ÂM THANH TỪ THƯ MỤC ASSETS ---
        self.sfx_shoot, self.sfx_bounce, self.sfx_explode = None, None, None
        try:
            self.sfx_shoot = pygame.mixer.Sound("assets/shoot.mp3")
            self.sfx_shoot.set_volume(0.3) # Chỉnh âm lượng nhỏ bớt (0.0 -> 1.0)
            self.sfx_bounce = pygame.mixer.Sound("assets/bounce.mp3")
            self.sfx_bounce.set_volume(0.5)
            self.sfx_explode = pygame.mixer.Sound("assets/explode.mp3")
            self.sfx_explode.set_volume(0.8)
        except Exception as e:
            print(f"No sfx files in assets/: {e}")

        # Font chữ dùng chung cho game
        self.title_font = pygame.font.SysFont(None, 74)
        self.info_font = pygame.font.SysFont(None, 36)
        self.button_font = pygame.font.SysFont(None, 36)
        
        self.walls = []
        self.bullets = []
        p1_start, p2_start = (100, 100), (self.WIDTH-100, self.HEIGHT-100)
        self.walls, self.bullets, self.particles = [], [], [] # <--- Thêm mảng particles
        self.powerups = []  # Power-up items
        
        # Powerup spawn settings
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 10000  # Spawn every 10 seconds
        
        self.state = "START"  # Các trạng thái: "START", "INSTRUCTIONS", "PLAYING", "GAME_OVER"
        self.winner = None
        self.running = True

        self.setup_ui_buttons()
        self.setup_level()

    def setup_ui_buttons(self):
        """Khởi tạo các nút bấm cho giao diện"""
        center_x = self.WIDTH // 2
        
        # Màu sắc đẹp hơn: (R, G, B)
        btn_base = (41, 128, 185)      # Xanh dương hiện đại
        btn_hover = (52, 152, 219)     # Xanh sáng khi hover
        btn_exit_base = (192, 57, 43)  # Đỏ đậm
        btn_exit_hover = (231, 76, 60) # Đỏ sáng
        btn_info_base = (39, 174, 96)  # Xanh lá
        btn_info_hover = (46, 204, 113) # Xanh lá sáng

        # Nút cho màn hình START
        self.start_btn = Button(center_x, 180, 240, 50, "START GAME", self.button_font, btn_base, btn_hover)
        self.instructions_btn = Button(center_x, 250, 240, 50, "INSTRUCTIONS", self.button_font, btn_info_base, btn_info_hover)
        self.exit_btn = Button(center_x, 320, 240, 50, "EXIT", self.button_font, btn_exit_base, btn_exit_hover)

        # Nút cho màn hình GAME OVER
        self.play_again_btn = Button(center_x, 160, 240, 50, "PLAY AGAIN", self.button_font, btn_base, btn_hover)
        self.menu_btn = Button(center_x, 230, 240, 50, "MAIN MENU", self.button_font, btn_base, btn_hover)
        
        # Nút cho màn hình INSTRUCTIONS
        self.back_btn = Button(center_x, self.HEIGHT - 80, 200, 50, "BACK", self.button_font, btn_base, btn_hover)

    def load_random_map(self):
        """Select a random map from available maps"""
        self.current_map_index = random.randint(0, len(LEVEL_MAPS) - 1)
        self.LEVEL_MAP = LEVEL_MAPS[self.current_map_index]
        
        # Recalculate map dimensions
        self.map_width = len(self.LEVEL_MAP[0]) * self.TILE_SIZE
        self.map_height = len(self.LEVEL_MAP) * self.TILE_SIZE
        
        # Recreate world surface with new dimensions
        self.world_surface = pygame.Surface((self.map_width, self.map_height))
        
        # Recalculate screen height to fit map + HUD
        self.HEIGHT = max(self.map_height + self.HUD_HEIGHT, 600)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        # Recalculate offsets for centering (map below HUD)
        self.offset_x = (self.WIDTH - self.map_width) // 2
        self.offset_y = max(self.HUD_HEIGHT, (self.HEIGHT - self.map_height) // 2)
        
        # Clear and reload level
        self.walls.clear()
        self.setup_level()

    def setup_level(self):
        """Đọc map và khởi tạo tường, người chơi"""        
        for r_idx, row in enumerate(self.LEVEL_MAP):
            for c_idx, char in enumerate(row):
                x, y = c_idx * self.TILE_SIZE, r_idx * self.TILE_SIZE
                if char == "W": 
                    self.walls.append(pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE))
                elif char == "1": 
                    self.p1_start = (x + self.TILE_SIZE//2, y + self.TILE_SIZE//2)
                elif char == "2": 
                    self.p2_start = (x + self.TILE_SIZE//2, y + self.TILE_SIZE//2)

        self.reset_game()

    def reset_game(self):
        self.bullets.clear()
        self.particles.clear() # <--- Xóa hiệu ứng nổ cũ
        self.powerups.clear()  # Clear powerups
        self.powerup_spawn_timer = pygame.time.get_ticks()  # Reset spawn timer
        self.winner=None

        # Save kill counts if players exist
        p1_kills = self.player1.kills if hasattr(self, 'player1') else 0
        p2_kills = self.player2.kills if hasattr(self, 'player2') else 0

        self.player1 = Tank(x=self.p1_start[0], y=self.p1_start[1], player_number=1, speed=4)
        self.player2 = Tank(x=self.p2_start[0], y=self.p2_start[1], player_number=2, speed=4)
        
        # Restore kill counts
        self.player1.kills = p1_kills
        self.player2.kills = p2_kills
        
        # Initialize HUD font
        self.hud_font = pygame.font.SysFont(None, 32)
        self.hud_large_font = pygame.font.SysFont(None, 48)

    def handle_events(self):
        """Xử lý thao tác phím và sự kiện hệ thống"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                self.running = False

            if self.state == "START":
                if self.start_btn.is_clicked(event):
                    self.load_random_map()  # Load a random map
                    self.state = "PLAYING"
                elif self.instructions_btn.is_clicked(event):
                    self.state = "INSTRUCTIONS"
                elif self.exit_btn.is_clicked(event):
                    self.running = False
            
            elif self.state == "INSTRUCTIONS":
                if self.back_btn.is_clicked(event):
                    self.state = "START"
            
            elif self.state == "GAME_OVER":
                if self.play_again_btn.is_clicked(event):
                    self.reset_game()
                    self.state = "PLAYING"
                elif self.menu_btn.is_clicked(event):
                    # Reset kills when going back to main menu
                    if hasattr(self, 'player1'):
                        self.player1.kills = 0
                    if hasattr(self, 'player2'):
                        self.player2.kills = 0
                    self.reset_game()
                    self.state = "START"
            
            # Nếu đang TRONG TRẬN -> Nhận lệnh bắn đạn
            elif self.state == "PLAYING" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f or event.key==pygame.K_SPACE:
                    b = self.player1.shoot()
                    if b: 
                        self.bullets.append(b)
                        if self.sfx_shoot: self.sfx_shoot.play()
                if event.key == pygame.K_m or event.key==pygame.K_RETURN:
                    b = self.player2.shoot()
                    if b: 
                        self.bullets.append(b)
                        if self.sfx_shoot: self.sfx_shoot.play()

    def explode_tank(self, loser_tank):
        """Hàm kích hoạt vụ nổ tại vị trí xe tăng thua cuộc"""
        if self.sfx_explode: 
            self.sfx_explode.play() # Phát tiếng nổ
        # Tạo 40 hạt lửa văng ra từ tâm xe tăng
        for _ in range(40):
            self.particles.append(Particle(loser_tank.x, loser_tank.y))

    def update(self):
        """Cập nhật logic, vị trí, va chạm (Physics/Logic) KHI PLAYING"""
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        if self.state != "PLAYING":
            return

        self.player1.update(walls=self.walls)
        self.player2.update(walls=self.walls)

        for bullet in self.bullets[:]:
            bounced = bullet.update(self.walls)
            if bounced and self.sfx_bounce:
                self.sfx_bounce.play() # <--- PHÁT ÂM TIẾNG DỘI TƯỜNG

            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            # Hit logic with health system
            if bullet.rect.colliderect(self.player1.rect) and (bullet.owner == 2 or bullet.bounces > 0):
                self.bullets.remove(bullet)
                if self.player1.take_damage(1):  # Tank is dead
                    self.winner = "PLAYER 2"
                    self.player2.kills += 1
                    self.explode_tank(self.player1)
                    self.state = "GAME_OVER"
            elif bullet.rect.colliderect(self.player2.rect) and (bullet.owner == 1 or bullet.bounces > 0):
                self.bullets.remove(bullet)
                if self.player2.take_damage(1):  # Tank is dead
                    self.winner = "PLAYER 1"
                    self.player1.kills += 1
                    self.explode_tank(self.player2)
                    self.state = "GAME_OVER"
        
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
        
        # Check powerup collection
        for powerup in self.powerups[:]:
            if powerup.active:
                if powerup.rect.colliderect(self.player1.rect):
                    if powerup.collect(self.player1):
                        self.powerups.remove(powerup)
                elif powerup.rect.colliderect(self.player2.rect):
                    if powerup.collect(self.player2):
                        self.powerups.remove(powerup)
        
        # Spawn powerups periodically
        current_time = pygame.time.get_ticks()
        if current_time - self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_spawn_timer = current_time
    
    def spawn_powerup(self):
        """Spawn a random powerup at a random location"""
        # Find valid spawn location (not on walls or too close to tanks)
        max_attempts = 20
        for _ in range(max_attempts):
            x = random.randint(50, self.map_width - 50)
            y = random.randint(50, self.map_height - 50)
            
            # Check if location is valid (not on wall)
            spawn_rect = pygame.Rect(x - 15, y - 15, 30, 30)
            if spawn_rect.collidelist(self.walls) == -1:
                # Randomly choose powerup type
                powerup_type = random.choice(['health', 'speed'])
                self.powerups.append(PowerUp(x, y, powerup_type))
                break

    def draw(self):
        """Render giao diện tùy theo State"""
        # Gradient background
        self.draw_gradient_background()

        self.world_surface.fill((40, 40, 40))
        
        # MÀN HÌNH BẮT ĐẦU
        if self.state == "START":
            self.draw_start_screen()
        
        # MÀN HÌNH INSTRUCTIONS
        elif self.state == "INSTRUCTIONS":
            self.draw_instructions_screen()

        elif self.state == "PLAYING" or self.state == "GAME_OVER":
            try:
                # load wall.png image and scale it to TILE_SIZE
                wall_image_original = pygame.image.load("./assets/wall.png").convert_alpha()
                wall_image = pygame.transform.scale(wall_image_original, (self.TILE_SIZE, self.TILE_SIZE))
                for wall in self.walls:
                    self.world_surface.blit(wall_image, wall)
            except Exception as e:
                print("Draw default wall image as no wall.png image used")
                for wall in self.walls:
                    pygame.draw.rect(self.world_surface, (139, 69, 19), wall)
                    pygame.draw.rect(self.world_surface, (0, 0, 0), wall, 2)
                
            self.player1.draw(self.world_surface)
            self.player2.draw(self.world_surface)
            
            # Draw powerups
            for powerup in self.powerups:
                powerup.draw(self.world_surface)
            
            for bullet in self.bullets:
                bullet.draw(self.world_surface)

            for p in self.particles: # <--- VẼ PARTICLES LÊN WORLD SURFACE
                p.draw(self.world_surface)

            self.screen.blit(self.world_surface, (self.offset_x, self.offset_y))
            
            # Draw HUD on top of game screen
            self.draw_hud()
        
        # CHỒNG THÊM UI GAME OVER LÊN TRÊN
            if self.state == "GAME_OVER":
                # Animated overlay with pulse effect
                overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                
                # Winner box with border
                box_width = 500
                box_height = 250
                box_x = (self.WIDTH - box_width) // 2
                box_y = 40
                
                # Box shadow
                shadow_rect = pygame.Rect(box_x + 5, box_y + 5, box_width, box_height)
                pygame.draw.rect(self.screen, (0, 0, 0, 150), shadow_rect, border_radius=15)
                
                # Main box
                box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
                pygame.draw.rect(self.screen, (30, 30, 40), box_rect, border_radius=15)
                
                # Glowing border
                winner_color = (100, 200, 255) if "1" in self.winner else (255, 100, 100)
                pygame.draw.rect(self.screen, winner_color, box_rect, 4, border_radius=15)
                
                # Winner text with shadow
                win_shadow = self.title_font.render(f"{self.winner} WINS!", True, (0, 0, 0))
                self.screen.blit(win_shadow, win_shadow.get_rect(center=(self.WIDTH//2 + 3, 93)))
                
                win_text = self.title_font.render(f"{self.winner} WINS!", True, winner_color)
                self.screen.blit(win_text, win_text.get_rect(center=(self.WIDTH//2, 90)))
                
                # Trophy or victory icon (simple star)
                self.draw_victory_stars(self.WIDTH//2, 90)
                
                # Vẽ 2 nút ở màn hình Game Over
                self.play_again_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)

        pygame.display.flip()

    def draw_gradient_background(self):
        """Vẽ nền gradient đẹp mắt"""
        for i in range(self.HEIGHT):
            color_value = int(20 + (i / self.HEIGHT) * 30)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 10), 
                           (0, i), (self.WIDTH, i))
    
    def draw_victory_stars(self, center_x, center_y):
        """Vẽ các ngôi sao trang trí xung quanh chữ WINS"""
        import math
        winner_color = (255, 215, 0)  # Gold color for stars
        
        # Draw stars at different positions
        star_positions = [
            (center_x - 200, center_y - 10),
            (center_x + 200, center_y - 10),
            (center_x - 180, center_y + 15),
            (center_x + 180, center_y + 15),
        ]
        
        for pos in star_positions:
            self.draw_star(self.screen, pos[0], pos[1], 15, winner_color)
    
    def draw_star(self, surface, x, y, size, color):
        """Vẽ một ngôi sao 5 cánh"""
        import math
        points = []
        for i in range(10):
            angle = math.pi / 2 + (2 * math.pi * i / 10)
            radius = size if i % 2 == 0 else size / 2
            point_x = x + radius * math.cos(angle)
            point_y = y - radius * math.sin(angle)
            points.append((point_x, point_y))
        
        pygame.draw.polygon(surface, color, points)

    def draw_start_screen(self):
        """Vẽ màn hình chính với tiêu đề đẹp"""
        # Vẽ tiêu đề với hiệu ứng shadow
        title_text = "TANK BATTLE"
        # Shadow
        shadow = self.title_font.render(title_text, True, (0, 0, 0))
        self.screen.blit(shadow, shadow.get_rect(center=(self.WIDTH//2 + 3, 83)))
        # Main title với gradient effect (vàng sang cam)
        title = self.title_font.render(title_text, True, (255, 215, 0))
        self.screen.blit(title, title.get_rect(center=(self.WIDTH//2, 80)))
        
        # Subtitle
        subtitle = self.info_font.render("A 2-Player Tank Combat Game", True, (200, 200, 200))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.WIDTH//2, 130)))
        
        # Map info
        small_font = pygame.font.SysFont(None, 28)
       
        
        # Draw buttons
        self.start_btn.draw(self.screen)
        self.instructions_btn.draw(self.screen)
        self.exit_btn.draw(self.screen)

    def draw_instructions_screen(self):
        """Vẽ màn hình hướng dẫn"""
        # Title
        title = self.title_font.render("HOW TO PLAY", True, (255, 215, 0))
        self.screen.blit(title, title.get_rect(center=(self.WIDTH//2, 50)))
        
        # Instructions content - more compact
        instructions = [
            "PLAYER 1 (Blue Tank):",
            "  W/A/S/D - Move  |  SPACE/F - Shoot  |  Q/E - Rotate Turret",
            "",
            "PLAYER 2 (Red Tank):",
            "  Arrow Keys - Move  |  ENTER/M - Shoot  |  ,/. - Rotate Turret",
            "",
            "POWER-UPS:",
            "  + (Red) - Restore 1 Health",
            "  » (Blue) - Speed Boost (5 seconds)",
            "GAME RULES:",
            "  • Each tank has 3 HP",
            "  • Bullets bounce off walls",
            "  • Collect power-ups to gain advantage",
            "  • Press ESC to exit anytime",
        ]
        
        y_start = 110
        line_spacing = 27
        for i, line in enumerate(instructions):
            if line.startswith("PLAYER"):
                color = (100, 200, 255) if "1" in line else (255, 100, 100)
                text = self.info_font.render(line, True, color)
            elif line.startswith("POWER-UPS") or line.startswith("GAME"):
                color = (255, 215, 0)
                text = self.info_font.render(line, True, color)
            elif line.startswith("  "):
                # Smaller font for details
                detail_font = pygame.font.SysFont(None, 30)
                text = detail_font.render(line, True, (220, 220, 220))
            else:
                text = self.info_font.render(line, True, (255, 255, 255))
            
            self.screen.blit(text, (self.WIDTH//2 - 300, y_start + i * line_spacing))
        
        # Draw back button
        self.back_btn.draw(self.screen)

    def draw_hud(self):
        """Draw enhanced HUD showing player kills and info"""
        hud_height = self.HUD_HEIGHT  # Use consistent HUD height
        padding = 20
        
        # Semi-transparent background with gradient for HUD
        hud_bg = pygame.Surface((self.WIDTH, hud_height), pygame.SRCALPHA)
        for i in range(hud_height):
            alpha = int(180 - (i / hud_height) * 50)
            pygame.draw.line(hud_bg, (0, 0, 0, alpha), (0, i), (self.WIDTH, i))
        self.screen.blit(hud_bg, (0, 0))
        
        # Decorative line at bottom of HUD (thicker separator)
        pygame.draw.line(self.screen, (255, 215, 0), (0, hud_height), (self.WIDTH, hud_height), 3)
        
        # Shadow below HUD for better separation
        shadow_surface = pygame.Surface((self.WIDTH, 10), pygame.SRCALPHA)
        for i in range(10):
            alpha = int(80 - (i * 8))
            pygame.draw.line(shadow_surface, (0, 0, 0, alpha), (0, i), (self.WIDTH, i))
        self.screen.blit(shadow_surface, (0, hud_height))
        
        # Player 1 HUD (Left side) with icon background
        p1_bg = pygame.Surface((280, 50), pygame.SRCALPHA)
        p1_bg.fill((41, 128, 185, 100))
        self.screen.blit(p1_bg, (padding, 10))
        
        p1_text = self.hud_font.render("PLAYER 1", True, (100, 200, 255))
        self.screen.blit(p1_text, (padding + 10, 12))
        
        # Player 1 Kills with better styling
        kills_bg = pygame.Rect(padding + 160, 15, 100, 30)
        pygame.draw.rect(self.screen, (30, 90, 140), kills_bg, border_radius=5)
        pygame.draw.rect(self.screen, (100, 200, 255), kills_bg, 2, border_radius=5)
        kills_text = self.hud_font.render(f"Kills: {self.player1.kills}", True, (255, 255, 255))
        self.screen.blit(kills_text, (padding + 165, 18))
        
        # Player 2 HUD (Right side) with icon background
        p2_bg = pygame.Surface((280, 50), pygame.SRCALPHA)
        p2_bg.fill((192, 57, 43, 100))
        self.screen.blit(p2_bg, (self.WIDTH - padding - 280, 10))
        
        p2_text = self.hud_font.render("PLAYER 2", True, (255, 100, 100))
        p2_text_rect = p2_text.get_rect(topright=(self.WIDTH - padding - 10, 12))
        self.screen.blit(p2_text, p2_text_rect)
        
        # Player 2 Kills with better styling
        kills2_bg = pygame.Rect(self.WIDTH - padding - 260, 15, 100, 30)
        pygame.draw.rect(self.screen, (140, 40, 30), kills2_bg, border_radius=5)
        pygame.draw.rect(self.screen, (255, 100, 100), kills2_bg, 2, border_radius=5)
        kills2_text = self.hud_font.render(f"Kills: {self.player2.kills}", True, (255, 255, 255))
        kills2_rect = kills2_text.get_rect(topright=(self.WIDTH - padding - 165, 18))
        self.screen.blit(kills2_text, kills2_rect)
        
        # Map indicator in center
        map_names = ["Classic Maze", "Arena", "Corridors", "Center Box", "Cross Pattern", "Diagonal"]
        map_font = pygame.font.SysFont(None, 28)
        map_text = map_font.render(f"Map: {map_names[self.current_map_index]}", True, (255, 215, 0))
        map_rect = map_text.get_rect(center=(self.WIDTH // 2, 25))
        self.screen.blit(map_text, map_rect)
        
        # Speed boost indicators
        small_font = pygame.font.SysFont(None, 24)
        
        # Player 1 speed boost
        if self.player1.has_speed_boost():
            boost_time = self.player1.speed_boost.get_remaining_time()
            boost_text = small_font.render(f"SPEED: {boost_time:.1f}s", True, (50, 200, 255))
            self.screen.blit(boost_text, (padding + 10, 48))
        
        # Player 2 speed boost
        if self.player2.has_speed_boost():
            boost_time = self.player2.speed_boost.get_remaining_time()
            boost_text = small_font.render(f"SPEED: {boost_time:.1f}s", True, (50, 200, 255))
            boost_rect = boost_text.get_rect(topright=(self.WIDTH - padding - 10, 48))
            self.screen.blit(boost_text, boost_rect)

    def run(self):
        """Vòng lặp chính của game"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()