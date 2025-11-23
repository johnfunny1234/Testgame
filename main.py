import math
import random
import sys
from dataclasses import dataclass
from typing import List

import pygame

# Game constants
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
CITY_GRID_SIZE = 80
PLAYER_SPEED = 4
PLAYER_MAX_HEALTH = 5
PLAYER_GROUND_Y = SCREEN_HEIGHT - 104
PUNCH_RANGE = 60
PUNCH_COOLDOWN = 280  # milliseconds
PUNCH_DAMAGE_CAMERAMAN = 2
PUNCH_DAMAGE_SPEAKERMAN = 5
FLASH_COOLDOWN = 6500  # milliseconds
FLASH_RADIUS = 120
FLASH_DAMAGE_CAMERAMAN = 2
FLASH_DAMAGE_SPEAKERMAN = 3
SOUNDWAVE_COOLDOWN = 5200  # milliseconds
SOUNDWAVE_DAMAGE = 2
SOUNDWAVE_RANGE = 220
SOUNDWAVE_HEIGHT = 130
SPEAKERMAN_SCORE_COST = 12
ENEMY_SPAWN_TIME = 2200  # milliseconds
MIN_ENEMY_SPAWN_TIME = 650
ENEMY_DAMAGE = 1
ENEMY_CONTACT_DISTANCE = 26
CITY_SCROLL_SPEED = 70  # pixels per second
PLAYER_DAMAGE_COOLDOWN = 1200  # milliseconds


@dataclass
class CameraMan:
    position: pygame.Vector2
    facing: pygame.Vector2
    form: str = "cameraman"
    health: int = PLAYER_MAX_HEALTH
    punch_cooldown_timer: int = 0
    flash_cooldown_timer: int = 0
    soundwave_cooldown_timer: int = 0
    damage_cooldown_timer: int = 0
    bob_phase: float = 0.0
    bob_amplitude: float = 2.5

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1

        if movement.length_squared() > 0:
            movement = movement.normalize() * PLAYER_SPEED
            self.position += movement
            self.position.x = max(26, min(SCREEN_WIDTH - 26, self.position.x))
            self.position.y = PLAYER_GROUND_Y
            self.facing = movement.normalize()
        else:
            self.position.y = PLAYER_GROUND_Y

    def can_punch(self) -> bool:
        return self.punch_cooldown_timer <= 0

    def start_punch(self) -> None:
        self.punch_cooldown_timer = PUNCH_COOLDOWN

    def can_flash(self) -> bool:
        return self.flash_cooldown_timer <= 0

    def start_flash(self) -> None:
        self.flash_cooldown_timer = FLASH_COOLDOWN

    def can_soundwave(self) -> bool:
        return self.form == "speakerman" and self.soundwave_cooldown_timer <= 0

    def start_soundwave(self) -> None:
        self.soundwave_cooldown_timer = SOUNDWAVE_COOLDOWN

    def take_damage(self, amount: int) -> None:
        if self.damage_cooldown_timer > 0:
            return
        self.health = max(0, self.health - amount)
        self.damage_cooldown_timer = PLAYER_DAMAGE_COOLDOWN

    def update(self, dt: int) -> None:
        self.punch_cooldown_timer = max(0, self.punch_cooldown_timer - dt)
        self.flash_cooldown_timer = max(0, self.flash_cooldown_timer - dt)
        self.soundwave_cooldown_timer = max(0, self.soundwave_cooldown_timer - dt)
        self.damage_cooldown_timer = max(0, self.damage_cooldown_timer - dt)
        self.bob_phase = (self.bob_phase + dt * 0.005) % (2 * math.pi)

    def upgrade_to_speakerman(self) -> None:
        self.form = "speakerman"
        # small celebratory bob boost for the upgraded stance
        self.bob_amplitude = 3.2

    def draw(self, surface: pygame.Surface) -> None:
        body_color = (30, 120, 200) if self.form == "cameraman" else (30, 30, 36)
        head_color = (230, 240, 255) if self.form == "cameraman" else (180, 180, 185)
        base_rect = pygame.Rect(0, 0, 36, 48)
        bob = math.sin(self.bob_phase) * self.bob_amplitude
        base_rect.center = (self.position.x, self.position.y + bob)
        pygame.draw.rect(surface, body_color, base_rect, border_radius=6)

        if self.form == "cameraman":
            head_rect = pygame.Rect(0, 0, 24, 18)
            head_rect.midbottom = base_rect.midtop
            pygame.draw.rect(surface, head_color, head_rect, border_radius=4)

            # Camera lens
            lens_center = (int(head_rect.centerx + self.facing.x * 6), int(head_rect.centery + self.facing.y * 6))
            pygame.draw.circle(surface, (20, 20, 20), lens_center, 4)
        else:
            speaker_rect = pygame.Rect(0, 0, 30, 20)
            speaker_rect.midbottom = base_rect.midtop
            pygame.draw.rect(surface, head_color, speaker_rect, border_radius=3)
            grill_rect = speaker_rect.inflate(-10, -8)
            pygame.draw.rect(surface, (40, 40, 44), grill_rect, border_radius=2, width=2)
            center = speaker_rect.center
            pygame.draw.circle(surface, (140, 140, 150), (center[0] - 6, center[1]), 4)
            pygame.draw.circle(surface, (90, 90, 100), (center[0] + 8, center[1]), 3)
            pygame.draw.rect(surface, (90, 90, 100), grill_rect.inflate(-6, -6), border_radius=2)


@dataclass
class SkibidiToilet:
    position: pygame.Vector2
    health: int
    speed: float
    label: str = ""
    scale: float = 1.0
    is_saint: bool = False
    angry: bool = False
    wobble_phase: float = 0.0
    wiggle_amp: float = 2.0
    body_color: tuple[int, int, int] = (210, 210, 210)
    rim_color: tuple[int, int, int] = (240, 240, 240)
    eye_color: tuple[int, int, int] = (40, 40, 40)
    _label_font: pygame.font.Font | None = None

    def update(self, target: pygame.Vector2, dt: int) -> None:
        direction = target - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
            speed = self.speed
            if self.is_saint and (self.angry or self.health <= 6):
                speed += 0.7
                self.angry = True
                self.eye_color = (160, 20, 20)
            self.position += direction * speed

        # Extra wobble and occasional vertical shimmy for variety.
        self.wobble_phase = (self.wobble_phase + dt * 0.01) % (2 * math.pi)
        self.position.y += math.sin(self.wobble_phase * 0.6) * 0.12 * self.wiggle_amp

    def take_damage(self, amount: int) -> None:
        self.health -= amount

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw(self, surface: pygame.Surface) -> None:
        wobble_offset = math.sin(self.wobble_phase) * self.wiggle_amp
        shadow_rect = pygame.Rect(0, 0, int(48 * self.scale), int(14 * self.scale))
        shadow_rect.center = (int(self.position.x), int(self.position.y + wobble_offset + 24))
        pygame.draw.ellipse(surface, (24, 24, 32), shadow_rect)

        base_rect = pygame.Rect(0, 0, int(44 * self.scale), int(30 * self.scale))
        base_rect.center = self.position
        base_rect.y += wobble_offset
        pygame.draw.rect(surface, self.body_color, base_rect, border_radius=8)

        tank_rect = pygame.Rect(0, 0, int(40 * self.scale), int(16 * self.scale))
        tank_rect.midbottom = base_rect.midtop
        tank_rect.y -= 6
        tank_rect.y += wobble_offset
        pygame.draw.rect(surface, (220, 225, 235), tank_rect, border_radius=6)
        pygame.draw.rect(surface, (110, 140, 170), tank_rect.inflate(-18, -8), border_radius=4, width=2)

        seat_rect = pygame.Rect(0, 0, int(32 * self.scale), int(14 * self.scale))
        seat_rect.midtop = base_rect.midtop
        seat_rect.y += wobble_offset - 2
        pygame.draw.rect(surface, self.rim_color, seat_rect, border_radius=8)
        pygame.draw.rect(surface, (180, 180, 200), seat_rect.inflate(-10, -6), border_radius=6)

        water_center = (base_rect.centerx, base_rect.centery + wobble_offset)
        pygame.draw.circle(surface, (130, 190, 255), water_center, 8)
        pygame.draw.circle(surface, (220, 240, 255), water_center, 4)

        # Face
        eye_y = base_rect.top + 8 * self.scale + wobble_offset
        eye_offset = 10 * self.scale
        eye_radius = max(3, int(5 * self.scale))
        pupil_radius = max(2, int(3 * self.scale))
        pygame.draw.circle(surface, (255, 255, 255), (base_rect.centerx - eye_offset, int(eye_y)), eye_radius)
        pygame.draw.circle(surface, (255, 255, 255), (base_rect.centerx + eye_offset, int(eye_y)), eye_radius)
        pygame.draw.circle(surface, self.eye_color, (base_rect.centerx - eye_offset, int(eye_y)), pupil_radius)
        pygame.draw.circle(surface, self.eye_color, (base_rect.centerx + eye_offset, int(eye_y)), pupil_radius)
        mouth_rect = pygame.Rect(0, 0, int(18 * self.scale), int(8 * self.scale))
        mouth_rect.midtop = (base_rect.centerx, eye_y + 8 * self.scale)
        pygame.draw.arc(surface, (180, 60, 60), mouth_rect, math.radians(10), math.radians(170), max(2, int(2 * self.scale)))

        if self.is_saint:
            halo_rect = pygame.Rect(0, 0, 40, 10)
            halo_rect.midbottom = (tank_rect.centerx, tank_rect.top - 8)
            halo_rect.y += math.sin(self.wobble_phase * 1.4) * 2
            pygame.draw.ellipse(surface, (255, 225, 120), halo_rect, width=3)
            pygame.draw.ellipse(surface, (255, 245, 200), halo_rect.inflate(-6, -4), width=2)

        if self.label:
            if SkibidiToilet._label_font is None:
                SkibidiToilet._label_font = pygame.font.SysFont("arial", 14)
            label_surface = SkibidiToilet._label_font.render(self.label, True, (20, 20, 40))
            label_rect = label_surface.get_rect(center=(base_rect.centerx, base_rect.top - 12))
            surface.blit(label_surface, label_rect)


class CityMap:
    def __init__(self) -> None:
        self.buildings: List[pygame.Rect] = []
        self.street_lines: List[int] = [SCREEN_HEIGHT - 160, SCREEN_HEIGHT - 110]
        start_x = 0
        for _ in range(14):
            w, h = random.randint(80, 200), random.randint(80, 180)
            x = start_x + random.randint(30, 120)
            start_x = x + w + random.randint(40, 120)
            y = SCREEN_HEIGHT - h - random.randint(120, 200)
            self.buildings.append(pygame.Rect(x, y, w, h))

    def update(self, dt: int) -> None:
        dx = CITY_SCROLL_SPEED * (dt / 1000.0)
        for building in list(self.buildings):
            building.x -= dx
            if building.right < -80:
                self.buildings.remove(building)
                w, h = random.randint(80, 200), random.randint(80, 180)
                x = SCREEN_WIDTH + random.randint(40, 180)
                y = SCREEN_HEIGHT - h - random.randint(120, 200)
                self.buildings.append(pygame.Rect(x, y, w, h))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((30, 34, 42))
        # Grid floor to hint the cameraman is moving right across the city.
        for x in range(-CITY_GRID_SIZE, SCREEN_WIDTH + CITY_GRID_SIZE, CITY_GRID_SIZE):
            pygame.draw.line(surface, (48, 54, 63), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CITY_GRID_SIZE):
            pygame.draw.line(surface, (48, 54, 63), (0, y), (SCREEN_WIDTH, y))

        for building in self.buildings:
            pygame.draw.rect(surface, (58, 68, 83), building)
            window_color = random.choice([(255, 200, 40), (120, 150, 190), (70, 90, 120)])
            for _ in range(random.randint(3, 7)):
                size = random.randint(6, 10)
                px = random.randint(building.left + 6, building.right - 6)
                py = random.randint(building.top + 6, building.bottom - 6)
                pygame.draw.rect(surface, window_color, pygame.Rect(px, py, size, size))

        # Street lane markers to sell the walking-forward direction.
        street_y = SCREEN_HEIGHT - 80
        pygame.draw.rect(surface, (26, 28, 34), pygame.Rect(0, street_y, SCREEN_WIDTH, 90))
        for i in range(0, SCREEN_WIDTH, 80):
            pygame.draw.rect(surface, (255, 215, 120), pygame.Rect(i + 10, street_y + 38, 40, 6), border_radius=3)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Skibidi City Showdown")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)

        self.city = CityMap()
        self.player = CameraMan(pygame.Vector2(SCREEN_WIDTH // 2, PLAYER_GROUND_Y), pygame.Vector2(1, 0))
        self.enemies: List[SkibidiToilet] = []
        self.last_spawn = 0
        self.score = 0
        self.flash_active_time = 0
        self.soundwave_active_time = 0
        self.game_over = False
        self.wave = 1
        self.wave_goal = 8
        self.wave_kills = 0
        self.saint_spawned = False

    def reset(self) -> None:
        self.city = CityMap()
        self.player = CameraMan(pygame.Vector2(SCREEN_WIDTH // 2, PLAYER_GROUND_Y), pygame.Vector2(1, 0))
        self.enemies = []
        self.last_spawn = 0
        self.score = 0
        self.flash_active_time = 0
        self.soundwave_active_time = 0
        self.game_over = False
        self.wave = 1
        self.wave_goal = 8
        self.wave_kills = 0
        self.saint_spawned = False

    def spawn_enemy(self) -> None:
        base_health = 2 + max(0, self.wave - 1) * 0.2
        base_speed = 1.2 + max(0, self.wave - 1) * 0.08
        pos = pygame.Vector2(SCREEN_WIDTH + 40, PLAYER_GROUND_Y + random.uniform(-6, 6))
        wiggle_amp = random.uniform(2.0, 3.5)

        if self.wave >= 5 and not self.saint_spawned:
            saint = SkibidiToilet(
                position=pos,
                health=14,
                speed=1.1,
                wiggle_amp=2.6,
                body_color=(235, 230, 225),
                rim_color=(245, 240, 220),
                eye_color=(80, 20, 20),
                is_saint=True,
                label="Saint",
                scale=1.35,
            )
            self.enemies.append(saint)
            self.saint_spawned = True
            return

        health_variation = random.choice([0, 0, 1])
        speed_variation = random.uniform(-0.05, 0.25)
        is_medium = self.wave >= 2 and random.random() < 0.35
        label = "Medium" if is_medium else ""
        enemy = SkibidiToilet(
            position=pos,
            health=int(base_health + health_variation + (2 if is_medium else 0)),
            speed=base_speed + speed_variation - (0.05 if is_medium else 0),
            wiggle_amp=wiggle_amp + (0.4 if is_medium else 0),
            body_color=random.choice([(214, 214, 220), (222, 228, 234), (210, 216, 224)]),
            rim_color=random.choice([(240, 240, 245), (236, 240, 242)]),
            label=label,
            scale=1.25 if is_medium else 1.0,
        )
        self.enemies.append(enemy)

    def punch_hitbox(self) -> pygame.Rect:
        if self.player.facing.length_squared() == 0:
            facing = pygame.Vector2(0, -1)
        else:
            facing = self.player.facing.normalize()

        punch_origin = self.player.position + facing * 28
        hitbox_center = punch_origin + facing * (PUNCH_RANGE // 2)
        size = (26, 26)
        hitbox = pygame.Rect(0, 0, *size)
        hitbox.center = (int(hitbox_center.x), int(hitbox_center.y))
        return hitbox

    def update(self, dt: int) -> None:
        self.city.update(dt)
        self.flash_active_time = max(0, self.flash_active_time - dt)
        self.soundwave_active_time = max(0, self.soundwave_active_time - dt)
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)

        if keys[pygame.K_u] and self.player.form == "cameraman" and self.score >= SPEAKERMAN_SCORE_COST:
            self.score -= SPEAKERMAN_SCORE_COST
            self.player.upgrade_to_speakerman()

        if keys[pygame.K_SPACE] and self.player.can_punch():
            self.player.start_punch()
            hitbox = self.punch_hitbox()
            for enemy in list(self.enemies):
                if hitbox.collidepoint(enemy.position):
                    damage = PUNCH_DAMAGE_SPEAKERMAN if self.player.form == "speakerman" else PUNCH_DAMAGE_CAMERAMAN
                    enemy.take_damage(damage)
                    offset = (enemy.position - self.player.position)
                    if offset.length_squared() > 0:
                        knock = 16 if self.player.form == "speakerman" else 12
                        enemy.position += offset.normalize() * knock
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += 1
                        self.wave_kills += 1

        flash_radius = FLASH_RADIUS + (24 if self.player.form == "speakerman" else 0)
        if keys[pygame.K_f] and self.player.can_flash():
            self.player.start_flash()
            self.flash_active_time = 250
            for enemy in list(self.enemies):
                if enemy.position.distance_to(self.player.position) <= flash_radius:
                    flash_damage = FLASH_DAMAGE_SPEAKERMAN if self.player.form == "speakerman" else FLASH_DAMAGE_CAMERAMAN
                    enemy.take_damage(flash_damage)
                    push = (enemy.position - self.player.position)
                    if push.length_squared() > 0:
                        enemy.position += push.normalize() * 20
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += 1
                        self.wave_kills += 1

        if (
            self.player.form == "speakerman"
            and keys[pygame.K_x]
            and self.player.can_soundwave()
        ):
            self.player.start_soundwave()
            self.soundwave_active_time = 240
            direction = 1 if self.player.facing.x >= 0 else -1
            wave_rect = pygame.Rect(
                self.player.position.x + (16 * direction),
                self.player.position.y - SOUNDWAVE_HEIGHT // 2,
                SOUNDWAVE_RANGE * direction,
                SOUNDWAVE_HEIGHT,
            )
            for enemy in list(self.enemies):
                if wave_rect.collidepoint(enemy.position.x, enemy.position.y):
                    enemy.take_damage(SOUNDWAVE_DAMAGE)
                    push_dir = pygame.Vector2(direction, 0)
                    enemy.position += push_dir * 26
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += 1
                        self.wave_kills += 1

        for enemy in list(self.enemies):
            enemy.update(self.player.position, dt)
            if enemy.position.distance_to(self.player.position) <= ENEMY_CONTACT_DISTANCE:
                self.player.take_damage(ENEMY_DAMAGE)
                away = (enemy.position - self.player.position)
                if away.length_squared() > 0:
                    enemy.position += away.normalize() * 16

        if self.wave_kills >= self.wave_goal:
            self.wave += 1
            self.wave_goal = min(16, self.wave_goal + 2)
            self.wave_kills = 0

        self.last_spawn += dt
        spawn_delay = max(
            MIN_ENEMY_SPAWN_TIME,
            (ENEMY_SPAWN_TIME - self.wave * 80) - self.score * 20,
        )
        if self.last_spawn >= spawn_delay:
            self.spawn_enemy()
            self.last_spawn = 0

        if self.player.health <= 0:
            self.game_over = True

    def draw_ui(self) -> None:
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        form = self.font.render(f"Form: {'Speakerman' if self.player.form == 'speakerman' else 'Cameraman'}", True, (190, 255, 210))
        cooldown = max(0, math.ceil(self.player.punch_cooldown_timer / 100))
        cd_text = self.font.render(f"Punch: {cooldown/10:.1f}s", True, (210, 210, 210))
        flash_cd = max(0, math.ceil(self.player.flash_cooldown_timer / 100))
        flash_text = self.font.render(f"Flash: {flash_cd/10:.1f}s", True, (190, 235, 255))
        sound_cd = max(0, math.ceil(self.player.soundwave_cooldown_timer / 100)) if self.player.form == "speakerman" else 0
        wave_text = self.font.render(f"Wave {self.wave}", True, (255, 235, 180))
        self.screen.blit(text, (12, 12))
        self.screen.blit(form, (12, 36))
        self.screen.blit(cd_text, (12, 60))
        self.screen.blit(flash_text, (12, 84))
        wave_y = 108
        if self.player.form == "speakerman":
            sound_label = self.font.render(f"Soundwave: {sound_cd/10:.1f}s", True, (220, 200, 255))
            self.screen.blit(sound_label, (12, wave_y))
            wave_y += 24
        self.screen.blit(wave_text, (12, wave_y))

        for i in range(PLAYER_MAX_HEALTH):
            color = (255, 90, 90) if i < self.player.health else (70, 60, 60)
            pygame.draw.rect(self.screen, color, pygame.Rect(12 + i * 26, wave_y + 28, 20, 16), border_radius=4)

        instructions = [
            "Move: A/D or Arrow Keys (walk the street)",
            "Punch: Spacebar",
            "Flash Burst: F (AoE + knockback)",
            f"Upgrade: U when score >= {SPEAKERMAN_SCORE_COST} to become Speakerman",
            "Soundwave: X (Speakerman cone blast)",
            "Toilets push in from the right—hold the ground!",
            "Wave 5 brings the Saint Skibidi Toilet.",
        ]
        for i, line in enumerate(instructions):
            label = self.font.render(line, True, (200, 215, 230))
            self.screen.blit(label, (12, SCREEN_HEIGHT - 24 * (len(instructions) - i)))

    def draw(self, punch_active: bool) -> None:
        self.city.draw(self.screen)
        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if punch_active:
            hitbox = self.punch_hitbox()
            pygame.draw.rect(self.screen, (255, 100, 100), hitbox, width=2)

        if self.flash_active_time > 0:
            base_radius = FLASH_RADIUS + (24 if self.player.form == "speakerman" else 0)
            radius = int(base_radius * (self.flash_active_time / 250))
            color = (255, 180, 90) if self.player.form == "speakerman" else (120, 200, 255)
            pygame.draw.circle(self.screen, color, self.player.position, radius, width=2)

        if self.soundwave_active_time > 0:
            direction = 1 if self.player.facing.x >= 0 else -1
            rect = pygame.Rect(
                self.player.position.x + (16 * direction),
                self.player.position.y - SOUNDWAVE_HEIGHT // 2,
                SOUNDWAVE_RANGE * direction,
                SOUNDWAVE_HEIGHT,
            )
            alpha = int(180 * (self.soundwave_active_time / 240))
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((150, 110, 255, alpha))
            self.screen.blit(overlay, rect.topleft)

        self.draw_ui()

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            title = self.font.render("Skibidi City Fell!", True, (255, 120, 120))
            prompt = self.font.render("Press R to restart", True, (230, 230, 230))
            score_text = self.font.render(f"Final score: {self.score}", True, (200, 220, 255))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
            self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)))
            self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                    self.reset()

            punch_active = pygame.key.get_pressed()[pygame.K_SPACE] and not self.player.can_punch()
            self.update(dt)
            self.draw(punch_active)

        pygame.quit()
        sys.exit()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
