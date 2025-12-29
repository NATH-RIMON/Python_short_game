import pygame
import math
import random

pygame.init()


WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle with Movable Lights")


clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont("consolas", 16)



class VehicleTwo:
    def __init__(self, x, y, radius=20, heading=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading if heading else random.uniform(0, 2 * math.pi)
        self.speed = 2
        self.max_speed = 6
        self.turn_speed = 0.05
        self.accelerating = False
        self.accel_timer = 0
        self.turn_timer = 0
        self.vx = math.cos(self.heading) * self.speed
        self.vy = math.sin(self.heading) * self.speed

    def _random_turn(self):
        # Make small random turns occasionally
        self.turn_timer -= 1
        if self.turn_timer <= 0:
            self.heading += random.uniform(-0.5, 0.5)
            self.turn_timer = random.randint(30, 120)

    def update(self, light_positions):
        # Random direction changes
        self._random_turn()

        # Handle acceleration boost
        if self.accelerating:
            self.accel_timer -= 1
            if self.accel_timer <= 0:
                self.accelerating = False
            current_speed = self.max_speed
        else:
            current_speed = self.speed

        # Compute velocity
        self.vx = math.cos(self.heading) * current_speed
        self.vy = math.sin(self.heading) * current_speed

        # Predict next position
        next_x = self.x + self.vx
        next_y = self.y + self.vy

        # Avoid lights (don't cross)
        safe = True
        for lx, ly in light_positions:
            dist = math.hypot(next_x - lx, next_y - ly)
            if dist < (self.radius + 20):  # 20 = light radius
                safe = False
                break

        # Update position if safe
        if safe:
            self.x, self.y = next_x, next_y
        else:
            # Turn slightly away from lights
            self.heading += random.uniform(-1, 1)

        # Wrap around screen edges
        self.x %= WIDTH
        self.y %= HEIGHT

    def accelerate(self, duration=60):
        self.accelerating = True
        self.accel_timer = duration

    def draw(self, surface):
        body_width, body_height = 80, 30
        head_width, head_height = 25, 20

        # Create body surface
        body_surf = pygame.Surface((body_width, body_height), pygame.SRCALPHA)

        # Main body (blue)
        pygame.draw.rect(body_surf, (0, 0, 255), (0, 0, body_width, body_height))
        pygame.draw.rect(body_surf, (0, 0, 0), (0, 0, body_width, body_height), 2)

        # Front (green)
        front_x = body_width - head_width - 40
        front_y = (body_height - head_height) // 2
        pygame.draw.rect(body_surf, (0, 255, 0), (front_x, front_y, head_width, head_height))
        pygame.draw.rect(body_surf, (0, 0, 0), (front_x, front_y, head_width, head_height), 2)

        # Nose line
        nose_start = (front_x + head_width, body_height // 2)
        nose_end = (body_width, body_height // 2)
        pygame.draw.line(body_surf, (0, 0, 0), nose_start, nose_end, 3)

        # Backside
        pygame.draw.line(body_surf, (0, 0, 0), (0, 0), (0, body_height), 4)

        # Rotate and draw
        rotated = pygame.transform.rotate(body_surf, -math.degrees(self.heading))
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

        # Debug info
        surface.blit(
            font.render(f"Speed={self.max_speed if self.accelerating else self.speed}", True, (0, 0, 0)),
            (10, 10),
        )
        surface.blit(
            font.render(f"Heading={round(math.degrees(self.heading))}°", True, (0, 0, 0)),
            (10, 30),
        )


# ==========================
# Light class
# ==========================
class Light:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius

    def pos(self):
        return (self.x, self.y)

    def move_light(self, new_pos):
        self.x, self.y = new_pos

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)



vehicle = VehicleTwo(WIDTH // 2, HEIGHT // 2)
lights = [
    Light(WIDTH // 3, HEIGHT // 2),
    Light(WIDTH * 2 // 3, HEIGHT // 2),
]


running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Move the nearest light instead of adding a new one
            mouse_pos = event.pos
            nearest_light = min(lights, key=lambda l: (l.x - mouse_pos[0]) ** 2 + (l.y - mouse_pos[1]) ** 2)
            nearest_light.move_light(mouse_pos)
            vehicle.accelerate(60)  # Boost for 1 second

    # Draw lights
    for light in lights:
        light.draw(screen)

    # Update and draw vehicle
    vehicle.update([l.pos() for l in lights])
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
