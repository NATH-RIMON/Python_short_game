import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicles – Love and Fear Explorer")

clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont("consolas", 16)

# -------------------------
# Vehicle Class
# -------------------------
class Vehicle:
    def __init__(self, x, y, color, explorer=False):
        self.x = x
        self.y = y
        self.heading = random.uniform(0, 2 * math.pi)
        self.color = color
        self.explorer = explorer
        self.max_speed = 4 if not explorer else 2
        self.min_speed = 0 if not explorer else 0.5
        self.sensor_offset = 25
        self.speed = 0
        self.stopped = False

    def update(self, light_positions):
        # Find the nearest light
        closest_light = min(light_positions, key=lambda l: math.dist((self.x, self.y), l))
        dx = closest_light[0] - self.x
        dy = closest_light[1] - self.y
        distance = math.hypot(dx, dy)

        if not self.explorer:
            # Blue Love vehicle: approach lights and stop near them
            left_sensor = (
                self.x + math.cos(self.heading + math.pi/6) * self.sensor_offset,
                self.y + math.sin(self.heading + math.pi/6) * self.sensor_offset
            )
            right_sensor = (
                self.x + math.cos(self.heading - math.pi/6) * self.sensor_offset,
                self.y + math.sin(self.heading - math.pi/6) * self.sensor_offset
            )

            left_intensity = sum(8000 / (math.dist(left_sensor, (lx, ly))**2 + 1) for lx, ly in light_positions)
            right_intensity = sum(8000 / (math.dist(right_sensor, (lx, ly))**2 + 1) for lx, ly in light_positions)

            left_motor = max(0, self.max_speed - left_intensity*0.05)
            right_motor = max(0, self.max_speed - right_intensity*0.05)

            speed = (left_motor + right_motor) / 2
            rotation = (right_motor - left_motor) * 0.05
            self.heading += rotation

            # Stop if very close
            if distance < 15:
                self.speed = 0
                self.stopped = True
            else:
                self.speed = speed
                self.stopped = False
        else:
            # Green Explorer: Fear behavior
            self.speed = self.max_speed
            self.stopped = False

            if distance < 120:  # fear radius
                angle_to_light = math.atan2(dy, dx)
                # Turn away from light
                self.heading += 0.1 * (math.pi + angle_to_light - self.heading)
                # Add slight random wandering
                self.heading += random.uniform(-0.02, 0.02)

        # Move vehicle
        self.x += math.cos(self.heading) * self.speed
        self.y += math.sin(self.heading) * self.speed

        # Screen wrap
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        radius = 15
        color = (150, 150, 255) if self.stopped else self.color
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)
        # heading line
        end_x = self.x + math.cos(self.heading) * radius * 1.5
        end_y = self.y + math.sin(self.heading) * radius * 1.5
        pygame.draw.line(surface, (0,0,0), (self.x, self.y), (end_x, end_y), 3)
        surface.blit(font.render(f"{round(self.speed,1)}", True, (0,0,0)), (self.x+10, self.y-10))


# -------------------------
# Light Class
# -------------------------
class Light:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
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

    def draw(self, surface):
        pygame.draw.circle(surface, (255,255,0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0,0,0), (int(self.x), int(self.y)), self.radius, 2)


# -------------------------
# Setup
# -------------------------
lights = [
    Light(WIDTH//3, HEIGHT//3),
    Light(WIDTH*2//3, HEIGHT*2//3)
]

love_vehicle = Vehicle(200, 300, (0,100,255), explorer=False)   # Blue, Love
explorer_vehicle = Vehicle(400, 300, (0,200,0), explorer=True)  # Green, Fear Explorer

vehicles = [love_vehicle, explorer_vehicle]


# -------------------------
# Main Loop
# -------------------------
running = True
while running:
    screen.fill((255,255,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
            for light in lights:
                light.handle_event(event)

    # Draw lights
    for light in lights:
        light.draw(screen)

    light_positions = [l.pos() for l in lights]

    # Update and draw vehicles
    for v in vehicles:
        v.update(light_positions)
        v.draw(screen)

    # Labels
    screen.blit(font.render("Blue: Love Vehicle (Stops near light)", True, (0,0,0)), (10, 10))
    screen.blit(font.render("Green: Fear Explorer (Moves away from lights)", True, (0,0,0)), (10, 30))
    screen.blit(font.render("Click/drag to move the nearest light", True, (0,0,0)), (10, HEIGHT-25))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
