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
MAX_WAVE = 8
FORM_MAX_HEALTH = {
    "cameraman": 5,
    "speakerman": 6,
    "tvman": 8,
    "large_cameraman": 9,
    "large_speakerman": 10,
}
PLAYER_GROUND_Y = SCREEN_HEIGHT - 104
PUNCH_RANGE = 60
PUNCH_COOLDOWN = 280  # milliseconds
PUNCH_DAMAGE_CAMERAMAN = 2
PUNCH_DAMAGE_SPEAKERMAN = 6
PUNCH_DAMAGE_TVMAN = 7
PUNCH_DAMAGE_LARGE = 8
PUNCH_DAMAGE_LARGE_SPEAK = 10
FLASH_COOLDOWN = 6500  # milliseconds
FLASH_BEAM_LENGTH = 260
FLASH_BEAM_WIDTH = 120
FLASH_DAMAGE_CAMERAMAN = 2
FLASH_DAMAGE_SPEAKERMAN = 4
FLASH_DAMAGE_LARGE = 5
FLASH_DAMAGE_LARGE_SPEAK = 7
STUN_COOLDOWN = 3600  # milliseconds
STUN_DURATION = 1800  # milliseconds
SOUNDWAVE_COOLDOWN = 4200  # milliseconds
SOUNDWAVE_DAMAGE = 3
SOUNDWAVE_RANGE = 220
SOUNDWAVE_HEIGHT = 130
KICK_COOLDOWN = 900  # milliseconds for large speakerman
KICK_DAMAGE = 10
KICK_RANGE = 84
SPEAKERMAN_SCORE_COST = 12
TVMAN_SCORE_COST = 15
LARGE_CAM_SCORE_COST = 25
LARGE_SPEAKER_SCORE_COST = 35
STAB_DAMAGE = 9
STAB_COOLDOWN = 1000  # milliseconds
STAB_RANGE = 70
ENEMY_SPAWN_TIME = 2200  # milliseconds
MIN_ENEMY_SPAWN_TIME = 650
ENEMY_DAMAGE = 1
POLICE_DAMAGE = 2
ALLY_FLASH_COOLDOWN = 2200
ENEMY_CONTACT_DISTANCE = 26
CITY_SCROLL_SPEED = 70  # pixels per second
CITY_SCROLL_SPEED_CENTER = 40
INTERMISSION_TIME = 2200  # milliseconds between waves
PLAYER_DAMAGE_COOLDOWN = 1200  # milliseconds


@dataclass
class CameraMan:
    position: pygame.Vector2
    facing: pygame.Vector2
    form: str = "cameraman"
    health: int = FORM_MAX_HEALTH["cameraman"]
    punch_cooldown_timer: int = 0
    flash_cooldown_timer: int = 0
    soundwave_cooldown_timer: int = 0
    stab_cooldown_timer: int = 0
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
        self.flash_cooldown_timer = FLASH_COOLDOWN if self.form != "tvman" else STUN_COOLDOWN

    def can_soundwave(self) -> bool:
        return self.form == "speakerman" and self.soundwave_cooldown_timer <= 0

    def start_soundwave(self) -> None:
        self.soundwave_cooldown_timer = SOUNDWAVE_COOLDOWN

    def can_kick(self) -> bool:
        return self.form == "large_speakerman" and self.soundwave_cooldown_timer <= 0

    def start_kick(self) -> None:
        self.soundwave_cooldown_timer = KICK_COOLDOWN

    def can_stab(self) -> bool:
        return self.form == "tvman" and self.stab_cooldown_timer <= 0

    def start_stab(self) -> None:
        self.stab_cooldown_timer = STAB_COOLDOWN

    def take_damage(self, amount: int) -> None:
        if self.damage_cooldown_timer > 0:
            return
        self.health = max(0, self.health - amount)
        self.damage_cooldown_timer = PLAYER_DAMAGE_COOLDOWN

    def update(self, dt: int) -> None:
        self.punch_cooldown_timer = max(0, self.punch_cooldown_timer - dt)
        self.flash_cooldown_timer = max(0, self.flash_cooldown_timer - dt)
        self.soundwave_cooldown_timer = max(0, self.soundwave_cooldown_timer - dt)
        self.stab_cooldown_timer = max(0, self.stab_cooldown_timer - dt)
        self.damage_cooldown_timer = max(0, self.damage_cooldown_timer - dt)
        self.bob_phase = (self.bob_phase + dt * 0.005) % (2 * math.pi)

    def upgrade_to_speakerman(self) -> None:
        self.form = "speakerman"
        # small celebratory bob boost for the upgraded stance
        self.bob_amplitude = 3.2
        self.health = FORM_MAX_HEALTH[self.form]

    def upgrade_to_tvman(self) -> None:
        self.form = "tvman"
        self.bob_amplitude = 3.4
        self.health = FORM_MAX_HEALTH[self.form]

    def upgrade_to_large_cameraman(self) -> None:
        self.form = "large_cameraman"
        self.bob_amplitude = 3.6
        self.health = FORM_MAX_HEALTH[self.form]

    def upgrade_to_large_speakerman(self) -> None:
        self.form = "large_speakerman"
        self.bob_amplitude = 3.8
        self.health = FORM_MAX_HEALTH[self.form]

    def draw(self, surface: pygame.Surface) -> None:
        body_color = (30, 120, 200) if self.form == "cameraman" else (30, 30, 36)
        if self.form == "large_cameraman":
            body_color = (44, 44, 48)
        if self.form == "large_speakerman":
            body_color = (46, 46, 56)
        head_color = (230, 240, 255) if self.form == "cameraman" else (180, 180, 185)
        base_size = (36, 48)
        if self.form == "large_cameraman":
            base_size = (50, 66)
        elif self.form == "large_speakerman":
            base_size = (56, 78)
        base_rect = pygame.Rect(0, 0, *base_size)
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
        elif self.form == "speakerman":
            speaker_rect = pygame.Rect(0, 0, 30, 20)
            speaker_rect.midbottom = base_rect.midtop
            pygame.draw.rect(surface, head_color, speaker_rect, border_radius=3)
            grill_rect = speaker_rect.inflate(-10, -8)
            pygame.draw.rect(surface, (40, 40, 44), grill_rect, border_radius=2, width=2)
            center = speaker_rect.center
            pygame.draw.circle(surface, (140, 140, 150), (center[0] - 6, center[1]), 4)
            pygame.draw.circle(surface, (90, 90, 100), (center[0] + 8, center[1]), 3)
            pygame.draw.rect(surface, (90, 90, 100), grill_rect.inflate(-6, -6), border_radius=2)
        elif self.form == "large_speakerman":
            speaker_rect = pygame.Rect(0, 0, 38, 26)
            speaker_rect.midbottom = base_rect.midtop
            pygame.draw.rect(surface, (34, 34, 42), speaker_rect, border_radius=4)
            inner = speaker_rect.inflate(-10, -8)
            pygame.draw.rect(surface, (90, 90, 100), inner, border_radius=3)
            pygame.draw.circle(surface, (140, 140, 150), inner.midtop, 6)
            pygame.draw.circle(surface, (210, 210, 220), (inner.centerx, inner.centery + 4), 10)
            pygame.draw.circle(surface, (120, 120, 132), (inner.centerx - 12, inner.centery - 6), 6)
            pygame.draw.circle(surface, (80, 80, 90), (inner.centerx + 12, inner.centery + 10), 5)
            beam_mount = pygame.Rect(0, 0, 12, 6)
            beam_mount.midtop = speaker_rect.midtop
            pygame.draw.rect(surface, (200, 80, 80), beam_mount, border_radius=2)
        elif self.form == "large_cameraman":
            head_rect = pygame.Rect(0, 0, 34, 24)
            head_rect.midbottom = base_rect.midtop
            pygame.draw.rect(surface, (38, 38, 44), head_rect, border_radius=3)
            lens_rect = pygame.Rect(0, 0, 22, 12)
            lens_rect.midleft = head_rect.midleft
            pygame.draw.rect(surface, (20, 24, 28), lens_rect, border_radius=2)
            rim_rect = lens_rect.inflate(-8, -4)
            pygame.draw.rect(surface, (130, 180, 220), rim_rect, border_radius=2)
            handle_rect = pygame.Rect(0, 0, 8, 20)
            handle_rect.midright = head_rect.midright
            pygame.draw.rect(surface, (22, 26, 30), handle_rect, border_radius=2)
            beam_mount = pygame.Rect(0, 0, 14, 6)
            beam_mount.midtop = head_rect.midtop
            pygame.draw.rect(surface, (60, 60, 66), beam_mount, border_radius=2)
        else:
            tv_rect = pygame.Rect(0, 0, 34, 26)
            tv_rect.midbottom = base_rect.midtop
            screen_rect = tv_rect.inflate(-8, -10)
            pygame.draw.rect(surface, (26, 26, 28), tv_rect, border_radius=3)
            pygame.draw.rect(surface, (160, 160, 180), screen_rect, border_radius=2)
            pygame.draw.rect(surface, (230, 230, 240), screen_rect.inflate(-6, -6), border_radius=2)
            scan_y = int(screen_rect.centery + math.sin(self.bob_phase * 1.6) * 3)
            pygame.draw.line(surface, (120, 120, 160), (screen_rect.left + 4, scan_y), (screen_rect.right - 4, scan_y), 2)
            antena_center = (tv_rect.centerx, tv_rect.top - 6)
            pygame.draw.line(surface, (200, 200, 210), antena_center, (antena_center[0] - 6, antena_center[1] - 10), 2)
            pygame.draw.line(surface, (200, 200, 210), antena_center, (antena_center[0] + 6, antena_center[1] - 10), 2)
            if self.health <= 1:
                crack_overlay = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
                for x in range(0, screen_rect.width, 4):
                    band_alpha = 80 + (x % 12) * 6
                    color = ((80 + x * 2) % 255, (120 + x * 3) % 255, (200 + x * 5) % 255, min(180, band_alpha))
                    pygame.draw.line(crack_overlay, color, (x, 0), (x, screen_rect.height))
                crack_points = [
                    (screen_rect.width * 0.15, screen_rect.height * 0.2),
                    (screen_rect.width * 0.5, screen_rect.height * 0.35),
                    (screen_rect.width * 0.35, screen_rect.height * 0.7),
                    (screen_rect.width * 0.75, screen_rect.height * 0.55),
                    (screen_rect.width * 0.6, screen_rect.height * 0.15),
                ]
                pygame.draw.lines(crack_overlay, (255, 255, 255, 220), False, crack_points, 2)
                pygame.draw.circle(crack_overlay, (255, 255, 255, 200), crack_points[1], 4, width=1)
                surface.blit(crack_overlay, screen_rect.topleft)


@dataclass
class SkibidiToilet:
    position: pygame.Vector2
    health: int
    speed: float
    label: str = ""
    scale: float = 1.0
    is_saint: bool = False
    is_medium: bool = False
    is_police: bool = False
    angry: bool = False
    wobble_phase: float = 0.0
    wiggle_amp: float = 2.0
    body_color: tuple[int, int, int] = (210, 210, 210)
    rim_color: tuple[int, int, int] = (240, 240, 240)
    eye_color: tuple[int, int, int] = (40, 40, 40)
    score_value: int = 1
    contact_damage: int = ENEMY_DAMAGE
    stun_timer: int = 0
    _label_font: pygame.font.Font | None = None

    def update(self, target: pygame.Vector2, dt: int) -> None:
        if self.stun_timer > 0:
            self.stun_timer = max(0, self.stun_timer - dt)
            self.wobble_phase = (self.wobble_phase + dt * 0.01) % (2 * math.pi)
            return
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

        if self.is_police:
            bar_rect = pygame.Rect(0, 0, int(34 * self.scale), int(8 * self.scale))
            bar_rect.midtop = tank_rect.midtop
            bar_rect.y -= 6
            bar_rect.x -= 2
            pygame.draw.rect(surface, (40, 40, 48), bar_rect, border_radius=3)
            pygame.draw.rect(surface, (220, 60, 70), bar_rect.inflate(-18, -2), border_radius=3)
            pygame.draw.rect(surface, (80, 140, 255), bar_rect.inflate(-6, -2), border_radius=3)
            hat_rect = pygame.Rect(0, 0, int(32 * self.scale), int(12 * self.scale))
            hat_rect.midbottom = (base_rect.centerx, tank_rect.top - 8)
            hat_rect.y += wobble_offset
            pygame.draw.rect(surface, (18, 18, 28), hat_rect, border_radius=3)
            brim = pygame.Rect(hat_rect.left - 6, hat_rect.bottom - 2, hat_rect.width + 12, 4)
            pygame.draw.rect(surface, (26, 26, 38), brim, border_radius=2)
            badge_center = (hat_rect.centerx, hat_rect.centery)
            pygame.draw.circle(surface, (180, 180, 120), badge_center, max(2, int(3 * self.scale)))

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

        if self.is_saint:
            bar_width = 120
            bar_height = 12
            bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
            bar_rect.midbottom = (base_rect.centerx, base_rect.top - 6)
            pygame.draw.rect(surface, (40, 20, 20), bar_rect.inflate(4, 4), border_radius=4)
            health_ratio = max(0, min(1, self.health / 14))
            fill_rect = bar_rect.copy()
            fill_rect.width = int(bar_width * health_ratio)
            pygame.draw.rect(surface, (220, 120, 120), fill_rect, border_radius=3)
            pygame.draw.rect(surface, (255, 220, 180), bar_rect, width=2, border_radius=4)

        if self.label:
            if SkibidiToilet._label_font is None:
                SkibidiToilet._label_font = pygame.font.SysFont("arial", 14)
            label_surface = SkibidiToilet._label_font.render(self.label, True, (20, 20, 40))
            label_rect = label_surface.get_rect(center=(base_rect.centerx, base_rect.top - 12))
            surface.blit(label_surface, label_rect)


class CityMap:
    def __init__(self, mode: str = "street") -> None:
        self.buildings: List[pygame.Rect] = []
        self.street_lines: List[int] = [SCREEN_HEIGHT - 160, SCREEN_HEIGHT - 110]
        self.mode = mode
        start_x = 0
        for _ in range(16):
            if self.mode == "center":
                w, h = random.randint(120, 220), random.randint(180, 260)
                y_offset = random.randint(80, 140)
            else:
                w, h = random.randint(80, 200), random.randint(80, 180)
                y_offset = random.randint(120, 200)
            x = start_x + random.randint(30, 120)
            start_x = x + w + random.randint(40, 120)
            y = SCREEN_HEIGHT - h - y_offset
            self.buildings.append(pygame.Rect(x, y, w, h))

    def update(self, dt: int) -> None:
        dx = (CITY_SCROLL_SPEED_CENTER if self.mode == "center" else CITY_SCROLL_SPEED) * (dt / 1000.0)
        for building in list(self.buildings):
            building.x -= dx
            if building.right < -80:
                self.buildings.remove(building)
                if self.mode == "center":
                    w, h = random.randint(120, 220), random.randint(180, 260)
                    y_offset = random.randint(80, 140)
                else:
                    w, h = random.randint(80, 200), random.randint(80, 180)
                    y_offset = random.randint(120, 200)
                x = SCREEN_WIDTH + random.randint(40, 180)
                y = SCREEN_HEIGHT - h - y_offset
                self.buildings.append(pygame.Rect(x, y, w, h))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((26, 30, 40) if self.mode == "center" else (30, 34, 42))
        # Grid floor to hint the cameraman is moving right across the city.
        for x in range(-CITY_GRID_SIZE, SCREEN_WIDTH + CITY_GRID_SIZE, CITY_GRID_SIZE):
            pygame.draw.line(surface, (48, 54, 63), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CITY_GRID_SIZE):
            pygame.draw.line(surface, (48, 54, 63), (0, y), (SCREEN_WIDTH, y))

        for building in self.buildings:
            pygame.draw.rect(surface, (70, 82, 102) if self.mode == "center" else (58, 68, 83), building)
            window_palette = (
                [(255, 220, 120), (140, 180, 230), (90, 110, 160)]
                if self.mode == "center"
                else [(255, 200, 40), (120, 150, 190), (70, 90, 120)]
            )
            window_color = random.choice(window_palette)
            for _ in range(random.randint(3, 7)):
                size = random.randint(6, 10)
                px = random.randint(building.left + 6, building.right - 6)
                py = random.randint(building.top + 6, building.bottom - 6)
                pygame.draw.rect(surface, window_color, pygame.Rect(px, py, size, size))

        # Street lane markers to sell the walking-forward direction.
        street_y = SCREEN_HEIGHT - (110 if self.mode == "center" else 80)
        pygame.draw.rect(surface, (20, 22, 28) if self.mode == "center" else (26, 28, 34), pygame.Rect(0, street_y, SCREEN_WIDTH, SCREEN_HEIGHT - street_y))
        dash_step = 60 if self.mode == "center" else 80
        for i in range(0, SCREEN_WIDTH, dash_step):
            pygame.draw.rect(surface, (255, 215, 120), pygame.Rect(i + 10, street_y + 38, 40, 6), border_radius=3)


@dataclass
class Ally:
    position: pygame.Vector2
    health: int = FORM_MAX_HEALTH["cameraman"]
    flash_cooldown_timer: int = 0

    def update(self, dt: int, enemies: List["SkibidiToilet"]) -> None:
        self.flash_cooldown_timer = max(0, self.flash_cooldown_timer - dt)
        if self.flash_cooldown_timer > 0:
            return
        # Auto flash toward enemies ahead
        ahead = [e for e in enemies if e.position.x > self.position.x and e.position.distance_to(self.position) < 260]
        if ahead:
            self.flash_cooldown_timer = ALLY_FLASH_COOLDOWN
            for enemy in ahead:
                enemy.take_damage(FLASH_DAMAGE_CAMERAMAN)
                enemy.stun_timer = max(enemy.stun_timer, 320)

    def draw(self, surface: pygame.Surface) -> None:
        torso = pygame.Rect(0, 0, 36, 48)
        torso.midbottom = (self.position.x, self.position.y)
        pygame.draw.rect(surface, (28, 110, 200), torso, border_radius=6)
        head = pygame.Rect(0, 0, 26, 20)
        head.midbottom = torso.midtop
        pygame.draw.rect(surface, (220, 230, 240), head, border_radius=3)
        lens = pygame.Rect(0, 0, 12, 8)
        lens.midleft = head.midleft
        pygame.draw.rect(surface, (20, 20, 26), lens, border_radius=2)
        bar_width = 36
        bar_height = 8
        bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
        bar_rect.midbottom = (torso.centerx, torso.top - 6)
        pygame.draw.rect(surface, (40, 20, 20), bar_rect.inflate(4, 4), border_radius=3)
        health_ratio = max(0, min(1, self.health / FORM_MAX_HEALTH["cameraman"]))
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_width * health_ratio)
        pygame.draw.rect(surface, (200, 80, 80), fill_rect, border_radius=3)
        pygame.draw.rect(surface, (255, 220, 180), bar_rect, width=2, border_radius=3)


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Skibidi City Showdown")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)

        self.state = "menu"
        self.start_button = pygame.Rect(0, 0, 220, 72)
        self.start_button.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        self.intermission_timer = 0

        self.city = CityMap()
        self.player = CameraMan(pygame.Vector2(SCREEN_WIDTH // 2, PLAYER_GROUND_Y), pygame.Vector2(1, 0))
        self.enemies: List[SkibidiToilet] = []
        self.allies: List[Ally] = []
        self.last_spawn = 0
        self.score = 0
        self.flash_active_time = 0
        self.soundwave_active_time = 0
        self.stun_active_time = 0
        self.stab_active_time = 0
        self.kick_active_time = 0
        self.flash_beam_rect: pygame.Rect | None = None
        self.game_over = False
        self.wave = 1
        self.wave_goal = 8
        self.wave_kills = 0
        self.saint_spawned = False
        self.pending_wave: int | None = None

    def reset(self) -> None:
        self.city = CityMap()
        self.player = CameraMan(pygame.Vector2(SCREEN_WIDTH // 2, PLAYER_GROUND_Y), pygame.Vector2(1, 0))
        self.enemies = []
        self.allies = []
        self.last_spawn = 0
        self.score = 0
        self.flash_active_time = 0
        self.soundwave_active_time = 0
        self.stun_active_time = 0
        self.stab_active_time = 0
        self.kick_active_time = 0
        self.flash_beam_rect = None
        self.game_over = False
        self.state = "playing"
        self.intermission_timer = 0
        self.pending_wave = None
        self.start_wave(1)

    def goal_for_wave(self, wave: int) -> int:
        if wave > MAX_WAVE:
            return 0
        if wave == 5:
            return 1
        return min(16, 8 + (wave - 1) * 2)

    def start_wave(self, wave: int) -> None:
        self.wave = wave
        self.wave_goal = self.goal_for_wave(wave)
        self.wave_kills = 0
        self.saint_spawned = False
        self.enemies = []
        self.last_spawn = 0
        self.pending_wave = None
        self.state = "playing"
        if self.wave == 7:
            self.city = CityMap(mode="center")
            self.allies = [
                Ally(pygame.Vector2(self.player.position.x - 90, PLAYER_GROUND_Y)),
                Ally(pygame.Vector2(self.player.position.x + 90, PLAYER_GROUND_Y)),
            ]

    def current_flash_beam_rect(self) -> pygame.Rect:
        direction = 1 if self.player.facing.x >= 0 else -1
        length = FLASH_BEAM_LENGTH
        if self.player.form == "speakerman":
            length += 30
        if self.player.form == "large_speakerman":
            length += 70
        if self.player.form == "large_cameraman":
            length += 50
        start_x = self.player.position.x + (20 * direction)
        rect = pygame.Rect(0, 0, length, FLASH_BEAM_WIDTH)
        if direction < 0:
            rect.right = start_x
        else:
            rect.left = start_x
        rect.centery = self.player.position.y - 4
        return rect

    def spawn_enemy(self) -> None:
        if self.wave == 5:
            if not self.saint_spawned:
                pos = pygame.Vector2(SCREEN_WIDTH + 40, PLAYER_GROUND_Y + random.uniform(-6, 6))
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
                    score_value=5,
                )
                self.enemies.append(saint)
                self.saint_spawned = True
            return

        base_health = 2 + max(0, self.wave - 1) * 0.2
        base_speed = 1.2 + max(0, self.wave - 1) * 0.08
        pos = pygame.Vector2(SCREEN_WIDTH + 40, PLAYER_GROUND_Y + random.uniform(-6, 6))
        wiggle_amp = random.uniform(2.0, 3.5)

        health_variation = random.choice([0, 0, 1])
        speed_variation = random.uniform(-0.05, 0.25)
        is_large = self.wave >= 8 and random.random() < 0.38
        is_police = (not is_large) and self.wave >= 6 and random.random() < 0.32
        is_medium = not (is_police or is_large) and self.wave >= 2 and random.random() < 0.35
        label = "Police" if is_police else ("Medium" if is_medium else ("Large" if is_large else ""))
        contact_damage = 3 if is_large else (POLICE_DAMAGE if is_police else ENEMY_DAMAGE)
        enemy = SkibidiToilet(
            position=pos,
            health=int(
                base_health
                + health_variation
                + (2 if is_medium else 0)
                + (6 if is_large else 0)
                + (0 if is_police else 0)
            ),
            speed=base_speed + speed_variation - (0.05 if is_medium else 0) - (0.02 if is_police else 0) - (0.4 if is_large else 0),
            wiggle_amp=wiggle_amp + (0.4 if is_medium else 0) - (0.2 if is_large else 0),
            body_color=
                (118, 118, 128)
                if is_police
                else (195, 195, 205) if is_large else random.choice([(214, 214, 220), (222, 228, 234), (210, 216, 224)]),
            rim_color=(175, 175, 182) if is_police else ((240, 240, 245) if is_large else random.choice([(240, 240, 245), (236, 240, 242)])),
            label=label,
            scale=1.1 if is_police else (1.25 if is_medium else (1.6 if is_large else 1.0)),
            is_medium=is_medium,
            is_police=is_police,
            score_value=2 if is_medium else (4 if is_large else 1),
            contact_damage=contact_damage,
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
        self.stun_active_time = max(0, self.stun_active_time - dt)
        self.stab_active_time = max(0, self.stab_active_time - dt)
        self.kick_active_time = max(0, self.kick_active_time - dt)
        if self.flash_active_time <= 0 and self.stun_active_time <= 0:
            self.flash_beam_rect = None
        self.player.update(dt)

        if self.state == "menu" or self.state == "game_over":
            return

        if self.state == "intermission":
            self.intermission_timer = max(0, self.intermission_timer - dt)
            if self.intermission_timer <= 0 and self.pending_wave:
                self.start_wave(self.pending_wave)
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        if keys[pygame.K_u] and self.player.form == "cameraman" and self.score >= SPEAKERMAN_SCORE_COST:
            self.score -= SPEAKERMAN_SCORE_COST
            self.player.upgrade_to_speakerman()

        if keys[pygame.K_u] and self.player.form == "speakerman" and self.score >= TVMAN_SCORE_COST:
            self.score -= TVMAN_SCORE_COST
            self.player.upgrade_to_tvman()

        if keys[pygame.K_u] and self.player.form == "tvman":
            if self.score >= LARGE_SPEAKER_SCORE_COST:
                self.score -= LARGE_SPEAKER_SCORE_COST
                self.player.upgrade_to_large_speakerman()
            elif self.score >= LARGE_CAM_SCORE_COST:
                self.score -= LARGE_CAM_SCORE_COST
                self.player.upgrade_to_large_cameraman()

        if keys[pygame.K_i] and self.player.form == "tvman" and self.score >= LARGE_SPEAKER_SCORE_COST:
            self.score -= LARGE_SPEAKER_SCORE_COST
            self.player.upgrade_to_large_speakerman()

        if keys[pygame.K_u] and self.player.form == "large_cameraman" and self.score >= LARGE_SPEAKER_SCORE_COST:
            self.score -= LARGE_SPEAKER_SCORE_COST
            self.player.upgrade_to_large_speakerman()

        if keys[pygame.K_SPACE] and self.player.can_punch():
            self.player.start_punch()
            hitbox = self.punch_hitbox()
            for enemy in list(self.enemies):
                if hitbox.collidepoint(enemy.position):
                    if self.player.form == "tvman":
                        damage = PUNCH_DAMAGE_TVMAN
                    elif self.player.form == "speakerman":
                        damage = PUNCH_DAMAGE_SPEAKERMAN
                    elif self.player.form == "large_speakerman":
                        damage = PUNCH_DAMAGE_LARGE_SPEAK
                    elif self.player.form == "large_cameraman":
                        damage = PUNCH_DAMAGE_LARGE
                    else:
                        damage = PUNCH_DAMAGE_CAMERAMAN
                    enemy.take_damage(damage)
                    offset = (enemy.position - self.player.position)
                    if offset.length_squared() > 0:
                        knock = 16 if self.player.form in {"speakerman", "tvman"} else 12
                        enemy.position += offset.normalize() * knock
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += enemy.score_value
                        self.wave_kills += 1

        if keys[pygame.K_f] and self.player.can_flash():
            self.player.start_flash()
            beam_rect = self.current_flash_beam_rect()
            self.flash_beam_rect = beam_rect
            if self.player.form == "tvman":
                self.stun_active_time = 260
                for enemy in list(self.enemies):
                    if beam_rect.collidepoint(enemy.position.x, enemy.position.y):
                        enemy.stun_timer = STUN_DURATION
            else:
                self.flash_active_time = 260
                for enemy in list(self.enemies):
                    if beam_rect.collidepoint(enemy.position.x, enemy.position.y):
                        if self.player.form == "speakerman":
                            flash_damage = FLASH_DAMAGE_SPEAKERMAN
                        elif self.player.form == "large_speakerman":
                            flash_damage = FLASH_DAMAGE_LARGE_SPEAK
                        elif self.player.form == "large_cameraman":
                            flash_damage = FLASH_DAMAGE_LARGE
                        else:
                            flash_damage = FLASH_DAMAGE_CAMERAMAN
                        enemy.take_damage(flash_damage)
                        push = (enemy.position - self.player.position)
                        if push.length_squared() > 0:
                            push_strength = 28 if self.player.form == "large_speakerman" else 20
                            enemy.position += push.normalize() * push_strength
                        if enemy.is_dead():
                            self.enemies.remove(enemy)
                            self.score += enemy.score_value
                            self.wave_kills += 1

        if self.player.form == "speakerman" and keys[pygame.K_x] and self.player.can_soundwave():
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
                        self.score += enemy.score_value
                        self.wave_kills += 1

        if self.player.form == "large_speakerman" and keys[pygame.K_x] and self.player.can_kick():
            self.player.start_kick()
            self.kick_active_time = 180
            direction = self.player.facing if self.player.facing.length_squared() > 0 else pygame.Vector2(1, 0)
            direction = direction.normalize()
            kick_origin = self.player.position + direction * 24
            kick_rect = pygame.Rect(0, 0, KICK_RANGE, 40)
            kick_rect.center = (kick_origin.x + direction.x * (KICK_RANGE // 2), kick_origin.y - 6)
            for enemy in list(self.enemies):
                if kick_rect.collidepoint(enemy.position.x, enemy.position.y):
                    enemy.take_damage(KICK_DAMAGE)
                    enemy.position += direction * 34
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += enemy.score_value
                        self.wave_kills += 1

        if self.player.form == "tvman" and keys[pygame.K_x] and self.player.can_stab():
            self.player.start_stab()
            self.stab_active_time = 150
            direction = self.player.facing if self.player.facing.length_squared() > 0 else pygame.Vector2(1, 0)
            stab_origin = self.player.position + direction.normalize() * 22
            stab_rect = pygame.Rect(0, 0, STAB_RANGE, 32)
            stab_rect.center = (stab_origin.x + direction.x * (STAB_RANGE // 2), stab_origin.y)
            for enemy in list(self.enemies):
                if stab_rect.collidepoint(enemy.position.x, enemy.position.y):
                    enemy.take_damage(STAB_DAMAGE)
                    enemy.stun_timer = max(enemy.stun_timer, 240)
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += enemy.score_value
                        self.wave_kills += 1

        for ally in list(self.allies):
            ally.update(dt, self.enemies)
            if ally.health <= 0:
                self.allies.remove(ally)

        for enemy in list(self.enemies):
            enemy.update(self.player.position, dt)
            if enemy.stun_timer <= 0 and enemy.position.distance_to(self.player.position) <= ENEMY_CONTACT_DISTANCE:
                self.player.take_damage(enemy.contact_damage)
                away = (enemy.position - self.player.position)
                if away.length_squared() > 0:
                    enemy.position += away.normalize() * 16
            for ally in list(self.allies):
                if enemy.stun_timer <= 0 and enemy.position.distance_to(ally.position) <= ENEMY_CONTACT_DISTANCE:
                    ally.health = max(0, ally.health - enemy.contact_damage)
                    repel = (enemy.position - ally.position)
                    if repel.length_squared() > 0:
                        enemy.position += repel.normalize() * 10

        if self.wave_kills >= self.wave_goal and not self.enemies and not self.pending_wave:
            if self.wave >= MAX_WAVE:
                self.game_over = True
                self.state = "victory"
            else:
                self.pending_wave = self.wave + 1
                self.state = "intermission"
                self.intermission_timer = INTERMISSION_TIME if self.wave < 6 else INTERMISSION_TIME + 800

        if self.state == "playing":
            self.last_spawn += dt
            if self.wave == 5:
                if not self.enemies and not self.saint_spawned:
                    self.spawn_enemy()
                    self.last_spawn = 0
            elif self.wave_kills < self.wave_goal:
                spawn_delay = max(
                    MIN_ENEMY_SPAWN_TIME,
                    (ENEMY_SPAWN_TIME - self.wave * 80) - self.score * 20,
                )
                if self.last_spawn >= spawn_delay:
                    self.spawn_enemy()
                    self.last_spawn = 0

        if self.player.health <= 0:
            self.game_over = True
            self.state = "game_over"

    def draw_ui(self) -> None:
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        form_label = (
            "Cameraman"
            if self.player.form == "cameraman"
            else "Speakerman"
            if self.player.form == "speakerman"
            else "TV Man"
            if self.player.form == "tvman"
            else "Large Speakerman"
            if self.player.form == "large_speakerman"
            else "Large Cameraman"
        )
        form = self.font.render(f"Form: {form_label}", True, (190, 255, 210))
        cooldown = max(0, math.ceil(self.player.punch_cooldown_timer / 100))
        cd_text = self.font.render(f"Punch: {cooldown/10:.1f}s", True, (210, 210, 210))
        flash_cd = max(0, math.ceil(self.player.flash_cooldown_timer / 100))
        if self.player.form == "tvman":
            flash_name = "Stun Screen"
        elif self.player.form == "large_speakerman":
            flash_name = "Ultra Blast"
        else:
            flash_name = "Flash"
        flash_text = self.font.render(f"{flash_name}: {flash_cd/10:.1f}s", True, (190, 235, 255))
        sound_cd = max(0, math.ceil(self.player.soundwave_cooldown_timer / 100)) if self.player.form in {"speakerman", "large_speakerman"} else 0
        stab_cd = max(0, math.ceil(self.player.stab_cooldown_timer / 100)) if self.player.form == "tvman" else 0
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
        if self.player.form == "large_speakerman":
            sound_label = self.font.render(f"Kick: {sound_cd/10:.1f}s", True, (255, 200, 180))
            self.screen.blit(sound_label, (12, wave_y))
            wave_y += 24
        if self.player.form == "tvman":
            stab_label = self.font.render(f"Stab: {stab_cd/10:.1f}s", True, (255, 205, 170))
            self.screen.blit(stab_label, (12, wave_y))
            wave_y += 24
        self.screen.blit(wave_text, (12, wave_y))

        max_health = FORM_MAX_HEALTH[self.player.form]
        for i in range(max_health):
            color = (255, 90, 90) if i < self.player.health else (70, 60, 60)
            pygame.draw.rect(self.screen, color, pygame.Rect(12 + i * 26, wave_y + 28, 20, 16), border_radius=4)

        instructions = ["Move: A/D or Arrows", "Punch: Space"]
        if self.player.form == "cameraman":
            instructions += [
                "F: Beam flash",
                f"U ({SPEAKERMAN_SCORE_COST} pts): Speakerman",
            ]
        elif self.player.form == "speakerman":
            instructions += [
                "F: Beam flash",
                "X: Soundwave cone",
                f"U ({TVMAN_SCORE_COST} pts): TV Man",
            ]
        elif self.player.form == "tvman":
            instructions += [
                "F: Stun screen",
                "X: Stab",
                f"U ({LARGE_CAM_SCORE_COST} pts): Large Cam",
                f"I ({LARGE_SPEAKER_SCORE_COST} pts): Large Speakerman",
            ]
        elif self.player.form == "large_cameraman":
            instructions += [
                "F: Heavy beam",
            ]
        elif self.player.form == "large_speakerman":
            instructions += [
                "F: Ultra sound blast",
                "X: Kick strike",
            ]

        instructions += [
            "Clear toilets to start intermission",
            "Wave 5: Saint boss only",
            "Wave 6: Last street wave (Police)",
            "Wave 7-8: Center city showdown",
            "Wave 8: Huge Skibidi appears",
        ]
        for i, line in enumerate(instructions):
            label = self.font.render(line, True, (200, 215, 230))
            self.screen.blit(label, (12, SCREEN_HEIGHT - 24 * (len(instructions) - i)))

    def draw_menu(self) -> None:
        self.city.draw(self.screen)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        title = self.font.render("Skibidi City Showdown", True, (255, 235, 180))
        subtitle = self.font.render("Press Start to defend the streets", True, (210, 220, 235))
        pygame.draw.rect(self.screen, (40, 160, 240), self.start_button, border_radius=12)
        start_label = self.font.render("Start", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
        self.screen.blit(start_label, start_label.get_rect(center=self.start_button.center))

        updates = [
            "Updates:",
            "- Intermissions between waves",
            "- Wave 5 is the Saint showdown",
            "- Start from new main menu",
            "- Wave 6 brings Police Toilets",
            "- Center map unlocks after wave 6",
            "- TV: U for Large upgrades (35 > Speak)",
            "- Allies await downtown",
        ]
        for i, line in enumerate(updates):
            label = self.font.render(line, True, (200, 215, 230))
            self.screen.blit(label, (SCREEN_WIDTH - 320, SCREEN_HEIGHT - 24 * (len(updates) - i)))

    def draw(self, punch_active: bool) -> None:
        if self.state == "menu":
            self.draw_menu()
            pygame.display.flip()
            return

        self.city.draw(self.screen)
        self.player.draw(self.screen)

        for ally in self.allies:
            ally.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if punch_active:
            hitbox = self.punch_hitbox()
            pygame.draw.rect(self.screen, (255, 100, 100), hitbox, width=2)

        if (self.flash_active_time > 0 or self.stun_active_time > 0) and self.flash_beam_rect:
            rect = self.flash_beam_rect
            active_time = self.flash_active_time if self.flash_active_time > 0 else self.stun_active_time
            intensity = active_time / 260
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            primary_color = (255, 200, 120) if self.player.form != "tvman" else (150, 130, 255)
            fringe_color = (80, 170, 255) if self.player.form != "tvman" else (220, 180, 255)
            for i in range(rect.width):
                t = i / rect.width
                alpha = int(180 * intensity * (1 - t * 0.65))
                edge_alpha = int(alpha * 0.6)
                pygame.draw.line(overlay, (*primary_color, alpha), (i, 0), (i, rect.height))
                if i % 16 == 0:
                    pygame.draw.line(overlay, (*fringe_color, edge_alpha), (i, 0), (i, rect.height))
            mid_x = rect.width // 3 if self.player.facing.x < 0 else rect.width // 3 * 2
            pygame.draw.line(overlay, (*fringe_color, int(220 * intensity)), (mid_x, 0), (mid_x, rect.height), 3)
            self.screen.blit(overlay, rect.topleft)

        if self.soundwave_active_time > 0:
            direction = 1 if self.player.facing.x >= 0 else -1
            start_x = self.player.position.x + (16 * direction)
            rect = pygame.Rect(0, 0, SOUNDWAVE_RANGE, SOUNDWAVE_HEIGHT)
            if direction < 0:
                rect.right = start_x
            else:
                rect.left = start_x
            alpha = int(180 * (self.soundwave_active_time / 240))
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((150, 110, 255, alpha))
            self.screen.blit(overlay, rect.topleft)

        if self.kick_active_time > 0:
            direction = self.player.facing if self.player.facing.length_squared() > 0 else pygame.Vector2(1, 0)
            direction = direction.normalize()
            kick_origin = self.player.position + direction * 24
            rect = pygame.Rect(0, 0, KICK_RANGE, 40)
            rect.center = (kick_origin.x + direction.x * (KICK_RANGE // 2), kick_origin.y - 6)
            alpha = int(180 * (self.kick_active_time / 180))
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((255, 140, 100, alpha))
            self.screen.blit(overlay, rect.topleft)

        if self.stab_active_time > 0:
            direction = self.player.facing if self.player.facing.length_squared() > 0 else pygame.Vector2(1, 0)
            stab_origin = self.player.position + direction.normalize() * 22
            stab_rect = pygame.Rect(0, 0, STAB_RANGE, 32)
            stab_rect.center = (stab_origin.x + direction.x * (STAB_RANGE // 2), stab_origin.y)
            pygame.draw.rect(self.screen, (255, 200, 120), stab_rect, width=2)

        self.draw_ui()

        if self.state == "intermission":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            self.screen.blit(overlay, (0, 0))
            seconds = max(0, math.ceil(self.intermission_timer / 100) / 10)
            title = self.font.render("Intermission", True, (255, 230, 180))
            timer_text = self.font.render(f"Next wave in {seconds:.1f}s", True, (210, 220, 255))
            note_text = "City center ahead..." if self.wave >= 6 else "All toilets cleared!"
            note = self.font.render(note_text, True, (200, 255, 200))
            center_x = SCREEN_WIDTH // 2
            self.screen.blit(title, title.get_rect(center=(center_x, SCREEN_HEIGHT // 2 - 20)))
            self.screen.blit(timer_text, timer_text.get_rect(center=(center_x, SCREEN_HEIGHT // 2 + 8)))
            self.screen.blit(note, note.get_rect(center=(center_x, SCREEN_HEIGHT // 2 + 36)))

        if self.game_over and self.state == "victory":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 30, 40, 180))
            self.screen.blit(overlay, (0, 0))
            title = self.font.render("City Secured!", True, (180, 255, 210))
            prompt = self.font.render("Press R to restart", True, (230, 230, 230))
            score_text = self.font.render(f"Final score: {self.score}", True, (200, 220, 255))
            wave_text = self.font.render("Center streets are safe.", True, (200, 255, 200))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
            self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            self.screen.blit(wave_text, wave_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 26)))
            self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 56)))

        if self.game_over and self.state == "game_over":
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
                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and self.start_button.collidepoint(event.pos):
                        self.reset()
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                    self.reset()

            punch_active = (
                self.state == "playing" and pygame.key.get_pressed()[pygame.K_SPACE] and not self.player.can_punch()
            )
            self.update(dt)
            self.draw(punch_active)

        pygame.quit()
        sys.exit()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
