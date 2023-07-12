import pygame
import os
from sys import exit
from random import randint, choice


class Player(pygame.sprite.Sprite):
    global game_active#fetches global variable 
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load('graphics/player_new/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load('graphics/player_new/player_walk_2.png').convert_alpha()
        player_walk_3 = pygame.image.load('graphics/player_new/player_walk_3.png').convert_alpha()
        player_walk_4 = pygame.image.load('graphics/player_new/player_walk_4.png').convert_alpha()
        self.player_walk = [player_walk_1, player_walk_2, player_walk_3, player_walk_4]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/player_new/jump.png').convert_alpha()
        
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midleft = (80,300))
        self.cooldown = 0
        #combat
        self.attacking = False
        self.attack_frame = 0
        self.player_attack = pygame.image.load('graphics/player_new/player_attack.png').convert_alpha()
        self.movement_penalty = 0
        self.invulnerable = 0
        #movement
        self.gravity = 0
        self.dash = 0
        self.dash_right = False
        self.dash_left = False
        self.dash_ability = False

    def player_input(self):
        self.dash_left = False
        self.dash_right = False
        self.dash_ability = False
        # self.attacking = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_x]:
            if self.attacking == False:
                if self.cooldown ==0:
                    self.attacking = True
                    self.attack_frame = 0              
                    self.movement_penalty = 3   
        if keys[pygame.K_z]:
            self.dash_ability = True
            self.dash = 25
        elif keys[pygame.K_UP] and self.rect.bottom >= 300:
            self.gravity = -20
            if(game_active):
                pygame.mixer.Channel(0).play(pygame.mixer.Sound('audio\jump.mp3'))
        elif keys[pygame.K_RIGHT]:
            self.dash_right = True
            self.dash = 5 - self.movement_penalty
        elif keys[pygame.K_LEFT]:
            self.dash_left = True
            self.dash = 5 - self.movement_penalty
        elif keys[pygame.K_DOWN]:
            self.gravity = 25
        else:
            self.dash_left = True
            self.dash = 3
        

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def apply_dash(self):

        if self.dash_right:
            self.rect.x += self.dash
            if self.rect.x >= 300:
                self.rect.x = 300
        if self.dash_left:
            self.rect.x -= self.dash
            if self.rect.x <= 80:
                self.rect.x = 80
        if self.dash_ability:
            self.rect.x += self.dash
            if self.rect.x >= 300:
                self.rect.x = 300

    
    def animation_state(self):#animation img
        if self.attacking == True:
            self.image = self.player_attack
        elif self.rect.bottom < 300:
           self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def game_over(self):#player dies
        self.dash_right = False
        self.dash_left = False
        self.gravity = 0
        self.rect.x = 80
        self.rect.bottom = 300

    def update(self, game_state):#runs every tick or 60 updates per second
        self.player_input()#checks latest inputs
        self.apply_gravity()
        self.apply_dash()
        self.attack()
        self.animation_state()
        if not(game_state):
            self.game_over()

    def attack(self):#when input is pressed, activate animation for 1/6 of a second        
      # If attack frame has reached end of sequence, return to base frame   
        if self.attack_frame > 15:#duration of attack
            self.attack_frame = 0
            self.attacking = False
            self.cooldown = 10
            self.movement_penalty = 0
            self.invulnerable = 8
      # Update the current attack frame  
        if self.cooldown !=0:
            self.cooldown -= 1
        if self.attacking == True:
            self.attack_frame += 1
        if self.invulnerable !=0:
            self.invulnerable -= 1
        

class Obstacle(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()

        if type == 'fly':
            fly_1 = pygame.image.load('graphics/fly_new/fly1.png').convert_alpha()
            fly_2 = pygame.image.load('graphics/fly_new/fly2.png').convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 150
        else:
            snail_1 = pygame.image.load('graphics/snail_new/snail1.png').convert_alpha()
            snail_2 = pygame.image.load('graphics/snail_new/snail2.png').convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300
        
        self.animation_index = 0
        
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(900, 1100),y_pos))
    
    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]
    
    def destroy(self):
        if self.rect.x <= -100:
            self.kill()
        
    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()
    

def display_score():
    global score
    score_surface = test_font.render(f'Score: {score}', False,(64,64,64))
    score_rect = score_surface.get_rect(center = (400,50))
    screen.blit(score_surface,score_rect)

def collission_sprite():
    global score,game_died,selected
    hits = pygame.sprite.spritecollide(player.sprite, obstacle_group, False)
    if hits and player_class.attacking==True: 
        obstacle_group.remove(obstacle_group.sprites()[0])#remove cuurently oldest sprite
        score +=1#add score when kill
        return True
    elif hits and player_class.invulnerable==0:   
        obstacle_group.empty()
        game_died = True
        selected = 5
        return False
    else:
        return True

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init() # <- starts pygame
pygame.mixer.init()
pygame.mixer.music.load('audio/music.wav')#music
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Rpi Game Project')
clock = pygame.time.Clock()
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False # active game loop
game_died = False # state when died
selected = 1 # menu options value
menu_state = 1 # is default menu
#2 is about us
start_time = 0
score = 0

player_class = Player()
player = pygame.sprite.GroupSingle()
player.add(player_class)

obstacle_group = pygame.sprite.Group()

sky_surface = pygame.image.load('graphics/bg.png').convert()
ground_surface = pygame.image.load('graphics/ground2.png').convert()

#intro screen (trial)

player_stand = pygame.image.load('graphics/player_new/player_attack.png').convert_alpha()
player_stand= pygame.transform.rotozoom(player_stand,0,0.8)
player_stand_rect = player_stand.get_rect(center = (120,80))

game_name = test_font.render('Rpi Project', False,(0,0,0))
game_name_rect = game_name.get_rect(center = (320,80))

game_message = test_font.render('Press space to run', False, (0,0,0))
game_message_rect = game_message.get_rect(center = (400, 340))

start_option = test_font.render('Start',False,(0,0,0))
start_option_rect = start_option.get_rect(center = (130,170))

option_option = test_font.render('About Us',False,(0,0,0))
option_option_rect = option_option.get_rect(center = (157,200))

exit_option = test_font.render('Exit',False,(0,0,0))
exit_option_rect = option_option.get_rect(center = (157,230))

about_us_info = test_font.render('About Us',False,(0,0,0))
about_us_info_rect = about_us_info.get_rect(center = (400,130))

play_again = test_font.render('Play Again',False,(0,0,0))
play_again_rect = play_again.get_rect(center = (400,240))

backtomenu = test_font.render('Back to Menu',False,(0,0,0))
backtomenu_rect = backtomenu.get_rect(center = (400,270))

about_us_member_info1 = test_font.render('John Isa Palacio, Dale Panganiban',False,(0,0,0))
about_us_member_info1_rect = about_us_member_info1.get_rect(center = (400,160))

about_us_member_info2 = test_font.render('Selwyne Ponce, Lanz Balbas',False,(0,0,0))
about_us_member_info2_rect = about_us_member_info2.get_rect(center = (400,190))

about_us_member_info3 = test_font.render('Justin Acosta, Don Sarabia',False,(0,0,0))
about_us_member_info3_rect = about_us_member_info3.get_rect(center = (400,220))

back_option = test_font.render('> Back',False,(0,0,0))
back_option_rect = back_option.get_rect(center = (380,250))

select1 = test_font.render('>',False,(0,0,0))
select1_rect = select1.get_rect(center = (70,170))

select2 = test_font.render('>',False,(0,0,0))
select2_rect = select2.get_rect(center = (70,200))

select3 = test_font.render('>',False,(0,0,0))
select3_rect = select3.get_rect(center = (70,230))

select5 = test_font.render('>',False,(0,0,0))
select5_rect = select5.get_rect(center = (300,240))

select6 = test_font.render('>',False,(0,0,0))
select6_rect = select6.get_rect(center = (270,270))
#Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1400)

snail_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_animation_timer, 500)

fly_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_animation_timer, 200)

while True:
    #gives close function of window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit() #from sys import exit
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_active == False:
                if selected == 1 and menu_state == 1:
                    game_active = True
                    score = 0
                    game_died = False
                    start_time = int(pygame.time.get_ticks() / 1000)
                elif selected == 2 and menu_state == 1:
                    menu_state = 2
                    selected = 4
                elif selected == 3 and menu_state == 1:
                    pygame.quit()
                    exit()
                elif selected == 4 and menu_state == 2:
                    menu_state = 1
                    selected = 2 
                elif selected == 5 and game_died == True:
                    game_active = True
                    score = 0
                    game_died = False
                    start_time = int(pygame.time.get_ticks() / 1000)
                elif selected == 6 and game_died == True:
                    selected = 1
                    menu_state = 1
                    game_died = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and game_active == False:
                if selected <3 and menu_state == 1:
                    selected += 1
                elif selected == 5 and game_died == True:
                    selected += 1    
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and game_active == False:
                if selected >1 and selected <=3 and menu_state == 1:
                    selected -= 1
                elif selected == 6 and game_died == True:
                    selected -= 1
        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail'])))

    if game_active:#play game is game_active is one
        screen.blit(sky_surface, (0,0)) 
        screen.blit(ground_surface, (0,300))
        display_score()

        #PLAYER
        player.draw(screen)
        player.update(game_active)
        

        #OBSTACLE
        obstacle_group.draw(screen)
        obstacle_group.update()

        #collision 
        game_active = collission_sprite()
    else:#main menu
        screen.blit(sky_surface, (0,0)) 
        screen.blit(ground_surface, (0,300))
        
        screen.blit(player_stand, player_stand_rect)
        score_message = test_font.render(f'Score: {score}', False, (0,0,0))
        score_message_rect = score_message.get_rect(center = (400, 150))

        screen.blit(game_name, game_name_rect)
        if game_died == True:
            screen.blit(score_message, score_message_rect)
            screen.blit(play_again,play_again_rect)
            screen.blit(backtomenu,backtomenu_rect)
            if(selected == 5):
                screen.blit(select5,select5_rect)
            if(selected == 6):
                screen.blit(select6,select6_rect)
        else:
            if menu_state == 1:
                screen.blit(start_option,start_option_rect)
                screen.blit(option_option,option_option_rect)
                screen.blit(exit_option,exit_option_rect)
                if selected == 1:
                    screen.blit(select1,select1_rect)
                elif selected == 2:
                    screen.blit(select2,select2_rect)
                elif selected == 3:
                    screen.blit(select3,select3_rect)
            if menu_state == 2:
                screen.blit(about_us_info,about_us_info_rect)
                screen.blit(about_us_member_info1,about_us_member_info1_rect)
                screen.blit(about_us_member_info2,about_us_member_info2_rect)
                screen.blit(about_us_member_info3,about_us_member_info3_rect)
                screen.blit(back_option,back_option_rect)

        player.update(game_active)
        
    pygame.display.update()
    clock.tick(60)#creates 60 FPS for the game