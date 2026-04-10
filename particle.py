import random


class Particle:
    def __init__(self, x, y, color):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = random.uniform(-2.5, 2.5)
        self.vy    = random.uniform(-2.5, 2.5)
        self.life  = 1.0
        self.color = color
        self.r     = random.randint(2, 4)

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.life -= 0.055
        return self.life > 0

    def draw(self, surface):
        import pygame
        r, g, b = self.color
        color = (min(255, r), min(255, g), min(255, b))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.r)
