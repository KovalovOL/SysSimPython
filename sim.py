from random import randint
import math
import pygame

# Settings
W, H = 800, 600       # Screen size
FPS = 60                # Frames per second
N_SHEEP = 20            # Number of sheeps
SHEEP_RADIUS = 10       # Sheep radius
SHEEP_ATTRACT_DIST = 70 # Attraction distance
SHEEP_REPEL_DIST = 30   # Repulsion distance
MOUSE_REPEL_DIST = 50   # Repulsion distance from mouse
DRONE_REPEL_DIST = 60   # Repulsion distance from drone
DRONE_RADIUS = 10       # Drone radius
DRONE_SPEED = 1         # Drone speed
FRICTION = 0.9          # Friction factor
LEAK_DIST = 60
DRONE_LIVE_TIME = 60

pygame.init()
screen = pygame.display.set_mode((W, H))

pygame.image.load('./res/sheep.png')
SHEEP_IMG = pygame.transform.scale_by(pygame.image.load('./res/sheep.png'), (0.52, 0.52))
ZONE_IMG = pygame.image.load('./res/zone.png').convert_alpha()
ZONE_IMG.set_alpha(165)
DRONE_IMG = pygame.image.load('./res/drone.png')
MAIN_DRONE_IMG = pygame.image.load('./res/main_drone.png')


alarms = []
targets = []

class Sheep:
    def __init__(self, pos):
        self.pos = pos
        self.speed = [0, 0]
        self.angle = 0

    def draw(self):
        angle_speed = math.atan(self.speed[1] / self.speed[0])
        self.angle += angle_speed * 0.05
        
        img = pygame.transform.rotate(SHEEP_IMG, math.degrees(self.angle))
        img_size = img.get_size()
        screen.blit(img, (self.pos[0] - img_size[0] // 2, self.pos[1] - img_size[1] // 2))


class AllowedZone:
    def __init__(self, first, second) -> None:
        self.first = first
        self.second = second
    
    def draw(self):
        pygame.draw.rect(screen, 'red', (
            self.first[0],
            self.first[1],
            self.second[0] - self.first[0],
            self.second[1] - self.first[1]
        ), 3)

    def check_sheep(self, sheep: Sheep) -> bool:
        tx = sheep.pos[0] > self.first[0] and sheep.pos[0] < self.second[0]
        ty = sheep.pos[1] > self.first[1] and sheep.pos[1] < self.second[1]
        return (tx and ty)
    
    def move(self, dx, dy):
        self.first[0] += dx
        self.first[1] += dy
        self.second[0] += dx
        self.second[1] += dy


class Drone:
    def __init__(self, pos):
        self.pos = pos
        self.speed = [0, 0]
        self.leak = None
        self.is_alarming = False
    
    def is_free(self):
        return self.leak is None
    
    def is_alarming(self):
        return self.is_alarming

    def calc_target(self):
        dx, dy = 0, 0
        if self.leak[0] < zone.first[0]:
            dx = -1
        elif self.leak[0] > zone.second[0]:
            dx = 1
        
        if self.leak[1] < zone.first[1]:
            dy = -1
        elif self.leak[1] > zone.second[1]:
            dy = 1
        
        ALPHA = 50
        return [self.leak[0] + dx * ALPHA, self.leak[1] + dy * ALPHA]

        
    def isInField(self, zone: AllowedZone) -> bool:
        isByX = self.pos[0] > zone.first[0] and self.pos[0] < zone.second[0]
        isByY = self.pos[1] > zone.first[1] and self.pos[1] < zone.second[1]

        if isByX and isByY:
            return True
        return False


    def move(self):
        if not self.is_free():

            target = self.calc_target()

            # move to target
            self.speed[0] += 1 if self.pos[0] < target[0] else -1
            self.speed[1] += 1 if self.pos[1] < target[1] else -1

            # exit case
            dist_to_target = math.sqrt(
                (self.pos[0] - target[0]) ** 2 + 
                (self.pos[1] - target[1]) ** 2
            )

            self.is_alarming = False
            if dist_to_target < 10:
                self.is_alarming = True
            if dist_to_target < 5:
                self.leak = None


        self.speed[0] *= 0.8
        self.speed[1] *= 0.8

        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

    def draw(self):
        img_size = DRONE_IMG.get_size()
        screen.blit(DRONE_IMG, (self.pos[0] - img_size[0] // 2, self.pos[1] - img_size[1] // 2))

# vars
sheeps = [Sheep([randint(int(W * 0.45), int(W * 0.55)), randint(int(H * 0.45), int(H * 0.55))]) for _ in range(N_SHEEP)]
leaks = []
drones = [Drone([0, 0]) for i in range(2)]
zone = AllowedZone(
    [W * 0.3, H * 0.3],
    [W * 0.7, H * 0.7]
)


def sheep_logic():
    def get_all_leaks():
        all_leaks = leaks.copy()
        for d in drones:
            if not d.is_free():
                all_leaks.append(d.leak)
        return all_leaks


    def is_in_leak(pos):
        all_leaks = get_all_leaks()

        for l in all_leaks:
            tx = abs(s.pos[0] - l[0]) < LEAK_DIST
            ty = abs(s.pos[0] - l[0]) < LEAK_DIST
            if tx and ty:
                return True

        return False

    for s in sheeps:
        for other in sheeps:
            if s == other: continue
            ox, oy = other.pos
            dx, dy = s.pos[0] - ox, s.pos[1] - oy
            dist_to_sheep = math.sqrt(dx**2 + dy**2)

            if dist_to_sheep > SHEEP_ATTRACT_DIST:
                s.speed[0] -= dx * 0.0001
                s.speed[1] -= dy * 0.0001
            elif dist_to_sheep < SHEEP_REPEL_DIST:
                factor = 0.5 / dist_to_sheep
                s.speed[0] += dx * factor
                s.speed[1] += dy * factor

            for d in drones:
                dx, dy = s.pos[0] - d.pos[0], s.pos[1] - d.pos[1]
                dist_to_drone = math.sqrt(dx**2 + dy**2)

                if dist_to_drone < DRONE_REPEL_DIST and not d.isInField(zone):
                    factor = 0.03 / dist_to_sheep
                    s.speed[0] += dx * factor
                    s.speed[1] += dy * factor

        # add leaks
        if not zone.check_sheep(s):
            if not is_in_leak(s.pos):
                leaks.append(s.pos.copy())

        # move
        s.speed[0] *= FRICTION
        s.speed[1] *= FRICTION
        s.pos[0] = min(max(SHEEP_RADIUS, s.pos[0] + s.speed[0]), W - SHEEP_RADIUS)
        s.pos[1] = min(max(SHEEP_RADIUS, s.pos[1] + s.speed[1]), H - SHEEP_RADIUS)


def drone_logic():
    # assign leak
    for d in drones:
        if d.is_free():
            if len(leaks) > 0:
                d.leak = leaks.pop()

        d.move()



def draw():
    # bg
    screen.fill((93, 138, 63))

    # sheeps
    for s in sheeps:
        s.draw()

    # drones
    for d in drones:
        d.draw()

    # leaks
    for l in leaks:
        pygame.draw.rect(screen, 'red', (l[0] - LEAK_DIST, l[1] - LEAK_DIST, LEAK_DIST*2, LEAK_DIST*2), 1)

    for d in drones:
        if not d.is_free():
            pygame.draw.rect(screen, 'black', (d.leak[0] - LEAK_DIST, d.leak[1] - LEAK_DIST, LEAK_DIST*2, LEAK_DIST*2), 1)

    # zone
    # zone.draw()


time = 0
def draw_main_drone():
    global time
    time += 0.01

    x, y = (math.sin(time) / 2 + 0.5) * W * 0.3 + W * 0.6, (math.cos(time) / 2 + 0.5) * H * 0.8 + H * 0.1

    screen.blit(MAIN_DRONE_IMG, (x, y))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        zone.move(-1, 0)
    if keys[pygame.K_RIGHT]:
        zone.move(1, 0)

    # Update logic
    sheep_logic()
    drone_logic()


    draw()


    draw_main_drone()


    screen.blit(ZONE_IMG, (W * 0.3, H * 0.3))

    pygame.display.flip()
    pygame.time.Clock().tick(FPS)
