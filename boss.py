import pygame
import math
import random
from settings import (
    SCREEN_W, SCREEN_H,
    BOSS_HP, BOSS_SPEED, BOSS_SHOOT_COOLDOWN, BOSS_BULLET_SPEED,
    BOSS_COLOR, BOSS_COLOR_LT, BOSS_ENTRY_Y
)


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_deg):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BOSS_COLOR_LT, (4, 4), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (4, 4), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self._x   = float(x)
        self._y   = float(y)
        angle_rad = math.radians(angle_deg)
        self.vx   = math.cos(angle_rad) * BOSS_BULLET_SPEED
        self.vy   = math.sin(angle_rad) * BOSS_BULLET_SPEED

    def update(self):
        self._x += self.vx
        self._y += self.vy

        # Rimbalzo sui bordi laterali
        if self._x <= 4:
            self._x = 4
            self.vx = abs(self.vx)
        elif self._x >= SCREEN_W - 4:
            self._x = SCREEN_W - 4
            self.vx = -abs(self.vx)

        self.rect.center = (int(self._x), int(self._y))

        # Esce dal basso o dall'alto
        if self._y > SCREEN_H + 10 or self._y < -10:
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hp       = BOSS_HP
        self.max_hp   = BOSS_HP
        self.w        = 90
        self.h        = 60
        self.image    = self._make_surface()
        self.rect     = self.image.get_rect(centerx=SCREEN_W // 2, bottom=0)
        self._x       = float(self.rect.x)
        self._dir     = 1
        self._entering = True       # True finche non raggiunge BOSS_ENTRY_Y
        self.shoot_timer = 0
        self.shoot_angle = 0        # rotazione pattern di sparo
        self.dead     = False
        self.exploding = False
        self._explode_timer = 0
        self._explode_duration = 90  # frame dell'animazione morte

    def _make_surface(self):
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        # Corpo centrale
        cx, cy = self.w // 2, self.h // 2
        pygame.draw.ellipse(surf, BOSS_COLOR, (10, 10, self.w - 20, self.h - 20))
        pygame.draw.ellipse(surf, BOSS_COLOR_LT, (22, 18, self.w - 44, self.h - 36))
        # Ali
        pygame.draw.polygon(surf, BOSS_COLOR, [(0, cy + 5), (20, cy - 10), (20, cy + 15)])
        pygame.draw.polygon(surf, BOSS_COLOR, [(self.w, cy + 5), (self.w - 20, cy - 10), (self.w - 20, cy + 15)])
        # Cannone centrale
        pygame.draw.rect(surf, BOSS_COLOR_LT, (cx - 5, self.h - 14, 10, 14), border_radius=3)
        return surf

    def update(self):
        if self.exploding:
            self._explode_timer += 1
            if self._explode_timer >= self._explode_duration:
                self.dead = True
                self.kill()
            return

        # Entrata dall'alto
        if self._entering:
            self.rect.y += 2
            if self.rect.top >= BOSS_ENTRY_Y:
                self.rect.top = BOSS_ENTRY_Y
                self._entering = False
            return

        # Movimento laterale con rimbalzo
        self._x += BOSS_SPEED * self._dir
        if self._x <= 0:
            self._x = 0
            self._dir = 1
        elif self._x >= SCREEN_W - self.w:
            self._x = SCREEN_W - self.w
            self._dir = -1
        self.rect.x = int(self._x)

        # Countdown sparo
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

    def can_shoot(self):
        return not self._entering and not self.exploding and self.shoot_timer == 0

    def shoot(self):
        """Spara 4 proiettili ruotati ogni volta, creando un pattern rotante."""
        self.shoot_timer = BOSS_SHOOT_COOLDOWN
        cx = self.rect.centerx
        cy = self.rect.bottom - 5
        bullets = []
        # Dritto giu, diagonale basso-sinistra, diagonale basso-destra
        for angle in [90, 135, 45]:
            bullets.append(BossBullet(cx, cy, angle))
        self.shoot_angle = (self.shoot_angle + 20) % 360
        return bullets

    def hit(self):
        """Riceve un colpo. Ritorna True se il boss e morto."""
        self.hp -= 1
        if self.hp <= 0:
            self.exploding = True
            return True
        return False

    def draw_hp_bar(self, surface):
        """Barra HP grande centrata in alto."""
        bar_w  = 300
        bar_h  = 12
        x      = (SCREEN_W - bar_w) // 2
        y      = 10
        filled = int(bar_w * self.hp / self.max_hp)
        # Sfondo
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h), border_radius=6)
        # HP rimasti (colore cambia con la vita)
        ratio = self.hp / self.max_hp
        color = (
            int(BOSS_COLOR[0] + (255 - BOSS_COLOR[0]) * (1 - ratio)),
            int(BOSS_COLOR[1] * ratio),
            int(BOSS_COLOR[2] * ratio),
        )
        if filled > 0:
            pygame.draw.rect(surface, color, (x, y, filled, bar_h), border_radius=6)
        # Bordo
        pygame.draw.rect(surface, BOSS_COLOR_LT, (x, y, bar_w, bar_h), width=1, border_radius=6)
        # Label
        font = pygame.font.SysFont("Arial", 13)
        label = font.render("BOSS", True, (255, 255, 255))
        surface.blit(label, (x - 38, y - 1))


# ---------------------------------------------------------------------------
# BOSS 2 — stage orizzontale, laser a fascia
# ---------------------------------------------------------------------------

class Boss2Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_deg=180):
        super().__init__()
        from settings import BOSS2_COLOR_LT, BOSS2_BULLET_SPEED
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BOSS2_COLOR_LT, (4, 4), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (4, 4), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self._x   = float(x)
        self._y   = float(y)
        rad = math.radians(angle_deg)
        self.vx   = math.cos(rad) * BOSS2_BULLET_SPEED
        self.vy   = math.sin(rad) * BOSS2_BULLET_SPEED

    def update(self):
        self._x += self.vx
        self._y += self.vy

        # Rimbalzo sui bordi superiore e inferiore
        if self._y <= 4:
            self._y = 4
            self.vy = abs(self.vy)
        elif self._y >= SCREEN_H - 4:
            self._y = SCREEN_H - 4
            self.vy = -abs(self.vy)

        self.rect.center = (int(self._x), int(self._y))
        if self._x < -10:
            self.kill()


class Boss2(pygame.sprite.Sprite):
    # stati laser
    LASER_IDLE    = 0
    LASER_WARNING = 1
    LASER_ACTIVE  = 2

    def __init__(self):
        super().__init__()
        from settings import (
            BOSS2_HP, BOSS2_COLOR, BOSS2_COLOR_LT, BOSS2_ENTRY_X,
            BOSS2_LASER_WARNING, BOSS2_LASER_DURATION, BOSS2_LASER_COOLDOWN,
            BOSS2_SHOOT_COOLDOWN, SCREEN_W, SCREEN_H
        )
        self.hp        = BOSS2_HP
        self.max_hp    = BOSS2_HP
        self.w         = 60
        self.h         = 90
        self.color     = BOSS2_COLOR
        self.color_lt  = BOSS2_COLOR_LT
        self.image     = self._make_surface()
        self.rect      = self.image.get_rect(left=SCREEN_W, centery=SCREEN_H // 2)
        self._y        = float(self.rect.y)
        self._dir      = 1
        self._entering = True
        self._entry_x  = BOSS2_ENTRY_X

        self.shoot_timer   = 0
        self.shoot_cooldown = BOSS2_SHOOT_COOLDOWN

        # Laser
        self.laser_state   = self.LASER_IDLE
        self.laser_timer   = 0
        self.laser_cooldown_timer = BOSS2_LASER_COOLDOWN // 2  # primo laser prima
        self.laser_y       = 0    # y superiore della fascia
        self.laser_warning_dur  = BOSS2_LASER_WARNING
        self.laser_active_dur   = BOSS2_LASER_DURATION
        self.laser_cooldown_dur = BOSS2_LASER_COOLDOWN
        self.laser_h       = 100

        self.dead      = False
        self.exploding = False
        self._explode_timer    = 0
        self._explode_duration = 90

    def _make_surface(self):
        from settings import BOSS2_COLOR, BOSS2_COLOR_LT
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        cx, cy = self.w // 2, self.h // 2
        # Corpo
        pygame.draw.ellipse(surf, BOSS2_COLOR, (10, 10, self.w - 20, self.h - 20))
        pygame.draw.ellipse(surf, BOSS2_COLOR_LT, (18, 22, self.w - 36, self.h - 44))
        # Ali orizzontali
        pygame.draw.polygon(surf, BOSS2_COLOR, [(cx + 5, 0), (cx - 10, 18), (cx + 15, 18)])
        pygame.draw.polygon(surf, BOSS2_COLOR, [(cx + 5, self.h), (cx - 10, self.h - 18), (cx + 15, self.h - 18)])
        # Cannone verso sinistra
        pygame.draw.rect(surf, BOSS2_COLOR_LT, (0, cy - 5, 14, 10), border_radius=3)
        return surf

    def update(self):
        from settings import SCREEN_H, BOSS2_SPEED
        if self.exploding:
            self._explode_timer += 1
            if self._explode_timer >= self._explode_duration:
                self.dead = True
                self.kill()
            return

        # Entrata da destra
        if self._entering:
            self.rect.x -= 2
            if self.rect.right <= self._entry_x + self.w:
                self.rect.right = self._entry_x + self.w
                self._entering = False
            return

        # Movimento verticale con rimbalzo
        self._y += BOSS2_SPEED * self._dir
        if self._y <= 0:
            self._y = 0
            self._dir = 1
        elif self._y >= SCREEN_H - self.h:
            self._y = SCREEN_H - self.h
            self._dir = -1
        self.rect.y = int(self._y)

        # Timer sparo
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Gestione laser
        if self.laser_state == self.LASER_IDLE:
            self.laser_cooldown_timer -= 1
            if self.laser_cooldown_timer <= 0:
                # Scegli fascia random
                self.laser_y = random.randint(0, SCREEN_H - self.laser_h)
                self.laser_state = self.LASER_WARNING
                self.laser_timer = self.laser_warning_dur
        elif self.laser_state == self.LASER_WARNING:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_state = self.LASER_ACTIVE
                self.laser_timer = self.laser_active_dur
        elif self.laser_state == self.LASER_ACTIVE:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_state = self.LASER_IDLE
                self.laser_cooldown_timer = self.laser_cooldown_dur

    def can_shoot(self):
        return not self._entering and not self.exploding and self.shoot_timer == 0

    def shoot(self):
        self.shoot_timer = self.shoot_cooldown
        cx = self.rect.left + 5
        cy = self.rect.centery
        # dritto, diagonale alto-sinistra, diagonale basso-sinistra
        angles = [180, 210, 150]
        bullets = []
        for angle in angles:
            bullets.append(Boss2Bullet(cx, cy, angle))
        return bullets

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.exploding = True
            return True
        return False

    def get_laser_rect(self):
        """Ritorna il rect della fascia laser attiva, o None."""
        if self.laser_state == self.LASER_ACTIVE:
            return pygame.Rect(0, self.laser_y, SCREEN_W, self.laser_h)
        return None

    def draw_laser(self, surface, frame):
        from settings import SCREEN_W
        if self.laser_state == self.LASER_WARNING:
            # Lampeggio rosso avviso
            if (frame // 6) % 2 == 0:
                warn_surf = pygame.Surface((SCREEN_W, self.laser_h), pygame.SRCALPHA)
                warn_surf.fill((255, 50, 50, 80))
                surface.blit(warn_surf, (0, self.laser_y))
                pygame.draw.rect(surface, (255, 80, 80), (0, self.laser_y, SCREEN_W, self.laser_h), 2)
        elif self.laser_state == self.LASER_ACTIVE:
            # Laser rosso pieno semitrasparente
            laser_surf = pygame.Surface((SCREEN_W, self.laser_h), pygame.SRCALPHA)
            laser_surf.fill((255, 30, 30, 120))
            surface.blit(laser_surf, (0, self.laser_y))
            # Bordi luminosi
            pygame.draw.rect(surface, (255, 100, 100), (0, self.laser_y, SCREEN_W, 3))
            pygame.draw.rect(surface, (255, 100, 100), (0, self.laser_y + self.laser_h - 3, SCREEN_W, 3))

    def draw_hp_bar(self, surface):
        from settings import SCREEN_W
        bar_w  = 300
        bar_h  = 12
        x      = (SCREEN_W - bar_w) // 2
        y      = 10
        filled = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h), border_radius=6)
        ratio = self.hp / self.max_hp
        color = (
            int(self.color[0] + (255 - self.color[0]) * (1 - ratio)),
            int(self.color[1] * ratio),
            int(self.color[2] * ratio),
        )
        if filled > 0:
            pygame.draw.rect(surface, color, (x, y, filled, bar_h), border_radius=6)
        pygame.draw.rect(surface, self.color_lt, (x, y, bar_w, bar_h), width=1, border_radius=6)
        font = pygame.font.SysFont("Arial", 13)
        label = font.render("BOSS 2", True, (255, 255, 255))
        surface.blit(label, (x - 50, y - 1))


# ---------------------------------------------------------------------------
# BOSS 3 — boss finale, stage 3, verticale con laser
# ---------------------------------------------------------------------------

class Boss3Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle_deg):
        super().__init__()
        from settings import BOSS3_COLOR_LT, BOSS3_BULLET_SPEED
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BOSS3_COLOR_LT, (4, 4), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (4, 4), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self._x   = float(x)
        self._y   = float(y)
        angle_rad = math.radians(angle_deg)
        self.vx   = math.cos(angle_rad) * BOSS3_BULLET_SPEED
        self.vy   = math.sin(angle_rad) * BOSS3_BULLET_SPEED

    def update(self):
        self._x += self.vx
        self._y += self.vy

        # Rimbalzo sui bordi laterali
        if self._x <= 4:
            self._x = 4
            self.vx = abs(self.vx)
        elif self._x >= SCREEN_W - 4:
            self._x = SCREEN_W - 4
            self.vx = -abs(self.vx)

        self.rect.center = (int(self._x), int(self._y))
        if self._y > SCREEN_H + 10 or self._y < -10:
            self.kill()


class Boss3(pygame.sprite.Sprite):
    LASER_IDLE    = 0
    LASER_WARNING = 1
    LASER_ACTIVE  = 2

    def __init__(self):
        super().__init__()
        from settings import (
            BOSS3_HP, BOSS3_COLOR, BOSS3_COLOR_LT, BOSS3_ENTRY_Y,
            BOSS3_SHOOT_COOLDOWN, BOSS3_LASER_WARNING, BOSS3_LASER_DURATION,
            BOSS3_LASER_COOLDOWN, BOSS3_LASER_H, SCREEN_W
        )
        self.hp       = BOSS3_HP
        self.max_hp   = BOSS3_HP
        self.w        = 100
        self.h        = 70
        self.color    = BOSS3_COLOR
        self.color_lt = BOSS3_COLOR_LT
        self.image    = self._make_surface()
        self.rect     = self.image.get_rect(centerx=SCREEN_W // 2, bottom=0)
        self._x       = float(self.rect.x)
        self._dir     = 1
        self._entering = True
        self._entry_y  = BOSS3_ENTRY_Y

        self.shoot_timer    = 0
        self.shoot_cooldown = BOSS3_SHOOT_COOLDOWN
        self.shoot_angle    = 0

        self.laser_state          = self.LASER_IDLE
        self.laser_timer          = 0
        self.laser_cooldown_timer = BOSS3_LASER_COOLDOWN // 3
        self.laser_y              = 0
        self.laser_warning_dur    = BOSS3_LASER_WARNING
        self.laser_active_dur     = BOSS3_LASER_DURATION
        self.laser_cooldown_dur   = BOSS3_LASER_COOLDOWN
        self.laser_h              = BOSS3_LASER_H

        self.dead      = False
        self.exploding = False
        self._explode_timer    = 0
        self._explode_duration = 120

    def _make_surface(self):
        from settings import BOSS3_COLOR, BOSS3_COLOR_LT
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        cx, cy = self.w // 2, self.h // 2
        # Corpo più grande e aggressivo
        pygame.draw.ellipse(surf, BOSS3_COLOR, (8, 8, self.w - 16, self.h - 16))
        pygame.draw.ellipse(surf, BOSS3_COLOR_LT, (20, 18, self.w - 40, self.h - 36))
        # Ali più larghe
        pygame.draw.polygon(surf, BOSS3_COLOR, [(0, cy + 8), (24, cy - 14), (24, cy + 18)])
        pygame.draw.polygon(surf, BOSS3_COLOR, [(self.w, cy + 8), (self.w - 24, cy - 14), (self.w - 24, cy + 18)])
        # Doppio cannone
        pygame.draw.rect(surf, BOSS3_COLOR_LT, (cx - 10, self.h - 16, 8, 16), border_radius=3)
        pygame.draw.rect(surf, BOSS3_COLOR_LT, (cx + 2,  self.h - 16, 8, 16), border_radius=3)
        return surf

    def update(self):
        from settings import SCREEN_W, SCREEN_H, BOSS3_SPEED
        if self.exploding:
            self._explode_timer += 1
            if self._explode_timer >= self._explode_duration:
                self.dead = True
                self.kill()
            return

        if self._entering:
            self.rect.y += 2
            if self.rect.top >= self._entry_y:
                self.rect.top = self._entry_y
                self._entering = False
            return

        # Movimento laterale più veloce
        self._x += BOSS3_SPEED * self._dir
        if self._x <= 0:
            self._x = 0
            self._dir = 1
        elif self._x >= SCREEN_W - self.w:
            self._x = SCREEN_W - self.w
            self._dir = -1
        self.rect.x = int(self._x)

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Gestione laser
        if self.laser_state == self.LASER_IDLE:
            self.laser_cooldown_timer -= 1
            if self.laser_cooldown_timer <= 0:
                self.laser_y = random.randint(0, SCREEN_H - self.laser_h)
                self.laser_state = self.LASER_WARNING
                self.laser_timer = self.laser_warning_dur
        elif self.laser_state == self.LASER_WARNING:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_state = self.LASER_ACTIVE
                self.laser_timer = self.laser_active_dur
        elif self.laser_state == self.LASER_ACTIVE:
            self.laser_timer -= 1
            if self.laser_timer <= 0:
                self.laser_state = self.LASER_IDLE
                self.laser_cooldown_timer = self.laser_cooldown_dur

    def can_shoot(self):
        return not self._entering and not self.exploding and self.shoot_timer == 0

    def shoot(self):
        self.shoot_timer = self.shoot_cooldown
        cx = self.rect.centerx
        cy = self.rect.bottom - 5
        bullets = []
        # 4 proiettili: dritto giu + 3 in diagonale
        for angle in [90, 60, 120, 75]:
            bullets.append(Boss3Bullet(cx, cy, angle))
        self.shoot_angle = (self.shoot_angle + 10) % 360
        return bullets

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.exploding = True
            return True
        return False

    def get_laser_rect(self):
        if self.laser_state == self.LASER_ACTIVE:
            return pygame.Rect(0, self.laser_y, SCREEN_W, self.laser_h)
        return None

    def draw_laser(self, surface, frame):
        if self.laser_state == self.LASER_WARNING:
            if (frame // 3) % 2 == 0:   # lampeggia più veloce (0.5s preavviso)
                warn_surf = pygame.Surface((SCREEN_W, self.laser_h), pygame.SRCALPHA)
                warn_surf.fill((255, 50, 50, 100))
                surface.blit(warn_surf, (0, self.laser_y))
                pygame.draw.rect(surface, (255, 80, 80), (0, self.laser_y, SCREEN_W, self.laser_h), 2)
        elif self.laser_state == self.LASER_ACTIVE:
            laser_surf = pygame.Surface((SCREEN_W, self.laser_h), pygame.SRCALPHA)
            laser_surf.fill((255, 30, 30, 140))
            surface.blit(laser_surf, (0, self.laser_y))
            pygame.draw.rect(surface, (255, 80, 80), (0, self.laser_y, SCREEN_W, 3))
            pygame.draw.rect(surface, (255, 80, 80), (0, self.laser_y + self.laser_h - 3, SCREEN_W, 3))

    def draw_hp_bar(self, surface):
        bar_w  = 300
        bar_h  = 12
        x      = (SCREEN_W - bar_w) // 2
        y      = 10
        filled = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h), border_radius=6)
        ratio = self.hp / self.max_hp
        color = (
            int(self.color[0]),
            int(self.color[1] * ratio),
            int(self.color[2] * ratio),
        )
        if filled > 0:
            pygame.draw.rect(surface, color, (x, y, filled, bar_h), border_radius=6)
        pygame.draw.rect(surface, self.color_lt, (x, y, bar_w, bar_h), width=1, border_radius=6)
        font = pygame.font.SysFont("Arial", 13)
        label = font.render("BOSS FINALE", True, (255, 255, 255))
        surface.blit(label, (x - 70, y - 1))
