import pygame
from settings import (
    PLAYER_SPEED, SHOOT_COOLDOWN, GREEN, GREEN_LIGHT, SCREEN_W, SCREEN_H,
    POWERUP_DOUBLESHOOT_DURATION,
    PERM_TRIPLE_COOLDOWN, PERM_FAST_COOLDOWN
)
from bullet import Bullet


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.stage       = 1
        self._surf_s1    = self._make_surface(stage=1)
        self._surf_s2    = self._make_surface(stage=2)
        self.image       = self._surf_s1
        self.rect        = self.image.get_rect(center=(SCREEN_W // 2, SCREEN_H - 80))
        self.shoot_timer = 0
        self.shield      = False
        self.doubleshoot = 0
        self.perm_upgrade = None   # "triple" | "fast" | "pierce"

    def _make_surface(self, stage=1):
        surf = pygame.Surface((36, 40), pygame.SRCALPHA)
        if stage == 1:
            # Punta verso l'alto
            points = [(18, 0), (4, 36), (18, 28), (32, 36)]
            inner  = [(18, 8), (10, 30), (18, 24), (26, 30)]
        else:
            # Punta verso destra
            points = [(36, 20), (0, 4), (12, 20), (0, 36)]
            inner  = [(28, 20), (8, 10), (16, 20), (8, 30)]
        pygame.draw.polygon(surf, GREEN, points)
        pygame.draw.polygon(surf, GREEN_LIGHT, inner)
        return surf

    def set_stage(self, stage):
        self.stage = stage
        self.image = self._surf_s2 if stage == 2 else self._surf_s1
        if stage == 2:
            self.rect = self.image.get_rect(center=(80, SCREEN_H // 2))

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.rect.y += PLAYER_SPEED
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())
        if self.shoot_timer > 0: self.shoot_timer -= 1
        if self.doubleshoot > 0: self.doubleshoot -= 1

    def _get_cooldown(self):
        return PERM_FAST_COOLDOWN if self.perm_upgrade == "fast" else SHOOT_COOLDOWN

    def can_shoot(self):
        return self.shoot_timer == 0

    def shoot(self):
        self.shoot_timer = self._get_cooldown()
        pierce = self.perm_upgrade == "pierce"
        s = self.stage

        if s == 1:
            cx, ty = self.rect.centerx, self.rect.top
            if self.doubleshoot > 0 and self.perm_upgrade == "triple":
                # Ogni proiettile del triplo viene raddoppiato: 6 colpi totali
                return [Bullet(cx - 4, ty, angle=0,   pierce=pierce, stage=1),
                        Bullet(cx + 4, ty, angle=0,   pierce=pierce, stage=1),
                        Bullet(cx - 4, ty, angle=-12, pierce=pierce, stage=1),
                        Bullet(cx + 4, ty, angle=-12, pierce=pierce, stage=1),
                        Bullet(cx - 4, ty, angle=12,  pierce=pierce, stage=1),
                        Bullet(cx + 4, ty, angle=12,  pierce=pierce, stage=1)]
            if self.doubleshoot > 0:
                return [Bullet(cx - 4, ty, pierce=pierce, stage=1),
                        Bullet(cx + 4, ty, pierce=pierce, stage=1)]
            if self.perm_upgrade == "triple":
                return [Bullet(cx, ty, angle=0,  stage=1),
                        Bullet(cx, ty, angle=-12, stage=1),
                        Bullet(cx, ty, angle=12,  stage=1)]
            return [Bullet(cx, ty, pierce=pierce, stage=1)]

        else:
            rx, cy = self.rect.right, self.rect.centery
            if self.doubleshoot > 0 and self.perm_upgrade == "triple":
                # Ogni proiettile del triplo viene raddoppiato: 6 colpi totali
                return [Bullet(rx, cy - 4, angle=0,   pierce=pierce, stage=2),
                        Bullet(rx, cy + 4, angle=0,   pierce=pierce, stage=2),
                        Bullet(rx, cy - 4, angle=-12, pierce=pierce, stage=2),
                        Bullet(rx, cy + 4, angle=-12, pierce=pierce, stage=2),
                        Bullet(rx, cy - 4, angle=12,  pierce=pierce, stage=2),
                        Bullet(rx, cy + 4, angle=12,  pierce=pierce, stage=2)]
            if self.doubleshoot > 0:
                return [Bullet(rx, cy - 4, angle=0, pierce=pierce, stage=2),
                        Bullet(rx, cy + 4, angle=0, pierce=pierce, stage=2)]
            if self.perm_upgrade == "triple":
                return [Bullet(rx, cy, angle=0,  stage=2),
                        Bullet(rx, cy, angle=-12, stage=2),
                        Bullet(rx, cy, angle=12,  stage=2)]
            return [Bullet(rx, cy, angle=0, pierce=pierce, stage=2)]

    def activate_shield(self):      self.shield = True
    def absorb_hit(self):
        if self.shield:
            self.shield = False
            return True
        return False
    def activate_doubleshoot(self): self.doubleshoot = POWERUP_DOUBLESHOOT_DURATION
    def activate_perm_upgrade(self, kind): self.perm_upgrade = kind
    def has_shield(self):           return self.shield

    def draw_powerup_hud(self, surface):
        x, y = 12, 32
        font = pygame.font.SysFont("Arial", 13)
        if self.shield:
            surface.blit(font.render("Scudo attivo", True, (80, 255, 160)), (x, y)); y += 18
        if self.doubleshoot > 0:
            secs = round(self.doubleshoot / 60, 1)
            surface.blit(font.render(f"Doppio sparo  {secs}s", True, (80, 200, 255)), (x, y)); y += 18
        if self.perm_upgrade:
            names = {"triple": "Triplo sparo", "fast": "Cadenza +", "pierce": "Perforante"}
            surface.blit(font.render(f"[PERM] {names[self.perm_upgrade]}", True, (255, 220, 80)), (x, y))

    def draw_shield(self, surface):
        if self.shield:
            pygame.draw.circle(surface, (80, 255, 160), self.rect.center, 28, 2)