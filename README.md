# Skibidi City Showdown

A small 2D Pygame prototype where you play as a brave Cameraman defending a stylized city from waves of Skibidi Toilets. Move around, line up your shots, and punch with the spacebar to keep the invasion at bay.

## Requirements
- Python 3.9–3.13
- Pygame (listed in `requirements.txt`)

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to play
1. Run the game:
   ```bash
   python main.py
   ```
2. Controls:
   - **Move:** WASD or arrow keys
   - **Punch:** Spacebar (short cooldown)
   - **Flash Burst:** F (area knockback/damage, longer cooldown)
   - **Restart:** R after defeat
3. Earn points by defeating Skibidi Toilets before they overrun the city.

## Notes
- The city map is procedurally generated each run, so every attempt looks a bit different.
- The red square that appears on spacebar hold shows the active punch hitbox.
- Dynamic difficulty ramps up enemy spawns; watch your health hearts in the HUD.
