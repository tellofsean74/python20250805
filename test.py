import pygame
import random

# 게임 설정
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 10

# 색상
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0)     # Z
]

# 테트로미노 도형
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],        # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

def rotate(shape):
    return [ [ shape[y][x] for y in range(len(shape)) ] for x in range(len(shape[0])-1, -1, -1) ]

class Tetromino:
    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color

    def rotate(self):
        self.shape = rotate(self.shape)

def create_grid(locked={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in locked:
                grid[y][x] = locked[(x, y)]
    return grid

def valid_space(shape, offset, grid):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                px = off_x + x
                py = off_y + y
                if px < 0 or px >= COLS or py >= ROWS:
                    return False
                if py >= 0 and grid[py][px] != BLACK:
                    return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS-1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLS):
                try:
                    del locked[(x, y)]
                except:
                    continue
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x, y2 = key
                if y2 < y:
                    locked[(x, y2+1)] = locked.pop((x, y2))
    return cleared

def get_shape():
    idx = random.randint(0, len(SHAPES)-1)
    return Tetromino(COLS//2-2, 0, SHAPES[idx], COLORS[idx])

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(surface, grid[y][x], (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
    for x in range(COLS):
        pygame.draw.line(surface, GRAY, (x*CELL_SIZE, 0), (x*CELL_SIZE, HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y*CELL_SIZE), (WIDTH, y*CELL_SIZE))

def draw_window(surface, grid, score):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, (255,255,255))
    surface.blit(label, (10, 10))

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    locked = {}
    grid = create_grid(locked)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    fall_time = 0
    score = 0

    while run:
        grid = create_grid(locked)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        if fall_time/1000 > 0.5:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                        for _ in range(3): current_piece.rotate()

        for y, row in enumerate(current_piece.shape):
            for x, cell in enumerate(row):
                if cell and current_piece.y + y >= 0:
                    grid[current_piece.y + y][current_piece.x + x] = current_piece.color

        if change_piece:
            for y, row in enumerate(current_piece.shape):
                for x, cell in enumerate(row):
                    if cell and current_piece.y + y >= 0:
                        locked[(current_piece.x + x, current_piece.y + y)] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked) * 100
            if not valid_space(current_piece.shape, (current_piece.x, current_piece.y), grid):
                run = False

        draw_window(win, grid, score)
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
