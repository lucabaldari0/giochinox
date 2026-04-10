import pygame
import random
import sys

from settings import (
    SCREEN_W, SCREEN_H, FPS, TITLE,
    BLACK, GRAY, GREEN, ORANGE, RED, WHITE,
    BASE_SPAWN_RATE, MIN_SPAWN_RATE,
    STARTING_LIVES, BOSS_TRIGGER_SCORE, BOSS2_TRIGGER_SCORE, BOSS3_TRIGGER_SCORE,
    INFINITE_BASE_SPAWN, INFINITE_MIN_SPAWN
)
from star     import Star
from player   import Player
from enemy    import Enemy
from particle import Particle
from powerup  import PowerUp
from boss     import Boss, BossBullet, Boss2, Boss2Bullet, Boss3, Boss3Bullet
from enemy_bullet import EnemyBullet
from hud      import init_fonts, draw_hud, draw_overlay

FLASH_DURATION    = 10
INVINCIBLE_FRAMES = 90

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def get_spawn_rate(score, infinite=False):
    if infinite:
        from settings import INFINITE_BASE_SPAWN, INFINITE_MIN_SPAWN
        rate = INFINITE_BASE_SPAWN - (score - 9000) // 3
        return max(INFINITE_MIN_SPAWN, rate)
    rate = BASE_SPAWN_RATE - score // 5
    return max(MIN_SPAWN_RATE, rate)

def pick_enemy_type(score, stage=1, infinite=False):
    if infinite:
        return random.choices(["red", "orange", "purple", "yellow"], weights=[3, 3, 2, 3])[0]
    if stage == 3:
        if score < 1500:
            return random.choices(["red", "orange", "yellow"], weights=[4, 3, 2])[0]
        else:
            return random.choices(["red", "orange", "purple", "yellow"], weights=[3, 3, 2, 3])[0]
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
# HIGHSCORE
# ---------------------------------------------------------------------------

HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(score):
    current = load_highscore()
    if score > current:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
        return True
    return False

# ---------------------------------------------------------------------------
# SCHERMATA TRANSIZIONE STAGE
# ---------------------------------------------------------------------------

def stage_transition(screen, clock, stars, font_big, font_med, stage_num=2):
    """Mostra il numero di stage per 2 secondi prima di continuare."""
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
        t = font_big.render(f"STAGE {stage_num}", True, (255, 220, 80))
        screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20)))

        pygame.display.flip()

# ---------------------------------------------------------------------------
# SCHERMATA TRANSIZIONE MODALITA INFINITO
# ---------------------------------------------------------------------------

def infinite_transition(screen, clock, stars, font_big, font_med):
    for frame in range(FPS * 3):
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        for s in stars: s.update()
        screen.fill(BLACK)
        for s in stars: s.draw(screen)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        t = font_big.render("MODALITÀ INFINITO", True, (255, 220, 80))
        screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20)))
        s2 = font_med.render("Sopravvivi il più a lungo possibile!", True, GRAY)
        screen.blit(s2, s2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))
        pygame.display.flip()

# ---------------------------------------------------------------------------
# SCHERMATA SCELTA UPGRADE
# ---------------------------------------------------------------------------

def upgrade_choice_screen(screen, clock, stars, font_big, font_med, font_small, options_keys=None):
    all_upgrades = {
        "triple": ("Triplo sparo",   ["Spara 3 proiettili", "contemporaneamente"],  (255, 200, 80)),
        "fast":   ("Cadenza x2",    ["4 colpi al secondo", "permanentemente"],       (80,  200, 255)),
        "pierce": ("Perforante",    ["Attraversa tutti", "i nemici"],               (255, 120, 80)),
        "split":  ("Sdoppiante",    ["I proiettili si", "sdoppiano al colpo"],      (180, 100, 255)),
        "speed":  ("Velocità +25%", ["Navicella più", "veloce del 25%"],              (100, 255, 180)),
    }
    if options_keys is None:
        options_keys = ["triple", "fast", "pierce"]
    options = []
    key_labels = ["1", "2", "3"]
    key_events = [pygame.K_1, pygame.K_2, pygame.K_3]
    key_map = {}
    for i, k in enumerate(options_keys):
        name, desc, color = all_upgrades[k]
        options.append((key_labels[i], name, desc, k, color))
        key_map[key_events[i]] = k

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
    boss2_bullets  = pygame.sprite.Group()
    enemy_bullets  = pygame.sprite.Group()
    boss3          = None
    boss3_spawned  = False
    boss3_bullets  = pygame.sprite.Group()
    infinite_mode  = False

    highscore  = load_highscore()

    flash_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    flash_surf.fill((220, 50, 50, 80))
    pause_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    pause_surf.fill((0, 0, 0, 140))

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "playing":
                        game_state = "paused"
                    elif game_state == "paused":
                        game_state = "playing"
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
                        particles.clear()
                        stage_transition(screen, clock, stars, font_big, font_med, stage_num=2)

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
                    boss2_defeated = True
                    boss2 = None
                    boss2_bullets.empty()
                    # Schermata upgrade boss 2
                    available = player.get_available_upgrades()[:2] + ["split"]
                    upgrade2 = upgrade_choice_screen(screen, clock, stars, font_big, font_med, font_small, available)
                    player.activate_perm_upgrade(upgrade2)
                    # Transizione stage 3
                    stage = 3
                    stars = make_stars(stage=1)
                    player.set_stage(1)
                    bullets.empty()
                    enemies.empty()
                    enemy_bullets.empty()
                    powerups.empty()
                    particles.clear()
                    stage_transition(screen, clock, stars, font_big, font_med, stage_num=3)

            # --- BOSS 3 (stage 3) ---
            if stage == 3 and score >= BOSS3_TRIGGER_SCORE and not boss3_spawned and len(enemies) == 0:
                boss3 = Boss3()
                boss3_spawned = True
                enemy_bullets.empty()

            if boss3 is not None and not boss3.dead:
                boss3.update()
                if boss3.can_shoot():
                    for bb in boss3.shoot():
                        boss3_bullets.add(bb)
                boss3_bullets.update()

                if boss3.exploding and frame % 3 == 0:
                    ox = boss3.rect.x + random.randint(0, boss3.w)
                    oy = boss3.rect.y + random.randint(0, boss3.h)
                    spawn_particles(particles, ox, oy, (220, 30, 30), 6)
                    spawn_particles(particles, ox, oy, (255, 150, 80), 4)

                for bullet in list(bullets):
                    if bullet.rect.colliderect(boss3.rect):
                        if bullet.split and not bullet._is_child:
                            for c in bullet.spawn_children():
                                bullets.add(c)
                        bullet.on_hit()
                        killed = boss3.hit()
                        spawn_particles(particles, boss3.rect.centerx, boss3.rect.centery, (255, 120, 120), 5)
                        if killed:
                            score += 1000
                            spawn_particles(particles, boss3.rect.centerx, boss3.rect.centery, (255, 220, 80), 40)

                if invincible == 0 and pygame.sprite.spritecollide(player, boss3_bullets, True):
                    if player.absorb_hit():
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 16)
                    else:
                        lives -= 1
                        flash_timer = FLASH_DURATION
                        invincible  = INVINCIBLE_FRAMES
                        spawn_particles(particles, player.rect.centerx, player.rect.centery, GREEN, 16)
                        if lives <= 0:
                            game_state = "gameover"
                            new_record = save_highscore(score)
                            if new_record: highscore = score

                laser_rect = boss3.get_laser_rect()
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
                            new_record = save_highscore(score)
                            if new_record: highscore = score

                if boss3.dead:
                    boss3 = None
                    boss3_bullets.empty()
                    particles.clear()
                    # Upgrade boss 3
                    available = [u for u in player.get_available_upgrades() if u != "speed"][:2] + ["speed"]
                    upgrade3 = upgrade_choice_screen(screen, clock, stars, font_big, font_med, font_small, available)
                    player.activate_perm_upgrade(upgrade3)
                    # Transizione modalita infinito
                    infinite_mode = True
                    enemies.empty()
                    enemy_bullets.empty()
                    powerups.empty()
                    particles.clear()
                    infinite_transition(screen, clock, stars, font_big, font_med)

            # --- NEMICI NORMALI (entrambi gli stage) ---
            can_spawn = (stage == 1 and (not boss_spawned or boss_defeated) and score < BOSS_TRIGGER_SCORE) \
                     or (stage == 2 and not boss2_spawned and score < BOSS2_TRIGGER_SCORE) \
                     or (stage == 3 and boss2_defeated and not boss3_spawned and score < BOSS3_TRIGGER_SCORE)\
                     or (infinite_mode)
            if can_spawn:
                sr = get_spawn_rate(score, infinite=infinite_mode)
                if frame % sr == 0:
                    kind = pick_enemy_type(score, stage=stage, infinite=infinite_mode)
                    enemies.add(Enemy(kind, stage=stage if not infinite_mode else 3))

            for e in list(enemies):
                result = e.update()
                if result == "escaped":
                    score += 1
                elif result == "shoot":
                    eb = EnemyBullet(e.rect.centerx, e.rect.bottom)
                    enemy_bullets.add(eb)
            enemy_bullets.update()

            # Proiettili player -> nemici
            for bullet in list(bullets):
                for enemy in list(enemies):
                    if bullet.rect.colliderect(enemy.rect):
                        if id(enemy) in bullet._hit_enemies:
                            continue
                        bullet._hit_enemies.add(id(enemy))
                        # Split: genera figli prima di on_hit
                        if bullet.split and not bullet._is_child:
                            children = bullet.spawn_children()
                            for c in children:
                                bullets.add(c)
                        bullet.on_hit()
                        killed = enemy.hit()
                        color = enemy.color if killed else enemy.color_lt
                        spawn_particles(particles, enemy.rect.centerx, enemy.rect.centery, color, 10 if killed else 4)
                        if killed:
                            score += enemy.points
                            drop = enemy.get_drop()
                            if drop:
                                pu_stage = 1 if stage in (1, 3) else 2
                                powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, drop, stage=pu_stage))
                        if not bullet.alive():
                            break

            # Proiettili nemici -> player
            if invincible == 0 and pygame.sprite.spritecollide(player, enemy_bullets, True):
                if player.absorb_hit():
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, (80, 255, 160), 16)
                else:
                    lives -= 1
                    flash_timer = FLASH_DURATION
                    invincible  = INVINCIBLE_FRAMES
                    spawn_particles(particles, player.rect.centerx, player.rect.centery, GREEN, 16)
                    if lives <= 0:
                        game_state = "gameover"
                        new_record = save_highscore(score)
                        if new_record:
                            highscore = score

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

        if boss3 is not None and not boss3.dead:
            boss3.draw_laser(screen, frame)
            if not boss3.exploding or (frame // 3) % 2 == 0:
                screen.blit(boss3.image, boss3.rect)
            boss3.draw_hp_bar(screen)
        boss3_bullets.draw(screen)

        bullets.draw(screen)
        boss_bullets.draw(screen)
        enemy_bullets.draw(screen)
        powerups.draw(screen)

        if game_state == "playing":
            if invincible == 0 or (invincible // 6) % 2 == 0:
                screen.blit(player.image, player.rect)
            if player.has_shield():
                player.draw_shield(screen)

        for p in particles: p.draw(screen)

        draw_hud(screen, score, lives)
        # Highscore in HUD
        font_s = pygame.font.SysFont("Arial", 13)
        hs_surf = font_s.render(f"Record: {highscore}", True, (255, 220, 80))
        screen.blit(hs_surf, hs_surf.get_rect(right=SCREEN_W - 10, top=48))
        player.draw_powerup_hud(screen)

        # Indicatore stage
        font_s = pygame.font.SysFont("Arial", 13)
        stage_label = "INFINITO" if infinite_mode else f"Stage {stage}"
        stage_surf = font_s.render(stage_label, True, (255, 220, 80) if infinite_mode else GRAY)
        screen.blit(stage_surf, (SCREEN_W - 80, 30))

        if flash_timer > 0:
            screen.blit(flash_surf, (0, 0))

        # Pausa
        if game_state == "paused":
            screen.blit(pause_surf, (0, 0))
            from hud import font_big, font_med, font_small
            t = font_big.render("PAUSA", True, WHITE)
            screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 40)))
            s = font_med.render("Premi ESC per continuare", True, GRAY)
            screen.blit(s, s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10)))
            hs = font_small.render(f"Highscore: {highscore}", True, (255, 220, 80))
            screen.blit(hs, hs.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50)))

        if game_state == "gameover":
            from hud import font_big, font_med, font_small
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 180))
            screen.blit(overlay, (0, 0))
            t = font_big.render("Game Over", True, RED)
            screen.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))
            sc = font_med.render(f"Punteggio: {score}", True, WHITE)
            screen.blit(sc, sc.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 10)))
            if score >= highscore:
                hs = font_med.render("Nuovo record!", True, (255, 220, 80))
            else:
                hs = font_med.render(f"Record: {highscore}", True, (255, 220, 80))
            screen.blit(hs, hs.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 35)))
            r = font_small.render("R per ricominciare", True, GRAY)
            screen.blit(r, r.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 80)))

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