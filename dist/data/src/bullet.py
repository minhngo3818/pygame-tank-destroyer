import pygame
import math
import random
from pygame.sprite import Sprite
from .settings import Settings


class Bullet(Sprite):

    #   Without image rotation engine
    def __init__(self, b_x, b_y, direction):
        super().__init__()
        self.setting = Settings()
        self.bullet_images = {"left": pygame.image.load("./data/images/bullet_left.png"),
                              "right": pygame.image.load("./data/images/bullet_right.png"),
                              "up": pygame.image.load("./data/images/bullet_up.png"),
                              "down": pygame.image.load("./data/images/bullet_down.png")}
        self.direction = direction
        self.image = self.bullet_images[self.direction].convert()
        self.rect = self.image.get_rect()
        self.rect.x = b_x
        self.rect.y = b_y
        self.speed = self.setting.bullet_speed  # Access Settings Files Later

    def update(self, win):
        if self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed
        elif self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed

        if self.rect.x < 0 or self.rect.x > self.setting.scr_width or \
                self.rect.y < 0 or self.rect.y > self.setting.scr_height:
            self.kill()

        self.image = self.bullet_images[self.direction]
        win.blit(self.image, (self.rect.x, self.rect.y))


class BossBullet(Sprite):

    #   With Rotate Engine
    def __init__(self, g_x, g_y, bullet_type, direction):
        super().__init__()

        self.setting = Settings()

        self.keysources = {"giant": [pygame.image.load("./data/images/Boss_Mega_Bullet.png"), self.setting.boss_cannon_speed],
                           "gatling": [pygame.image.load("./data/images/boss_gatl_bullet.png"),
                                       self.setting.boss_gatling_speed]}

        self.bullet_type = bullet_type
        self.image = self.keysources[self.bullet_type][0]
        self.rect = self.image.get_rect()
        self.direction = direction
        self.angle = 180
        self.rect.x = g_x
        self.rect.y = g_y
        self.speed = self.keysources[self.bullet_type][1]

    def update(self, win):
        if self.direction == "left":
            self.rect.x -= self.speed
            self.angle = 90
        elif self.direction == "right":
            self.rect.x += self.speed
            self.angle = 270
        elif self.direction == "up":
            self.rect.y -= self.speed
            self.angle = 0
        elif self.direction == "down":
            self.rect.y += self.speed
            self.angle = 180

        if self.rect.x < 0 or self.rect.x > self.setting.scr_width or \
                self.rect.y < 0 or self.rect.y > self.setting.scr_height:
            self.kill()

        rotate = pygame.transform.rotate
        rotate_image = rotate(self.image, self.angle)

        win.blit(rotate_image, (self.rect.x, self.rect.y))


class Laser(Sprite):
    def __init__(self, x, y, width, height, direction):
        Sprite.__init__(self)
        self.setting = Settings()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction
        self.angle = 0

    def move(self):

        if self.direction == "up":
            self.angle = 0
            self.rect.y -= 10
        elif self.direction == "down":
            self.angle = 180
            self.rect.y += 10
        elif self.direction == "left":
            self.angle = 90
            self.rect.x -= 10
        elif self.direction == "right":
            self.angle = 270
            self.rect.x += 10

    def update(self, win):
        self.move()
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.image.get_rect(center=(self.rect.x, self.rect.y)).center)
        win.blit(rotated_image, (rotated_rect.x, rotated_rect.y))


class LaserLayers:
    def __init__(self, x, y, width, height, direction):
        self.color_list = [(255, 0, 127), (255, 102, 178), (255, 204, 229)]
        self.laser_list = pygame.sprite.Group()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.direction = direction

    def add_laser_layers(self):
        laser1 = Laser(self.x, self.y, self.width, self.height, self.direction)
        laser1.image.fill(self.color_list[0])
        laser2 = Laser(self.x, self.y, self.width - 10, self.height, self.direction)
        laser2.image.fill(self.color_list[1])
        laser3 = Laser(self.x, self.y, self.width - 15, self.height, self.direction)
        laser3.image.fill(self.color_list[2])
        self.laser_list.add(laser1)
        self.laser_list.add(laser2)
        self.laser_list.add(laser3)

    def update_laser_list(self, win):
        self.add_laser_layers()
        for laser in self.laser_list:
            laser.update(win)


# Update laser_layers
def update_laser(laser_group, win):
    for laser_object in laser_group:
        laser_object.update_laser_list(win)


class Particles(Sprite):
    def __init__(self, x, y, target_x, target_y, color, direction):
        Sprite.__init__(self)
        self.radius = 5
        self.surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.rect = self.surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color
        self.target_x = target_x
        self.target_y = target_y
        self.direction = direction
        self.speed = 3

    def draw_circle(self, win):
        pygame.draw.circle(win, self.color, (self.rect.x, self.rect.y), self.radius)

    # Helper functions for update() aka position update
    # Helper function: updates linear x or y for horizontal or vertical tendencies
    def _left_right_y_update(self):
        if self.rect.y < self.target_y:
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed

    def _up_down_x_update(self):
        if self.rect.x < self.target_x:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

    # Helper functions: different direction cases
    def _move_left(self, dx, dy):
        para_center = (self.rect.x, self.target_y)  # center(x,y) of parabolic
        self._left_right_y_update()

        self.rect.x = para_center[0] + abs(dx) * math.sqrt(
            abs(1 - ((self.rect.y - para_center[1]) / abs(dy)) ** 2))

    def _move_right(self, dx, dy):
        para_center = (self.rect.x, self.target_y)
        self._left_right_y_update()

        self.rect.x = para_center[0] - abs(dx) * math.sqrt(
            abs(1 - ((self.rect.y - para_center[1]) / abs(dy)) ** 2))

    def _move_up(self, dx, dy):
        para_center = (self.target_x, self.rect.y)
        self._up_down_x_update()

        self.rect.y = para_center[1] + abs(dy) * math.sqrt(
            abs(1 - ((self.rect.x - para_center[0]) / abs(dx)) ** 2))

    def _move_down(self, dx, dy):
        para_center = (self.target_x, self.rect.y)
        self._up_down_x_update()

        self.rect.y = para_center[1] - abs(dy) * math.sqrt(
            abs(1 - ((self.rect.x - para_center[0]) / abs(dx)) ** 2))

    # Position update function
    def update(self, win):
        dx = self.rect.x - self.target_x
        dy = self.rect.y - self.target_y

        if abs(dx) > 0 and abs(dy) > 0:
            if self.direction == 'up':
                self._move_up(dx, dy)
            elif self.direction == 'down':
                self._move_down(dx, dy)
            elif self.direction == 'left':
                self._move_left(dx, dy)
            elif self.direction == 'right':
                self._move_right(dx, dy)

        elif dx < 0 and dy == 0:
            self.rect.x += self.speed
        elif dx > 0 and dy == 0:
            self.rect.x -= self.speed
        elif dx == 0 and dy < 0:
            self.rect.y += self.speed
        elif dx == 0 and dy > 0:
            self.rect.y -= self.speed

        self.draw_circle(win)


def spawn_particles(charge_group, density, boss):
    pos_x = 0
    pos_y = 0
    pos_gather_x = 0
    pos_gather_y = 0

    if boss.direction == "up":
        pos_x = random.randrange(boss.rect.x - 50, boss.rect.x + 178)
        pos_y = random.randrange(boss.rect.y - 50, boss.rect.y)
        (pos_gather_x, pos_gather_y) = boss.rect.midtop

    elif boss.direction == "down":
        pos_x = random.randrange(boss.rect.x - 50, boss.rect.x + 178)
        pos_y = random.randrange(boss.rect.y + 128, boss.rect.y + 178)
        (pos_gather_x, pos_gather_y) = boss.rect.midbottom

    elif boss.direction == "left":
        pos_x = random.randrange(boss.rect.x - 50, boss.rect.x)
        pos_y = random.randrange(boss.rect.y, boss.rect.y + 178)
        (pos_gather_x, pos_gather_y) = boss.rect.midleft

    elif boss.direction == "right":
        pos_x = random.randrange(boss.rect.x + 128, boss.rect.x + 178)
        pos_y = random.randrange(boss.rect.y, boss.rect.y + 178)
        (pos_gather_x, pos_gather_y) = boss.rect.midright

    for i in range(density):
        charge_group.add(Particles(pos_x, pos_y, pos_gather_x, pos_gather_y, (255, 255, 255), boss.direction))


def remove_particles(charge_group, boss):
    for c in charge_group:
        if (pygame.sprite.collide_rect(c, boss) or (
                (boss.direction == 'up' and c.rect.y >= boss.rect.midtop[1]) or
                (boss.direction == 'down' and c.rect.y <= boss.rect.midbottom[1]) or
                (boss.direction == 'left' and c.rect.x >= boss.rect.midleft[0]) or
                (boss.direction == 'right' and c.rect.x <= boss.rect.midright[0])
        )):
            charge_group.remove(c)
