import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 3: Memory & Internal State")

clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont("consolas", 16)

# ==========================
# Vehicle with Memory (Chapter 3)
# ==========================
class VehicleThree:
    def __init__(self, x, y, color, cross_wired=False):
        self.x = x
        self.y = y
        self.heading = random.uniform(0, 2 * math.pi)

        self.color = color
        self.cross_wired = cross_wired  # False = Fear, True = Aggression

        self.sensor_offset = 25
        self.max_speed = 120

        # -------- Chapter 3 addition --------
        self.memory = 0.5      # internal state (0–1)
        self.memory_decay = 0.995
        self.memory_gain = 0.0008
        # ------------------------------------

        self.speed = 0

    def update(self, light_positions):
        # Sensor positions
        left_sensor = (
            self.x + math.cos(self.heading + math.pi / 6) * self.sensor_offset,
            self.y + math.sin(self.heading + math.pi / 6) * self.sensor_offset
        )
        right_sensor = (
            self.x + math.cos(self.heading - math.pi / 6) * self.sensor_offset,
            self.y + math.sin(self.heading - math.pi / 6) * self.sensor_offset
        )

        # Light intensities
        left_intensity, right_intensity = 0, 0
        for lx, ly in light_positions:
            left_intensity += 8000 / (math.dist(left_sensor, (lx, ly))**2 + 1)
            right_intensity += 8000 / (math.dist(right_sensor, (lx, ly))**2 + 1)

        total_light = left_intensity + right_intensity

        # -------- Memory update (Chapter 3) --------
        self.memory += total_light * self.memory_gain
        self.memory *= self.memory_decay
        self.memory = max(0.1, min(self.memory, 2.0))
        # ------------------------------------------

        # Motor wiring
        if self.cross_wired:
            left_motor = right_intensity
            right_motor = left_intensity
        else:
            left_motor = left_intensity
            right_motor = right_intensity

        # Memory affects turning strength
        turn_rate = (right_motor - left_motor) * 0.006 * self.memory
        self.heading += turn_rate

        # Memory affects speed
        base_speed = 1.5
        self.speed = min((left_motor + right_motor) * 0.04 * self.memory + base_speed, self.max_speed)

        self.x += math.cos(self.heading) * self.speed
        self.y += math.sin(self.heading) * self.speed

        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        body = pygame.Surface((120, 45), pygame.SRCALPHA)
        pygame.draw.rect(body, self.color, (0, 0, 120, 45))
        pygame.draw.rect(body, (0, 0, 0), (0, 0, 120, 45), 3)

        pygame.draw.circle(body, (255, 0, 0), (80, 10), 5)
        pygame.draw.circle(body, (0, 255, 0), (80, 35), 5)

        rotated = pygame.transform.rotate(body, -math.degrees(self.heading))
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

        # Debug (shows memory = internal state)
        surface.blit(
            font.render(f"Memory={round(self.memory, 2)}", True, (0, 0, 0)),
            (int(self.x - 40), int(self.y - 40))
        )

# ==========================
# Light
# ==========================
class Light:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius

    def pos(self):
        return (self.x, self.y)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

# ==========================
# Setup
# ==========================
lights = [
    Light(WIDTH // 2, HEIGHT // 3),
    Light(WIDTH // 2, HEIGHT * 2 // 3),
]

vehicle_fear = VehicleThree(350, 300, (0, 120, 255), cross_wired=False)
vehicle_aggr = VehicleThree(550, 300, (255, 120, 0), cross_wired=True)

# ==========================
# Main Loop
# ==========================
running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            lights[0].x, lights[0].y = event.pos

    for light in lights:
        light.draw(screen)

    positions = [l.pos() for l in lights]
    vehicle_fear.update(positions)
    vehicle_aggr.update(positions)

    vehicle_fear.draw(screen)
    vehicle_aggr.draw(screen)

    screen.blit(font.render("Vehicle 3a: Fear + Memory", True, (0, 0, 150)), (20, 20))
    screen.blit(font.render("Vehicle 3b: Aggression + Memory", True, (150, 0, 0)), (20, 40))
    screen.blit(font.render("Click to move light", True, (0, 0, 0)), (20, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
