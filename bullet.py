import pygame
import math
from settings import BULLET_SPEED, GREEN_LIGHT, PERM_PIERCE_MAX_HITS, PERM_SPLIT_SPEED, SCREEN_W, SCREEN_H


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, pierce=False, stage=1, split=False, _is_child=False):
        super().__init__()
        self.pierce     = pierce
        self.split      = split
        self._is_child  = _is_child   # i figli non si sdoppiano di nuovo
        self.hits_left  = PERM_PIERCE_MAX_HITS if pierce else 1
        self.stage      = stage
        self._hit_enemies = set()

        color = (255, 220, 80) if pierce else (180, 255, 100) if split else GREEN_LIGHT

        if stage in (1, 3):
            self.image = pygame.Surface((5, 14), pygame.SRCALPHA)
            pygame.draw.rect(self.image, color, (0, 0, 5, 14), border_radius=2)
            self.rect = self.image.get_rect(centerx=x, bottom=y)
            rad = math.radians(angle)
            self.vx =  math.sin(rad) * BULLET_SPEED
            self.vy = -math.cos(rad) * BULLET_SPEED
        else:
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
        if self.rect.bottom < 0 or self.rect.top > SCREEN_H + 20:
            self.kill()
        if self.rect.right < 0 or self.rect.left > SCREEN_W + 20:
            self.kill()

    def on_hit(self):
        """Ritorna True se il proiettile deve sparire."""
        self.hits_left -= 1
        if self.hits_left <= 0:
            self.kill()
            return True
        return False

    def spawn_children(self):
        """Crea i due proiettili figli dopo lo split. Da chiamare prima di kill()."""
        if self._is_child or not self.split:
            return []
        # Calcola angolo corrente del proiettile
        angle = math.degrees(math.atan2(self.vx, -self.vy))
        children = []
        for offset in [-30, 30]:
            child = Bullet(
                int(self._x), int(self._y),
                angle=angle + offset,
                pierce=self.pierce,
                stage=self.stage,
                split=False,
                _is_child=True
            )
            # Imposta la velocità manualmente per usare PERM_SPLIT_SPEED
            rad = math.radians(angle + offset)
            if self.stage in (1, 3):
                child.vx =  math.sin(rad) * PERM_SPLIT_SPEED
                child.vy = -math.cos(rad) * PERM_SPLIT_SPEED
            else:
                child.vx =  math.cos(rad) * PERM_SPLIT_SPEED
                child.vy =  math.sin(rad) * PERM_SPLIT_SPEED
            children.append(child)
        return children
