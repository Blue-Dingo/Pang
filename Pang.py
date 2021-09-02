# making exe file
# pyinstaller -w -F --add-data '.\images\*.png;.\images' --add-data '*.ttf;.' .\Pang.py

#####################################################################################
# 게임개발 기본 templete
import os
import pygame
import math

# 리소스 복사를 위한 간접 path 사용


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# 필수초기화
pygame.init()

# 화면크기
screen_w = 640
screen_h = 480
screen = pygame.display.set_mode((screen_w, screen_h))

# 타이틀
pygame.display.set_caption("My Pang")

# FPS
clock = pygame.time.Clock()

#####################################################################################
# images load

current_path = resource_path(os.path.dirname(__file__))  # 현재 파일위치 반환
image_path = os.path.join(current_path, "images")

# 배경
background = pygame.image.load(os.path.join(image_path, "background.png"))

# 스테이지
stage = pygame.image.load(os.path.join(image_path, "stage.png"))
stage_h = stage.get_rect().size[1]

# 캐릭터
character = pygame.image.load(os.path.join(image_path, "character.png"))
character_w = character.get_rect().size[0]
character_h = character.get_rect().size[1]

# 무기
weapon = pygame.image.load(os.path.join(image_path, "weapon.png"))
weapon_w = weapon.get_rect().size[0]

# Ball
ball_images = []
ball_images.append(pygame.image.load(os.path.join(image_path, "ballon1.png")))
ball_images.append(pygame.image.load(os.path.join(image_path, "ballon2.png")))
ball_images.append(pygame.image.load(os.path.join(image_path, "ballon3.png")))
ball_images.append(pygame.image.load(os.path.join(image_path, "ballon4.png")))
ball_sizes = [image.get_rect().size[0] for image in ball_images]


#####################################################################################
# 설정초기화

# 캐릭터
character_x = screen_w/2 - character_w/2
character_y = screen_h - character_h - stage_h
character_speed = 0.3
character_to_x = 0  # 캐릭터 이동방향: -1 = 왼쪽, 1 = 오른쪽

# 무기
weapons = []  # 다중발사를 위한 리스트
weapon_speed = 0.5

# Ball
# 제일 큰공 (0,0)위치에서 오른쪽/아래로 자유낙하
balls = [{"id": 0, "x": 0, "y": 0, "to_x": 1, "to_y": 1, "v": 0}]
bounding_h = [int((screen_h-stage_h)*h)
              for h in [0.8, 0.7, 0.5, 0.3]]  # 튀기는 높이 지정
ball_speed = 0.1  # x축 속도
gravity = 0.001  # y축 중력 가속도 (화면 아래방향)

# 타이머 & 메시지
game_font = pygame.font.Font(os.path.join(
    current_path, "freesansbold.ttf"), 40)  # 폰트,크기
game_result = ["Game Over", "Time Over", "Mission Complete"]
result_msg = ""
start_ticks = pygame.time.get_ticks()
total_time = 30


#####################################################################################
# 이벤트 루프
running = True
while running:

    # fps 설정 , dt = 직전 업데이트 후 경과시간
    dt = clock.tick(60)

    # 이벤트 처리 (키보드, 마우스 등)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                character_to_x -= character_speed
            elif event.key == pygame.K_RIGHT:
                character_to_x += character_speed
            elif event.key == pygame.K_SPACE:
                weapon_x = character_x + character_w/2-weapon_w/2
                weapon_y = character_y
                weapons.append([weapon_x, weapon_y])

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                character_to_x = 0

    # 캐릭터 위치 & 경계
    character_x += character_to_x * dt
    if character_x < 0:
        character_x = 0
    elif character_x > screen_w-character_w:
        character_x = screen_w-character_w

    # 무기 위치
    weapons = [[w[0], w[1]-weapon_speed*dt] for w in weapons]
    # 무기 천정 닫으면 없애기
    weapons = [[w[0], w[1]] for w in weapons if w[1] > 0]

    # 볼 위치
    for ball in balls:
        x = ball["x"] + ball_speed * ball["to_x"] * dt
        y = ball["y"] + ball["v"]*dt + (0.5 * gravity * dt**2)
        v = ball["v"] + gravity * dt
        id = ball["id"]

        if ball["to_y"] > 0:  # falling
            if y >= screen_h - stage_h-ball_sizes[id]:
                y = screen_h - stage_h-ball_sizes[id]
                v = - math.sqrt(2*gravity*bounding_h[id])  # 화면 위쪽 방향
                ball["to_y"] = -1
        else:  # bounding
            if v >= 0:
                v = 0
                ball["to_y"] = 1

        if ball["to_x"] > 0:
            if x >= screen_w - ball_sizes[id]:
                x = screen_w - ball_sizes[id]
                ball["to_x"] = -1
        else:
            if x <= 0:
                x = 0
                ball["to_x"] = 1

        ball["x"] = x
        ball["y"] = y
        ball["v"] = v

    # 충돌처리
    rect_c = character.get_rect()
    rect_c.top = character_y
    rect_c.left = character_x

    for ball in balls:
        id = ball["id"]
        rect_b = ball_images[id].get_rect()
        rect_b.top = ball["y"]
        rect_b.left = ball["x"]
        if rect_b.colliderect(rect_c):  # 캐릭터 충돌
            result_msg = game_result[0]
            running = False
            break

        for w in weapons:
            rect_w = weapon.get_rect()
            rect_w.top = w[1]
            rect_w.left = w[0]
            if rect_w.colliderect(rect_b):  # 공 무기 충돌
                if id < 3:
                    x0 = ball["x"]
                    y0 = ball["y"]
                    size0 = ball_sizes[id]
                    size = ball_sizes[id+1]

                    balls.append({
                        "id": id+1,
                        "x": x0+size0/2-size/2,
                        "y": y0+size0/2+size/2,
                        "to_x": -1,
                        "to_y": -1,
                        "v": -0.3})
                    balls.append({
                        "id": id+1,
                        "x": x0+size0/2-size/2,
                        "y": y0+size0/2+size/2,
                        "to_x": 1,
                        "to_y": -1,
                        "v": -0.3})

                weapons.remove(w)
                balls.remove(ball)

    # 공 전부 제거
    if len(balls) == 0:
        result_msg = game_result[2]
        running = False
        break

    # 그리기
    screen.blit(background, (0, 0))
    for weapon_x, weapon_y in weapons:
        screen.blit(weapon, (weapon_x, weapon_y))
    screen.blit(stage, (0, screen_h-stage_h))
    screen.blit(character, (character_x, character_y))
    for ball in balls:
        x = ball["x"]
        y = ball["y"]
        screen.blit(ball_images[ball["id"]], (x, y))

     # timer
    elapsed_time = (pygame.time.get_ticks()-start_ticks)/1000  # ms
    timer = game_font.render(
        "Time: " + str(int(total_time - elapsed_time)), True, (255, 255, 255))
    screen.blit(timer, (10, 10))

    if total_time - elapsed_time <= 0:
        result_msg = game_result[1]
        running = False

    pygame.display.update()


# result
result = game_font.render(result_msg, True, (255, 255, 0))
result_rect = result.get_rect(center=(screen_w/2, screen_h/2))
screen.blit(result, result_rect)
pygame.display.update()

pygame.time.delay(2000)
pygame.quit()
