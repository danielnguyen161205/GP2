import pygame
import math

class Bullet:
    def __init__(self, x, y, angle, image_path, owner, speed=8):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.owner = owner # ID của người bắn (1 hoặc 2)
        self.bounces = 0
        self.max_bounces = 10
        self.active = True

        # Tải và xoay ảnh đạn
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        except:
            # Fallback nếu không có ảnh: Tạo một khối màu nhỏ
            self.original_image = pygame.Surface((6, 15), pygame.SRCALPHA)
            self.original_image.fill((255, 200, 0) if owner == 1 else (0, 255, 255))

        # Xoay ảnh cho đúng hướng
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Tính vận tốc (Pygame Y ngược)
        angle_rad = math.radians(self.angle + 90)
        self.velocity_x = self.speed * math.cos(angle_rad)
        self.velocity_y = self.speed * math.sin(angle_rad) * -1

    def update(self, walls):
        bounced=False
        # 1. Di chuyển trục X và kiểm tra nảy mặt dọc (Trái/Phải)
        self.x += self.velocity_x
        self.rect.centerx = int(self.x)
        if self._check_bounce(walls, 'x'): bounced=True

        # 2. Di chuyển trục Y và kiểm tra nảy mặt ngang (Trên/Dưới)
        self.y += self.velocity_y
        self.rect.centery = int(self.y)
        if self._check_bounce(walls, 'y'): bounced=True

        # Hủy đạn nếu quá 10 lần nảy
        if self.bounces >= self.max_bounces:
            self.active = False
        return bounced

    def _check_bounce(self, walls, axis):
        for wall in walls:
            if self.rect.colliderect(wall):
                if axis == 'x':
                    self.velocity_x *= -1  # Phản xạ trục X
                    # Đẩy đạn ra khỏi tường để tránh kẹt
                    if self.velocity_x > 0: self.rect.left = wall.right
                    else: self.rect.right = wall.left
                    self.x = self.rect.centerx
                elif axis == 'y':
                    self.velocity_y *= -1  # Phản xạ trục Y
                    if self.velocity_y > 0: self.rect.top = wall.bottom
                    else: self.rect.bottom = wall.top
                    self.y = self.rect.centery
                
                self.bounces += 1
                self._update_rotation() # Xoay lại ảnh đạn sau khi dội
                return True
        return False
    
    def _update_rotation(self):
        # Tính lại góc quay từ vận tốc mới và xoay ảnh
        new_angle_rad = math.atan2(-self.velocity_y, self.velocity_x)
        new_angle_deg = math.degrees(new_angle_rad) - 90
        self.image = pygame.transform.rotate(self.original_image, new_angle_deg)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)