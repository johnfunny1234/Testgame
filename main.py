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
PUNCH_RANGE = 50
PUNCH_COOLDOWN = 350  # milliseconds
ENEMY_SPAWN_TIME = 2500  # milliseconds
ENEMY_HEALTH = 3


@dataclass
class CameraMan:
    position: pygame.Vector2
    facing: pygame.Vector2
    health: int = 3
    punch_cooldown_timer: int = 0

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

    def update(self, dt: int) -> None:
        self.punch_cooldown_timer = max(0, self.punch_cooldown_timer - dt)

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

    def update(self, target: pygame.Vector2) -> None:
        direction = target - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.position += direction * self.speed

    def take_damage(self, amount: int) -> None:
        self.health -= amount

    def is_dead(self) -> bool:
        return self.health <= 0

    def draw(self, surface: pygame.Surface) -> None:
        base_rect = pygame.Rect(0, 0, 36, 26)
        base_rect.center = self.position
        pygame.draw.rect(surface, (210, 210, 210), base_rect, border_radius=4)
        bowl_rect = pygame.Rect(0, 0, 26, 12)
        bowl_rect.midtop = base_rect.midtop
        pygame.draw.rect(surface, (240, 240, 240), bowl_rect, border_radius=6)
        pygame.draw.circle(surface, (120, 180, 255), base_rect.center, 6)


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
        self.enemies.append(SkibidiToilet(pos))

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

        for enemy in list(self.enemies):
            enemy.update(self.player.position)

        self.last_spawn += dt
        if self.last_spawn >= ENEMY_SPAWN_TIME:
            self.spawn_enemy()
            self.last_spawn = 0

    def draw_ui(self) -> None:
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        cooldown = max(0, math.ceil(self.player.punch_cooldown_timer / 100))
        cd_text = self.font.render(f"Punch CD: {cooldown/10:.1f}s", True, (210, 210, 210))
        self.screen.blit(text, (12, 12))
        self.screen.blit(cd_text, (12, 36))

        instructions = [
            "Move: WASD or Arrow Keys",
            "Punch: Spacebar",
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

        self.draw_ui()
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            punch_active = pygame.key.get_pressed()[pygame.K_SPACE] and not self.player.can_punch()
            self.update(dt)
            self.draw(punch_active)

        pygame.quit()
        sys.exit()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
