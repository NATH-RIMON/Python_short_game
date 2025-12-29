import pygame
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Rectangular Vehicle Control")
clock = pygame.time.Clock()

class Vehicle:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle  # Facing angle in degrees
        self.speed = 0
        self.max_speed = 5
        self.rotation_speed = 4

    def update(self, keys):
        # Rotate vehicle
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed

        # Move forward/backward
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + 0.1, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - 0.1, -self.max_speed / 2)
        else:
            # Natural slowing down
            self.speed *= 0.95

        # Update position
        rad = math.radians(-self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)

    def draw(self, surface):
     body_width, body_height = 80, 30
     head_width, head_height = 25, 20

     # Create vehicle surface (transparent)
     body_surf = pygame.Surface((body_width, body_height), pygame.SRCALPHA)
     
     # Main body (blue)
     pygame.draw.rect(body_surf, (0, 0, 255), (0, 0, body_width, body_height))
     pygame.draw.rect(body_surf, (0, 0, 0), (0, 0, body_width, body_height), 2)

     # Front (green rectangle)
     front_x = body_width - head_width - 40  # slightly behind front
     front_y = (body_height - head_height) // 2
     pygame.draw.rect(body_surf, (0, 255, 0), (front_x, front_y, head_width, head_height))
     pygame.draw.rect(body_surf, (0, 0, 0), (front_x, front_y, head_width, head_height), 2)

     # Front black “nose line” pointing forward
     nose_start = (front_x + head_width, body_height // 2)
     nose_end = (body_width, body_height // 2)  # points to actual front edge
     pygame.draw.line(body_surf, (0, 0, 0), nose_start, nose_end, 3)

     # Backside (black line)
     pygame.draw.line(body_surf, (0, 0, 0), (0, 0), (0, body_height), 4)

     # Rotate vehicle
     rotated = pygame.transform.rotate(body_surf, -math.degrees(self.heading))
     rect = rotated.get_rect(center=(self.x, self.y))
     surface.blit(rotated, rect)

     # Optional debug info
     surface.blit(font.render(f"Pos=({int(self.x)}, {int(self.y)})", True, (0, 0, 0)), (10, 10))
     surface.blit(font.render(f"Heading={round(math.degrees(self.heading))}°", True, (0, 0, 0)), (10, 30))

     body_width, body_height = 80, 30
     head_width, head_height = 25, 20

          # Create vehicle surface (transparent)
     body_surf = pygame.Surface((body_width, body_height), pygame.SRCALPHA)
          
          # Main body (blue)
     pygame.draw.rect(body_surf, (0, 0, 255), (0, 0, body_width, body_height))
     pygame.draw.rect(body_surf, (0, 0, 0), (0, 0, body_width, body_height), 2)

          # Front (green rectangle)
     pygame.draw.rect(
               body_surf,
               (0, 255, 0),
               (body_width - head_width-40, (body_height - head_height)//2, head_width, head_height)
          )
     pygame.draw.rect(
               body_surf,
               (0, 0, 0),
               (body_width - head_width-40, (body_height - head_height)//2, head_width, head_height),
               2
          )

          # Backside (black line)
     pygame.draw.line(
               body_surf,
               (0, 0, 0),
               (0, 0),
               (0, body_height),
               4
          )

          # Rotate vehicle
     rotated = pygame.transform.rotate(body_surf, -self.angle)
     rect = rotated.get_rect(center=(self.x, self.y))
     surface.blit(rotated, rect)

          # Direction arrow
     arrow_length = 50
     end_x = self.x + arrow_length * math.cos(math.radians(-self.angle))
     end_y = self.y + arrow_length * math.sin(math.radians(-self.angle))
     pygame.draw.line(surface, (0, 0, 0), (self.x, self.y), (end_x, end_y), 3)
     pygame.draw.circle(surface, (0, 0, 0), (int(end_x), int(end_y)), 4)

# Create vehicle
vehicle = Vehicle(400, 300)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    vehicle.update(keys)

    screen.fill((255, 255, 255))
    vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
