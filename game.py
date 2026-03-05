import pygame
import sys
from tank_class import Tank
from level_map import LEVEL_MAP
from button import Button
from particle import Particle

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # <--- KHỞI TẠO HỆ THỐNG ÂM THANH

        self.TILE_SIZE = 50
        
        self.LEVEL_MAP = LEVEL_MAP
        
        self.map_width = len(self.LEVEL_MAP[0]) * self.TILE_SIZE
        self.map_height = len(self.LEVEL_MAP) * self.TILE_SIZE
        
        self.world_surface = pygame.Surface((self.map_width, self.map_height))
        
        MIN_WIDTH, MIN_HEIGHT = 800, 600
        self.WIDTH = max(self.map_width, MIN_WIDTH)
        self.HEIGHT = max(self.map_height, MIN_HEIGHT)

        self.offset_x = (self.WIDTH - self.map_width) // 2
        self.offset_y = (self.HEIGHT - self.map_height) // 2

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
        
        self.state = "START"  # Các trạng thái: "START", "PLAYING", "GAME_OVER"
        self.winner = None
        self.running = True

        self.setup_ui_buttons()
        self.setup_level()

    def setup_ui_buttons(self):
        """Khởi tạo các nút bấm cho giao diện"""
        center_x = self.WIDTH // 2
        
        # Màu sắc: (R, G, B)
        btn_base = (70, 130, 180)   # Xanh bưu điện
        btn_hover = (100, 150, 200) # Xanh nhạt hơn khi hover
        btn_exit_base = (180, 50, 50)
        btn_exit_hover = (220, 80, 80)

        # Nút cho màn hình START
        self.start_btn = Button(center_x, 120, 200, 40, "START", self.button_font, btn_base, btn_hover)
        self.exit_btn = Button(center_x, 180, 200, 40, "EXIT", self.button_font, btn_exit_base, btn_exit_hover)

        # Nút cho màn hình GAME OVER
        self.play_again_btn = Button(center_x, 130, 200, 40, "PLAY AGAIN", self.button_font, btn_base, btn_hover)
        self.menu_btn = Button(center_x, 190, 200, 40, "MAIN MENU", self.button_font, btn_base, btn_hover)

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
                    self.state = "PLAYING"
                elif self.exit_btn.is_clicked(event):
                    self.running = False
            
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

    def draw(self):
        """Render giao diện tùy theo State"""
        self.screen.fill((20, 20, 20))

        self.world_surface.fill((40, 40, 40))
        
        # MÀN HÌNH BẮT ĐẦU
        if self.state == "START":
            title = self.title_font.render("TANK MAZE", True, (255, 215, 0))
            self.screen.blit(title, title.get_rect(center=(self.WIDTH//2, 50)))
            self.start_btn.draw(self.screen)
            self.exit_btn.draw(self.screen)

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
            
            for bullet in self.bullets:
                bullet.draw(self.world_surface)

            for p in self.particles: # <--- VẼ PARTICLES LÊN WORLD SURFACE
                p.draw(self.world_surface)

            self.screen.blit(self.world_surface, (self.offset_x, self.offset_y))
            
            # Draw HUD on top of game screen
            self.draw_hud()
        
        # CHỒNG THÊM UI GAME OVER LÊN TRÊN
            if self.state == "GAME_OVER":
                overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                self.screen.blit(overlay, (0, 0))
                
                win_text = self.title_font.render(f"{self.winner} WINS!", True, (255, 50, 50))
                self.screen.blit(win_text, win_text.get_rect(center=(self.WIDTH//2, 60)))
                
                # Vẽ 2 nút ở màn hình Game Over
                self.play_again_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)

        pygame.display.flip()

    def draw_hud(self):
        """Draw HUD showing player kills and info"""
        hud_height = 60
        padding = 20
        
        # Semi-transparent background for HUD
        hud_bg = pygame.Surface((self.WIDTH, hud_height), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        self.screen.blit(hud_bg, (0, 0))
        
        # Player 1 HUD (Left side)
        p1_text = self.hud_font.render("PLAYER 1", True, (100, 150, 255))
        self.screen.blit(p1_text, (padding, 10))
        
        # Player 1 Kills
        kills_text = self.hud_font.render(f"Kills: {self.player1.kills}", True, (255, 255, 255))
        self.screen.blit(kills_text, (padding + 150, 10))
        
        # Player 2 HUD (Right side)
        p2_text = self.hud_font.render("PLAYER 2", True, (255, 100, 100))
        p2_text_rect = p2_text.get_rect(topright=(self.WIDTH - padding, 10))
        self.screen.blit(p2_text, p2_text_rect)
        
        # Player 2 Kills
        kills2_text = self.hud_font.render(f"Kills: {self.player2.kills}", True, (255, 255, 255))
        kills2_rect = kills2_text.get_rect(topright=(self.WIDTH - padding - 150, 10))
        self.screen.blit(kills2_text, kills2_rect)

    def run(self):
        """Vòng lặp chính của game"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()