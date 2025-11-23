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
- **F:** Forward **beam flash** (cameraman/speakerman/large cameraman) or **TV screen stun beam** (TV Man), or the **ultra sound blast** for **Large Speakerman**. Flash/blast damage knocks foes back; the Large Speakerman’s blast now radiates **360°** around you, and the stun beam freezes toilets in place.
   - **X:** Soundwave (Speakerman cone shove), **blade stab** (TV Man), or the **kicking strike** (Large Speakerman) for massive close damage.
   - **Upgrade:**
     - Press **U** when you have **12+ score** to become a **Speakerman** (harder punches, longer flash beam, faster/harder soundwave, speaker-headed suit look) — upgrading refills your health to the new form’s maximum.
     - After you are a Speakerman, press **U** again with **15+ score** to become a **TV Man** (CRT head, hypnosis stun beam on F, high-damage blade stab on X, tougher fists) — health refills and the TV Man’s heart count climbs.
     - After reaching **TV Man**, press **U** with **25+ score** to become a **Large Cameraman** (giant cinema cam head, heavy punch/flash damage) or press **I** with **35+ score** to become a **Large Speakerman** (tall twin-speaker head, strongest punches, ultra sound blast on F, crushing kick on X). Upgrading always refreshes you to full health.
   - **Restart:** R after defeat
3. Earn points by defeating Skibidi Toilets before they overrun the city. Enemies enter from the right edge, scaling up by wave. Each wave now ends only after every toilet is defeated, triggering a short intermission before the next assault. Wave 5 is entirely the Saint Skibidi Toilet boss wave with his own health bar, and wave 6 introduces Police Skibidi Toilets that hit harder.

## Notes
- The city skyline scrolls by automatically to sell the “walking forward” feel.
- The red square that appears on spacebar hold shows the active punch hitbox.
- Dynamic difficulty ramps up enemy spawns and waves; watch your health hearts and the wave counter in the HUD. After you wipe a wave, a brief intermission banner shows when the next wave begins.
- Upgrading to Speakerman costs 12 score and boosts your fists plus your flash beam and a harder, faster soundwave blast, letting you shoulder the late-wave toilet rush. Health refills when you switch forms.
- Upgrading to TV Man costs 15 score once you are already a Speakerman and swaps your toolkit: F becomes a hypnosis stun beam that freezes toilets (even the Saint), and X becomes a fast blade stab that downs normals in two strikes and shreds Mediums. TV Man now hits harder with punches and shows a cracked CRT overlay when on the last bar.
- Upgrading to Large Cameraman costs 25 score after TV Man and returns you to a heavy-duty flash/punch kit with a longer beam reach and a beefy heart pool. Press **U** while TV Man if you prefer this path.
- Upgrading to Large Speakerman costs 35 score after TV Man (press **U** to auto-upgrade when you have the points, or **I** as an explicit shortcut) and grants the biggest health pool, the strongest punches, an **ultra sound blast** on F that chunks and launches crowds, and a **kicking smash** on X that deletes normals in two hits and Mediums in one. If you became a Large Cameraman, you can still press **U** later with 35 score to swap into Large Speakerman.
- The Saint Skibidi Toilet now appears as a solo boss in wave 5 with a visible health bar and an angrier, faster phase.
- Medium Skibidi Toilets start appearing in wave 2 as beefier commanders; they’re larger, tougher, wobble more than the basic units, and reward **2 points** when defeated.
- Police Skibidi Toilets roll in starting at wave 6 with siren bars and higher contact damage, so avoid letting them collide with you.
- Wave 6 is the final wave on the opening street. After the intermission you walk into a **larger, taller center-city** map (wave 7 onward) where two friendly Cameraman allies stand with you; they share your base stats, strafe forward to **fight with punches and flashes**, and have their own health bars.
- Wave 8 introduces a rare **Large Skibidi Toilet**: an even **bigger, bulkier** variant about the size of a Large Speakerman with big health and dangerous contact damage.
- A main menu now appears on boot with a Start button and a quick changelog so you can hop in or review what’s new.
