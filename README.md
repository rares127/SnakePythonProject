# Python Snake Game

An arcade-style Snake game built with **Python** and **Pygame**. It features a robust **MVC architecture**, custom level configurations, and modern mechanics like undo (resurrect) and dynamic speed control.

## Key Features
* **Classic Arcade Action:** Eat food, grow, and avoid walls/obstacles.
* **Resurrection (Undo):** Crash? Press `U` to undo the last move and get a 3-second countdown to save yourself.
* **Dynamic Speed:** Adjust game speed in real-time with `+` and `-`.
* **Persistent High Scores:** Automatically saves your best runs.
* **Customizable:** Edit `config/config.json` to change board size and obstacles.

## Quick Start

**Prerequisites:** Python 3.x and `pygame`.

```bash
# 1. Install dependencies
pip install pygame

# 2. Run the game
python src/main.py
