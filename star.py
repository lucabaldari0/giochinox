import pygame
import random
from settings import SCREEN_W, SCREEN_H


class Star:
    def __init__(self, stage=1):
        self.stage = stage
        self.reset(
            random.randint(0, SCREEN_H) if stage == 1 else random.randint(0, SCREEN_W)
        )

    def reset(self, pos=0):
        if self.stage == 1:
            self.x      = random.randint(0, SCREEN_W)
            self.y      = float(pos)
        else:
            self.x      = float(pos)
            self.y      = random.randint(0, SCREEN_H)
        self.speed      = random.uniform(0.5, 2.0)
        self.r          = random.uniform(0.5, 1.8)
        self.brightness = random.randint(100, 220)

    def update(self):
        if self.stage == 1:
            self.y += self.speed
            if self.y > SCREEN_H:
                self.reset()
        else:
            self.x -= self.speed
            if self.x < 0:
                self.reset(SCREEN_W)

    def draw(self, surface):
        c = self.brightness
        pygame.draw.circle(
            surface, (c, c, c),
            (int(self.x), int(self.y)),
            max(1, int(self.r))
        )
