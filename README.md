# Skibidi City Showdown

A small 2D Pygame prototype where you play as a brave Cameraman walking down an endless city block while waves of Skibidi Toilets roll in from the right. Keep moving forward on the street, line up your shots, and punch with the spacebar to keep the invasion at bay.

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
   - **Move:** A/D or arrow keys (walk the street, grounded)
   - **Punch:** Spacebar (buffed damage/knockback, short cooldown)
   - **Flash Burst:** F (area knockback/damage, longer cooldown; extra punch when upgraded)
   - **Soundwave (Speakerman):** X (cone-shaped blast that shoves and chips enemies)
   - **Upgrade:** Press **U** when you have **12+ score** to become a **Speakerman** (punches drop toilets in roughly three hits, wider flash wave, speaker-headed suit look)
   - **Restart:** R after defeat
3. Earn points by defeating Skibidi Toilets before they overrun the city. Enemies enter from the right edge, scaling up by wave. Wave 5 brings the Saint Skibidi Toilet boss with a halo and angrier red-eyed phase.

## Notes
- The city skyline scrolls by automatically to sell the “walking forward” feel.
- The red square that appears on spacebar hold shows the active punch hitbox.
- Dynamic difficulty ramps up enemy spawns and waves; watch your health hearts and the wave counter in the HUD.
- Upgrading to Speakerman costs 12 score and boosts your fists plus your flash wave and soundwave blast, letting you shoulder the late-wave toilet rush.
- The Saint Skibidi Toilet in wave 5 lunges faster when angry and is tougher than standard toilets.
- Medium Skibidi Toilets start appearing in wave 2 as beefier commanders; they’re larger, tougher, and wobble more than the basic units.
