import pygame
import math
import random

pygame.init()

# ==========================
# Screen setup
# ==========================
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 2: Fear and Aggression")

clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("consolas", 16)

# ==========================
# Vehicle Class
# ==========================
class VehicleTwo:
    def __init__(self, x, y, color, cross_wired=False):
        self.x = x
        self.y = y
        self.heading = random.uniform(0, 2 * math.pi)
        self.color = color
        self.cross_wired = cross_wired
        self.sensor_offset = 25
        self.max_speed = 100
        self.speed = 0

    def update(self, light_positions):
        # --- Calculate sensor positions ---
        left_sensor = (
            self.x + math.cos(self.heading + math.pi / 6) * self.sensor_offset,
            self.y + math.sin(self.heading + math.pi / 6) * self.sensor_offset
        )
        right_sensor = (
            self.x + math.cos(self.heading - math.pi / 6) * self.sensor_offset,
            self.y + math.sin(self.heading - math.pi / 6) * self.sensor_offset
        )

        # --- Calculate light intensity ---
        left_intensity = sum(8000 / (math.dist(left_sensor, (lx, ly)) ** 2 + 1) for lx, ly in light_positions)
        right_intensity = sum(8000 / (math.dist(right_sensor, (lx, ly)) ** 2 + 1) for lx, ly in light_positions)

        # --- Motor control ---
        if self.cross_wired:  # Aggression
            left_motor = right_intensity
            right_motor = left_intensity
        else:  # Fear
            left_motor = left_intensity
            right_motor = right_intensity

        # --- Update heading ---
        turn_rate = (right_motor - left_motor) * 0.007
        self.heading += turn_rate

        # --- Smooth speed ---
        target_speed = min((left_motor + right_motor) * 0.05 + 1, self.max_speed)
        self.speed += (target_speed - self.speed) * 0.1  # smooth acceleration

        # --- Move vehicle ---
        self.x += math.cos(self.heading) * self.speed
        self.y += math.sin(self.heading) * self.speed

        # --- Screen wrap ---
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        # --- Vehicle body ---
        body_width, body_height = 120, 45
        head_width, head_height = 40, 30
        sensor_radius = 6

        body_surf = pygame.Surface((body_width, body_height), pygame.SRCALPHA)
        pygame.draw.rect(body_surf, self.color, (0, 0, body_width, body_height))
        pygame.draw.rect(body_surf, (0, 0, 0), (0, 0, body_width, body_height), 3)

        # Front / head
        front_x = body_width - head_width - 50
        front_y = (body_height - head_height) // 2
        pygame.draw.rect(body_surf, (255, 255, 0), (front_x, front_y, head_width, head_height))
        pygame.draw.rect(body_surf, (0, 0, 0), (front_x, front_y, head_width, head_height), 3)

        # Nose
        pygame.draw.line(body_surf, (0, 0, 0),
                         (front_x + head_width, body_height // 2),
                         (body_width, body_height // 2), 4)

        # Sensors
        pygame.draw.circle(body_surf, (255, 0, 0),
                           (front_x + 5, front_y - sensor_radius - 2), sensor_radius)
        pygame.draw.circle(body_surf, (0, 255, 0),
                           (front_x + 5, front_y + head_height + sensor_radius + 2), sensor_radius)

        # --- Rotate and draw ---
        rotated = pygame.transform.rotate(body_surf, -math.degrees(self.heading))
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

        # --- Debug info ---
        surface.blit(font.render(f"Speed={round(self.speed, 2)}", True, (0, 0, 0)), (10, 10))
        surface.blit(font.render(f"Heading={round(math.degrees(self.heading))}°", True, (0, 0, 0)), (10, 30))


# ==========================
# Light Class
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


# ==========================
# Setup
# ==========================
lights = [Light(WIDTH // 2, HEIGHT // 3), Light(WIDTH // 2, HEIGHT * 2 // 3)]

vehicle_fear = VehicleTwo(400, 300, (0, 100, 255), cross_wired=False)
vehicle_aggr = VehicleTwo(600, 300, (255, 100, 0), cross_wired=True)


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
            mouse_pos = event.pos
            nearest_light = min(lights, key=lambda l: (l.x - mouse_pos[0])**2 + (l.y - mouse_pos[1])**2)
            nearest_light.move_light(mouse_pos)

    # Draw lights
    for light in lights:
        light.draw(screen)

    # Update vehicles
    light_positions = [l.pos() for l in lights]
    vehicle_fear.update(light_positions)
    vehicle_aggr.update(light_positions)

    # Draw vehicles
    vehicle_fear.draw(screen)
    vehicle_aggr.draw(screen)

    # Labels
    screen.blit(font.render("Vehicle 2a (Fear / Coward)", True, (0, 0, 150)), (20, 20))
    screen.blit(font.render("Vehicle 2b (Aggression / Anger)", True, (150, 0, 0)), (20, 40))
    screen.blit(font.render("Click to move lights", True, (0, 0, 0)), (20, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
