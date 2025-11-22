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
PUNCH_RANGE = 50
PUNCH_COOLDOWN = 350  # milliseconds
FLASH_COOLDOWN = 6500  # milliseconds
FLASH_RADIUS = 120
ENEMY_SPAWN_TIME = 2400  # milliseconds
MIN_ENEMY_SPAWN_TIME = 700
ENEMY_HEALTH = 3
ENEMY_DAMAGE = 1
ENEMY_CONTACT_DISTANCE = 26
PLAYER_DAMAGE_COOLDOWN = 1200  # milliseconds


@dataclass
class CameraMan:
    position: pygame.Vector2
    facing: pygame.Vector2
    health: int = PLAYER_MAX_HEALTH
    punch_cooldown_timer: int = 0
    flash_cooldown_timer: int = 0
    damage_cooldown_timer: int = 0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            movement.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            movement.y += 1

        if movement.length_squared() > 0:
            movement = movement.normalize() * PLAYER_SPEED
            self.position += movement
            self.position.x = max(20, min(SCREEN_WIDTH - 20, self.position.x))
            self.position.y = max(20, min(SCREEN_HEIGHT - 20, self.position.y))
            self.facing = movement.normalize()

    def can_punch(self) -> bool:
        return self.punch_cooldown_timer <= 0

    def start_punch(self) -> None:
        self.punch_cooldown_timer = PUNCH_COOLDOWN

    def can_flash(self) -> bool:
        return self.flash_cooldown_timer <= 0

    def start_flash(self) -> None:
        self.flash_cooldown_timer = FLASH_COOLDOWN

    def take_damage(self, amount: int) -> None:
        if self.damage_cooldown_timer > 0:
            return
        self.health = max(0, self.health - amount)
        self.damage_cooldown_timer = PLAYER_DAMAGE_COOLDOWN

    def update(self, dt: int) -> None:
        self.punch_cooldown_timer = max(0, self.punch_cooldown_timer - dt)
        self.flash_cooldown_timer = max(0, self.flash_cooldown_timer - dt)
        self.damage_cooldown_timer = max(0, self.damage_cooldown_timer - dt)

    def draw(self, surface: pygame.Surface) -> None:
        body_color = (30, 120, 200)
        head_color = (230, 240, 255)
        base_rect = pygame.Rect(0, 0, 36, 48)
        base_rect.center = self.position
        pygame.draw.rect(surface, body_color, base_rect, border_radius=6)

        head_rect = pygame.Rect(0, 0, 24, 18)
        head_rect.midbottom = base_rect.midtop
        pygame.draw.rect(surface, head_color, head_rect, border_radius=4)

        # Camera lens
        lens_center = (int(head_rect.centerx + self.facing.x * 6), int(head_rect.centery + self.facing.y * 6))
        pygame.draw.circle(surface, (20, 20, 20), lens_center, 4)


@dataclass
class SkibidiToilet:
    position: pygame.Vector2
    health: int = ENEMY_HEALTH
    speed: float = 1.5
    wobble_phase: float = 0.0

    def update(self, target: pygame.Vector2, dt: int) -> None:
        direction = target - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed
        self.wobble_phase = (self.wobble_phase + dt * 0.01) % (2 * math.pi)

    def take_damage(self, amount: int) -> None:
        self.health -= amount

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw(self, surface: pygame.Surface) -> None:
        base_rect = pygame.Rect(0, 0, 36, 26)
        base_rect.center = self.position
        wobble_offset = math.sin(self.wobble_phase) * 2
        base_rect.y += wobble_offset
        pygame.draw.rect(surface, (210, 210, 210), base_rect, border_radius=4)
        bowl_rect = pygame.Rect(0, 0, 26, 12)
        bowl_rect.midtop = base_rect.midtop
        bowl_rect.y += wobble_offset
        pygame.draw.rect(surface, (240, 240, 240), bowl_rect, border_radius=6)
        pygame.draw.circle(surface, (120, 180, 255), (base_rect.centerx, base_rect.centery + wobble_offset), 6)


class CityMap:
    def __init__(self) -> None:
        self.buildings: List[pygame.Rect] = []
        for _ in range(20):
            w, h = random.randint(50, 140), random.randint(50, 120)
            x = random.randint(30, SCREEN_WIDTH - w - 30)
            y = random.randint(30, SCREEN_HEIGHT - h - 30)
            self.buildings.append(pygame.Rect(x, y, w, h))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((35, 40, 48))
        for x in range(0, SCREEN_WIDTH, CITY_GRID_SIZE):
            pygame.draw.line(surface, (48, 54, 63), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CITY_GRID_SIZE):
            pygame.draw.line(surface, (48, 54, 63), (0, y), (SCREEN_WIDTH, y))

        for building in self.buildings:
            pygame.draw.rect(surface, (58, 68, 83), building)
            window_color = random.choice([(255, 200, 40), (120, 150, 190), (70, 90, 120)])
            for _ in range(random.randint(2, 6)):
                size = random.randint(6, 10)
                px = random.randint(building.left + 6, building.right - 6)
                py = random.randint(building.top + 6, building.bottom - 6)
                pygame.draw.rect(surface, window_color, pygame.Rect(px, py, size, size))


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Skibidi City Showdown")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)

        self.city = CityMap()
        self.player = CameraMan(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), pygame.Vector2(0, 1))
        self.enemies: List[SkibidiToilet] = []
        self.last_spawn = 0
        self.score = 0
        self.flash_active_time = 0
        self.game_over = False

    def reset(self) -> None:
        self.city = CityMap()
        self.player = CameraMan(pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), pygame.Vector2(0, 1))
        self.enemies = []
        self.last_spawn = 0
        self.score = 0
        self.flash_active_time = 0
        self.game_over = False

    def spawn_enemy(self) -> None:
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            pos = pygame.Vector2(random.randint(0, SCREEN_WIDTH), -20)
        elif side == "bottom":
            pos = pygame.Vector2(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 20)
        elif side == "left":
            pos = pygame.Vector2(-20, random.randint(0, SCREEN_HEIGHT))
        else:
            pos = pygame.Vector2(SCREEN_WIDTH + 20, random.randint(0, SCREEN_HEIGHT))
        speed_variation = random.uniform(0.0, 0.8)
        self.enemies.append(SkibidiToilet(pos, speed=1.4 + speed_variation))

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
        self.flash_active_time = max(0, self.flash_active_time - dt)
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)

        if keys[pygame.K_SPACE] and self.player.can_punch():
            self.player.start_punch()
            hitbox = self.punch_hitbox()
            for enemy in list(self.enemies):
                if hitbox.collidepoint(enemy.position):
                    enemy.take_damage(1)
                    offset = (enemy.position - self.player.position)
                    if offset.length_squared() > 0:
                        enemy.position += offset.normalize() * 12
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += 1

        if keys[pygame.K_f] and self.player.can_flash():
            self.player.start_flash()
            self.flash_active_time = 250
            for enemy in list(self.enemies):
                if enemy.position.distance_to(self.player.position) <= FLASH_RADIUS:
                    enemy.take_damage(2)
                    push = (enemy.position - self.player.position)
                    if push.length_squared() > 0:
                        enemy.position += push.normalize() * 20
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                        self.score += 1

        for enemy in list(self.enemies):
            enemy.update(self.player.position, dt)
            if enemy.position.distance_to(self.player.position) <= ENEMY_CONTACT_DISTANCE:
                self.player.take_damage(ENEMY_DAMAGE)
                away = (enemy.position - self.player.position)
                if away.length_squared() > 0:
                    enemy.position += away.normalize() * 16

        self.last_spawn += dt
        spawn_delay = max(MIN_ENEMY_SPAWN_TIME, ENEMY_SPAWN_TIME - self.score * 35)
        if self.last_spawn >= spawn_delay:
            self.spawn_enemy()
            self.last_spawn = 0

        if self.player.health <= 0:
            self.game_over = True

    def draw_ui(self) -> None:
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        cooldown = max(0, math.ceil(self.player.punch_cooldown_timer / 100))
        cd_text = self.font.render(f"Punch: {cooldown/10:.1f}s", True, (210, 210, 210))
        flash_cd = max(0, math.ceil(self.player.flash_cooldown_timer / 100))
        flash_text = self.font.render(f"Flash: {flash_cd/10:.1f}s", True, (190, 235, 255))
        self.screen.blit(text, (12, 12))
        self.screen.blit(cd_text, (12, 36))
        self.screen.blit(flash_text, (12, 60))

        for i in range(PLAYER_MAX_HEALTH):
            color = (255, 90, 90) if i < self.player.health else (70, 60, 60)
            pygame.draw.rect(self.screen, color, pygame.Rect(12 + i * 26, 88, 20, 16), border_radius=4)

        instructions = [
            "Move: WASD or Arrow Keys",
            "Punch: Spacebar",
            "Flash Burst: F (AoE + knockback)",
            "Defeat skibidi toilets before they overrun the city!",
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
            radius = int(FLASH_RADIUS * (self.flash_active_time / 250))
            pygame.draw.circle(self.screen, (120, 200, 255), self.player.position, radius, width=2)

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
