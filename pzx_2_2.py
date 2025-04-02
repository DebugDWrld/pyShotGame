import os, time, subprocess, sys, math, pygame

# 检测pip安装
try:
    import pip
except ImportError:
    print("未检测到pip，正在安装...")
    subprocess.check_call(['python', '-m', 'ensurepip', '--upgrade'])
    print("pip 安装成功！")
    sys.exit(0)
else:
    print("pip已安装，版本为：", pip.__version__)

# 检测Pygame安装
try:
    import pygame
except ImportError:
    print("未检测到Pygame，正在安装...")
    subprocess.check_call(['pip', 'install', 'pygame'])
    print("Pygame 安装成功！")
else:
    print("Pygame 已安装，版本为:", pygame.__version__)

# 初始化Pygame
pygame.init()

# 获取当前脚本文件的路径
current_path = os.path.dirname(os.path.abspath(__file__))
print(current_path)

# 获取显示屏信息
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# 创建游戏窗口
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("小游戏")

# 定义文本颜色和字体
red = (255, 0, 0)
font = pygame.font.Font(None, 64)

# 加载背景图片
background_image_path = os.path.join(current_path, "background.png")
background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))  # 缩放到窗口大小

# 加载玩家贴图
player_image_path = os.path.join(current_path, "player.png")
player_image_original = pygame.image.load(player_image_path)
player_image_original = pygame.transform.scale(player_image_original, (64, 64))
player_image = player_image_original

# 加载子弹贴图
bullet_image_path = os.path.join(current_path, "bullet.png")
bullet_image_original = pygame.image.load(bullet_image_path)
bullet_image_original = pygame.transform.scale(bullet_image_original, (32, 32))

# 玩家参数
player_x = 400.0
player_y = 300.0
move_speed = 1.0
player_direction = [0.0, 0.0]
last_direction = None
player_angle = 0.0

# 子弹参数
bullets = []
bullet_speed = 3.0
BULLET_LIFETIME = 3000  # 3秒
SHOOT_COOLDOWN = 200  # 0.2秒
last_shot_time = 0

# 游戏主循环
running = True
while running:
    #win.fill((0, 0, 0))
    win.blit(background_image, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 玩家移动（只保留全向移动逻辑）
    keys = pygame.key.get_pressed()
    move_x = 0.0
    move_y = 0.0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        move_x -= 1.0
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        move_x += 1.0
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        move_y -= 1.0
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_y += 1.0
    if keys[pygame.K_ESCAPE]:
        running = False

    if move_x != 0 or move_y != 0:
        length = math.sqrt(move_x ** 2 + move_y ** 2)
        player_direction = [move_x / length, move_y / length]
        last_direction = player_direction[:]  # 更新最后方向
        player_x += player_direction[0] * move_speed
        player_y += player_direction[1] * move_speed
        player_angle = math.degrees(math.atan2(-player_direction[1], player_direction[0]))
        player_image = pygame.transform.rotate(player_image_original, player_angle)
    else:
        player_direction = [0.0, 0.0]
        if last_direction is not None:
            player_angle = math.degrees(math.atan2(-last_direction[1], last_direction[0]))
            player_image = pygame.transform.rotate(player_image_original, player_angle)

    # 射击逻辑
    current_time = pygame.time.get_ticks()
    can_shoot = current_time - last_shot_time >= SHOOT_COOLDOWN

    # 按 K 键发射子弹
    if keys[pygame.K_k] and can_shoot:
        bullet = {
            "x": player_x + 16,
            "y": player_y + 16,
            "velocity": [0.0, 0.0],
            "spawn_time": current_time,
            "visible": True,
            "angle": 0.0
        }
        if player_direction != [0.0, 0.0]:  # 玩家正在移动
            bullet["velocity"] = [player_direction[0] * bullet_speed, player_direction[1] * bullet_speed]
            bullet["angle"] = math.degrees(math.atan2(-player_direction[1], player_direction[0]))
        elif last_direction is not None:  # 使用最后方向
            bullet["velocity"] = [last_direction[0] * bullet_speed, last_direction[1] * bullet_speed]
            bullet["angle"] = math.degrees(math.atan2(-last_direction[1], last_direction[0]))
        else:  # 初始默认向右
            bullet["velocity"] = [bullet_speed, 0.0]
            bullet["angle"] = 0.0
            last_direction = [1.0, 0.0]
        bullets.append(bullet)
        last_shot_time = current_time

    # 按 L 键发射子弹（速度翻倍）
    if keys[pygame.K_l] and can_shoot:
        bullet = {
            "x": player_x + 16,
            "y": player_y + 16,
            "velocity": [0.0, 0.0],
            "spawn_time": current_time,
            "visible": True,
            "angle": 0.0
        }
        if player_direction != [0.0, 0.0]:  # 玩家正在移动
            bullet["velocity"] = [player_direction[0] * bullet_speed * 2, player_direction[1] * bullet_speed * 2]
            bullet["angle"] = math.degrees(math.atan2(-player_direction[1], player_direction[0]))
        elif last_direction is not None:  # 使用最后方向
            bullet["velocity"] = [last_direction[0] * bullet_speed * 2, last_direction[1] * bullet_speed * 2]
            bullet["angle"] = math.degrees(math.atan2(-last_direction[1], last_direction[0]))
        else:  # 初始默认向右
            bullet["velocity"] = [bullet_speed * 2, 0.0]
            bullet["angle"] = 0.0
            last_direction = [1.0, 0.0]
        bullets.append(bullet)
        last_shot_time = current_time

    # 更新所有子弹
    for bullet in bullets[:]:
        bullet["x"] += bullet["velocity"][0]
        bullet["y"] += bullet["velocity"][1]
        if (bullet["x"] < 0 or bullet["x"] > screen_width or 
            bullet["y"] < 0 or bullet["y"] > screen_height):
            bullet["visible"] = False
        if current_time - bullet["spawn_time"] > BULLET_LIFETIME:
            bullet["visible"] = False
        if not bullet["visible"]:
            bullets.remove(bullet)

    # 绘制玩家和子弹贴图
    player_rect = player_image.get_rect(center=(player_x + 32, player_y + 32))
    win.blit(player_image, player_rect)
    for bullet in bullets:
        if bullet["visible"]:
            rotated_bullet = pygame.transform.rotate(bullet_image_original, bullet["angle"])
            bullet_rect = rotated_bullet.get_rect(center=(bullet["x"] + 16, bullet["y"] + 16))
            win.blit(rotated_bullet, bullet_rect)

    # 更新显示
    pygame.display.update()

    # 玩家消失检测
    if player_x < 0 or player_x > screen_width or player_y < 0 or player_y > screen_height:
        win.fill((255, 255, 255))
        text_surface = font.render("GAME OVER", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        win.blit(text_surface, text_rect)
        pygame.display.update()
        time.sleep(3)
        running = False

    # 碰撞检测（示例）
    player_rect = pygame.Rect(player_x, player_y, 64, 64)
    for bullet in bullets:
        bullet_rect = pygame.Rect(bullet["x"], bullet["y"], 32, 32)
        if player_rect.colliderect(bullet_rect) and bullet["visible"]:
            pass  # 可在此添加碰撞逻辑

# 退出游戏
pygame.quit()