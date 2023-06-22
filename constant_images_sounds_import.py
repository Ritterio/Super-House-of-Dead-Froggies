import pygame
import os

pygame.init()
pygame.mixer.init()

TITLE_FONT = pygame.font.SysFont('consolas', 70)
MENU_FONT = pygame.font.SysFont('consolas', 40)

BEIGE = ("#FFCDB2")
WHITE = ("#B5838D")
PINK = ("#6D6875")
BLACK = (0, 0, 0)

FPS = 60
SPEED = 5
WALL_THICKNESS = 30

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 740
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super House of DeadFroggies")

FROG_WIDTH, FROG_HEIGHT = 70, 70
ENEMY_WIDTH, ENEMY_HEIGHT = 100, 100
HEART_WIDTH, HEART_HEIGHT = 50, 50
FLOWER_WIDTH, FLOWER_HEIGHT = 50, 50

# grafiki
path = os.path.join(os.getcwd(), 'images')
file_names = sorted(os.listdir(path))
BACKGROUND = pygame.image.load(os.path.join(path, 'background_settings.jpg')).convert()
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
BACKGROUND_SETTINGS = pygame.image.load(os.path.join(path, 'background_settings.jpg')).convert()
BACKGROUND_SETTINGS = pygame.transform.scale(BACKGROUND_SETTINGS, (SCREEN_WIDTH, SCREEN_HEIGHT))

#file_names.remove('background.jpg')
file_names.remove('background_settings.jpg')
IMAGES = {}
for file_name in file_names:
    image_name = file_name[:-4].upper()
    IMAGES[image_name] = pygame.image.load(os.path.join(path, file_name)).convert_alpha(BACKGROUND)

IMAGES['FROG'] = pygame.transform.scale(IMAGES['FROG'], (FROG_WIDTH, FROG_HEIGHT))
IMAGES['FROG_RED'] = pygame.transform.scale(IMAGES['FROG_RED'], (FROG_WIDTH, FROG_HEIGHT))
IMAGES['STORK'] = pygame.transform.scale(IMAGES['STORK'], (ENEMY_WIDTH, ENEMY_HEIGHT))
IMAGES['HEART'] = pygame.transform.scale(IMAGES['HEART'], (HEART_WIDTH, HEART_HEIGHT))
IMAGES['FLOWER'] = pygame.transform.scale(IMAGES['FLOWER'], (FLOWER_WIDTH, FLOWER_HEIGHT))
IMAGES['BULLET'] = pygame.transform.scale(IMAGES['BULLET'], (40, 40))
IMAGES['BULLET_L'] = pygame.transform.scale(IMAGES['BULLET_L'], (40, 40))


#dzwieki
path = os.path.join(os.getcwd(), 'sounds')
file_names = sorted(os.listdir(path))

SOUNDS = {}
for file_name in file_names:
    sound_name = file_name[:-4].upper()
    SOUNDS[sound_name] = pygame.mixer.Sound(os.path.join(path, file_name))
