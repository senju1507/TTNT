import pygame
import random
import time
import math
from heapq import heappop, heappush
import os  # Thêm import os để lấy đường dẫn

# Khởi tạo pygame
pygame.init()

# Màu sắc
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
PURPLE = (148, 0, 211)
YELLOW = (255, 255, 0)
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]

# Kích thước màn hình
WIDTH, HEIGHT = 1200, 800
BLOCK_SIZE = 20
INITIAL_SPEED = 5
speed = INITIAL_SPEED

# Đường dẫn đến thư mục chứa file Python (thư mục BÉNANHOM9)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Font chữ
font_style = pygame.font.Font(os.path.join(BASE_DIR, "arial.ttf"), 50)
score_font = pygame.font.Font(os.path.join(BASE_DIR, "arial.ttf"), 60)

# Khởi tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BÉ NA ĐÓI RỒI")
clock = pygame.time.Clock()

# Tải tài nguyên
background_image = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "background.jpg")), (WIDTH, HEIGHT))
pause_background = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "pause_background.jpg")), (WIDTH, HEIGHT))
game_over_background = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "game_over_background_3.jpg")), (WIDTH, HEIGHT))
eat_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "eat_sound.mp3"))
game_over_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "game_over_sound_2.mp3"))
pygame.mixer.music.load(os.path.join(BASE_DIR, "background_music.mp3"))
pygame.mixer.music.play(-1)

# Vẽ nền map
def draw_checkerboard_background():
    screen.fill(BLACK)

# Hiển thị điểm số
def display_score(score):
    value = score_font.render("ĐIỂM: " + str(score), True, (0, 191, 255))
    screen.blit(value, [10, 10])

# Vẽ rắn với hiệu ứng cầu vồng
def draw_snake(block_size, snake_list, invincible=False, rainbow_counter=0):
    if not invincible:
        for i, block in enumerate(snake_list):
            color = (0, 255 - i % 100, 0)
            pygame.draw.rect(screen, color, [block[0] * BLOCK_SIZE, block[1] * BLOCK_SIZE, block_size, block_size])
    else:
        if len(snake_list) == 1:
            color_index = int(rainbow_counter) % len(COLORS)
            color = COLORS[color_index]
            pygame.draw.rect(screen, color, [snake_list[0][0] * BLOCK_SIZE, snake_list[0][1] * BLOCK_SIZE, block_size, block_size])
        else:
            for i, block in enumerate(snake_list):
                color_index = int(rainbow_counter - i * 0.5) % len(COLORS)
                color = COLORS[color_index]
                pygame.draw.rect(screen, color, [block[0] * BLOCK_SIZE, block[1] * BLOCK_SIZE, block_size, block_size])

# Vẽ thức ăn
def draw_food(food_pos, alpha):
    food_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
    pygame.draw.rect(food_surface, (255, 0, 0, alpha), (0, 0, BLOCK_SIZE, BLOCK_SIZE))
    screen.blit(food_surface, (food_pos[0] * BLOCK_SIZE, food_pos[1] * BLOCK_SIZE))

# Hiển thị thông báo
def display_message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3 + y_offset])

# Thuật toán A* tìm đường
def a_star(start, goal, snake_list, obstacles, width, height):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heappop(open_set)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if (0 <= neighbor[0] < width and 0 <= neighbor[1] < height and
                neighbor not in snake_list and neighbor not in obstacles):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))
    return None

# Tạo chướng ngại vật
def create_border_obstacles():
    obstacles = []
    for x in range(WIDTH // BLOCK_SIZE):
        obstacles.append((x, 0))
        obstacles.append((x, HEIGHT // BLOCK_SIZE - 1))
    for y in range(HEIGHT // BLOCK_SIZE):
        obstacles.append((0, y))
        obstacles.append((WIDTH // BLOCK_SIZE - 1, y))
    return obstacles

def create_random_obstacles(count=10):
    obstacles = []
    for _ in range(count):
        while True:
            obstacle = (random.randint(1, WIDTH // BLOCK_SIZE - 2), random.randint(1, HEIGHT // BLOCK_SIZE - 2))
            if obstacle not in obstacles:
                obstacles.append(obstacle)
                break
    return obstacles

def create_moving_obstacles(count, snake_list, food):
    obstacles = []
    for _ in range(count):
        while True:
            pos = (random.randint(1, WIDTH // BLOCK_SIZE - 2), random.randint(1, HEIGHT // BLOCK_SIZE - 2))
            if pos not in obstacles and pos not in snake_list and pos != food:
                obstacles.append([pos, random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])])
                break
    return obstacles

# Cập nhật vị trí chướng ngại vật di động
def update_moving_obstacles(obstacles, snake_list, food):
    for obs in obstacles:
        pos, direction = obs
        new_pos = (pos[0] + direction[0], pos[1] + direction[1])
        if (new_pos[0] <= 0 or new_pos[0] >= WIDTH // BLOCK_SIZE - 1 or
            new_pos[1] <= 0 or new_pos[1] >= HEIGHT // BLOCK_SIZE - 1 or
            new_pos in [o[0] for o in obstacles if o != obs]):
            direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        else:
            obs[0] = new_pos
        obs[1] = direction

# Tạo thức ăn
def create_food(snake_list, obstacles):
    max_attempts = 100
    attempts = 0
    while attempts < max_attempts:
        food = (random.randint(1, WIDTH // BLOCK_SIZE - 2), random.randint(1, HEIGHT // BLOCK_SIZE - 2))
        if food not in snake_list and food not in [obs[0] if isinstance(obs, list) else obs for obs in obstacles]:
            return food
        attempts += 1
    return None

# Menu chọn cấp độ (cho chế độ Free)
def select_level():
    level_menu = True
    while level_menu:
        screen.blit(background_image, (0, 0))
        display_message("Chọn cấp độ", WHITE, -100)
        display_message("1. Dễ", WHITE, -50)
        display_message("2. Trung bình", WHITE, 0)
        display_message("3. Khó", WHITE, 50)
        display_message("4. Asian", WHITE, 100)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: return 5
                elif event.key == pygame.K_2: return 10
                elif event.key == pygame.K_3: return 15
                elif event.key == pygame.K_4: return 35

# Menu chính
def main_menu():
    pygame.mixer.music.play(-1)
    menu = True
    while menu:
        screen.blit(background_image, (0, 0))
        display_message("Bé Na Nhóm 9", WHITE, -100)
        display_message("1. Bé Na Trong Chuồng", WHITE, -50)
        display_message("2. Bé Na Săn Mồi", WHITE, 0)
        display_message("Nhấn Q để Thoát", WHITE, 50)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    pygame.mixer.music.stop()
                    return "walled", INITIAL_SPEED  # Chế độ 1 không chọn cấp độ
                elif event.key == pygame.K_2:
                    pygame.mixer.music.stop()
                    return "free", select_level()  # Chế độ 2 có chọn cấp độ
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

# Hàm chơi game
def game_loop(mode, initial_speed):
    global speed
    speed = initial_speed
    game_over = False
    game_close = False
    paused = False
    sound_played = False

    snake_list = [(WIDTH // BLOCK_SIZE // 2, HEIGHT // BLOCK_SIZE // 2)]
    direction = (0, 1)
    obstacles = create_border_obstacles() if mode == "walled" else create_random_obstacles()
    moving_obstacles = [] if mode == "free" else create_moving_obstacles(3, snake_list, None)
    food = create_food(snake_list, obstacles + moving_obstacles)
    score = 0
    invincible = False
    invincible_start_time = 0
    food_alpha = 255
    path = []
    rainbow_counter = 0
    move_counter = 0

    while not game_over:
        while game_close:
            if not sound_played:
                game_over_sound.play()
                sound_played = True
            screen.blit(game_over_background, (0, 0))
            display_message("Thua rồi! Nhấn C-Chơi lại, Q để Menu chính", WHITE)
            display_score(score)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.mixer.music.play(-1)
                        return
                    if event.key == pygame.K_c:
                        speed = initial_speed
                        sound_played = False
                        game_loop(mode, initial_speed)

        while paused:
            screen.blit(pause_background, (0, 0))
            display_message("Tạm dừng", WHITE, -50)
            display_message("R để tiếp tục, Q để Menu chính", WHITE, 0)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        paused = False
                    if event.key == pygame.K_q:
                        pygame.mixer.music.play(-1)
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if mode == "free":
                    if event.key == pygame.K_LEFT and direction != (1, 0): direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0): direction = (1, 0)
                    elif event.key == pygame.K_UP and direction != (0, 1): direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1): direction = (0, 1)
                if event.key == pygame.K_ESCAPE: paused = not paused

        if not paused:
            if mode == "walled":
                move_counter += 1
                if move_counter % 10 == 0:
                    update_moving_obstacles(moving_obstacles, snake_list, food)
                    path = a_star(snake_list[0], food, snake_list, obstacles + [obs[0] for obs in moving_obstacles],
                                  WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE) or []

            if mode == "walled" and path:
                next_pos = path.pop(0)
                direction = (next_pos[0] - snake_list[0][0], next_pos[1] - snake_list[0][1])
                new_head = next_pos
            else:
                new_head = (snake_list[0][0] + direction[0], snake_list[0][1] + direction[1])

            if mode == "free":
                new_head = (new_head[0] % (WIDTH // BLOCK_SIZE), new_head[1] % (HEIGHT // BLOCK_SIZE))

            if ((mode == "walled" and (new_head in obstacles or new_head in [obs[0] for obs in moving_obstacles] or new_head in snake_list[1:])) or
                (mode == "free" and not invincible and (new_head in obstacles or new_head in snake_list[1:]))):
                game_close = True

            snake_list.insert(0, new_head)

            if new_head == food:
                eat_sound.play()
                food = create_food(snake_list, obstacles + moving_obstacles)
                if food is None:
                    game_close = True
                score += 1
                invincible = mode == "free"
                invincible_start_time = time.time() if invincible else 0
                if mode == "free":
                    obstacles = create_random_obstacles()
                if mode == "walled":
                    new_obstacles = create_moving_obstacles(2, snake_list, food)
                    moving_obstacles.extend(new_obstacles)
                    speed += 0.5
                    print(f"Điểm {score}: Tốc độ {speed}, Chướng ngại vật: {len(moving_obstacles)}")
            else:
                snake_list.pop()

            if mode == "walled":
                path = a_star(snake_list[0], food, snake_list, obstacles + [obs[0] for obs in moving_obstacles],
                              WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE) or []

            rainbow_counter += 0.2
            food_alpha = max(128, 128 + int(127 * math.sin(time.time() * 2.5)))

            draw_checkerboard_background()
            draw_food(food, food_alpha)
            for obstacle in obstacles:
                pygame.draw.rect(screen, YELLOW, [obstacle[0] * BLOCK_SIZE, obstacle[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
            for obs in moving_obstacles:
                pygame.draw.rect(screen, PURPLE, [obs[0][0] * BLOCK_SIZE, obs[0][1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
            draw_snake(BLOCK_SIZE, snake_list, invincible, rainbow_counter)
            display_score(score)
            pygame.display.update()

            if invincible and time.time() - invincible_start_time > 3:
                invincible = False

            clock.tick(speed)

    pygame.quit()
    quit()

# Chạy game
while True:
    mode, initial_speed = main_menu()
    game_loop(mode, initial_speed)