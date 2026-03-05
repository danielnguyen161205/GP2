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

    def draw(self, surface):
        # Lấy vị trí chuột hiện tại để làm hiệu ứng Hover
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect, border_radius=8)
        else:
            pygame.draw.rect(surface, self.base_color, self.rect, border_radius=8)
        
        # Vẽ viền cho nút bấm
        pygame.draw.rect(surface, self.text_color, self.rect, 2, border_radius=8)

        # Render và căn giữa chữ bên trong nút
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        # Kiểm tra xem có sự kiện click chuột trái vào nút không
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False