import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

landing_sound = pygame.mixer.Sound("landing.wav")
vanish_sound = pygame.mixer.Sound("vanish.wav")

BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE + 50
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]


def create_piece(x):
    blocks = []
    colors = [random.choice(COLORS) for _ in range(3)]
    for i in range(3):
        blocks.append((x, i, colors[i]))
    return blocks, 0, blocks[1]


def rotate_piece(blocks, orientation, grid):
    new_blocks = []
    new_orientation = (orientation + 1) % 4

    if new_orientation % 2 == 1:
        offsets = (
            [(-1, 0), (0, 0), (1, 0)]
            if new_orientation == 1
            else [(1, 0), (0, 0), (-1, 0)]
        )
    else:
        offsets = (
            [(0, -1), (0, 0), (0, 1)]
            if new_orientation == 0
            else [(0, 1), (0, 0), (0, -1)]
        )

    center_x, center_y, _ = blocks[1]
    for dx, dy in offsets:
        new_x = center_x + dx
        new_y = center_y + dy

        if (
            not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT)
            or grid[new_y][new_x]
        ):
            return blocks, orientation
        new_blocks.append((new_x, new_y, None))

    for i, (x, y, _) in enumerate(new_blocks):
        new_blocks[i] = (x, y, blocks[i][2])

    return new_blocks, new_orientation, new_blocks[1]


def move_piece(blocks, dx, grid):
    new_positions = [(x + dx, y) for x, y, _ in blocks]
    if all(0 <= x < GRID_WIDTH and not grid[y][x] for x, y in new_positions):
        for i, (new_x, y) in enumerate(new_positions):
            blocks[i] = (new_x, y, blocks[i][2])
    return blocks


def fall_piece(blocks, grid, fast=False):
    falling_blocks = sorted(blocks.copy(), key=lambda b: -b[1])
    any_falling = False
    will_land = True

    for i, (x, y, color) in enumerate(falling_blocks):
        if y + 1 < GRID_HEIGHT and not grid[y + 1][x]:
            falling_blocks[i] = (x, y + 1, color)
            any_falling = True
            will_land = False
        else:
            grid[y][x] = color

    if will_land and not any_falling:
        landing_sound.play()

    if fast and any_falling:
        return fall_piece(falling_blocks, grid, fast)

    return falling_blocks, any_falling


def settle_blocks(grid):
    settled = False
    while not settled:
        settled = True
        for y in range(GRID_HEIGHT - 2, -1, -1):
            for x in range(GRID_WIDTH):
                if grid[y][x] and not grid[y + 1][x]:
                    grid[y + 1][x] = grid[y][x]
                    grid[y][x] = None
                    settled = False


def check_matches(grid):
    matches = set()

    # Horizontal and vertical matches
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH - 2):
            if grid[y][x] and grid[y][x + 1] and grid[y][x + 2]:
                if grid[y][x] == grid[y][x + 1] == grid[y][x + 2]:
                    matches.update([(y, x), (y, x + 1), (y, x + 2)])

    for y in range(GRID_HEIGHT - 2):
        for x in range(GRID_WIDTH):
            if grid[y][x] and grid[y + 1][x] and grid[y + 2][x]:
                if grid[y][x] == grid[y + 1][x] == grid[y + 2][x]:
                    matches.update([(y, x), (y + 1, x), (y + 2, x)])

    # Diagonal matches (down-right)
    for y in range(GRID_HEIGHT - 2):
        for x in range(GRID_WIDTH - 2):
            if grid[y][x] and grid[y + 1][x + 1] and grid[y + 2][x + 2]:
                if grid[y][x] == grid[y + 1][x + 1] == grid[y + 2][x + 2]:
                    matches.update([(y, x), (y + 1, x + 1), (y + 2, x + 2)])

    # Diagonal matches (up-right)
    for y in range(2, GRID_HEIGHT):
        for x in range(GRID_WIDTH - 2):
            if grid[y][x] and grid[y - 1][x + 1] and grid[y - 2][x + 2]:
                if grid[y][x] == grid[y - 1][x + 1] == grid[y - 2][x + 2]:
                    matches.update([(y, x), (y - 1, x + 1), (y - 2, x + 2)])

    if matches:
        vanish_sound.play()

    for y, x in matches:
        grid[y][x] = None

    return len(matches)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Color Block Game")
    clock = pygame.time.Clock()
    score = 0

    font = pygame.font.Font(None, 36)

    grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    blocks, orientation, center_block = create_piece(GRID_WIDTH // 2)
    fall_time = 0
    fall_speed = 500

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    blocks = move_piece(blocks, -1, grid)
                elif event.key == pygame.K_RIGHT:
                    blocks = move_piece(blocks, 1, grid)
                elif event.key == pygame.K_UP:
                    blocks, orientation, center_block = rotate_piece(
                        blocks, orientation, grid
                    )
                elif event.key == pygame.K_DOWN:
                    blocks, _ = fall_piece(blocks, grid, fast=True)
                    fall_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if current_time - fall_time > fall_speed:
            blocks, falling = fall_piece(blocks, grid)
            if not falling:
                while True:
                    settle_blocks(grid)
                    matched = check_matches(grid)
                    if matched == 0:
                        break
                    score += matched

                blocks, orientation, center_block = create_piece(
                    GRID_WIDTH // 2
                )

                if any(grid[0][x] for x in range(GRID_WIDTH)):
                    pygame.quit()
                    sys.exit()

            fall_time = current_time

        screen.fill((0, 0, 0))

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    pygame.draw.rect(
                        screen,
                        grid[y][x],
                        (
                            x * BLOCK_SIZE,
                            y * BLOCK_SIZE,
                            BLOCK_SIZE,
                            BLOCK_SIZE,
                        ),
                    )

        for x, y, color in blocks:
            pygame.draw.rect(
                screen,
                color,
                (
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE,
                ),
            )

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
