import pygame
import random
import sys
from typing import List, Tuple

pygame.init()
pygame.mixer.init()

landing_sound = pygame.mixer.Sound("landing.wav")
vanish_sound = pygame.mixer.Sound("vanish.wav")

BLOCK_SIZE = 30
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE + 50
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]


class Block:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color


class Piece:
    def __init__(self, x: int):
        self.blocks = []
        colors = [random.choice(COLORS) for _ in range(3)]
        for i in range(3):
            self.blocks.append(Block(x, i, colors[i]))
        self.orientation = 0
        self.center_block = self.blocks[1]

    def rotate(self, grid: List[List[Block]]):
        new_blocks = []
        self.orientation = (self.orientation + 1) % 4

        if self.orientation % 2 == 1:
            offsets = (
                [(-1, 0), (0, 0), (1, 0)]
                if self.orientation == 1
                else [(1, 0), (0, 0), (-1, 0)]
            )
        else:
            offsets = (
                [(0, -1), (0, 0), (0, 1)]
                if self.orientation == 0
                else [(0, 1), (0, 0), (0, -1)]
            )

        center_x, center_y = self.center_block.x, self.center_block.y
        for i, (dx, dy) in enumerate(offsets):
            new_x = center_x + dx
            new_y = center_y + dy

            if (
                not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT)
                or grid[new_y][new_x]
            ):
                return
            new_blocks.append(Block(new_x, new_y, self.blocks[i].color))

        self.blocks = new_blocks

    def move(self, dx: int, grid: List[List[Block]]):
        new_positions = [(block.x + dx, block.y) for block in self.blocks]
        if all(
            0 <= x < GRID_WIDTH and not grid[y][x] for x, y in new_positions
        ):
            for block, (new_x, _) in zip(self.blocks, new_positions):
                block.x = new_x
            self.center_block = self.blocks[1]

    def fall(self, grid: List[List[Block]], fast: bool = False) -> bool:
        falling_blocks = sorted(self.blocks.copy(), key=lambda b: -b.y)
        any_falling = False
        will_land = True

        for block in falling_blocks:
            if block.y + 1 < GRID_HEIGHT and not grid[block.y + 1][block.x]:
                block.y += 1
                any_falling = True
                will_land = False
            else:
                grid[block.y][block.x] = block

        if will_land and not any_falling:
            landing_sound.play()

        if fast and any_falling:
            return self.fall(grid, fast)

        return any_falling


def settle_blocks(grid: List[List[Block]]):
    settled = False
    while not settled:
        settled = True
        for y in range(GRID_HEIGHT - 2, -1, -1):
            for x in range(GRID_WIDTH):
                if grid[y][x] and not grid[y + 1][x]:
                    grid[y + 1][x] = grid[y][x]
                    grid[y][x] = None
                    settled = False


def check_matches(grid: List[List[Block]]) -> int:
    matches = set()

    # Horizontal and vertical matches
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH - 2):
            if grid[y][x] and grid[y][x + 1] and grid[y][x + 2]:
                if (
                    grid[y][x].color
                    == grid[y][x + 1].color
                    == grid[y][x + 2].color
                ):
                    matches.update([(y, x), (y, x + 1), (y, x + 2)])

    for y in range(GRID_HEIGHT - 2):
        for x in range(GRID_WIDTH):
            if grid[y][x] and grid[y + 1][x] and grid[y + 2][x]:
                if (
                    grid[y][x].color
                    == grid[y + 1][x].color
                    == grid[y + 2][x].color
                ):
                    matches.update([(y, x), (y + 1, x), (y + 2, x)])

    # Diagonal matches (down-right)
    for y in range(GRID_HEIGHT - 2):
        for x in range(GRID_WIDTH - 2):
            if grid[y][x] and grid[y + 1][x + 1] and grid[y + 2][x + 2]:
                if (
                    grid[y][x].color
                    == grid[y + 1][x + 1].color
                    == grid[y + 2][x + 2].color
                ):
                    matches.update([(y, x), (y + 1, x + 1), (y + 2, x + 2)])

    # Diagonal matches (up-right)
    for y in range(2, GRID_HEIGHT):
        for x in range(GRID_WIDTH - 2):
            if grid[y][x] and grid[y - 1][x + 1] and grid[y - 2][x + 2]:
                if (
                    grid[y][x].color
                    == grid[y - 1][x + 1].color
                    == grid[y - 2][x + 2].color
                ):
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
    current_piece = Piece(GRID_WIDTH // 2)
    fall_time = 0
    fall_speed = 500

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.move(-1, grid)
                elif event.key == pygame.K_RIGHT:
                    current_piece.move(1, grid)
                elif event.key == pygame.K_UP:
                    current_piece.rotate(grid)
                elif event.key == pygame.K_DOWN:
                    current_piece.fall(grid, fast=True)
                    fall_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        if current_time - fall_time > fall_speed:
            if not current_piece.fall(grid):
                while True:
                    settle_blocks(grid)
                    matched = check_matches(grid)
                    if matched == 0:
                        break
                    score += matched

                current_piece = Piece(GRID_WIDTH // 2)

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
                        grid[y][x].color,
                        (
                            x * BLOCK_SIZE,
                            y * BLOCK_SIZE,
                            BLOCK_SIZE,
                            BLOCK_SIZE,
                        ),
                    )

        for block in current_piece.blocks:
            pygame.draw.rect(
                screen,
                block.color,
                (
                    block.x * BLOCK_SIZE,
                    block.y * BLOCK_SIZE,
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
