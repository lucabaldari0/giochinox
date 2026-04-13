import pygame
import math
import os
from settings import BULLET_SPEED, GREEN_LIGHT, PERM_PIERCE_MAX_HITS, PERM_SPLIT_SPEED, SCREEN_W, SCREEN_H

BUBBLE_SHEET_PATH = os.path.join("assets", "bubble_spritesheet.png")
BUBBLE_FRAME_SIZE = 32
BUBBLE_FRAME_COUNT = 7
BUBBLE_ANIM_SPEED = 7   # cambia frame ogni 7 frame di gioco

_bubble_frames_v = None   # verticale (stage 1/3/infinito)
_bubble_frames_h = None   # orizzontale (stage 2)

def _load_bubble_frames():
    global _bubble_frames_v, _bubble_frames_h
    if _bubble_frames_v is not None:
        return
    if os.path.exists(BUBBLE_SHEET_PATH):
        sheet = pygame.image.load(BUBBLE_SHEET_PATH).convert_alpha()
        frames = []
        for i in range(BUBBLE_FRAME_COUNT):
            frame = sheet.subsurface((i * BUBBLE_FRAME_SIZE, 0, BUBBLE_FRAME_SIZE, BUBBLE_FRAME_SIZE))
            frames.append(frame)
        _bubble_frames_v = [pygame.transform.rotate(f, 90) for f in frames]
        _bubble_frames_h = frames   # originale e gia orizzontale
    else:
        # Fallback geometrico
        surf_v = pygame.Surface((10, 14), pygame.SRCALPHA)
        pygame.draw.rect(surf_v, GREEN_LIGHT, (0, 0, 10, 14), border_radius=5)
        surf_h = pygame.transform.rotate(surf_v, -90)
        _bubble_frames_v = [surf_v] * BUBBLE_FRAME_COUNT
        _bubble_frames_h = [surf_h] * BUBBLE_FRAME_COUNT


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, pierce=False, stage=1, split=False, _is_child=False):
        super().__init__()
        _load_bubble_frames()

        self.pierce       = pierce
        self.split        = split
        self._is_child    = _is_child
        self.hits_left    = PERM_PIERCE_MAX_HITS if pierce else 1
        self.stage        = stage
        self._hit_enemies = set()
        self._anim_frame  = 0
        self._anim_timer  = 0

        # Scegli frames in base allo stage
        frames = _bubble_frames_h if stage == 2 else _bubble_frames_v
        self.image = frames[0]

        if stage in (1, 3) or stage == 0:  # 0 = infinito trattato come verticale
            self.rect = self.image.get_rect(centerx=x, bottom=y)
            rad = math.radians(angle)
            self.vx =  math.sin(rad) * BULLET_SPEED
            self.vy = -math.cos(rad) * BULLET_SPEED
        else:
            self.rect = self.image.get_rect(left=x, centery=y)
            rad = math.radians(angle)
            self.vx =  math.cos(rad) * BULLET_SPEED
            self.vy =  math.sin(rad) * BULLET_SPEED

        self._x = float(self.rect.centerx)
        self._y = float(self.rect.centery)

    def update(self):
        # Animazione bollicina
        self._anim_timer += 1
        if self._anim_timer >= BUBBLE_ANIM_SPEED:
            self._anim_timer = 0
            self._anim_frame = (self._anim_frame + 1) % BUBBLE_FRAME_COUNT
        frames = _bubble_frames_h if self.stage == 2 else _bubble_frames_v
        self.image = frames[self._anim_frame]

        # Movimento
        self._x += self.vx
        self._y += self.vy
        self.rect.center = (int(self._x), int(self._y))

        if self.rect.bottom < 0 or self.rect.top > SCREEN_H + 20:
            self.kill()
        if self.rect.right < 0 or self.rect.left > SCREEN_W + 20:
            self.kill()

    def on_hit(self):
        self.hits_left -= 1
        if self.hits_left <= 0:
            self.kill()
            return True
        return False

    def spawn_children(self):
        if self._is_child or not self.split:
            return []
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
            rad = math.radians(angle + offset)
            if self.stage in (1, 3):
                child.vx =  math.sin(rad) * PERM_SPLIT_SPEED
                child.vy = -math.cos(rad) * PERM_SPLIT_SPEED
            else:
                child.vx =  math.cos(rad) * PERM_SPLIT_SPEED
                child.vy =  math.sin(rad) * PERM_SPLIT_SPEED
            children.append(child)
        return children
