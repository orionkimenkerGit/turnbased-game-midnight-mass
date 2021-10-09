import pygame
import random
import button 
pygame.init()

game_clock = pygame.time.Clock()
fps = 60

#game window size
bottom_panel = 150
window_width = 800
window_height = 300 + bottom_panel

#game window itself
game_window = pygame.display.set_mode((window_width, window_height))

pygame.display.set_caption('Midnight Mass')


#define game variables 
curr_fighter = 1 
total_fighters = 3 
action_cooldown = 0 
action_wait_time = 90
attack = False
FlameAttack = False
clicked = False
game_over = 0 

#define fonts
font = pygame.font.SysFont('Times New Roman', 22)

#define colors
red = (150, 0 , 0)
green = (0, 120, 100)

#load images
#background images
background_image = pygame.image.load('images/Background/09.png').convert_alpha()
#panel image
panel_image = pygame.image.load('images/Background/grey.png').convert_alpha()
#cursor image
cursor_image = pygame.image.load('images/Background/sword5.png').convert_alpha()
#victory and defeat images
victory_image = pygame.image.load('images/Background/victory.png').convert_alpha()
victory_image = pygame.transform.scale(victory_image, (255, 200))
defeat_image = pygame.image.load('images/Background/defeat.png').convert_alpha()
defeat_image = pygame.transform.scale(defeat_image, (255, 200))
restart_image = pygame.image.load('images/Background/restart.png').convert_alpha()


#create function for drawing text
def draw_text(text, font, text_color,x, y):
	image = font.render(text, True, text_color)
	game_window.blit(image, (x, y))

#function for drawing background
def draw_background():
	game_window.blit(background_image, (-200,-150)) 

def draw_panel():
	#draw panel rectangel 
	game_window.blit(panel_image, (0, window_height - bottom_panel + 5))
	game_window.blit(panel_image, (300, window_height - bottom_panel + 5))
	game_window.blit(panel_image, (600, window_height - bottom_panel + 5))
	#show knight stats
	draw_text(f'Dark Knight HP: {DarkKnight.health}', font, red, 100, window_height - bottom_panel + 10)
	for count, i in enumerate(Cultists_list):
		#show name and health 
		draw_text(f'         Cultist HP: {i.health}', font, red, 500, (window_height - bottom_panel + 10) + count * 60)


class Character():
	def __init__(self, x, y, name, max_health, strength):
		self.name = name
		self.max_health = max_health
		self.health = max_health
		self.strength = strength 
		self.alive = True
		self.animation_list = []
		self.frame_index = 0
		self.action = 0 #0: idle 1: attack 2: FlameAttack 3: hurt 4: death
		self.update_time = pygame.time.get_ticks()
		#load idle images
		temp_list = []
		for i in range(10):
			if i >= 8 and self.name == 'Cultists':
				break
			img = pygame.image.load(f'images/{self.name}/{self.name}/Sprites/{self.name}/Idle/Idle_{i}.png')
			img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
			temp_list.append(img)
		self.animation_list.append(temp_list)
		#load attack images
		temp_list = []
		for i in range(18):
			if i >= 12  and self.name == 'DarkKnight':
				break
			else:
				img = pygame.image.load(f'images/{self.name}/{self.name}/Sprites/{self.name}/Attack/Attack_{i}.png')
				img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
				temp_list.append(img)
		self.animation_list.append(temp_list)
		#load flame attack images
		temp_list = []
		for i in range(13):
			img = pygame.image.load(f'images/DarkKnight/DarkKnight/Sprites/DarkKnight/FlameAttack/DarkKnight_FlameAttack_{i}.png')
			img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
			temp_list.append(img)
		self.animation_list.append(temp_list)
		#load hurt images
		temp_list = []
		for i in range(3):
			img = pygame.image.load(f'images/{self.name}/{self.name}/Sprites/{self.name}/Hurt/Hurt_{i}.png')
			img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
			temp_list.append(img)
		self.animation_list.append(temp_list)
		#load death animation images
		temp_list = []
		for i in range(12):
			if i >= 11  and self.name == 'Cultists':
				break
			img = pygame.image.load(f'images/{self.name}/{self.name}/Sprites/{self.name}/Death/Death_{i}.png')
			img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
			temp_list.append(img)
		self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)

	def update(self):
		animation_cooldown = 100
		#handle animation
		#update image
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > animation_cooldown:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out then reset back to the start 
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 4:
				self.frame_index = len(self.animation_list[self.action]) -1
			else:
				self.idle()

	def idle(self):
		#set variables to idle animation
		self.action = 0
		self.frame_index = 0 
		self.update_time = pygame.time.get_ticks()

	def attack(self, target):
		#deal damage to enemy 
		rand = random.randint(-5, 5)
		damage = self.strength + rand
		target.health -= damage
		#run hurt animation for enemy
		target.hurt()
		#check if target has died
		if target.health < 1:
			target.health = 0 
			target.alive = False
			target.death()
		damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
		damage_text_group.add(damage_text)
		#set variables to attack animation
		self.action = 1 
		self.frame_index = 0 
		self.update_time = pygame.time.get_ticks()


	def FlameAttack(self, target):
		rand = random.randint(-4, 10)
		damage = self.strength + rand 
		target.health -= damage
		#run hurt animation for enemy
		target.hurt()
		self.health += damage // 3
		if target.health < 1:
			target.health = 0 
			target.alive = False
			target.death()
		damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
		damage_text_group.add(damage_text)
		damage_text = DamageText(DarkKnight.rect.centerx, DarkKnight.rect.y, str(damage//3), green)
		damage_text_group.add(damage_text)
		self.action = 2
		self.frame_index = 0
		self.update_time = pygame.time.get_ticks()

	def hurt(self):
		#set variables to hurt animation
		self.action = 3
		self.frame_index = 0 
		self.update_time = pygame.time.get_ticks()

	def death(self):
		self.action = 4
		self.frame_index = 0
		self.update_time = pygame.time.get_ticks()


	def reset(self):
		self.alive = True 
		self.health = self.max_health
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()




	def draw(self):
		game_window.blit(self.image, self.rect)




class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x 
		self.y = y 
		self.health = health 
		self.max_health = max_health 


	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health 
		pygame.draw.rect(game_window, red, (self.x, self.y, 150, 20))
		pygame.draw.rect(game_window, green, (self.x, self.y, 150 * ratio, 20))


class DamageText(pygame.sprite.Sprite):
	def __init__(self, x, y, damage, color):
		pygame.sprite.Sprite.__init__(self)
		self.image = font.render(damage, True, color)
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)
		self.counter = 0 

	def update(self):
		#move damage text up 
		self.rect.y -= 1 
		self.counter += 1
		if self.counter > 30:
			self.kill()


damage_text_group = pygame.sprite.Group()




DarkKnight = Character(160, 220, 'DarkKnight', 30, 10)
Cultists_one = Character(360, 220, 'Cultists', 20, 9)
Cultists_two = Character(550, 220, 'Cultists', 20, 9)

Cultists_list = []
Cultists_list.append(Cultists_one)
Cultists_list.append(Cultists_two)


DarkKnight_health_bar = HealthBar(110, window_height - bottom_panel + 40, DarkKnight.health, DarkKnight.max_health)
Cultists_one_health_bar = HealthBar(550, window_height- bottom_panel + 40, Cultists_one.health, Cultists_one.max_health)
Cultists_two_health_bar = HealthBar(550, window_height - bottom_panel + 100, Cultists_two.health, Cultists_two.max_health)

#create buttons
restart_button = button.Button(game_window, 500, 30, restart_image, 120, 30)



#run game loop until user quits out
run = True 
while run:

	game_clock.tick(fps)

	#draw background
	draw_background()

	draw_panel()
	DarkKnight_health_bar.draw(DarkKnight.health)
	Cultists_one_health_bar.draw(Cultists_one.health)
	Cultists_two_health_bar.draw(Cultists_two.health)

	#draw characters
	DarkKnight.update()
	DarkKnight.draw()

	for Cultists in Cultists_list:
		Cultists.update()
		Cultists.image = pygame.transform.flip(Cultists.image, True, False)
		Cultists.draw()

	#draw damage text
	damage_text_group.update()
	damage_text_group.draw(game_window)
	#control player actions
	#reset action variables
	attack = False
	FlameAttack = False
	target = None
	pygame.mouse.set_visible(True)
	position = pygame.mouse.get_pos()
	for count, Cultists in enumerate(Cultists_list):
		if Cultists.rect.collidepoint(position):
			#hide mouse
			pygame.mouse.set_visible(False)
			#show new cursor 
			game_window.blit(cursor_image, position)
			if clicked == True and DarkKnight.health >= 10 and Cultists.alive == True:
				attack = True 
				target = Cultists_list[count] 
			elif clicked == True and DarkKnight.health < 10 and Cultists.alive == True:
				FlameAttack = True
				target = Cultists_list[count]


	if game_over == 0:
		#player action
		if DarkKnight.alive: 
			if curr_fighter == 1:
				action_cooldown += 1
				if action_cooldown >= action_wait_time and DarkKnight.health >= 10:
					#player action
					#attack
					if attack == True and target != None:
						DarkKnight.attack(target)
						curr_fighter += 1
						action_cooldown = 0
				if action_cooldown >= action_wait_time and DarkKnight.health < 10:
					if FlameAttack == True and target != None:
						DarkKnight.FlameAttack(target)
						curr_fighter += 1
						action_cooldown = 0
		else:
			game_over = -1

		#enemy action
		for count, Cultists in enumerate(Cultists_list):
			if curr_fighter == 2 + count:
				if Cultists.alive:
					action_cooldown += 1
					if action_cooldown >= action_wait_time:
						#attack 
						Cultists.attack(DarkKnight)
						curr_fighter += 1
						action_cooldown = 0 
				else:
					curr_fighter += 1
		#if all charactes have had a turn then you can reset
		if curr_fighter > total_fighters:
			curr_fighter = 1

	#check if all cultists are dead
	alive_Cultists = 0
	for Cultists in Cultists_list:
		if Cultists.alive == True:
			alive_Cultists += 1
	if alive_Cultists == 0:
		game_over = 1

	#check if game over
	if game_over != 0:
		if game_over == 1:
			game_window.blit(victory_image, (275,-20))
		if game_over == -1:
			game_window.blit(defeat_image, (275, -30))
		if restart_button.draw():
			DarkKnight.reset()
			for Cultists in Cultists_list:
				Cultists.reset()
			curr_fighter = 1 
			action_cooldown
			game_over = 0 



	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			clicked = True
		else:
			clicked = False

	pygame.display.update()

pygame.quit()