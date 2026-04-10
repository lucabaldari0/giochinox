import pygame
import random
import sys

from settings import (
    SCREEN_W, SCREEN_H, FPS, TITLE,
    BLACK, GRAY, GREEN, ORANGE, RED, WHITE,
    BASE_SPAWN_RATE, MIN_SPAWN_RATE,
    STARTING_LIVES, BOSS_TRIGGER_SCORE, BOSS2_TRIGGER_SCORE
)
from star     import Star
from player   import Player
from enemy    import Enemy
from particle import Particle
from powerup  import PowerUp
from boss     import Boss, BossBullet, Boss2, Boss2Bullet
from hud      import init_fonts, draw_hud, draw_overlay

FLASH_DURATION    = 10
INVINCIBLE_FRAMES = 90

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def get_spawn_rate(score):
    rate = BASE_SPAWN_RATE - score // 5
    return max(MIN_SPAWN_RATE, rate)

def pick_enemy_type(score):
    if score < 30:
        return "red"
    elif score < 80:
        return random.choice(["red", "red", "orange"])
    else:
        return random.choices(["red", "orange", "purple"], weights=[4, 3, 2])[0]

def make_stars(stage=1):
    return [Star(stage=stage) for _ in range(80)]

def spawn_particles(particles, x, y, color, n):
    for _ in range(n):
        particles.append(Particle(x, y, color))

# ---------------------------------------------------------------------------
# SCHERMATA TRANSIZIONE STAGE
# ---------------------------------------------------------------------------

def stage_transition(screen, clock, stars, font_big, font_med):
    """Mostra 'Stage 2' per 2 secondi prima di continuare."""
    for frame in range(FPS * 2):
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        for s in stars: s.update()
        screen.fill(BLACK)
        for s in stars: s.draw(screen)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        t = font_big.render("STAGE 2", True, (255, 220, 80))
        screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20)))
        s2 = font_med.render("I nemici arrivano da destra!", True, GRAY)
        screen.blit(s2, s2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))
        pygame.display.flip()

# ---------------------------------------------------------------------------
# SCHERMATA SCELTA UPGRADE
# ---------------------------------------------------------------------------

def upgrade_choice_screen(screen, clock, stars, font_big, font_med, font_small):
    options = [
        ("1", "Triplo sparo",   ["Spara 3 proiettili", "contemporaneamente"],  "triple", (255, 200, 80)),
        ("2", "Cadenza x2",    ["4 colpi al secondo", "permanentemente"],       "fast",   (80,  200, 255)),
        ("3", "Perforante",    ["Attraversa tutti", "i nemici"],       "pierce", (255, 120, 80)),
    ]
    key_map = {pygame.K_1: "triple", pygame.K_2: "fast", pygame.K_3: "pierce"}

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key in key_map:
                return key_map[event.key]

        for s in stars: s.update()
        screen.fill(BLACK)
        for s in stars: s.draw(screen)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        title = font_big.render("BOSS SCONFITTO!", True, (255, 220, 80))
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 100)))
        sub = font_med.render("Scegli il potenziamento permanente", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 155)))

        card_w, card_h = 160, 170
        gap = 15
        start_x = (SCREEN_W - (3 * card_w + 2 * gap)) // 2
        y = 200

        for i, (key, name, desc_lines, _, color) in enumerate(options):
            x = start_x + i * (card_w + gap)
            pygame.draw.rect(screen, (25, 25, 40), (x, y, card_w, card_h), border_radius=10)
            pygame.draw.rect(screen, color, (x, y, card_w, card_h), width=2, border_radius=10)
            # Numero tasto
            k_surf = font_big.render(key, True, color)
            screen.blit(k_surf, k_surf.get_rect(center=(x + card_w // 2, y + 32)))
            # Nome
            n_surf = font_med.render(name, True, WHITE)
            screen.blit(n_surf, n_surf.get_rect(center=(x + card_w // 2, y + 75)))
            # Descrizione su due righe
            for j, line in enumerate(desc_lines):
                d_surf = font_small.render(line, True, GRAY)
                screen.blit(d_surf, d_surf.get_rect(center=(x + card_w // 2, y + 110 + j * 18)))

        hint = font_small.render("Premi 1, 2 o 3 per scegliere", True, (80, 80, 100))
        screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, 410)))
        pygame.display.flip()

# ---------------------------------------------------------------------------
# MENU
# ---------------------------------------------------------------------------

def menu(screen, clock, font_big, font_med, font_small):
    stars = make_stars(stage=1)
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return
        for s in stars: s.update()
        screen.fill(BLACK)
        for s in stars: s.draw(screen)
        title = font_big.render("SPACE SHOOTER", True, GREEN)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))
        sub = font_med.render("Premi INVIO o SPAZIO per iniziare", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10)))
        hint = font_small.render("Frecce / WASD per muoverti  |  Sparo automatico", True, (80, 80, 100))
        screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 55)))
        pygame.display.flip()

# ---------------------------------------------------------------------------
# GAME LOOP
# ---------------------------------------------------------------------------

def run_game(screen, clock):
    from hud import font_big, font_med, font_small

    stage        = 1
    stars        = make_stars(stage=1)
    player       = Player()
    bullets      = pygame.sprite.Group()
    enemies      = pygame.sprite.Group()
    powerups     = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    particles    = []

    score         = 0
    lives         = STARTING_LIVES
    frame         = 0
    game_state    = "playing"
    flash_timer   = 0
    invincible    = 0
    boss          = None
    boss_spawned  = False
    boss_defeated = False
    boss2         = None
    boss2_spawned = False
    boss2_bullets = pygame.sprite.Group()

    flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    flash_surf.fill((220, 50, 50, 80))

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_state == "gameover" and event.key == pygame.K_r:
                    return

        # ---- UPDATE ----
        if game_state == "playing":
            frame += 1
            if flash_timer > 0: flash_timer -= 1
            if invincible > 0:  invincible -= 1

            for s in stars: s.update()
            player.update(keys)

            # Sparo automatico
            if player.can_shoot():
                for b in player.shoot():
                    bullets.add(b)
            bullets.update()

            # Power-up raccolti
            for pu in pygame.sprite.spritecollide(player, powerups, True):
                if pu.kind == "shield":
                    player.activate_shield()
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 12)
                elif pu.kind == "doubleshoot":
                    player.activate_doubleshoot()
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 200, 255), 12)
                elif pu.kind == "life":
                    lives = min(lives + 1, 3)
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, (255, 80, 80), 12)

            # --- BOSS (solo stage 1) ---
            if stage == 1:
                boss_incoming = score >= BOSS_TRIGGER_SCORE and not boss_spawned
                if boss_incoming and len(enemies) == 0:
                    boss = Boss()
                    boss_spawned = True

                if boss is not None and not boss.dead:
                    boss.update()
                    if boss.can_shoot():
                        for bb in boss.shoot():
                            boss_bullets.add(bb)
                    boss_bullets.update()

                    if boss.exploding and frame % 4 == 0:
                        ox = boss.rect.x + random.randint(0, boss.w)
                        oy = boss.rect.y + random.randint(0, boss.h)
                        spawn_particles(particles, ox, oy, (160, 30, 200), 6)
                        spawn_particles(particles, ox, oy, (255, 200, 80), 4)

                    for bullet in list(bullets):
                        if bullet.rect.colliderect(boss.rect):
                            bullet.on_hit()
                            killed = boss.hit()
                            spawn_particles(particles, boss.rect.centerx, boss.rect.centery, (210, 120, 255), 5)
                            if killed:
                                score += 200
                                spawn_particles(particles, boss.rect.centerx, boss.rect.centery, (255, 200, 80), 30)

                    if invincible == 0 and pygame.sprite.spritecollide(player, boss_bullets, True):
                        if player.absorb_hit():
                            spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 16)
                        else:
                            lives -= 1
                            flash_timer = FLASH_DURATION
                            invincible  = INVINCIBLE_FRAMES
                            spawn_particles(particles, player.rect.centerx, player.rect.centery, GREEN, 16)
                            if lives <= 0:
                                game_state = "gameover"

                    if boss.dead:
                        boss_defeated = True
                        boss = None
                        boss_bullets.empty()
                        # Schermata upgrade
                        upgrade = upgrade_choice_screen(screen, clock, stars, font_big, font_med, font_small)
                        player.activate_perm_upgrade(upgrade)
                        # Transizione stage 2
                        stage = 2
                        stars = make_stars(stage=2)
                        player.set_stage(2)
                        bullets.empty()
                        enemies.empty()
                        powerups.empty()
                        stage_transition(screen, clock, stars, font_big, font_med)

            # --- BOSS 2 (stage 2) ---
            if stage == 2 and score >= BOSS2_TRIGGER_SCORE and not boss2_spawned and len(enemies) == 0:
                boss2 = Boss2()
                boss2_spawned = True

            if boss2 is not None and not boss2.dead:
                boss2.update()
                if boss2.can_shoot():
                    for bb in boss2.shoot():
                        boss2_bullets.add(bb)
                boss2_bullets.update()

                if boss2.exploding and frame % 4 == 0:
                    ox = boss2.rect.x + random.randint(0, boss2.w)
                    oy = boss2.rect.y + random.randint(0, boss2.h)
                    spawn_particles(particles, ox, oy, (200, 50, 30), 6)
                    spawn_particles(particles, ox, oy, (255, 150, 80), 4)

                # Proiettili player -> boss2
                for bullet in list(bullets):
                    if bullet.rect.colliderect(boss2.rect):
                        bullet.on_hit()
                        killed = boss2.hit()
                        spawn_particles(particles, boss2.rect.centerx, boss2.rect.centery, (255, 150, 100), 5)
                        if killed:
                            score += 500
                            spawn_particles(particles, boss2.rect.centerx, boss2.rect.centery, (255, 200, 80), 30)

                # Proiettili boss2 -> player
                if invincible == 0 and pygame.sprite.spritecollide(player, boss2_bullets, True):
                    if player.absorb_hit():
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 16)
                    else:
                        lives -= 1
                        flash_timer = FLASH_DURATION
                        invincible  = INVINCIBLE_FRAMES
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, GREEN, 16)
                        if lives <= 0:
                            game_state = "gameover"

                # Laser -> player
                laser_rect = boss2.get_laser_rect()
                if laser_rect and invincible == 0 and laser_rect.colliderect(player.rect):
                    if player.absorb_hit():
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 16)
                    else:
                        lives -= 1
                        flash_timer = FLASH_DURATION
                        invincible  = INVINCIBLE_FRAMES
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, GREEN, 16)
                        if lives <= 0:
                            game_state = "gameover"

                if boss2.dead:
                    boss2 = None
                    boss2_bullets.empty()

            # --- NEMICI NORMALI (entrambi gli stage) ---
            can_spawn = (stage == 1 and (not boss_spawned or boss_defeated) and score < BOSS_TRIGGER_SCORE) \
                     or (stage == 2 and not boss2_spawned and score < BOSS2_TRIGGER_SCORE)
            if can_spawn:
                sr = get_spawn_rate(score)
                if frame % sr == 0:
                    kind = pick_enemy_type(score)
                    enemies.add(Enemy(kind, stage=stage))

            for e in list(enemies):
                result = e.update()
                if result == "escaped":
                    score += 1

            # Proiettili player -> nemici
            for bullet in list(bullets):
                for enemy in list(enemies):
                    if bullet.rect.colliderect(enemy.rect):
                        if not hasattr(bullet, '_hit_enemies'):
                            bullet._hit_enemies = set()
                        if id(enemy) in bullet._hit_enemies:
                            continue
                        bullet._hit_enemies.add(id(enemy))
                        bullet.on_hit()
                        killed = enemy.hit()
                        color = enemy.color if killed else enemy.color_lt
                        spawn_particles(particles, enemy.rect.centerx, enemy.rect.centery, color, 10 if killed else 4)
                        if killed:
                            score += enemy.points
                            drop = enemy.get_drop()
                            if drop:
                                powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, drop, stage=stage))
                        if not bullet.alive():
                            break

            # Nemici -> player
            if invincible == 0 and pygame.sprite.spritecollide(player, enemies, True):
                if player.absorb_hit():
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 16)
                else:
                    lives -= 1
                    flash_timer = FLASH_DURATION
                    invincible  = INVINCIBLE_FRAMES
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, GREEN, 16)
                    if lives <= 0:
                        game_state = "gameover"

            powerups.update()
            particles = [p for p in particles if p.update()]

        # ---- DRAW ----
        screen.fill(BLACK)
        for s in stars: s.draw(screen)

        for e in enemies:
            screen.blit(e.image, e.rect)
            e.draw_hp_bar(screen)

        if boss is not None and not boss.dead:
            if not boss.exploding or (frame // 4) % 2 == 0:
                screen.blit(boss.image, boss.rect)
            boss.draw_hp_bar(screen)

        # Laser boss2
        if boss2 is not None and not boss2.dead:
            boss2.draw_laser(screen, frame)
            if not boss2.exploding or (frame // 4) % 2 == 0:
                screen.blit(boss2.image, boss2.rect)
            boss2.draw_hp_bar(screen)
        boss2_bullets.draw(screen)

        bullets.draw(screen)
        boss_bullets.draw(screen)
        powerups.draw(screen)

        if game_state == "playing":
            if invincible == 0 or (invincible // 6) % 2 == 0:
                screen.blit(player.image, player.rect)
            if player.has_shield():
                player.draw_shield(screen)

        for p in particles: p.draw(screen)

        draw_hud(screen, score, lives)
        player.draw_powerup_hud(screen)

        # Indicatore stage
        font_s = pygame.font.SysFont("Arial", 13)
        stage_surf = font_s.render(f"Stage {stage}", True, GRAY)
        screen.blit(stage_surf, (SCREEN_W - 70, 30))

        if flash_timer > 0:
            screen.blit(flash_surf, (0, 0))

        if game_state == "gameover":
            draw_overlay(screen, "Game Over", f"Punteggio: {score}  |  R per ricominciare", RED)

        pygame.display.flip()

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    init_fonts()
    from hud import font_big, font_med, font_small
    while True:
        menu(screen, clock, font_big, font_med, font_small)
        run_game(screen, clock)
