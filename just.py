import pygame
import os
# from pygame.locals import *
import sys
import datetime

# константы
FPS = 60
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

PURPLE = 61, 23, 140
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 195, 245, 0
ORANGE = 255, 195, 0
LIGHT_YELLOW = 212, 250, 62

game = False
titles = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # return image
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# класс кнопок
class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        #  получаем позицию мыши
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # выводим кнопку
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


# класс доски
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

        f = open('data/level_1.txt', encoding='utf8')
        self.board = []
        lines = f.readlines()
        for line in lines:
            board = [int(i) for i in line if i not in '\n']
            self.board.append(board)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        self.screen = screen
        left = self.left
        top = self.top
        for i in self.board:
            for j in i:
                coors = (left, top, self.cell_size, self.cell_size)
                if j:
                    pygame.draw.rect(screen, ORANGE, coors)
                pygame.draw.rect(screen, 'white', coors, 1)
                left += self.cell_size
            left = self.left
            top += self.cell_size

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
        if mouse_pos[0] < self.left or mouse_pos[0] > (self.left + self.width * self.cell_size):
            return None
        if mouse_pos[1] < self.top or mouse_pos[1] > (self.top + self.height * self.cell_size):
            return None
        x = (mouse_pos[0] - self.left) // self.cell_size
        y = (mouse_pos[1] - self.top) // self.cell_size
        return x, y

    def on_click(self, cell_coords):
        if not cell_coords:
            return


class Slime(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.alive = True


# начальный экран
def intro():
    global game
    global running

    screen.fill(PURPLE)
    font = pygame.font.Font(None, 110)
    s1 = font.render('СлаймШот', True, WHITE)
    rect = s1.get_rect()
    pygame.draw.rect(s1, YELLOW, rect, 5)
    screen.blit(s1, (90, 100))

    # создаем кнопки
    font1 = pygame.font.Font(None, 80)
    image1 = font1.render('Начать', True, YELLOW)
    image2 = font1.render('Выйти', True, YELLOW)
    start_button = Button(SCREEN_WIDTH // 2 + 70, SCREEN_HEIGHT // 2 - 30, image1, 1)
    exit_button = Button(SCREEN_WIDTH // 2 + 70, SCREEN_HEIGHT // 2 + 50, image2, 1)

    if start_button.draw(screen):
        game = True
    if exit_button.draw(screen):
        running = False


# сама игра
def play():
    global game
    global titles
    # определяем фон в зависимости от времени суток
    if str(datetime.datetime.now())[11:13] < '04' or str(datetime.datetime.now())[11:13] > '21':
        image = 'background_night.jpg'
    elif str(datetime.datetime.now())[11:13] < '12':
        image = 'background_morning.jpg'
    elif str(datetime.datetime.now())[11:13] > '17':
        image = 'background_evening.jpg'
    else:
        image = 'background_classic.jpg'
    image = load_image(image)
    rect = image.get_rect()
    rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    screen.blit(image, rect)
    # клетчатое поле
    board = Board(SCREEN_WIDTH // 75, SCREEN_HEIGHT // 75)
    board.set_view(0, 0, 75)
    board.render(screen)
    # стоп
    font1 = pygame.font.Font(None, 80)
    img_stop = font1.render('| |', True, BLACK)
    stop = Button(14, 9, img_stop, 1)
    if stop.draw(screen):
        titles = True
        game = False

    pygame.display.flip()


# конец
def end():
    global titles
    global running
    screen.fill(PURPLE)

    font = pygame.font.Font(None, 120)
    s1 = font.render('Конец', True, WHITE)
    screen.blit(s1, (310, 150))

    font1 = pygame.font.Font(None, 80)
    image1 = font1.render('Вернуться в начало', True, YELLOW)
    image2 = font1.render('Выйти', True, YELLOW)
    restart_button = Button(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT // 2 + 115, image1, 1)
    exit_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, image2, 1)

    if restart_button.draw(screen):
        titles = False
    if exit_button.draw(screen):
        running = False


if __name__ == '__main__':
    pygame.init()
    running = True
    clock.tick(FPS)
    while running:
        if not game:
            if titles:
                end()
            else:
                intro()
        else:
            play()
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                running = False
            # keyboard presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_q:
                    grenade = True
                if event.key == pygame.K_w:
                    pass
                if event.key == pygame.K_ESCAPE:
                    running = False

            # keyboard button released
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_q:
                    grenade = False
                    grenade_thrown = False

        pygame.display.update()

    pygame.quit()
