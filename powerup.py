import pygame
import random
from settings import SCREEN_H, SCREEN_W, POWERUP_SPEED, POWERUP_COLORS


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind, stage=1):
        super().__init__()
        self.kind  = kind
        self.stage = stage
        self.color = POWERUP_COLORS[kind]
        self.image = self._make_surface()
        self.rect  = self.image.get_rect(centerx=x, top=y)
        self._x    = float(self.rect.x)
        self._y    = float(self.rect.y)
        self._frame = 0

    def _make_surface(self):
        surf = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (11, 11), 11)
        if self.kind == "life":
            pygame.draw.circle(surf, (255, 255, 255), (8, 9), 4)
            pygame.draw.circle(surf, (255, 255, 255), (14, 9), 4)
            pygame.draw.polygon(surf, (255, 255, 255), [(4, 11), (18, 11), (11, 18)])
        elif self.kind == "doubleshoot":
            pygame.draw.polygon(surf, (255, 255, 255), [(7, 5), (4, 11), (10, 11)])
            pygame.draw.polygon(surf, (255, 255, 255), [(15, 5), (12, 11), (18, 11)])
        elif self.kind == "shield":
            pygame.draw.polygon(surf, (255, 255, 255),
                                 [(11, 4), (18, 8), (18, 13), (11, 18), (4, 13), (4, 8)])
        return surf

    def update(self):
        self._frame += 1
        oscillation = 1.5 * pygame.math.Vector2(1, 0).rotate(self._frame * 3).x * 0.3

        if self.stage == 1:
            self._y += POWERUP_SPEED
            self._x += oscillation
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)
            if self.rect.top > SCREEN_H:
                self.kill()
        else:
            self._x -= POWERUP_SPEED
            self._y += oscillation
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)
            if self.rect.right < 0:
                self.kill()
