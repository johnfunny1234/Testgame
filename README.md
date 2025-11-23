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
   - **F:** Forward **beam flash** (cameraman/speakerman) or **TV screen stun beam** (TV Man) with a short cooldown that freezes toilets in place
   - **X:** Soundwave (Speakerman cone shove) or **blade stab** (TV Man) that chunks foes in two hits
   - **Upgrade:**
     - Press **U** when you have **12+ score** to become a **Speakerman** (harder punches, longer flash beam, faster/harder soundwave, speaker-headed suit look) — upgrading refills your health to the new form’s maximum.
     - After you are a Speakerman, press **U** again with **15+ score** to become a **TV Man** (CRT head, hypnosis stun beam on F, high-damage blade stab on X) — health refills and the TV Man’s heart count is the highest.
   - **Restart:** R after defeat
3. Earn points by defeating Skibidi Toilets before they overrun the city. Enemies enter from the right edge, scaling up by wave. Wave 5 brings the Saint Skibidi Toilet boss with a halo and angrier red-eyed phase.

## Notes
- The city skyline scrolls by automatically to sell the “walking forward” feel.
- The red square that appears on spacebar hold shows the active punch hitbox.
- Dynamic difficulty ramps up enemy spawns and waves; watch your health hearts and the wave counter in the HUD.
- Upgrading to Speakerman costs 12 score and boosts your fists plus your flash beam and a harder, faster soundwave blast, letting you shoulder the late-wave toilet rush. Health refills when you switch forms.
- Upgrading to TV Man costs 15 score once you are already a Speakerman and swaps your toolkit: F becomes a hypnosis stun beam that freezes toilets (even the Saint), and X becomes a fast blade stab that downs normals in two strikes and shreds Mediums. The TV Man carries the most health, and his CRT screen shows a cracked overlay when you are on your last bar.
- The Saint Skibidi Toilet in wave 5 lunges faster when angry and is tougher than standard toilets.
- Medium Skibidi Toilets start appearing in wave 2 as beefier commanders; they’re larger, tougher, and wobble more than the basic units.
