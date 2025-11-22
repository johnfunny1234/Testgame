# Skibidi City Showdown

A small 2D Pygame prototype where you play as a brave Cameraman walking down an endless city block while waves of Skibidi Toilets roll in from the right. Keep moving forward, line up your shots, and punch with the spacebar to keep the invasion at bay.

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
   - **Move:** WASD or arrow keys (hold right to advance down the block)
   - **Punch:** Spacebar (short cooldown)
   - **Flash Burst:** F (area knockback/damage, longer cooldown)
   - **Restart:** R after defeat
3. Earn points by defeating Skibidi Toilets before they overrun the city. Enemies enter from the right edge and include variants inspired by Skibidi Toilet episodes 1–10, each with unique speed/health mixes.

## Notes
- The city skyline scrolls by automatically to sell the “walking forward” feel.
- The red square that appears on spacebar hold shows the active punch hitbox.
- Dynamic difficulty ramps up enemy spawns; watch your health hearts in the HUD.
- Episode labels hover over each toilet (Ep1–Ep10) so you can see which variant is rushing you.
