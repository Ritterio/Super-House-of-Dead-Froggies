# Super-House-of-Dead-Froggies

## Description

This code implements a simple game called "Super House of Dead Froggies" inspired by "Super House of Dead Ninjas" using the Pygame library. The game involves controlling a frog character and jumping on platforms to reach the bottom of the level while avoiding and/or shooting enemies and collecting flowers.

## Dependencies

The code requires the Pygame library to be installed. Pygame is used for handling game-related functionalities such as graphics, sound, and input.

## How to Run

###  To run the code, follow these steps:

Make sure Pygame is installed:
    
    pip install pygame

Run the Python script using a Python interpreter:

    python game.py

## Game Controls

Use the left and right arrow keys to move the frog character.
Press the spacebar to shoot bullets.
Press the up arrow key to jump.

## Code Structure:

The code is structured into multiple classes:

- Game:

Main game class that manages the game loop and overall game functionality.
Handles game initialization, event handling, updating game state, and drawing.

- Camera

    - Manages the camera movement and view area.

- Character:

    - Base class for player character.

- Player:

    - Inherits from the Character class.
    - Represents the player-controlled frog character.
    - Handles player movement, jumping, shooting and collision detection.

- Bullet:

    - Represents the bullets shot by the player.
    - Handles bullet movement.

- Floor:

    - Responsible for creating level, which contains 3 platforms, 2 enemies, and 1 flower.

- Platform:

    - represents a single platform.

- Enemy:

    - Represents enemy characters.

- Flower:

    - Represents collectible flowers.

## Game Flow:

- The game starts with a start screen, where the player can choose to start the game or exit.

- Once the game starts, the player controls the frog character using the arrow keys and spacebar.

- The player must navigate the frog to jump on platforms and reach the bottom of the level.

- The player can shoot bullets to eliminate enemies

- The player can collect flowers and gain points.

- The player has 3 hearts, which decrease upon colliding with enemies.

- If the player loses all hearts, the game ends, and a game over screen is shown with the player's score.

- If the player reaches the bottom of the level, the game ends, and a game over screen is shown with the player's score.

- The player can choose to play again or exit from the game over screen.
