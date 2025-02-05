import pygame
import pygame.freetype
import math
import random
import sys

ACC = 240.0
PLAYER_VEL = 100.0
PROJ_VEL = 120.0

class Display:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.run = True
        self.delta = 0
        self.font = None
        
    def draw_text(self, msg, x, y, color):
        surface, rect = self.font.render(msg, color)
        self.screen.blit(surface, (x-rect.w//2, y-rect.h))
        
def init_display(sw, sh):
    pygame.init()
    screen = pygame.display.set_mode((sw,sh))
    clock = pygame.time.Clock()
    display = Display(screen, clock)
    display.font = pygame.freetype.Font('JuliaMono-Bold.ttf', 18)
    return display

def length(x,y):
    return math.sqrt(x*x+y*y)

class Gobj:
    def __init__(self, x, y, radius, color, gtype):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.gtype = gtype
        self.vx = 0
        self.vy = 0
        self.orientation = 0.0
        self.rotation = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.turn = 0.0
        self.alive = True
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self.x, self.y),
            self.radius,
            0)
    def collides(self, gobj):
        dist = math.sqrt(
            (gobj.x-self.x)**2 + (gobj.y-self.y)**2)
        if dist < self.radius+gobj.radius:
            return True
        return False

    def update(self, x, y, vx, vy, dt):
        pass

class Player(Gobj):
    
    def handle_input(self, keys, dt):

        mx = 0
        my = 0
        
        if keys[pygame.K_a]:
            mx = -1
            # self.x -= PMAX_VEL*dt
        elif keys[pygame.K_d]:
            mx = 1
            # self.x += PMAX_VEL*dt
        if keys[pygame.K_w]:
            my = -1
            # self.y -= PMAX_VEL*dt
        elif keys[pygame.K_s]:
            my = 1
            # self.y += PMAX_VEL*dt
        l = length(mx,my)
        if l > 0:
            self.x += (mx/l)*PLAYER_VEL*dt
            self.y += (my/l)*PLAYER_VEL*dt

class Tower(Gobj):
    def move(self, x, y, dt):
        tx = x - self.x
        ty = y - self.y
        dlen = length(tx, ty)
        self.vx = PLAYER_VEL*(tx/dlen)*dt
        self.vy = PLAYER_VEL*(ty/dlen)*dt
        self.orientation = math.atan2(self.vy,self.vx)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self.x, self.y),
            self.radius,
            0)
        pygame.draw.line(
            screen,
            "black",
            (self.x, self.y),
            (self.x+math.cos(self.orientation)*self.radius*2,
             self.y+math.sin(self.orientation)*self.radius*2),
            4)
    def update(self, x, y, vx, vy, dt):
        tx = x
        ty = y
        self.move(tx,ty, dt)
class Missile(Gobj):
    def __init__(self, x, y, radius, color, gtype):
        Gobj.__init__(self, x, y, radius, color, gtype)
    def move(self, x, y, dt):
        
        # movement
        tx = x - self.x
        ty = y - self.y
        dlen = length(tx, ty)
        self.vx = self.vx + tx/dlen * ACC * dt
        self.vy = self.vy + ty/dlen * ACC * dt
        vlen = length(self.vx,self.vy)
        if vlen > PROJ_VEL:
            self.vx = self.vx/vlen * PROJ_VEL
            self.vy = self.vy/vlen * PROJ_VEL
        self.x += self.vx*dt
        self.y += self.vy*dt
        # orientation
        self.orientation = math.atan2(self.vy,self.vx)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self.x, self.y),
            self.radius,
            0)
        pygame.draw.line(
            screen,
            "white",
            (self.x, self.y),
            (self.x+math.cos(self.orientation)*self.radius,
             self.y+math.sin(self.orientation)*self.radius),
            2)

    def update(self, x, y, vx, vy, dt):
        tx = x
        ty = y
        self.move(tx, ty, dt)

# ####################################################################
# ####################################################################
# ####################################################################
# ####################################################################
class RedMissile(Missile):
    def __init__(self, x, y, radius, color, gtype):
        Missile.__init__(self, x, y, radius, color, gtype)
    def update(self, x, y, vx, vy, dt):
        self.move(x, y, dt)
        
class BlueMissile(Missile):
    def __init__(self, x, y, radius, color, gtype):
        Missile.__init__(self, x, y, radius, color, gtype)
    def update(self, x, y, vx, vy, dt):
        self.move(x, y, dt)

class YellowMissile(Missile):
    def __init__(self, x, y, radius, color, gtype):
        Missile.__init__(self, x, y, radius, color, gtype)
    def update(self, x, y, vx, vy, dt):
        self.move(x, y, dt)

class GreenMissile(Missile):
    def __init__(self, x, y, radius, color, gtype):
        Missile.__init__(self, x, y, radius, color, gtype)
    def update(self, x, y, vx, vy, dt):
        self.move(x, y, dt)
# ####################################################################
# ####################################################################
# ####################################################################
# ####################################################################

        
def game_loop(display, max_missiles, missile_timer):
    
    win_w, win_h = pygame.display.get_window_size()
    d_rect = (0, 0, win_w, win_h)

    player = Player(win_w//2, win_h//2, 10, "deeppink", "player")
    red = Tower(10,10, 10, "red", "ai")
    blue = Tower(win_w-10, win_h-10, 10, "cyan", "ai")
    yellow = Tower(win_w-10, 10, 10, "yellow", "ai")
    green = Tower(10, win_h-10, 10, "green", "ai")
    
    missile_colors = ["r","b","g","y"]
    time_last_missile = pygame.time.get_ticks()
    missiles_in_flight = 0
    objs = [player, red, blue, green, yellow]

    score = 0

    for i in range(4):
        x = random.randint(100,win_w-100)
        y = random.randint(100,win_w-100)
        while abs(player.x-x) < player.radius+20:
            x = random.randint(100,win_w-100)
        while abs(player.y-y) < player.radius+20:
            y = random.randint(100,win_h-100)
        obstacle = Gobj(
            random.randint(100,win_w-100),
            random.randint(100,win_h-100),
            20, "gray90", "obstacle")
        objs.append(obstacle)

    while display.run:
        dt = display.clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                display.run = False
        keys = pygame.key.get_pressed()
        
        display.screen.fill("dodgerblue4")

        # red.update(player.x, player.y, player.vx, player.vy, dt)
        # blue.update(player.x, player.y, player.vx, player.vy, dt)
        player.handle_input(keys, dt)

        if missiles_in_flight < max_missiles:
            if (pygame.time.get_ticks() - time_last_missile) > missile_timer:
                color = random.choice(missile_colors)
                if color == "r":
                    new_missile = RedMissile(
                        red.x, red.y, 5, "red", "missile")
                    objs.append(new_missile)
                elif color == "b":
                    new_missile = BlueMissile(
                        blue.x, blue.y, 5, "cyan", "missile")
                    objs.append(new_missile)
                elif color == "g":
                    new_missile = GreenMissile(
                        green.x, green.y, 5, "green", "missile")
                    objs.append(new_missile)
                else:
                    new_missile = YellowMissile(
                        yellow.x, yellow.y, 5, "yellow", "missile")
                    objs.append(new_missile)
                time_last_missile = pygame.time.get_ticks()
        
        for o in objs:
            o.update(player.x, player.y, player.vx, player.vy, dt)

        for i in range(len(objs)):
            if objs[i].gtype == "ai":
                continue
            for j in range(i+1, len(objs)):
                if objs[i].collides(objs[j]):
                    if objs[j].gtype == "ai":
                        continue
                    elif objs[i].gtype == "obstacle":
                        objs[j].alive = False
                    elif objs[j].gtype == "obstacle":
                        objs[i].alive = False
                    else:
                        objs[i].alive = False
                        objs[j].alive = False

                    if objs[i].gtype == "missile":
                        score += 1
                    if objs[j].gtype == "missile":
                        score += 1

        if not player.alive:
            display.run = False
                        
        objs = [o for o in objs if o.alive]
                        
        for o in objs:
            o.draw(display.screen)

        display.draw_text(f"Score {score}", win_w//2, win_h-30, "white")
    
        pygame.display.flip()

    print(f"FINAL SCORE: {score}")

def main():
    if len(sys.argv) < 3:
        print("Missing num missiles and/or timer args.")
        return
    max_missiles = int(sys.argv[1])
    missile_timer = int(sys.argv[2])
    display = init_display(800,600)
    game_loop(display, max_missiles, missile_timer)

if __name__ == "__main__":
    main()
