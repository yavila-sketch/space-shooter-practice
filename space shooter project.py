import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH /2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        #cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        #transorm test
        #self.image = pygame.transform.rotate(self.image, 0)
        #self.rotation = 0

        #Mask
        #self.mask = pygame.mask.from_surface(self.image) #dont need the bottom 3 is you have this one
        #mask_surf = mask.to_surface()
        #mask_surf.set_colorkey((0, 0, 0))
        #self.image = mask_surf

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = (pygame.key.get_pressed())
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH),randint(0, WINDOW_HEIGHT)))
           
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        #self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()
        
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400, 500)
        self.rotation_speed = randint(20, 50)
        
        self.rotation = 0

        

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        
        #continous rotation
        self.rotation += 40 * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

def collisions():
    global running

    collision_sprites =  pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
        #damage_sound.play()
    
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
    
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center = pos)
        #explosion_sound.play() :: can also be placed here for same result

    def update(self, dt):
        self.frames_index += 20 * dt
        if self.frames_index < len(self.frames):
           self.image = self.frames[int(self.frames_index)] #% len(self.frames)
        else:
            self.kill()

def display_score():
    current_time = pygame.time.get_ticks() // 100 #slows down the score
    text_surf = font.render(str(current_time), True, (128, 200, 123))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (128, 200, 123), text_rect.inflate(20, 15).move(0, -8), 5, 13)

# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('space shooter')
running = True
clock = pygame.time.Clock()

#import
star_surf = pygame.image.load(join('images', 'images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'images','explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'audio', 'explosion.wav'))
explosion_sound.set_volume(0.7)
#damage_sound = pygame.mixer.Sound(join('audio', 'audio', 'damage.ogg'))
game_music = pygame.mixer.Sound(join('audio', 'audio', 'game_music.wav'))
game_music.set_volume(0.3)
game_music.play(loops= -1) # -1 loops music indefinitly

#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

#costum events ---> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick()/ 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    #update
    all_sprites.update(dt)
    collisions()

    # draw the game
    display_surface.fill('#3a2e3f') # fill the window with a red color // if you dont fill in the surface you while be able to see every frame
    display_score()
    all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()