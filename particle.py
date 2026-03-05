import pygame
import random

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Vận tốc ngẫu nhiên văng ra mọi hướng
        self.velocity_x = random.uniform(-4, 4)
        self.velocity_y = random.uniform(-4, 4)
        
        # Thời gian tồn tại (số khung hình) và kích thước
        self.lifetime = random.randint(20, 40)
        self.radius = random.randint(3, 7)
        
        # Random màu sắc của vụ nổ (Đỏ, Cam, Vàng)
        colors = [(255, 69, 0), (255, 140, 0), (255, 215, 0), (255, 0, 0)]
        self.color = random.choice(colors)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        # Hạt nhỏ dần theo thời gian
        if self.radius > 0:
            self.radius -= 0.15

    def draw(self, surface):
        if self.lifetime > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))