import pygame
import random
import time
from constant_images_sounds_import import *

class Floor:
    def __init__(self, x, y, width, height, if_enemies):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.flowers = pygame.sprite.Group()
        self.create_platforms(if_enemies)
        
    def create_platforms(self, if_enemies):
        offset = 50

        # Boczne ściany
        left_wall = Platform(self.x, self.y + self.height, WALL_THICKNESS, self.height)
        right_wall = Platform(self.x + self.width - WALL_THICKNESS, self.y + self.height, WALL_THICKNESS, self.height)

        # przerwa miedzy poziomymi platformami
        gap_width = 200
        gap_x = random.randint(WALL_THICKNESS + offset, self.width - WALL_THICKNESS - gap_width - offset)  # Losowa pozycja X dziury

        # Platformy górne
        horizontal_platform1_width = gap_x - WALL_THICKNESS
        horizontal_platform2_x = self.x + gap_x + gap_width
        horizontal_platform2_width = self.width - gap_x - gap_width - WALL_THICKNESS

        horizontal_platform1 = Platform(self.x + WALL_THICKNESS, self.y + self.height, horizontal_platform1_width, -WALL_THICKNESS)
        horizontal_platform2 = Platform(horizontal_platform2_x, self.y + self.height, horizontal_platform2_width, -WALL_THICKNESS)

        self.platforms.add(left_wall, right_wall, horizontal_platform1, horizontal_platform2)

        if(if_enemies):
            self.create_enemies(horizontal_platform1, horizontal_platform2)
            self.create_flowers(horizontal_platform1)


    def create_enemies(self, horizontal_platform1, horizontal_platform2):
        enemy1 = Enemy(horizontal_platform1)
        enemy1.rect.x = WALL_THICKNESS
        enemy1.rect.bottom = horizontal_platform1.rect.top
        self.enemies.add(enemy1)
        enemy2 = Enemy(horizontal_platform2)
        enemy2.rect.x = horizontal_platform2.rect.left
        enemy2.rect.bottom = horizontal_platform1.rect.top
        self.enemies.add(enemy2)

    def create_flowers(self, horizontal_platform1):
        flower = Flower(horizontal_platform1)
        flower.rect.x = random.randint(WALL_THICKNESS, SCREEN_WIDTH-WALL_THICKNESS-FLOWER_WIDTH)
        flower.rect.bottom = horizontal_platform1.rect.top - 30
        self.flowers.add(flower)

    def update(self):
        pass

    def draw(self, surface):
        # self.platforms.draw(surface)  # Rysowanie platform
        # for enemy in self.enemies:
        #     enemy.draw(surface) 
        # self.enemies.draw(surface)  # Rysowanie przeciwników
        pass


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Inicjalizacja platformy
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width, abs(self.height)))  # Używamy wartości bezwzględnej dla wysokości
        self.image.fill(PINK)  # Wypełnienie powierzchni białym kolorem
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, surface):
        # Rysowanie platformy na powierzchni
        surface.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, platform):
        super().__init__()
        self.image = IMAGES['STORK'].copy()
        self.image_origin = IMAGES['STORK'].copy()
        self.rect = self.image.get_rect()
        self.platform = platform
        self.direction = "right"
        self.speed = 4
        self.hearts = 3
        self.filter_duration = 1.0  # Czas trwania nakładania filtru w sekundach
        self.filter_start_time = None

    def update(self):
        if self.direction == "right":
            self.rect.x += self.speed
        if self.rect.x + ENEMY_WIDTH >= self.platform.rect.right:
            self.direction = "left"
            self.image = pygame.transform.flip(self.image, True, False)
        if self.direction == "left":
            self.rect.x -= self.speed
            if self.rect.x <= self.platform.rect.left:
                self.direction = "right"
                self.image = pygame.transform.flip(self.image, True, False)
        if self.filter_start_time is not None:
            current_time = time.time()
            elapsed_time = current_time - self.filter_start_time
            if elapsed_time < self.filter_duration:
                red = (255, 0, 0, 255)
                self.image.fill(red, special_flags=pygame.BLEND_RGBA_MIN)
            else:
                if self.direction == 'right':
                    self.image = self.image_origin
                else:
                    self.image = pygame.transform.flip(self.image_origin, True, False)
    
    def turn_red(self):
        self.filter_start_time = time.time()
        
    #   self.animate()

    # def animate(self):
    #     self.animation_counter += 1
    #     if self.animation_counter >= self.animation_delay:
    #         self.animation_counter = 0
    #         self.animation_index = (self.animation_index + 1) % len(self.images)
    #         self.image = self.images[self.animation_index]

    def draw(self):
        pass


class Flower(pygame.sprite.Sprite):
    def __init__(self, platform):
        super().__init__()
        self.image = IMAGES['FLOWER']
        self.rect = self.image.get_rect()
        self.platform = platform
        self.visible = True

    def update(self):
        pass
    
    def draw(self):
        pass