import os
import pygame

# Открытие текстового файла в режиме для чтения
f = open("data/best_s", 'r')
try:
    best_score = int(f.readline())
except ValueError:
    best_score = 0
f.close()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Инициализация PeGame
pygame.init()
# Размеры окна
size = width, height = 933, 560
# Screen
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Judy")  # Шапка
pygame.display.set_icon(pygame.image.load("data/judy.png"))
font = pygame.font.SysFont("Songer SemiExpanded", 30, bold=True)
true_over = False

# Музыка
music = pygame.mixer.Sound("sound/music.wav")
music.play()

# Группы
all_sprites = pygame.sprite.Group()
Judy_group = pygame.sprite.Group()
Blocks_group = pygame.sprite.Group()


# Класс камеры
class Camera:
    # Зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0

    # Сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx

    # Позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)


# Gero
class Judy(pygame.sprite.Sprite):
    score = 0

    def __init__(self, x, y):
        super().__init__(Judy_group, all_sprites)
        self.image = load_image("judy.png", -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dx = 0  # Изменение горизонтального положения
        self.dy = 0  # Изменение вертикального положения
        self.ddy = 0.35  # Скорость изменения вертикального положения
        self.rost = 1
        self.padenie = True
        self.pryzhok = False
        self.left = False  # Идет ли персонаж вправо
        self.right = False  # Идёт ли персонаж влево
        self.right_side = True  # Персонаж смотрит вправо?
        self.sel = False
        self.stoit = False
        self.speed = 5  # Скорость
        self.jump_speed = 10.5
        self.neuz = 0
        self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)
        self.slovar_of_rost = {1: 'judy.png',
                               2: 'judy_big.png', 3: 'judy_sweet.png'}


    def set_rost(self, r):
        x = self.rect.x
        y = self.rect.y
        k = 40 if self.rost == 1 else 0
        self.rost = r
        self.image = load_image(self.slovar_of_rost[self.rost], -1)
        if self.right_side:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - k
        self.mask = pygame.mask.from_surface(self.image)

    def collision(self, dx, dy, blocks):
        for b in pygame.sprite.spritecollide(self, blocks, False):
            if b.description == '-':
                self.kill()
            if dx > 0:
                self.rect.right = b.rect.left
            if dx < 0:
                self.rect.left = b.rect.right
            if dy > 0:
                self.rect.bottom = b.rect.top
                self.stoit = True
                self.padenie = False
                self.dy = 0
            if dy < 0:
                if b.description == '?':
                    b.collision()
                if b.description == 'bl-r':
                    b.breaking()
                self.rect.top = b.rect.bottom
                self.dy = 0

    # Обновление героя
    def update(self, *args):
        if self.neuz != 0:
            self.neuz -= 10
        # Если нажали клавишу
        if args[0].type == pygame.KEYDOWN:
            if args[0].key == 119 or args[0].key == 273 or args[0].key == 32:
                # 'w'
                self.pryzhok = True
            elif args[0].key == 115 or args[0].key == 274:
                # 's'
                self.sel = True
            elif args[0].key == 100 or args[0].key == 275:
                # 'd'
                self.right = True
            elif args[0].key == 97 or args[0].key == 276:
                # 'a'
                self.left = True
        # Если клавишу отпустили
        elif args[0].type == pygame.KEYUP:
            if args[0].key == 119 or args[0].key == 273 or args[0].key == 32:
                # 'w'
                self.pryzhok = False
            elif args[0].key == 115 or args[0].key == 274:
                # 's'
                self.sel = False
            elif args[0].key == 100 or args[0].key == 275:
                # 'd'
                self.right = False
            elif args[0].key == 97 or args[0].key == 276:
                # 'a'
                self.left = False

    # Функции движения
    def horizontal_moving(self):
        if self.right and self.left:
            self.dx = 0
        elif self.right:
            self.dx = self.speed
            if not self.right_side:
                self.image = pygame.transform.flip(self.image, True, False)
                self.right_side = True
        elif self.left:
            self.dx = -self.speed
            if self.right_side:
                self.image = pygame.transform.flip(self.image, True, False)
                self.right_side = False
        else:
            self.dx = 0
        self.rect.x += self.dx

    def vertical_moving(self):
        if self.pryzhok and self.stoit:
            # 'w'
            self.dy = -self.jump_speed
        if self.padenie:
            if self.rect.y + self.speed < height:
                self.dy += self.ddy
            else:
                self.kill()
        self.rect.y += self.dy

    def Moving(self):
        self.horizontal_moving()
        self.collision(self.dx, 0, Blocks_group)
        self.vertical_moving()
        self.padenie = True
        self.stoit = False
        self.collision(0, self.dy, Blocks_group)
        if self.sel:
            # 's'
            pass


list_of_blocks = {'pol': "ground.png", 'bl-r': "block_razb.png",
                  "?": 'zagadka.png', '-?-': 'zagadka_bez_zagadki.png',
                  'block': 'dop_block.png', '-': 'death.png'}


# Blocks
class Blocks(pygame.sprite.Sprite):
    def __init__(self, x, y, image_name="pol"):
        super().__init__(Blocks_group, all_sprites)
        self.image = load_image(list_of_blocks[image_name])
        self.description = image_name
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        pass


class Death_blocks(Blocks):
    def __init__(self, x, y, image_name='-'):
        super().__init__(x, y, image_name)

    def update(self, *args):
        pass


class Block_razb(Blocks):
    def __init__(self, x, y, lollip=False):
        super().__init__(x, y, image_name='bl-r')
        self.lollip = lollip

    def update(self, *args):
        pass

    def breaking(self):
        if self.lollip:
            if self.lollipops > 1:
                self.lollipops -= 1
                Lollipop(self.rect.x, self.rect.y - 40)
            elif self.lollipops == 1:
                self.lollipops -= 1
                Lollipop(self.rect.x, self.rect.y - 40)
                self.image = load_image(list_of_blocks['-?-'])
        else:
            if Gero.rost != 1:
                self.kill()


class Block_zagadka(Blocks):
    def __init__(self, x, y, lollip=True):
        super().__init__(x, y, image_name='?')
        self.lollip = lollip
        self.lollipops = 1 if lollip else 0
        self.sost = 1

    def update(self, *args):
        pass

    def collision(self):
        if self.sost:
            if self.lollip:
                if self.lollipops == 1:
                    self.lollipops -= 1
                    Lollipop(self.rect.x, self.rect.y - 40)
                    self.sost = 0
                    self.image = load_image(list_of_blocks['-?-'])
            else:
                if Gero.rost == 1:
                    Elixir(self.rect.x, self.rect.y - 40)
                    self.sost = 0
                    self.image = load_image(list_of_blocks['-?-'])
                else:
                    Konfeta(self.rect.x, self.rect.y - 40)
                    self.sost = 0
                    self.image = load_image(list_of_blocks['-?-'])


class Lollipop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image('lollipop.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.k = 0
        self.schetchik = 2
        LollipopEvent = 1
        pygame.time.set_timer(LollipopEvent, 30, 25)

    def update(self, *args):
        if args[0].type == 1:
            self.fly()

    def fly(self):
        self.k += 10
        self.rect.y -= 1
        if self.k == 250:
            self.kill()
            Judy.score = Judy.score + self.schetchik


class Elixir(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image('elixir.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.k = 0

    def update(self, *args):
        if pygame.sprite.spritecollide(self, Judy_group, False):
            if Gero.rost == 1:
                Gero.set_rost(2)
            self.kill()


class Konfeta(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image('konfeta.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.k = 0

    def update(self, *args):
        if pygame.sprite.spritecollide(self, Judy_group, False):
            if Gero.rost == 2:
                Gero.set_rost(3)
            elif Gero.rost == 1:
                Gero.set_rost(2)
            self.kill()


class Game_over(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(Over_group)
        self.image = load_image('Game_over.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

    def update(self, *args):
        pass


class You_win(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(Over_group)
        self.image = load_image('You_win.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

    def update(self, *args):
        pass


class Dom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image('dom.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        global true_over
        if pygame.sprite.spritecollide(self, Judy_group, False):
            true_over = True


# Инициализация героя и блоков
def load_level(filename):
    filename = "data/" + filename
    # Читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # И подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


level = load_level('lvl1_2.txt')

# level = load_level('lvl')
for i in range(len(level)):
    for j in range(len(level[i])):
        if level[i][j] == '.':
            pass
        elif level[i][j] == '#':
            Blocks(j * 40, i * 40)
        elif level[i][j] == '=':
            Block_razb(j * 40, i * 40)
        elif level[i][j] == '$':
            Block_razb(j * 40, i * 40, True)
        elif level[i][j] == 'B':
            Blocks(j * 40, i * 40, 'block')
        elif level[i][j] == 'Z':
            Dom(j * 40, i * 40)
        elif level[i][j] == '?':
            Block_zagadka(j * 40, i * 40)
        elif level[i][j] == 'G':
            Block_zagadka(j * 40, i * 40, False)
        elif level[i][j] == '@':
            Gero = Judy(j * 40, i * 40)
        elif level[i][j] == '-':
            Death_blocks(j * 40, i * 40)

camera = Camera()
clock = pygame.time.Clock()
running = True
screen.fill((114, 208, 237))
# Ожидание закрытия окна
while running and not true_over:
    if not Gero.alive():
        true_over = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            Gero.kill()
        all_sprites.update(event)
    Gero.Moving()
    # Изменяем ракурс камеры
    camera.update(Gero)
    # Обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.fill((114, 208, 237))
    all_sprites.draw(screen)
    score = Judy.score
    f = open("data/best_s", 'w')
    f.write(str(best_score))
    if best_score < score:
        best_score = score
    f.close()
    render_best_score = font.render(f'BEST SCORE: {best_score}', 1, pygame.Color(1, 13, 101))
    render_score = font.render(f'SCORE: {score}', 1, pygame.Color(1, 13, 101))
    screen.blit(render_score, (10, 10))
    screen.blit(render_best_score, (200, 10))
    pygame.display.flip()
    clock.tick(60)
Over_group = pygame.sprite.Group()
Over = Game_over() if not Gero.alive() else You_win()
# Завершение работы:
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    Over.update()
    Over_group.draw(screen)
    pygame.display.flip()
pygame.quit()
