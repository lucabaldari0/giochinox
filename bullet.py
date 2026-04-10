import pygame
import math
from settings import BULLET_SPEED, GREEN_LIGHT, PERM_PIERCE_MAX_HITS


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, pierce=False, stage=1):
        super().__init__()
        self.pierce    = pierce
        self.hits_left = PERM_PIERCE_MAX_HITS if pierce else 1
        self.stage     = stage

        color = (255, 220, 80) if pierce else GREEN_LIGHT

        if stage == 1:
            # Proiettile verticale, angolo in gradi dalla verticale
            self.image = pygame.Surface((5, 14), pygame.SRCALPHA)
            pygame.draw.rect(self.image, color, (0, 0, 5, 14), border_radius=2)
            self.rect = self.image.get_rect(centerx=x, bottom=y)
            rad = math.radians(angle)
            self.vx =  math.sin(rad) * BULLET_SPEED
            self.vy = -math.cos(rad) * BULLET_SPEED
        else:
            # Proiettile orizzontale, va verso destra
            self.image = pygame.Surface((14, 5), pygame.SRCALPHA)
            pygame.draw.rect(self.image, color, (0, 0, 14, 5), border_radius=2)
            self.rect = self.image.get_rect(left=x, centery=y)
            rad = math.radians(angle)
            self.vx =  math.cos(rad) * BULLET_SPEED
            self.vy =  math.sin(rad) * BULLET_SPEED

        self._x = float(self.rect.centerx)
        self._y = float(self.rect.centery)

    def update(self):
        self._x += self.vx
        self._y += self.vy
        self.rect.center = (int(self._x), int(self._y))
        # Esce dallo schermo
        if self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()
        if self.rect.right < 0 or self.rect.left > SCREEN_W + 20:
            self.kill()

    def on_hit(self):
        self.hits_left -= 1
        if self.hits_left <= 0:
            self.kill()
            return True
        return False


# Importazione lazy per evitare import circolari
from settings import SCREEN_W
