import pygame
import sys
import time
from constant_images_sounds_import import *
from floor import *

pygame.init()
pygame.mixer.init()

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(SCREEN_WIDTH / 2)
        y = -target.rect.y + int(SCREEN_HEIGHT / 2)

        # Ograniczenie ruchu kamery do granic planszy
        x = min(0, x)  # Lewa krawędź
        y = min(0, y)  # Górna krawędź
        x = max(-(self.width - SCREEN_WIDTH), x)  # Prawa krawędź
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Dolna krawędź

        self.camera = pygame.Rect(x, y, self.width, self.height)

class Character(pygame.sprite.Sprite): #player i enemy
    def __init__(self, all_sprites, camera):
        super().__init__(all_sprites)
        # Inicjalizacja postaci
        self.speed = 5
        self.camera = camera
        self.collided = False
        self.hearts = 3
        self.filter_duration = 1.0
        self.filter_start_time = None
        self.direction = 'right'

    def update(self):
        pass

    def draw(self):
        pass

#####################################

class Player(Character):
    def __init__(self, all_sprites, camera, shooting_enabled):
        super().__init__(all_sprites, camera)
        self.width = 100
        self.height = 100
        self.image = IMAGES['FROG']
        self.rect = self.image.get_rect()
        self.speed = 5
        self.jump_power = 20
        self.vertical_speed = 0
        self.gravity = 1
        self.collided = False
        self.space_pressed = False
        self.shooting_enabled = shooting_enabled
        self.bullets = pygame.sprite.Group()

    def update(self, floors):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = 'left'
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 'right'
        if self.shooting_enabled:
            if keys[pygame.K_SPACE] and not self.space_pressed and len(self.bullets) <= 5:
                self.space_pressed = True
                bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
                self.bullets.add(bullet)
            if not keys[pygame.K_SPACE]:
                self.space_pressed = False                

        # Sprawdzenie zwolnienia klawisza skoku
        if not keys[pygame.K_UP] and self.vertical_speed < 0:
            self.vertical_speed = 0

        # Skok
        if keys[pygame.K_UP] and self.vertical_speed == 0 and not self.is_jumping:
            SOUNDS['JUMP'].play()
            self.vertical_speed = -self.jump_power
            self.is_jumping = True

        self.vertical_speed += self.gravity
        self.rect.y += self.vertical_speed

        # Sprawdzenie kolizji z platformami
        collision_platform = pygame.sprite.spritecollideany(self, floors)
        if collision_platform:
            if self.vertical_speed > 0:  # Kolizja z platformą, poruszanie się w dół
                self.rect.bottom = collision_platform.rect.top
                self.vertical_speed = 0
                self.is_jumping = False
            elif self.vertical_speed < 0:  # Kolizja z platformą, poruszanie się w górę
                self.rect.top = collision_platform.rect.bottom
                self.vertical_speed = 0
                self.is_jumping = False
            else:
                self.is_jumping = True

        # Ograniczenia ruchu gracza do granic ekranu
        if self.rect.left < 0 + WALL_THICKNESS:
            self.rect.left = WALL_THICKNESS
        if self.rect.right > SCREEN_WIDTH - WALL_THICKNESS:
            self.rect.right = SCREEN_WIDTH - WALL_THICKNESS
        
        if self.filter_start_time is not None:
            current_time = time.time()
            elapsed_time = current_time - self.filter_start_time
            if elapsed_time < self.filter_duration:
                self.image = IMAGES['FROG_RED'].copy()
            else:
                self.image = IMAGES['FROG'].copy()

    def hurt(self, enemy):
        if self.rect.colliderect(enemy.rect):
            if not enemy.collided:
                SOUNDS['HURT'].play()
                self.hearts -= 1
                enemy.collided = True
                self.filter_start_time = time.time()
        else:
            enemy.collided = False
        
    def draw(self):
        pass


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = IMAGES['BULLET']
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Ustaw początkowe położenie pocisku na środek gracza
        self.speed = 10  # Prędkość pocisku
        self.direction = direction
        if direction == 'left':
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        if self.direction == 'right':
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

    def draw(self):
        pass

#####################################

class Game:
    def __init__(self, mode):
        self.mode = mode
        if self.mode == 'pacyfist':
            self.shooting_enabled = False
        else:
            self.shooting_enabled = True
        self.clock = pygame.time.Clock()
        self.running = True
        self.points = 0

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.generate_floors()

    def generate_floors(self):
        self.floors = []
        self.floor_height = int(SCREEN_HEIGHT * 0.45)  # Wysokość piętra
        self.num_floors = 10  # Ilość pięter
        self.level_height = self.num_floors * self.floor_height
        self.lowest_platform = None 
        if_enemies = False
        self.camera = Camera(SCREEN_WIDTH, self.level_height)
        self.player = Player(self.all_sprites, self.camera, self.shooting_enabled)

        for floor in range(self.num_floors):
            floor_x = 0
            floor_y = self.level_height - (floor + 1) * self.floor_height  # Pozycja Y piętra
            floor_width = SCREEN_WIDTH  # Szerokość piętra
            if floor == self.num_floors-1:
                if_enemies = False
            floor = Floor(floor_x, floor_y, floor_width, self.floor_height, if_enemies)
            if_enemies = True
            self.floors.append(floor)
            self.all_sprites.add(floor.platforms)
            self.platforms.add(floor.platforms)
            if self.lowest_platform is None or floor_y > self.lowest_platform.y:
                self.lowest_platform = floor

    def run(self):
        SOUNDS['SOUNDTRACK'].play(-1)
        while self.running:
            if self.mode != 'speedrun':
                self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        SOUNDS['SOUNDTRACK'].stop()
        start_screen()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.mode == 'speedrun':
            global current_time
            current_time += self.clock.tick(FPS) / 1000
        if self.player.hearts <= 0:
            self.running = False
            self.winner_text = "Przegrana"
            SOUNDS['SOUNDTRACK'].stop()
            SOUNDS['LOSE'].play()
            game_over_screen(self.winner_text, self.points)
        if self.mode == 'speedrun' and current_time >= level_time:
            self.running = False
            self.winner_text = "Koniec czasu"
            SOUNDS['SOUNDTRACK'].stop()
            SOUNDS['LOSE'].play()
            game_over_screen(self.winner_text, self.points)
        self.all_sprites.update(self.platforms)
        self.camera.update(self.player)
        if self.player.rect.y + self.player.height >= self.lowest_platform.y + self.floor_height:
            self.running = False
            SOUNDS['SOUNDTRACK'].stop()
            SOUNDS['WIN'].play()
            self.winner_text = "Wygrana"
            game_over_screen(self.winner_text, self.points)
        for floor in self.floors:
            for enemy in floor.enemies:
                enemy.update()
                self.player.hurt(enemy)
                collisions = pygame.sprite.spritecollide(enemy, self.player.bullets, True)
                for _ in collisions:
                    enemy.hearts -= 1
                    enemy.turn_red()
                if enemy.hearts <= 0:
                    SOUNDS['ENEMY_DIED'].play()
                    floor.enemies.remove(enemy)
            for flower in floor.flowers:
                if flower.visible and self.player.rect.colliderect(flower.rect):
                    SOUNDS['FLOWER'].play()
                    self.points += 1
                    flower.visible = False
        for bullet in self.player.bullets:
            bullet.update()
            if bullet.rect.right > SCREEN_WIDTH - WALL_THICKNESS or bullet.rect.x < 0 + WALL_THICKNESS:
                self.player.bullets.remove(bullet)
        
    def draw(self):
        WINDOW.blit(BACKGROUND, (0, 0))
        for sprite in self.all_sprites:
            sprite_rect = self.camera.apply(sprite)
            WINDOW.blit(sprite.image, sprite_rect) 
        for floor in self.floors:
            for enemy in floor.enemies:
                sprite_rect = self.camera.apply(enemy)
                WINDOW.blit(enemy.image, sprite_rect)
            for flower in floor.flowers:
                if flower.visible:
                    sprite_rect = self.camera.apply(flower)
                    WINDOW.blit(flower.image, sprite_rect)
        for bullet in self.player.bullets:
            sprite_rect = self.camera.apply(bullet)
            WINDOW.blit(bullet.image, sprite_rect)
        x = 10
        for _ in range (0, self.player.hearts):
            WINDOW.blit(IMAGES['HEART'], (x, 10))
            x += 10 + HEART_WIDTH
        WINDOW.blit(IMAGES['FLOWER'], (10, 10+HEART_HEIGHT+10))
        points_text = MENU_FONT.render("x" + str(self.points), True, BEIGE)
        WINDOW.blit(points_text, (70, 85))
        if self.mode == 'speedrun':
            time_text = MENU_FONT.render(str(int(level_time - current_time)), True, BEIGE)
            WINDOW.blit(time_text, (10, 130))
            
        pygame.display.update()

def start_screen():
    running = True
    global mode
    text_color_start = WHITE
    text_color_settings = WHITE
    text_color_exit = WHITE

    while running:
        WINDOW.blit(BACKGROUND_SETTINGS, (0, 0))  # Wypełnienie ekranu czarnym kolorem

        # Wyswietlanie tytulu
        title_text1 = MENU_FONT.render("Super House of", True, PINK)
        title_rect1 = title_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        WINDOW.blit(title_text1, title_rect1)

        title_text2 = TITLE_FONT.render("D e a d F r o g g i e s", True, PINK)
        title_rect2 = title_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        WINDOW.blit(title_text2, title_rect2)

        # Wyswietlanie opcji menu
        start_text_surface = MENU_FONT.render("Start", True, text_color_start)
        start_rect = start_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        WINDOW.blit(start_text_surface, start_rect)

        settings_text_surface = MENU_FONT.render("Ustawienia", True, text_color_settings)
        settings_rect = settings_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        WINDOW.blit(settings_text_surface, settings_rect)

        exit_text_surface = MENU_FONT.render("Zakończ", True, text_color_exit)
        exit_rect = exit_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        WINDOW.blit(exit_text_surface, exit_rect)

        pygame.display.flip()  # Odświeżenie ekranu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    text_color_start = pygame.Color(PINK)
                else:
                    text_color_start = WHITE
                if settings_rect.collidepoint(mouse_pos):
                    text_color_settings = pygame.Color(PINK)
                else:
                    text_color_settings = WHITE
                if exit_rect.collidepoint(mouse_pos):
                    text_color_exit = pygame.Color(PINK)
                else:
                    text_color_exit = WHITE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    running = False
                    option = 1
                elif settings_rect.collidepoint(mouse_pos):
                    running = False
                    option = 2
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
    if option == 1:
        game = Game(mode)
        game.run()
    elif option == 2:
        settings_screen()

def settings_screen():
    running = True
    global mode
    text_color_back = WHITE
    text_color_mode = WHITE
    text_color_sound = WHITE
    text_color_normal = WHITE
    text_color_pacifist = WHITE
    text_color_speedrun = WHITE

    while running:
        WINDOW.blit(BACKGROUND_SETTINGS, (0, 0))  # Wypełnienie ekranu tłem ustawień

        # Wyświetlanie tytułu
        title_text = TITLE_FONT.render("Ustawienia", True, PINK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        WINDOW.blit(title_text, title_rect)

        # Wyświetlanie opcji ustawień
        back_text_surface = MENU_FONT.render("Powrót", True, text_color_back)
        back_rect = back_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        WINDOW.blit(back_text_surface, back_rect)

        sound_text_surface = MENU_FONT.render("Dźwięk", True, text_color_sound)
        sound_rect = sound_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        WINDOW.blit(sound_text_surface, sound_rect)

        mode_text_surface = MENU_FONT.render("Tryb:", True, text_color_mode)
        mode_rect = mode_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        WINDOW.blit(mode_text_surface, mode_rect)

        normal_text_surface = MENU_FONT.render("Normalny", True, text_color_normal)
        normal_rect = normal_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 190))
        WINDOW.blit(normal_text_surface, normal_rect)

        pacifist_text_surface = MENU_FONT.render("Pacyfistyczny", True, text_color_pacifist)
        pacifist_rect = pacifist_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 230))
        WINDOW.blit(pacifist_text_surface, pacifist_rect)

        speedrun_text_surface = MENU_FONT.render("Speedrun", True, text_color_speedrun)
        speedrun_rect = speedrun_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 270))
        WINDOW.blit(speedrun_text_surface, speedrun_rect)

        pygame.display.flip()  # Odświeżenie ekranu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    text_color_back = pygame.Color(PINK)
                else:
                    text_color_back = WHITE
                if sound_rect.collidepoint(mouse_pos):
                    text_color_sound = pygame.Color(PINK)
                else:
                    text_color_sound = WHITE
                if normal_rect.collidepoint(mouse_pos):
                    text_color_normal = pygame.Color(PINK)
                else:
                    text_color_normal = WHITE
                if pacifist_rect.collidepoint(mouse_pos):
                    text_color_pacifist = pygame.Color(PINK)
                else:
                    text_color_pacifist = WHITE
                if speedrun_rect.collidepoint(mouse_pos):
                    text_color_speedrun = pygame.Color(PINK)
                else:
                    text_color_speedrun = WHITE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    running = False
                    start_screen()  # Powrót do ekranu startowego
                elif sound_rect.collidepoint(mouse_pos):
                    volume_settings()
                elif normal_rect.collidepoint(mouse_pos):
                    mode = 'standard'
                    pass
                elif pacifist_rect.collidepoint(mouse_pos):
                    mode = 'pacyfist'
                    pass
                elif speedrun_rect.collidepoint(mouse_pos):
                    mode = 'speedrun'
                    pass

def volume_settings():
    running = True
    text_color_back = WHITE
    text_color_mute = WHITE
    text_color_volume = WHITE
    text_color_proc_25 = WHITE
    text_color_proc_50 = WHITE
    text_color_proc_75 = WHITE
    text_color_proc_100 = WHITE

    while running:
        WINDOW.blit(BACKGROUND_SETTINGS, (0, 0))  # Wypełnienie ekranu tłem ustawień

        # Wyświetlanie tytułu
        title_text = TITLE_FONT.render("Ustawienia", True, PINK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        WINDOW.blit(title_text, title_rect)

        # Wyświetlanie opcji ustawień
        back_text_surface = MENU_FONT.render("Powrót", True, text_color_back)
        back_rect = back_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        WINDOW.blit(back_text_surface, back_rect)

        mute_text_surface = MENU_FONT.render("Wycisz", True, text_color_mute)
        mute_rect = mute_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        WINDOW.blit(mute_text_surface, mute_rect)

        volume_text_surface = MENU_FONT.render("Głośność:", True, text_color_volume)
        volume_rect = volume_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        WINDOW.blit(volume_text_surface, volume_rect)

        proc_25_text_surface = MENU_FONT.render("25%", True, text_color_proc_25)
        proc_25_rect = proc_25_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 190))
        WINDOW.blit(proc_25_text_surface, proc_25_rect)

        proc_50_text_surface = MENU_FONT.render("50%", True, text_color_proc_50)
        proc_50_rect = proc_50_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 230))
        WINDOW.blit(proc_50_text_surface, proc_50_rect)

        proc_75_text_surface = MENU_FONT.render("75%", True, text_color_proc_75)
        proc_75_rect = proc_75_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 270))
        WINDOW.blit(proc_75_text_surface, proc_75_rect)

        proc_100_text_surface = MENU_FONT.render("100%", True, text_color_proc_100)
        proc_100_rect = proc_100_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 310))
        WINDOW.blit(proc_100_text_surface, proc_100_rect)

        pygame.display.flip()  # Odświeżenie ekranu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    text_color_back = pygame.Color(PINK)
                else:
                    text_color_back = WHITE
                if mute_rect.collidepoint(mouse_pos):
                    text_color_mute = pygame.Color(PINK)
                else:
                    text_color_mute = WHITE
                if proc_25_rect.collidepoint(mouse_pos):
                    text_color_proc_25 = pygame.Color(PINK)
                else:
                    text_color_proc_25 = WHITE
                if proc_50_rect.collidepoint(mouse_pos):
                    text_color_proc_50 = pygame.Color(PINK)
                else:
                    text_color_proc_50 = WHITE
                if proc_75_rect.collidepoint(mouse_pos):
                    text_color_proc_75 = pygame.Color(PINK)
                else:
                    text_color_proc_75 = WHITE
                if proc_100_rect.collidepoint(mouse_pos):
                    text_color_proc_100 = pygame.Color(PINK)
                else:
                    text_color_proc_100 = WHITE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    running = False
                    start_screen()  # Powrót do ekranu startowego
                elif mute_rect.collidepoint(mouse_pos): 
                    for sound in SOUNDS.values():
                        sound.set_volume(0.0)
                elif proc_25_rect.collidepoint(mouse_pos):
                    for sound in SOUNDS.values():
                        sound.set_volume(0.25)
                elif proc_50_rect.collidepoint(mouse_pos):
                    for sound in SOUNDS.values():
                        sound.set_volume(0.5)
                elif proc_75_rect.collidepoint(mouse_pos):
                    for sound in SOUNDS.values():
                        sound.set_volume(0.75)
                elif proc_100_rect.collidepoint(mouse_pos):
                    for sound in SOUNDS.values():
                        sound.set_volume(1.0)
                SOUNDS['TEST'].play()
                 
def game_over_screen(text, points):
    running = True
    global mode
    text_color_start = WHITE
    text_color_settings = WHITE
    text_color_exit = WHITE

    while running:
        WINDOW.blit(BACKGROUND_SETTINGS, (0, 0))  # Wypełnienie ekranu czarnym kolorem

        # Wyswietlanie tytulu
        title_text1 = TITLE_FONT.render(text, True, PINK)
        title_rect1 = title_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        WINDOW.blit(title_text1, title_rect1)
        
        title_text1 = MENU_FONT.render("liczba punktow: " + str(points) + "/" + str(8), True, PINK)
        title_rect1 = title_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        WINDOW.blit(title_text1, title_rect1)

        # Wyswietlanie opcji menu
        start_text_surface = MENU_FONT.render("Zagraj jeszcze raz", True, text_color_start)
        start_rect = start_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        WINDOW.blit(start_text_surface, start_rect)

        settings_text_surface = MENU_FONT.render("Ustawienia", True, text_color_settings)
        settings_rect = settings_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        WINDOW.blit(settings_text_surface, settings_rect)

        exit_text_surface = MENU_FONT.render("Zakończ", True, text_color_exit)
        exit_rect = exit_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
        WINDOW.blit(exit_text_surface, exit_rect)

        pygame.display.flip()  # Odświeżenie ekranu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    text_color_start = pygame.Color(PINK)
                else:
                    text_color_start = WHITE
                if settings_rect.collidepoint(mouse_pos):
                    text_color_settings = pygame.Color(PINK)
                else:
                    text_color_settings = WHITE
                if exit_rect.collidepoint(mouse_pos):
                    text_color_exit = pygame.Color(PINK)
                else:
                    text_color_exit = WHITE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    running = False
                    option = 1
                elif settings_rect.collidepoint(mouse_pos):
                    running = False
                    option = 2
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
    if option == 1:
        game = Game(mode)
        game.run()
    elif option == 2:
        settings_screen()


if __name__ == "__main__":
    level_time = 30
    current_time = 0
    mode = 'standard'
    start_screen()

pygame.quit()