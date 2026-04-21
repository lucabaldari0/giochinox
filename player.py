import pygame
import os
from settings import (
    PLAYER_SPEED, SHOOT_COOLDOWN, GREEN, GREEN_LIGHT, SCREEN_W, SCREEN_H,
    POWERUP_DOUBLESHOOT_DURATION,
    PERM_TRIPLE_COOLDOWN, PERM_FAST_COOLDOWN
)
from bullet import Bullet

SPRITESHEET_PATH = os.path.join("assets", "turtle_spritesheet.png")
FRAME_SIZE       = 64    # ogni frame e 64x64
FRAME_COUNT      = 4
ANIM_SPEED       = 8     # cambia frame ogni 8 frame di gioco


def _make_fallback(angle=0):
    """Forma geometrica di fallback se lo spritesheet non esiste."""
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    if angle == 0:
        points = [(20, 0), (4, 36), (20, 28), (36, 36)]
        inner  = [(20, 8), (10, 30), (20, 24), (30, 30)]
    else:
        points = [(36, 20), (0, 4), (12, 20), (0, 36)]
        inner  = [(28, 20), (8, 10), (16, 20), (8, 30)]
    pygame.draw.polygon(surf, GREEN, points)
    pygame.draw.polygon(surf, GREEN_LIGHT, inner)
    return surf


def _load_frames():
    """Carica i frame dallo spritesheet. Fallback geometrico se non trovato."""
    if os.path.exists(SPRITESHEET_PATH):
        sheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
        frames_s1 = []
        for i in range(FRAME_COUNT):
            frame = sheet.subsurface((i * FRAME_SIZE, 0, FRAME_SIZE, FRAME_SIZE))
            frames_s1.append(frame)
        # Stage 2: ruota di -90 gradi (punta a destra)
        frames_s2 = [pygame.transform.rotate(f, -90) for f in frames_s1]
        return frames_s1, frames_s2
    else:
        # Fallback: 4 copie dello stesso sprite geometrico
        f1 = _make_fallback(angle=0)
        f2 = _make_fallback(angle=-90)
        return [f1] * FRAME_COUNT, [f2] * FRAME_COUNT


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.stage         = 1
        self._frames_s1, self._frames_s2 = _load_frames()
        self._anim_frame   = 0
        self._anim_timer   = 0
        self.image         = self._frames_s1[0]
        self.rect          = self.image.get_rect(center=(SCREEN_W // 2, SCREEN_H - 80))
        self.shoot_timer   = 0
        self.shield        = False
        self.doubleshoot   = 0
        self.perm_upgrades = []

    def set_stage(self, stage):
        self.stage = stage
        if stage == 2:
            self.rect = self._frames_s2[0].get_rect(center=(80, SCREEN_H // 2))
        else:
            self.rect = self._frames_s1[0].get_rect(center=(SCREEN_W // 2, SCREEN_H - 80))

    def _get_speed(self):
        from settings import PERM_SPEED_BONUS
        return int(PLAYER_SPEED * PERM_SPEED_BONUS) if self.has_upgrade("speed") else PLAYER_SPEED

    def update(self, keys):
        # Animazione
        self._anim_timer += 1
        if self._anim_timer >= ANIM_SPEED:
            self._anim_timer = 0
            self._anim_frame = (self._anim_frame + 1) % FRAME_COUNT
        frames = self._frames_s2 if self.stage == 2 else self._frames_s1
        self.image = frames[self._anim_frame]

        # Movimento
        spd = self._get_speed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.rect.x -= spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.rect.y -= spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.rect.y += spd
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())

        if self.shoot_timer > 0: self.shoot_timer -= 1
        if self.doubleshoot > 0: self.doubleshoot -= 1

    def _get_cooldown(self):
        return PERM_FAST_COOLDOWN if self.has_upgrade("fast") else SHOOT_COOLDOWN

    def can_shoot(self):
        return self.shoot_timer == 0

    def _make_bullets(self, positions, angles, pierce, split, stage):
        bullets = []
        for x, y in positions:
            for angle in angles:
                bullets.append(Bullet(x, y, angle=angle, pierce=pierce, stage=stage, split=split))
        return bullets

    def shoot(self):
        self.shoot_timer = self._get_cooldown()
        pierce = self.has_upgrade("pierce")
        split  = self.has_upgrade("split")
        triple = self.has_upgrade("triple")
        s      = self.stage

        if s in (1, 3):
            cx, ty = self.rect.centerx, self.rect.top
            positions = [(cx - 4, ty), (cx + 4, ty)] if self.doubleshoot > 0 else [(cx, ty)]
            angles = [0, -12, 12] if triple else [0]
            return self._make_bullets(positions, angles, pierce, split, s)
        else:
            rx, cy = self.rect.right, self.rect.centery
            positions = [(rx, cy - 4), (rx, cy + 4)] if self.doubleshoot > 0 else [(rx, cy)]
            angles = [0, -12, 12] if triple else [0]
            return self._make_bullets(positions, angles, pierce, split, s)

    def activate_shield(self):
        self.shield = True

    def absorb_hit(self):
        if self.shield:
            self.shield = False
            return True
        return False

    def activate_doubleshoot(self):
        self.doubleshoot = POWERUP_DOUBLESHOOT_DURATION

    def activate_perm_upgrade(self, kind):
        if kind not in self.perm_upgrades:
            self.perm_upgrades.append(kind)

    def get_available_upgrades(self):
        all_upgrades = ["triple", "fast", "pierce", "split", "speed"]
        return [u for u in all_upgrades if u not in self.perm_upgrades]

    def has_upgrade(self, kind):
        return kind in self.perm_upgrades

    def has_shield(self):
        return self.shield

    def draw_powerup_hud(self, surface):
        x, y = 12, 32
        font = pygame.font.SysFont("Arial", 13)
        names = {"triple": "Triple shot", "fast": "Fire rate +", "pierce": "Piercing",
                 "split": "Splitting", "speed": "Speed +25%"}
        if self.shield:
            surface.blit(font.render("Shield active", True, (80, 255, 160)), (x, y)); y += 18
        if self.doubleshoot > 0:
            secs = round(self.doubleshoot / 60, 1)
            surface.blit(font.render(f"Double shot  {secs}s", True, (80, 200, 255)), (x, y)); y += 18
        for u in self.perm_upgrades:
            surface.blit(font.render(f"[PERM] {names[u]}", True, (255, 220, 80)), (x, y)); y += 18

    def draw_shield(self, surface):
        if self.shield:
            pygame.draw.circle(surface, (80, 255, 160), self.rect.center, 28, 2)
