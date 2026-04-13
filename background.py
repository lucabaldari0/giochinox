import pygame
import random
from settings import SCREEN_W, SCREEN_H

OCEAN_COLOR  = (20, 80, 140)
BUBBLE_COLOR = (150, 210, 240)


class Bubble:
    def __init__(self):
        self.reset(random.randint(0, SCREEN_H))

    def reset(self, y=None):
        self.x     = random.randint(0, SCREEN_W)
        self.y     = float(y if y is not None else SCREEN_H)
        self.r     = random.randint(2, 5)
        self.speed = random.uniform(0.3, 0.9)
        self.drift = random.uniform(-0.2, 0.2)
        self.alpha = random.randint(60, 140)

    def update(self):
        self.y -= self.speed
        self.x += self.drift
        if self.y < -10:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*BUBBLE_COLOR, self.alpha), (self.r+1, self.r+1), self.r)
        surface.blit(s, (int(self.x)-self.r, int(self.y)-self.r))


class OceanBackground:
    def __init__(self):
        self.bubbles = [Bubble() for _ in range(20)]

    def update(self):
        for b in self.bubbles:
            b.update()

    def draw(self, surface):
        surface.fill(OCEAN_COLOR)
        for b in self.bubbles:
            b.draw(surface)