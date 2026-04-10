import pygame
from settings import SCREEN_W, WHITE, GRAY, GREEN, ORANGE, RED

font_big   = None
font_med   = None
font_small = None


def init_fonts():
    """Inizializza i font — da chiamare dopo pygame.init()."""
    global font_big, font_med, font_small
    font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    font_med   = pygame.font.SysFont("Arial", 28)
    font_small = pygame.font.SysFont("Arial", 18)


def draw_hud(surface, score, lives):
    """Disegna punteggio e vite in alto."""
    score_surf = font_small.render(f"Punteggio: {score}", True, WHITE)
    surface.blit(score_surf, (12, 10))

    lives_label = font_small.render("Vite:", True, WHITE)
    surface.blit(lives_label, (SCREEN_W - 130, 10))

    for i in range(lives):
        points = [
            (SCREEN_W - 80 + i * 22, 14),
            (SCREEN_W - 91 + i * 22, 28),
            (SCREEN_W - 80 + i * 22, 24),
            (SCREEN_W - 69 + i * 22, 28),
        ]
        pygame.draw.polygon(surface, GREEN, points)


def draw_overlay(surface, title, subtitle, color=WHITE):
    """Overlay semitrasparente con titolo e sottotitolo (usato per morte e game over)."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((10, 10, 20, 180))
    surface.blit(overlay, (0, 0))

    t = font_big.render(title, True, color)
    surface.blit(t, t.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 40)))

    s = font_med.render(subtitle, True, GRAY)
    surface.blit(s, s.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 20)))
