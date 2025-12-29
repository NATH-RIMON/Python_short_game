import pygame
import math
import random
import numpy as np

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicles – Multiple Agents")

clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont("consolas", 16)

# -------------------------
# Vehicle Class
# -------------------------
class Vehicle:
    def __init__(self, x, y, color, behavior):
        self.x = x
        self.y = y
        self.heading = random.uniform(0, 2 * math.pi)
        self.color = color
        self.behavior = behavior
        self.sensor_offset = 20
        self.time = random.random() * 10

        self.max_speed = 6 if behavior != "explorer" else 4
        self.speed = 0

    def sensor_position(self, side):
        angle = math.pi / 4 if side == "left" else -math.pi / 4
        return (
            self.x + math.cos(self.heading + angle) * self.sensor_offset,
            self.y + math.sin(self.heading + angle) * self.sensor_offset
        )

    def sensor_value(self, sx, sy, lights):
        intensity = 0
        for lx, ly in lights:
            d = max(1, math.dist((sx, sy), (lx, ly)))
            intensity += 5000 / (d ** 2)
        return intensity

    def update(self, light_positions):
        self.time += 1 / fps

        lx, ly = self.sensor_position("left")
        rx, ry = self.sensor_position("right")

        left_sensor = self.sensor_value(lx, ly, light_positions)
        right_sensor = self.sensor_value(rx, ry, light_positions)

        if self.behavior == "love":
            threshold = 50
            left_motor = max(0, self.max_speed * (1 - left_sensor / threshold))
            right_motor = max(0, self.max_speed * (1 - right_sensor / threshold))

        elif self.behavior == "explorer":
            total = sum(5000 / max(1, math.dist((self.x, self.y), l)) ** 2
                        for l in light_positions)
            self.speed = self.max_speed / (1 + np.log1p(total))

            target = min(light_positions,
                         key=lambda l: math.dist((self.x, self.y), l))
            angle = math.atan2(target[1] - self.y, target[0] - self.x)
            diff = (angle - self.heading + math.pi) % (2 * math.pi) - math.pi
            self.heading += 0.05 * diff
            left_motor = right_motor = self.speed

        elif self.behavior == "figure8":
            total = sum(5000 / max(1, math.dist((self.x, self.y), l)) ** 2
                        for l in light_positions)
            threshold = 50
            self.speed = self.max_speed * max(0, 1 - total / threshold)

            self.heading += 0.12 * math.sin(2 * math.pi * 0.6 * self.time)

            target = min(light_positions,
                         key=lambda l: math.dist((self.x, self.y), l))
            angle = math.atan2(target[1] - self.y, target[0] - self.x)
            diff = (angle - self.heading + math.pi) % (2 * math.pi) - math.pi
            self.heading += 0.03 * diff

            left_motor = right_motor = self.speed

        rotation = (right_motor - left_motor) * 0.05
        self.heading += rotation

        if self.behavior in ["love", "figure8"]:
            self.speed = (left_motor + right_motor) / 2

        self.x += math.cos(self.heading) * self.speed
        self.y += math.sin(self.heading) * self.speed
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 14)
        hx = self.x + math.cos(self.heading) * 20
        hy = self.y + math.sin(self.heading) * 20
        pygame.draw.line(screen, (0, 0, 0), (self.x, self.y), (hx, hy), 3)

# -------------------------
# Light Class (DRAGGABLE)
# -------------------------
class Light:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.dragging = False

    def pos(self):
        return (self.x, self.y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if math.dist(event.pos, (self.x, self.y)) < self.radius:
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.x, self.y = event.pos

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

# -------------------------
# CREATE MULTIPLE AGENTS
# -------------------------
NUM_EACH = 3

vehicles = []

for _ in range(NUM_EACH):
    vehicles.append(Vehicle(random.randint(100, 800), random.randint(100, 500),
                             (0, 100, 255), "love"))

for _ in range(NUM_EACH):
    vehicles.append(Vehicle(random.randint(100, 800), random.randint(100, 500),
                             (0, 200, 0), "explorer"))

for _ in range(NUM_EACH):
    vehicles.append(Vehicle(random.randint(100, 800), random.randint(100, 500),
                             (200, 0, 200), "figure8"))

lights = [
    Light(200, 150),
    Light(450, 150),
    Light(700, 150),
    Light(300, 450),
    Light(600, 450)
]

# -------------------------
# MAIN LOOP
# -------------------------
running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for l in lights:
            l.handle_event(event)

    for l in lights:
        l.draw()

    light_positions = [l.pos() for l in lights]

    for v in vehicles:
        v.update(light_positions)
        v.draw()

    screen.blit(font.render("Blue: Love | Green: Explorer | Purple: Figure-8", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render("Drag lights with mouse", True, (0, 0, 0)), (10, 30))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
