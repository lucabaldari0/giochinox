# ---------------------------------------------------------------------------
# SETTINGS — tutte le costanti del gioco
# ---------------------------------------------------------------------------

# Schermo
SCREEN_W = 600
SCREEN_H = 700
FPS      = 60
TITLE    = "Space Shooter"

# Giocatore
PLAYER_SPEED    = 4
SHOOT_COOLDOWN  = 30   # frame tra un colpo e l'altro (30 = 2 colpi/sec a 60 FPS)

# Proiettili
BULLET_SPEED = 8

# Difficoltà
BASE_SPAWN_RATE = 90   # frame tra uno spawn e l'altro all'inizio
MIN_SPAWN_RATE  = 25   # limite minimo (difficoltà massima)

# Vite
STARTING_LIVES = 3

# Colori
BLACK      = (10,  10,  20)
WHITE      = (255, 255, 255)
GRAY       = (150, 150, 160)
DARK_GRAY  = (80,  80,  100)
GREEN      = (29,  158, 117)
GREEN_LIGHT= (95,  202, 165)
RED        = (226, 75,  74)
ORANGE     = (239, 159, 39)
PURPLE     = (83,  74,  183)
PURPLE_LT  = (175, 169, 236)

# Tipi di nemici: hp, colore, colore_chiaro, velocità_base, punti
ENEMY_TYPES = {
    "red":    (2, RED,    (255, 130, 130), 1.8, 10),
    "orange": (1, ORANGE, (255, 210, 130), 2.5, 15),
    "purple": (3, PURPLE, PURPLE_LT,       1.1, 30),
    "yellow": (2, (255, 220, 50), (255, 240, 150), 1.5, 30),
}

# Boss
BOSS_TRIGGER_SCORE  = 0   # punteggio per far apparire il boss
BOSS_HP             = 2
BOSS_SPEED          = 1.8   # velocita movimento laterale
BOSS_SHOOT_COOLDOWN = 60    # frame tra un colpo e l'altro (60 = 1 proiettile/sec)
BOSS_BULLET_SPEED   = 3
BOSS_COLOR          = (160, 30, 200)
BOSS_COLOR_LT       = (210, 120, 255)
BOSS_ENTRY_Y        = 80    # posizione Y finale dopo l'entrata

# Power-up
POWERUP_SHIELD_DURATION      = 0           # non usato, lo scudo assorbe un colpo e sparisce
POWERUP_DOUBLESHOOT_DURATION = 60 * 10    # frame (10 secondi)
POWERUP_SPEED                = 2.5        # velocita di caduta del power-up
POWERUP_DROP_RATES = {
    "red":    ("life",        0.10),
    "orange": ("doubleshoot", 0.30),
    "purple": ("shield",      0.30),
}
POWERUP_COLORS = {
    "life":        (255, 80,  80),
    "doubleshoot": (80,  200, 255),
    "shield":      (80,  255, 160),
}

# Power-up permanenti post-boss
PERM_TRIPLE_COOLDOWN   = 30    # stesso cooldown, ma 3 proiettili
PERM_FAST_COOLDOWN     = 15    # 4 colpi al secondo (da 30 a 15 frame)
PERM_PIERCE_MAX_HITS   = 999   # perforante: colpisce tutti i nemici, sparisce solo fuori schermo

# Stage 2
STAGE2_TRIGGER = "boss_defeated"   # il secondo stage inizia dopo il boss

# Boss 2
BOSS2_TRIGGER_SCORE   = 4
BOSS2_HP              = 4
BOSS2_SPEED           = 1.5   # velocita movimento verticale
BOSS2_SHOOT_COOLDOWN  = 50    # proiettili normali
BOSS2_BULLET_SPEED    = 4
BOSS2_COLOR           = (200, 50, 30)
BOSS2_COLOR_LT        = (255, 150, 100)
BOSS2_ENTRY_X         = SCREEN_W - 100  # posizione X finale dopo entrata da destra
BOSS2_LASER_WARNING   = 60    # frame avviso lampeggio (1 sec)
BOSS2_LASER_DURATION  = 60 * 8  # frame laser attivo (8 sec)
BOSS2_LASER_COOLDOWN  = 60 * 6  # frame tra un laser e l'altro (6 sec)
BOSS2_LASER_H         = 100   # altezza fascia laser in pixel

# Nemico giallo
YELLOW        = (255, 220, 50)
YELLOW_LT     = (255, 240, 150)
ENEMY_BULLET_SPEED   = 4
ENEMY_SHOOT_COOLDOWN = 60   # 1 colpo al secondo

# Stage 3
STAGE3_TRIGGER = "boss2_defeated"

# Power-up boss 2 (split)
PERM_SPLIT_SPEED = 5   # velocita dei proiettili figli dopo lo split

# Boss Finale (stage 3)
BOSS3_TRIGGER_SCORE   = 100
BOSS3_HP              = 1
BOSS3_SPEED           = 2.2
BOSS3_SHOOT_COOLDOWN  = 30    # 0.5 secondi tra un colpo e l altro
BOSS3_BULLET_SPEED    = 5
BOSS3_COLOR           = (220, 30, 30)
BOSS3_COLOR_LT        = (255, 120, 120)
BOSS3_ENTRY_Y         = 80
BOSS3_LASER_WARNING   = 30    # 0.5 secondi di preavviso
BOSS3_LASER_DURATION  = 60 * 8
BOSS3_LASER_COOLDOWN  = 60 * 5
BOSS3_LASER_H         = 100

# Power-up boss 3
PERM_SPEED_BONUS = 1.25   # moltiplicatore velocita navicella +25%

# Modalita infinito
INFINITE_BASE_SPAWN  = 60   # spawn rate iniziale modalita infinito
INFINITE_MIN_SPAWN   = 10   # spawn rate minimo