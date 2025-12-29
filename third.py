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
        self.max_speed = 100
        self.color = color
        self.cross_wired = cross_wired  # False = Fear, True = Aggression
        self.sensor_offset = 25
        self.speed = 0  # Store current speed for display

    def update(self, light_positions):
        # sensor positions
        left_sensor = (
            self.x + math.cos(self.heading + math.pi / 6) * self.sensor_offset,
            self.y + math.sin(self.heading + math.pi / 6) * self.sensor_offset
        )
        right_sensor = (
            self.x + math.cos(self.heading - math.pi / 6) * self.sensor_offset,
            self.y + math.sin(self.heading - math.pi / 6) * self.sensor_offset
        )

        # light intensities
        left_intensity, right_intensity = 0, 0
        for lx, ly in light_positions:
            left_intensity += 8000 / (math.dist(left_sensor, (lx, ly)) ** 2 + 1)
            right_intensity += 8000 / (math.dist(right_sensor, (lx, ly)) ** 2 + 1)

        # Motor control
        if self.cross_wired:
            # Aggressive → moves TOWARD light
            left_motor = right_intensity
            right_motor = left_intensity
        else:
            # Fearful → moves AWAY from light
            left_motor = left_intensity
            right_motor = right_intensity

        # TURN RATE (smooth)
        turn_rate = (right_motor - left_motor) * 0.007
        self.heading += turn_rate

        # smooth speed
        base_speed = 2
        target_speed = min((left_motor + right_motor) * 0.05 + base_speed, self.max_speed)
        self.speed += (target_speed - self.speed) * 0.1

        # move vehicle
        self.x += math.cos(self.heading) * self.speed
        self.y += math.sin(self.heading) * self.speed

        # wrap screen
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        body_width, body_height = 120, 45
        head_width, head_height = 40, 30
        sensor_radius = 6

        body_surf = pygame.Surface((body_width, body_height), pygame.SRCALPHA)

        # body
        pygame.draw.rect(body_surf, self.color, (0, 0, body_width, body_height))
        pygame.draw.rect(body_surf, (0, 0, 0), (0, 0, body_width, body_height), 3)

        # head (yellow)
        front_x = body_width - head_width - 50
        front_y = (body_height - head_height) // 2
        pygame.draw.rect(body_surf, (255, 255, 0), (front_x, front_y, head_width, head_height))
        pygame.draw.rect(body_surf, (0, 0, 0), (front_x, front_y, head_width, head_height), 3)

        # front nose
        pygame.draw.line(body_surf, (0, 0, 0),
                         (front_x + head_width, body_height // 2),
                         (body_width, body_height // 2), 4)

        # back line
        pygame.draw.line(body_surf, (0, 0, 0), (0, 0), (0, body_height), 5)

        # sensors
        left_sensor_x = front_x + 5
        left_sensor_y = front_y - sensor_radius - 2
        pygame.draw.circle(body_surf, (255, 0, 0), (left_sensor_x, left_sensor_y), sensor_radius)
        pygame.draw.circle(body_surf, (0, 0, 0), (left_sensor_x, left_sensor_y), sensor_radius, 2)

        right_sensor_x = front_x + 5
        right_sensor_y = front_y + head_height + sensor_radius + 2
        pygame.draw.circle(body_surf, (0, 255, 0), (right_sensor_x, right_sensor_y), sensor_radius)
        pygame.draw.circle(body_surf, (0, 0, 0), (right_sensor_x, right_sensor_y), sensor_radius, 2)

        # rotate & draw
        rotated = pygame.transform.rotate(body_surf, -math.degrees(self.heading))
        rect = rotated.get_rect(center=(self.x, self.y))
        surface.blit(rotated, rect)

        # debug text
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
lights = [
    Light(WIDTH // 2, HEIGHT // 3),
    Light(WIDTH // 2, HEIGHT * 2 // 3),
]

vehicle_fear = VehicleTwo(400, 300, color=(0, 100, 255), cross_wired=False)   # Fear
vehicle_aggr = VehicleTwo(600, 300, color=(255, 100, 0), cross_wired=True)   # Aggression

# ==========================
# Main Loop
# ==========================
running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse interactions
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if event.button == 3:  # RIGHT CLICK = add new light
                lights.append(Light(mouse_x, mouse_y))

            if event.button == 1:  # LEFT CLICK = move nearest light
                nearest_light = min(
                    lights,
                    key=lambda l: (l.x - mouse_x)**2 + (l.y - mouse_y)**2
                )
                nearest_light.move_light((mouse_x, mouse_y))

    # Draw lights
    for light in lights:
        light.draw(screen)

    # Update & draw vehicles
    light_positions = [l.pos() for l in lights]
    vehicle_fear.update(light_positions)
    vehicle_aggr.update(light_positions)

    vehicle_fear.draw(screen)
    vehicle_aggr.draw(screen)

    # Labels
    screen.blit(font.render("Vehicle 2a (Fear / Coward)", True, (0, 0, 150)), (20, 20))
    screen.blit(font.render("Vehicle 2b (Aggression / Anger)", True, (150, 0, 0)), (20, 40))
    screen.blit(font.render("Left click: Move light | Right click: Add light", True, (0, 0, 0)), (20, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
