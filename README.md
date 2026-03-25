# 2D Top-Down Shooter

A simple 2D top-down shooter game built with Pygame.

## Files

- `topdown_shooter.py` - Main game file
- `player.py` - Player class with movement and aiming
- `cargame.py` - Original car racing game (legacy)
- `Gun.py` - Basic pygame setup (placeholder)

## How to Run

1. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
```

2. Install dependencies:
```bash
python -m pip install pygame
```

3. Run the game:
```bash
python topdown_shooter.py
```

## Controls

- **WASD** - Move player
- **Mouse** - Aim direction
- Player appears as a green circle with a yellow aim indicator

## Features

- Smooth player movement with diagonal normalization
- Mouse-based aiming system
- Health system
- Boundary collision detection
```
This matters because pip is the tool that installs Python packages. Using python -m pip is clearer than just typing pip, because it makes sure the package installer belongs to the currently selected Python interpreter.

Example package install

If the project later needs a package such as requests, you would install it like this:
```
python -m pip install pygame
```
