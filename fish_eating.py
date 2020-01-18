import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30  # кадры в секунду для обновления экрана
WINWIDTH = 640  # ширина окна программы, в пикселях
WINHEIGHT = 480  # высота в пикселях
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CAMERASLACK = 90  # как далеко от центра движется рыба, прежде чем переместить камеру
MOVERATE = 7  # как быстро движется игрок
BOUNCERATE = 6  # как быстро игрок отскакивает (большой медленнее)
BOUNCEHEIGHT = 30  # как высоко подпрыгивает игрок
STARTSIZE = 25 #стартовый размер игрока
WINSIZE = 300  # насколько большим должен быть игрок, чтобы выиграть
INVULNTIME = 2  # как долго игрок остается неуязвимым после удара в считанные секунды
GAMEOVERTIME = 4  # как долго текст" ВЫ СТАЛИ ОБЕДОМ "
MAXHEALTH = 3  # количество здоровья с которым игрок начинает

NUMGRASS = 80  # количество объектов акул
NUMFISH = 30  # количество рыб
SQUIRRELMINSPEED = 3  # самая медленная скорость рыб
SQUIRRELMAXSPEED = 7  # самая быстрая скорость рыб
DIRCHANGEFREQ = 2  # шанс изменения направления других рыб в каждом кадре
LEFT = 'left'
RIGHT = 'right'
bg = pygame.image.load('tmb_17924_7695.jpg')


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('box.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('РЫБА-МАТРЁШКА')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_SQUIR_IMG = pygame.image.load('28_581759.png')
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    GRASSIMAGES = []
    GRASSIMAGES.append(pygame.image.load('shark_PNG18825.png'))

    while True:
        run_game()


def run_game():
    # Настройка переменных для начала новой игры
    invulnerable_mode = False  # если игрок неуязвим
    invulnerable_start_time = 0  # время, когда игрок становился неуязвимым
    game_over_mode = False  # если игрок проиграл
    game_over_start_time = 0  # время, которое игрок потерял
    win_mode = False  # если игрок выиграл

    # создание поверхностей для хранения игрового текста
    game_over_surf = BASICFONT.render('ВЫ СТАЛИ ОБЕДОМ', True, RED)
    game_over_rect = game_over_surf.get_rect()
    game_over_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf = BASICFONT.render('ВЫ САМАЯ ЖИРНАЯ РЫБА ЗЕМЛИ', True, RED)
    win_rect = win_surf.get_rect()
    win_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf2 = BASICFONT.render('НАЖМИ "r" ЧТОБЫ ПЕРЕЗАПУСТИТЬ', True, (219, 238, 0))
    win_rect2 = win_surf2.get_rect()
    win_rect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camera_x и camera_y - это верхний левый угол, где находится вид камеры
    camera_x = 0
    camera_y = 0


    shark_objs = []  # хранит все объекты акул в игре
    fish_objs = []  # хранит все неигровые объекты рыб
    # сохраняет объект игрока:
    player_obj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce': 0,
                 'health': MAXHEALTH}

    move_left = False
    move_right = False
    move_up = False
    move_down = False

    # начнинает с некоторого изображения акул на экране
    for i in range(10):
        shark_objs.append(make_new_grass(camera_x, camera_y))
        shark_objs[i]['x'] = random.randint(0, WINWIDTH)
        shark_objs[i]['y'] = random.randint(0, WINHEIGHT)

    while True:  # основной игровой цикл
        # Проверьте, стоит ли нам отключать неуязвимость
        if invulnerable_mode and time.time() - invulnerable_start_time > INVULNTIME:
            invulnerable_mode = False

        # переместите всех рыб
        for sObj in fish_objs:
            # переместите рыбу и приспособьтесь к их отскоку
            sObj['x'] += sObj['movex']
            sObj['y'] += sObj['movey']
            sObj['bounce'] += 1
            if sObj['bounce'] > sObj['bouncerate']:
                sObj['bounce'] = 0  # сброс количества отказов

            # случайный шанс, что они меняют направление
            if random.randint(0, 99) < DIRCHANGEFREQ:
                sObj['movex'] = get_random_velocity()
                sObj['movey'] = get_random_velocity()
                if sObj['movex'] > 0:  # лица справа
                    sObj['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sObj['width'], sObj['height']))
                else:  # лица слева
                    sObj['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sObj['width'], sObj['height']))

        # пройдите через все объекты и посмотрите, нужно ли их удалять.
        for i in range(len(shark_objs) - 1, -1, -1):
            if is_outside_active_area(camera_x, camera_y, shark_objs[i]):
                del shark_objs[i]
        for i in range(len(fish_objs) - 1, -1, -1):
            if is_outside_active_area(camera_x, camera_y, fish_objs[i]):
                del fish_objs[i]

        # добавьте больше травы и белок, если у нас их недостаточно.
        while len(shark_objs) < NUMGRASS:
            shark_objs.append(make_new_grass(camera_x, camera_y))
        while len(fish_objs) < NUMFISH:
            fish_objs.append(make_new_squirrel(camera_x, camera_y))

        # отрегулируйте camera_x и camera_y, если за пределами "CAMERASLACK"
        player_centerx = player_obj['x'] + int(player_obj['size'] / 2)
        playerCentery = player_obj['y'] + int(player_obj['size'] / 2)
        if (camera_x + HALF_WINWIDTH) - player_centerx > CAMERASLACK:
            camera_x = player_centerx + CAMERASLACK - HALF_WINWIDTH
        elif player_centerx - (camera_x + HALF_WINWIDTH) > CAMERASLACK:
            camera_x = player_centerx - CAMERASLACK - HALF_WINWIDTH
        if (camera_y + HALF_WINHEIGHT) - playerCentery > CAMERASLACK:
            camera_y = playerCentery + CAMERASLACK - HALF_WINHEIGHT
        elif playerCentery - (camera_y + HALF_WINHEIGHT) > CAMERASLACK:
            camera_y = playerCentery - CAMERASLACK - HALF_WINHEIGHT

        # нарисуйте морской фон
        DISPLAYSURF.blit(bg, (0, 0))
        # нарисуйте все объекты акул на экране
        for gObj in shark_objs:
            gRect = pygame.Rect((gObj['x'] - camera_x,
                                 gObj['y'] - camera_y,
                                 gObj['width'],
                                 gObj['height']))
            DISPLAYSURF.blit(GRASSIMAGES[gObj['grassImage']], gRect)

        # нарисуй других рыб
        for sObj in fish_objs:
            sObj['rect'] = pygame.Rect((sObj['x'] - camera_x,
                                        sObj['y'] - camera_y - get_bounce_amount(sObj['bounce'], sObj['bouncerate'],
                                                                                 sObj['bounceheight']),
                                        sObj['width'],
                                        sObj['height']))
            DISPLAYSURF.blit(sObj['surface'], sObj['rect'])

        # нарисуй других рыб
        flashIsOn = round(time.time(), 1) * 10 % 2 == 1
        if not game_over_mode and not (invulnerable_mode and flashIsOn):
            player_obj['rect'] = pygame.Rect((player_obj['x'] - camera_x,
                                              player_obj['y'] - camera_y - get_bounce_amount(player_obj['bounce'], BOUNCERATE,
                                                                                             BOUNCEHEIGHT),
                                              player_obj['size'],
                                              player_obj['size']))
            DISPLAYSURF.blit(player_obj['surface'], player_obj['rect'])

        # нарисуйте счетчик здоровья
        drawHealthMeter(player_obj['health'])

        for event in pygame.event.get():  # цикл обработки событий
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    move_down = False
                    move_up = True
                elif event.key in (K_DOWN, K_s):
                    move_up = False
                    move_down = True
                elif event.key in (K_LEFT, K_a):
                    move_right = False
                    move_left = True
                    if player_obj['facing'] != LEFT:  # изменение образа игрока
                        player_obj['surface'] = pygame.transform.scale(L_SQUIR_IMG,
                                                                      (player_obj['size'], player_obj['size']))
                    player_obj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    move_left = False
                    move_right = True
                    if player_obj['facing'] != RIGHT:  # изменение образа игрока
                        player_obj['surface'] = pygame.transform.scale(R_SQUIR_IMG,
                                                                      (player_obj['size'], player_obj['size']))
                    player_obj['facing'] = RIGHT
                elif win_mode and event.key == K_r:
                    return

            elif event.type == KEYUP:
                # перестань двигать белку игрока
                if event.key in (K_LEFT, K_a):
                    move_left = False
                elif event.key in (K_RIGHT, K_d):
                    move_right = False
                elif event.key in (K_UP, K_w):
                    move_up = False
                elif event.key in (K_DOWN, K_s):
                    move_down = False

                elif event.key == K_ESCAPE:
                    terminate()

        if not game_over_mode:
            # фактически переместите игрока
            if move_left:
                player_obj['x'] -= MOVERATE
            if move_right:
                player_obj['x'] += MOVERATE
            if move_up:
                player_obj['y'] -= MOVERATE
            if move_down:
                player_obj['y'] += MOVERATE

            if (move_left or move_right or move_up or move_down) or player_obj['bounce'] != 0:
                player_obj['bounce'] += 1

            if player_obj['bounce'] > BOUNCERATE:
                player_obj['bounce'] = 0  # сброс количества отказов

            # проверьте, не столкнулся ли игрок с какими-нибудь белками
            for i in range(len(fish_objs) - 1, -1, -1):
                sqObj = fish_objs[i]
                if 'rect' in sqObj and player_obj['rect'].colliderect(sqObj['rect']):
                    # произошло столкновение игрока и белки

                    if sqObj['width'] * sqObj['height'] <= player_obj['size'] ** 2:
                        # игрок больше и ест белку
                        player_obj['size'] += int((sqObj['width'] * sqObj['height']) ** 0.2) + 1
                        del fish_objs[i]

                        if player_obj['facing'] == LEFT:
                            player_obj['surface'] = pygame.transform.scale(L_SQUIR_IMG,
                                                                          (player_obj['size'], player_obj['size']))
                        if player_obj['facing'] == RIGHT:
                            player_obj['surface'] = pygame.transform.scale(R_SQUIR_IMG,
                                                                          (player_obj['size'], player_obj['size']))

                        if player_obj['size'] > WINSIZE:
                            win_mode = True  # включить " режим выигрыша"

                    elif not invulnerable_mode:
                        # игрок меньше и получает урона
                        invulnerable_mode = True
                        invulnerable_start_time = time.time()
                        player_obj['health'] -= 1
                        if player_obj['health'] == 0:
                            game_over_mode = True  # включить режим "game over"
                            game_over_start_time = time.time()
        else:
            # игра закончилась, показывать "Игра окончена" текст
            DISPLAYSURF.blit(game_over_surf, game_over_rect)
            if time.time() - game_over_start_time > GAMEOVERTIME:
                return  # end the current game

        # проверьте, выиграл ли игрок.
        if win_mode:
            DISPLAYSURF.blit(win_surf, win_rect)
            DISPLAYSURF.blit(win_surf2, win_rect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawHealthMeter(currentHealth):
    for i in range(currentHealth):  # нарисуйте красные полосы здоровья
        pygame.draw.rect(DISPLAYSURF, RED, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH):  # нарисуйте белые контуры
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)


def terminate():
    pygame.quit()
    sys.exit()


def get_bounce_amount(currentBounce, bounceRate, bounceHeight):
    # Возвращает количество пикселей для смещения на основе отскока.
    # Возвращает количество пикселей для смещения на основе отскока.
    # Большая высота отскока означает более высокий отскок.
    # текущий отказ всегда будет меньше, чем показатель отказов
    return int(math.sin((math.pi / float(bounceRate)) * currentBounce) * bounceHeight) // 4


def get_random_velocity():
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed


def getRandomOffCameraPos(camerax, cameray, objWidth, objHeight):
    # # создайте остальную часть вида камеры
    cameraRect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # создать объект прямоугольник со случайными координатами и использовать colliderect()
        # чтобы убедиться, что правый край не находится в поле зрения камеры.
        objRect = pygame.Rect(x, y, objWidth, objHeight)
        if not objRect.colliderect(cameraRect):
            return x, y


def make_new_squirrel(camerax, cameray):
    sq = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = getRandomOffCameraPos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = get_random_velocity()
    sq['movey'] = get_random_velocity()
    if sq['movex'] < 0:  # squirrel is facing left
        sq['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sq['width'], sq['height']))
    else:  # squirrel is facing right
        sq['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq


def make_new_grass(camerax, cameray):
    gr = {}
    gr['grassImage'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = getRandomOffCameraPos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect((gr['x'], gr['y'], gr['width'], gr['height']))
    return gr


def is_outside_active_area(camerax, cameray, obj):
    # Return False, если camerax и cameray больше, чем
    # половина длины окна за краем окна.
    boundsLeftEdge = camerax - WINWIDTH
    boundsTopEdge = cameray - WINHEIGHT
    boundsRect = pygame.Rect(boundsLeftEdge, boundsTopEdge, WINWIDTH * 3, WINHEIGHT * 3)
    objRect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not boundsRect.colliderect(objRect)


if __name__ == '__main__':
    main()

"""

    Ключи, используемые всеми тремя структурами данных:
    'x' - координата левого края объекта в игровом мире (не пиксельная координата на экране)
    'y' - координата верхнего края объекта в игровом мире (не пиксельная координата на экране)
    "rect" - игра в пятерки.Rect объект, представляющий, где на экране находится объект.
Ключи структуры данных плеера:
    "surface" - это игра в пятнашки.Поверхностный объект, который хранит изображение белки, которая будет нарисована на экране.
    "facing" - устанавливается либо влево, либо вправо, в зависимости от того, в каком направлении находится игрок.
    "size" - ширина и высота плеера в пикселях. (Ширина и высота всегда одинаковы.)
    "bounce" - обозначает, в какой момент отскока находится игрок. 0 означает стояние (без отскока), вплоть до отскока (завершение отскока)
    "health" - целое число, показывающее, сколько еще раз игрок может быть поражен более крупной рыбой перед смертью.
Ключи структуры данных вражеской белки:
    "surface" - это игра в пятнашки.Поверхностный объект, который хранит изображение рыбы, которая будет нарисована на экране.
    'movex' - сколько пикселей на кадр рыба перемещает по горизонтали. Отрицательное целое число движется влево, положительное-вправо.
    'movey' - сколько пикселей на кадр рыба перемещает по вертикали. Отрицательное целое число движется вверх, положительное-вниз.
    'width' - ширина изображения рыбы, в пикселях
    'height' - высота изображения рыбы, в пикселях
    "bounce" - обозначает, в какой момент отскока находится игрок. 0 означает стояние (без отскока), вплоть до отскока (завершение отскока)
    "bouncerate" - как быстро отскакивает рыба. Меньшее число означает более быстрый отскок.
    'bounceheight' - как высоко (в пикселях) подпрыгивает рыба
Ключи структуры данных Grass:
    'grassImage' - целое число, которое относится к индексу pygame.Поверхностный объект в GRASSIMAGES используемый для этого объекта травы
"""
