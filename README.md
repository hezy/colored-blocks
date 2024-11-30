# Color Block Game

This is a simple color-matching game implemented in Python using the Pygame library.

## Gameplay

The objective of the game is to match three or more blocks of the same color in a row, column, or diagonal. The blocks are arranged in a grid, and the player can rotate and move the falling piece to create matches. When a match is made, the blocks disappear, and the player earns points. The game ends when the blocks reach the top of the grid.

## Features

- Randomly generated falling pieces with different colors
- Rotating and moving the falling piece using arrow keys
- Settling blocks after a piece lands
- Checking for matches in horizontal, vertical, and diagonal directions
- Sound effects for landing and vanishing blocks
- Scoring system based on the number of matched blocks

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Make sure you have Python 3.x installed on your system.
2. Install the Pygame library by running the following command:
   ```
   pip install pygame
   ```
3. Clone or download this repository to your local machine.

## Usage

1. Navigate to the project directory.
2. Run the following command to start the game:
   ```
   python color_block_game.py
   ```
3. Use the arrow keys to control the falling piece:
   - Left arrow: Move the piece to the left
   - Right arrow: Move the piece to the right
   - Up arrow: Rotate the piece
   - Down arrow: Speed up the falling of the piece
4. Match three or more blocks of the same color to earn points.
5. The game ends when the blocks reach the top of the grid.

## Customization

You can customize the game by modifying the following constants in the code:

- `BLOCK_SIZE`: The size of each block in pixels
- `GRID_WIDTH`: The width of the game grid in blocks
- `GRID_HEIGHT`: The height of the game grid in blocks
- `COLORS`: The list of colors used for the blocks

## Credits

- Sound effects: [landing.wav](landing.wav) and [vanish.wav](vanish.wav) (replace with the actual sound file names)

## License

This project is licensed under the [MIT License](LICENSE).