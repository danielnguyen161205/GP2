import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color, text_color=(255, 255, 255)):
        # x, y là tọa độ điểm giữa (center) của nút bấm
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hover_scale = 1.0
        self.target_scale = 1.0

    def draw(self, surface):
        # Lấy vị trí chuột hiện tại để làm hiệu ứng Hover
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(mouse_pos)
        
        # Smooth scaling animation
        self.target_scale = 1.05 if is_hovering else 1.0
        self.hover_scale += (self.target_scale - self.hover_scale) * 0.2
        
        # Calculate scaled rect
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_rect.center = self.rect.center
        
        # Draw shadow effect
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Draw button with gradient effect
        color = self.hover_color if is_hovering else self.base_color
        
        # Main button body
        pygame.draw.rect(surface, color, scaled_rect, border_radius=10)
        
        # Lighter top for 3D effect
        top_color = tuple(min(255, c + 30) for c in color)
        top_rect = pygame.Rect(scaled_rect.x, scaled_rect.y, scaled_rect.width, scaled_rect.height // 3)
        pygame.draw.rect(surface, top_color, top_rect, border_radius=10)
        pygame.draw.rect(surface, top_color, scaled_rect, border_radius=10)
        
        # Draw border with glow effect when hovering
        border_color = tuple(min(255, c + 50) for c in self.text_color) if is_hovering else self.text_color
        border_width = 3 if is_hovering else 2
        pygame.draw.rect(surface, border_color, scaled_rect, border_width, border_radius=10)

        # Render text with shadow
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        
        # Text shadow
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(scaled_rect.centerx + 2, scaled_rect.centery + 2))
        surface.blit(shadow_surf, shadow_rect)
        
        # Main text
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        # Kiểm tra xem có sự kiện click chuột trái vào nút không
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False