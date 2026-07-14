import pygame
import random

pygame.init()

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 1000  # Rozmiar okna gry
WHITE = (255, 255, 255)    # Kolor tła
GREEN = (0, 255, 0)        # Kolor platform
RED = (255, 0, 0)          # Kolor komunikatu Game Over
BLUE = (0, 0, 255)         # Kolor gracza

# Stałe fizyczne
GRAVITY = 0.7       # Grawitacja
JUMP_STRENGTH = -19 # Siła skoku
SPEED = 5           # Prędkość pozioma gracza
SCROLL_SPEED = 1.75    # Prędkość przesuwania ekranu
WIN_SCORE = 2500    # Liczba punktów potrzebna do wygranej

# Inicjalizacja okna gry
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wspinaczka Platformowa")

# Wczytanie i przeskalowanie tła
background = pygame.image.load("background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


class Player:
    """Klasa gracza"""
    def __init__(self, first_platform):
        # Ustawienie początkowej pozycji na pierwszej platformie
        self.rect = pygame.Rect(first_platform.x + 30, first_platform.y - 40, 40, 40)
        self.vel_x = 0  # Prędkość pozioma
        self.vel_y = 0  # Prędkość pionowa
        self.on_ground = False  # Czy gracz stoi na platformie?
        self.score = 0  # Wynik

    def move(self, platforms, scroll_offset):
        """Ruch gracza"""
        self.vel_y += GRAVITY  # Grawitacja działa na gracza
        self.rect.x += self.vel_x  # Ruch poziomy

        # Kolizja pozioma
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:  # Ruch w prawo
                    self.rect.right = platform.left
                if self.vel_x < 0:  # Ruch w lewo
                    self.rect.left = platform.right

        self.rect.y += self.vel_y  # Ruch pionowy
        self.on_ground = False  # Reset statusu kolizji

        # Kolizja pionowa
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:  # Spadanie na platformę
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  # Uderzenie w platformę od dołu
                    self.rect.top = platform.bottom
                    self.vel_y = 0

        # Aktualizacja wyniku
        self.score = max(self.score, scroll_offset + (HEIGHT - self.rect.y))

    def draw(self):
        """Rysowanie gracza"""
        pygame.draw.rect(screen, BLUE, self.rect)


class Level:
    """Klasa reprezentująca poziom gry"""
    def __init__(self, num_platforms):
        self.platforms = self.generate_platforms(num_platforms)  # Generowanie platform

    def generate_platforms(self, num):
        """Tworzenie losowych platform"""
        platforms = []
        last_y = HEIGHT - 50  # Dolna platforma
        for _ in range(num):
            x = random.randint(50, WIDTH - 150)  # Losowa pozycja X
            y = last_y - random.randint(70, 100)  # Odstępy między platformami
            platforms.append(pygame.Rect(x, y, 100, 20))  # Tworzenie platformy
            last_y = y
        return platforms

    def draw(self):
        """Rysowanie platform"""
        for platform in self.platforms:
            pygame.draw.rect(screen, GREEN, platform)


def show_game_over():
    """Ekran końca gry"""
    screen.fill(WHITE)
    font = pygame.font.Font(None, 50)
    text = font.render("Game Over! Naciśnij R, aby zrestartować", True, RED)
    screen.blit(text, (WIDTH // 2 - 250, HEIGHT // 2))
    pygame.display.flip()

    # Czekanie na restart lub zamknięcie gry
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                waiting = False  # Restart gry

# Tworzenie poziomu i gracza
level = Level(10)
player = Player(level.platforms[0])
scroll_offset = 0

clock = pygame.time.Clock()
running = True

# Pętla gry
while running:
    screen.blit(background, (0, 0))  # Rysowanie tła

    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                player.vel_x = -SPEED  # Ruch w lewo
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                player.vel_x = SPEED  # Ruch w prawo
            if event.key in [pygame.K_UP, pygame.K_w] and player.on_ground:
                player.vel_y = JUMP_STRENGTH  # Skok
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d]:
                player.vel_x = 0  # Zatrzymanie

    # Przesuwanie ekranu i platform
    scroll_offset += SCROLL_SPEED
    for platform in level.platforms:
        platform.y += SCROLL_SPEED
    player.rect.y += SCROLL_SPEED

    # Ruch gracza
    player.move(level.platforms, scroll_offset)

    # Sprawdzenie, czy gracz spadł poza ekran
    if player.rect.top > HEIGHT:
        show_game_over()
        level = Level(10)  # Restart poziomu
        player = Player(level.platforms[0])  # Restart gracza
        scroll_offset = 0

    # Dodawanie nowych platform na górze
    while level.platforms[-1].y > 50:
        new_platform = pygame.Rect(random.randint(50, WIDTH - 150),
                                   level.platforms[-1].y - random.randint(70, 100),
                                   100, 20)
        level.platforms.append(new_platform)

    level.platforms = [p for p in level.platforms if p.y < HEIGHT]

    # Sprawdzenie warunku wygranej
    if player.score >= WIN_SCORE:
        font = pygame.font.Font(None, 50)
        win_text = font.render("Gratulacje! Wygrałeś!", True, RED)
        screen.blit(win_text, (WIDTH // 2 - 180, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    level.draw()
    player.draw()

    # Wyświetlanie wyniku
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Punkty: {int(player.score)}/{WIN_SCORE}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)  # Ograniczenie FPS do 60

pygame.quit()
