import pygame
from settings import SCREEN_H, SCREEN_W, ENEMY_BULLET_SPEED


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 240, 100), (0, 0, 5, 10), border_radius=2)
        self.rect  = self.image.get_rect(centerx=x, top=y)
        self._y    = float(self.rect.y)

    def update(self):
        self._y += ENEMY_BULLET_SPEED
        self.rect.y = int(self._y)
        if self.rect.top > SCREEN_H:
            self.kill()
