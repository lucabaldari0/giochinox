import pygame
import random
import os
from settings import SCREEN_W, SCREEN_H, ENEMY_TYPES, POWERUP_DROP_RATES, ENEMY_SHOOT_COOLDOWN

ANIM_SPEED = {
    "red":    16,
    "orange": 30,
    "purple": 18,
    "yellow": 12,
}

# Spritesheet per ogni tipo di nemico
ENEMY_SHEETS = {
    "red":    os.path.join("assets", "red_spritesheet.png"),
    "orange": os.path.join("assets", "orange_spritesheet.png"),
    "purple": os.path.join("assets", "purple_spritesheet.png"),
    "yellow": None,
}
ENEMY_FRAME_COUNT = 4
ENEMY_FRAME_SIZE  = 40   # usato solo per red, gli altri vengono divisi in 4 parti uguali

_enemy_frames = {}   # cache: kind -> (frames_v, frames_h)

def _load_enemy_frames(kind, color, color_lt):
    """Carica i frame per un tipo di nemico. Fallback geometrico se non trovato."""
    if kind in _enemy_frames:
        return _enemy_frames[kind]

    path = ENEMY_SHEETS.get(kind)
    if path and os.path.exists(path):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frame_w = sheet.get_width() // ENEMY_FRAME_COUNT
            frame_h = sheet.get_height()
            frames = []
            for i in range(ENEMY_FRAME_COUNT):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                frames.append(frame)
            frames_v = frames
            frames_h = [pygame.transform.rotate(f, 90) for f in frames]
        except Exception as e:
            print(f"[ENEMY SPRITE ERROR] {kind}: {e}")
            size = 30 if kind == "purple" else 24
            surf = _make_fallback(size, color, color_lt)
            surf_h = pygame.transform.rotate(surf, 90)
            frames_v = [surf] * ENEMY_FRAME_COUNT
            frames_h = [surf_h] * ENEMY_FRAME_COUNT
    else:
        # Fallback geometrico
        size = 30 if kind == "purple" else 24
        surf = _make_fallback(size, color, color_lt)
        surf_h = pygame.transform.rotate(surf, 90)
        frames_v = [surf] * ENEMY_FRAME_COUNT
        frames_h = [surf_h] * ENEMY_FRAME_COUNT

    _enemy_frames[kind] = (frames_v, frames_h)
    return frames_v, frames_h


def _make_fallback(size, color, color_lt):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    half = size // 2
    points = [(half, size), (0, half//2), (half//4, 0), (3*half//4, 0), (size, half//2)]
    inner  = [(half, size-8), (6, half), (half, 6), (size-6, half)]
    pygame.draw.polygon(surf, color, points)
    pygame.draw.polygon(surf, color_lt, inner)
    return surf


class Enemy(pygame.sprite.Sprite):
    def __init__(self, kind, stage=1):
        super().__init__()
        self.kind  = kind
        self.stage = stage
        self.max_hp, self.color, self.color_lt, speed_base, self.points = ENEMY_TYPES[kind]
        self.hp    = self.max_hp
        self.speed = speed_base + random.uniform(-0.2, 0.4)

        self._frames_v, self._frames_h = _load_enemy_frames(kind, self.color, self.color_lt)
        self._anim_frame = 0
        self._anim_timer = 0
        self.image = self._frames_v[0] if stage != 2 else self._frames_h[0]

        if stage in (1, 3):
            self.rect = self.image.get_rect(
                centerx=random.randint(20, SCREEN_W - 20),
                bottom=0
            )
        else:
            self.rect = self.image.get_rect(
                left=SCREEN_W,
                centery=random.randint(20, SCREEN_H - 20)
            )

        self._base_x = float(self.rect.x)
        self._base_y = float(self.rect.y)
        self._dir    = random.choice([-1, 1])
        self._frame  = random.randint(0, 100)
        self.shoot_timer = random.randint(0, ENEMY_SHOOT_COOLDOWN)

    def update(self):
        # Animazione
        self._anim_timer += 1
        if self._anim_timer >= ANIM_SPEED[self.kind]:
            self._anim_timer = 0
            self._anim_frame = (self._anim_frame + 1) % ENEMY_FRAME_COUNT
        self.image = self._frames_h[self._anim_frame] if self.stage == 2 else self._frames_v[self._anim_frame]

        self._frame += 1

        if self.stage in (1, 3):
            self.rect.y += self.speed
            if self.kind in ("orange", "yellow"):
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

        if self.kind == "yellow":
            if self.shoot_timer > 0:
                self.shoot_timer -= 1
            if self.shoot_timer == 0:
                self.shoot_timer = ENEMY_SHOOT_COOLDOWN
                return "shoot"

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def get_drop(self):
        if self.kind == "yellow":
            return None
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