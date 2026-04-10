import pygame
import random
from settings import SCREEN_W, SCREEN_H, ENEMY_TYPES, POWERUP_DROP_RATES


class Enemy(pygame.sprite.Sprite):
    def __init__(self, kind, stage=1):
        super().__init__()
        self.kind  = kind
        self.stage = stage
        self.max_hp, self.color, self.color_lt, speed_base, self.points = ENEMY_TYPES[kind]
        self.hp    = self.max_hp
        self.speed = speed_base + random.uniform(-0.2, 0.4)

        size       = 30 if kind == "purple" else 24
        self.image = self._make_surface(size)

        if stage == 1:
            self.rect = self.image.get_rect(
                centerx=random.randint(20, SCREEN_W - 20),
                bottom=0
            )
            self._base_x = float(self.rect.x)
            self._base_y = float(self.rect.y)
        else:
            # Stage 2: entrano da destra
            self.rect = self.image.get_rect(
                left=SCREEN_W,
                centery=random.randint(20, SCREEN_H - 20)
            )
            self._base_x = float(self.rect.x)
            self._base_y = float(self.rect.y)

        self._dir   = random.choice([-1, 1])
        self._frame = random.randint(0, 100)

    def _make_surface(self, size):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        half = size // 2
        points = [(half, size), (0, half // 2), (half // 4, 0), (3 * half // 4, 0), (size, half // 2)]
        inner  = [(half, size - 8), (6, half), (half, 6), (size - 6, half)]
        pygame.draw.polygon(surf, self.color, points)
        pygame.draw.polygon(surf, self.color_lt, inner)
        if self.stage == 2:
            surf = pygame.transform.rotate(surf, 90)
        return surf

    def update(self):
        self._frame += 1

        if self.stage == 1:
            self.rect.y += self.speed
            # Arancioni rimbalzano lateralmente
            if self.kind == "orange":
                self._base_x += self.speed * 1.2 * self._dir
                if self._base_x <= 0:
                    self._base_x = 0
                    self._dir = 1
                elif self._base_x >= SCREEN_W - self.rect.width:
                    self._base_x = SCREEN_W - self.rect.width
                    self._dir = -1
                self.rect.x = int(self._base_x)
            if self.rect.top > SCREEN_H:
                self.kill()
                return "escaped"

        else:
            self.rect.x -= self.speed
            # Arancioni rimbalzano su e giu
            if self.kind == "orange":
                self._base_y += self.speed * 1.2 * self._dir
                if self._base_y <= 0:
                    self._base_y = 0
                    self._dir = 1
                elif self._base_y >= SCREEN_H - self.rect.height:
                    self._base_y = SCREEN_H - self.rect.height
                    self._dir = -1
                self.rect.y = int(self._base_y)
            if self.rect.right < 0:
                self.kill()
                return "escaped"

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def get_drop(self):
        kind, rate = POWERUP_DROP_RATES[self.kind]
        if random.random() < rate:
            return kind
        return None

    def draw_hp_bar(self, surface):
        if self.hp == self.max_hp:
            return
        bar_w  = self.rect.width
        filled = int(bar_w * self.hp / self.max_hp)
        bar_rect = pygame.Rect(self.rect.x, self.rect.top - 6, bar_w, 4)
        pygame.draw.rect(surface, (80, 80, 80), bar_rect, border_radius=2)
        pygame.draw.rect(surface, self.color_lt, (*bar_rect.topleft, filled, 4), border_radius=2)