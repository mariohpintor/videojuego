import pygame, random
from tiles import *
from settings import tile_size, screen_width, screen_height
from player import Player
from ecuacion import Ecuacion
from respuestas import Respuestas
from enemies import Enemy
from game_data import *
from support import *
import time

class Level:
	def __init__(self,surface,current_level,create_results,change_coins,change_health,check_game_over,nivel_dificultad):
		# general setup
		self.calificacion = pygame.image.load("imagenes/manzana.png").convert_alpha()
		self.calificacion.set_alpha(0)
		self.display_surface = surface
		self.world_shift = 0
		self.meta = False
		self.nivel_dificultad = nivel_dificultad

		self.inicio = time.time()
		self.contador_palomas = 0
		self.contador_ecuaciones = 0
		self.caidas = 0

		#audio
		#self.coin_sound = pygame.mixer.Sound('../clear_code/audio/effects/coin.wav')

		# overworld connection
		self.create_results = create_results
		self.current_level = current_level
		level_data = levels[self.current_level]
		self.new_max_level = level_data['unlock']

		self.alternancia_r = 0
		self.alternancia_l = 0

		self.change_coins = change_coins
		self.check_game_over = check_game_over

		#player 
		player_layout = import_csv_layout(level_data['player'])
		self.player = pygame.sprite.GroupSingle()
		self.goal = pygame.sprite.GroupSingle()
		self.player_setup(player_layout,change_health)

		#ecuacion
		ecuacion_layout = import_csv_layout(level_data['ecuacion'])
		self.ecuacion_group= pygame.sprite.GroupSingle()
		self.ecuacion_setup(ecuacion_layout)

		#terrain setup

		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')

		#'respuestas_r' setup

		respuestas_r_layout = import_csv_layout(level_data['respuestas_r'])
		self.respuestas_r_sprites = self.create_tile_group(respuestas_r_layout,'respuestas_r')

		#'respuestas_l' setup

		respuestas_l_layout = import_csv_layout(level_data['respuestas_l'])
		self.respuestas_l_sprites = self.create_tile_group(respuestas_l_layout,'respuestas_l')

		#enemy
		enemy_layout = import_csv_layout(level_data['enemies'])
		self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

		#constraint
		constrains_layout = import_csv_layout(level_data['constrains'])
		self.constrains_sprites = self.create_tile_group(constrains_layout, 'constrains')

		sprite = random.choice(self.respuestas_r_sprites.sprites())
		sprite.texto = 	str(self.ecuacion.respuesta_correcta)

	def create_tile_group(self, layout, type):
		sprite_group = pygame.sprite.Group()

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				if val != '-1':
					x = col_index*tile_size
					y = row_index*tile_size

					if type == 'terrain':
						terrain_tile_list = import_cut_graphics('imagenes/terrain_tiles.png')
						tile_surface = terrain_tile_list[int(val)]
						sprite = StaticTile(tile_size,x,y,tile_surface)

					if type == 'respuestas_r':
						sprite = Respuestas((x,y),tile_size,self.ecuacion.respuesta_correcta)

					if type == 'respuestas_l':
						sprite = Respuestas((x,y),tile_size,self.ecuacion.respuesta_correcta)

					if type == 'enemies':
						sprite = Enemy(tile_size,x,y)

					if type == 'constrains':
						sprite = Tile(tile_size,x,y)

				
					sprite_group.add(sprite)

		return sprite_group	

	def player_setup(self,layout,change_health):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index*tile_size
				y = row_index*tile_size
				if val == '0':
					sprite = Player((x,y),change_health)
					self.player.add(sprite)
				if val == '1':
					hat_surface = pygame.image.load('imagenes/manzana.png').convert_alpha()
					hat_surface = pygame.transform.scale(hat_surface, (60,60))
					sprite = StaticTile(tile_size,x,y,hat_surface)
					self.goal.add(sprite)
	
	def ecuacion_setup(self,layout):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index*tile_size
				y = row_index*tile_size
				if val == '0':
					self.ecuacion = Ecuacion((x,y),tile_size,self.current_level)
					self.ecuacion_group.add(self.ecuacion)

	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy,self.constrains_sprites,False):
				enemy.reverse()	

	def scroll_x(self):
		player = self.player.sprite
		player_x = player.rect.centerx
		direction_x = player.direction.x
		if player_x < screen_width/4 and direction_x < 0:
			self.world_shift = 8
			player.speed = 0
		elif player_x > screen_width - (screen_width/4) and direction_x > 0:
			self.world_shift = -8
			player.speed = 0	    	
		else:
			self.world_shift = 0
			player.speed = 8

	def horizontal_movement_collision(self,type_sprites):
		player = self.player.sprite
		player.rect.x += player.direction.x*player.speed

		for sprite in type_sprites:
			if sprite.rect.colliderect(player.rect) and player.rect.y > sprite.rect.y:
				if player.direction.x < 0:
					player.rect.left = sprite.rect.right
				elif player.direction.x > 0:
				    player.rect.right = sprite.rect.left
				keys = pygame.key.get_pressed()
				if keys[pygame.K_a] and type_sprites != self.terrain_sprites.sprites():
					self.collision_respuestas(sprite,type_sprites)					    	
	
	def vertical_movement_collision(self,type_sprites):
		player = self.player.sprite
		player.apply_gravity()

		for sprite in type_sprites:
			if sprite.rect.colliderect(player.rect):
				if player.direction.y > 0:
					player.rect.bottom = sprite.rect.top
					player.direction.y = 0
				elif player.direction.y < 0:
				    player.rect.top = sprite.rect.bottom
				    player.direction.y = 0
				keys = pygame.key.get_pressed()    
				if keys[pygame.K_a] and type_sprites != self.terrain_sprites.sprites():
					self.collision_respuestas(sprite,type_sprites)	

	def collision_respuestas(self,sprite,type_sprites):
	
		if type_sprites == self.respuestas_r_sprites.sprites():
			self.alternancia_r += 1
			self.alternancia_l = 0
		else:
			self.alternancia_l += 1 
			self.alternancia_r = 0

		if self.alternancia_r == 1 or self.alternancia_l == 1:
			#sprite.revisar(self.ecuacion.respuesta_correcta,self.display_surface)
			self.calificacion, self.contador_palomas, self.contador_ecuaciones = sprite.revisar(self.ecuacion.respuesta_correcta,self.contador_palomas,self.contador_ecuaciones)
			self.change_coins(self.contador_palomas)
			for sprite in type_sprites:
				sprite.texto = 'x'			
			if self.alternancia_r == 1:
				type_sprites = self.respuestas_l_sprites.sprites()
			if self.alternancia_l == 1:
				type_sprites = self.respuestas_r_sprites.sprites()	

			respuetas_temporal = []
			self.ecuacion.respuesta_correcta = self.ecuacion.generator(self.current_level)         	
			for sprite in type_sprites:
				if screen_width/4 < sprite.rect.x and sprite.rect.x < screen_width + tile_size*6:
					if self.current_level == 2:
						sprite.texto = str(random.randint(-10,10))
					else:
						sprite.texto = str(random.randint(1,10))
					respuetas_temporal.append(sprite)

			sprite = random.choice(respuetas_temporal)	
			sprite.texto = 	str(self.ecuacion.respuesta_correcta)				

	def check_death(self):
		if self.caidas > 1 and self.player.sprite.rect.top > screen_height:
			fin = time.time()
			self.create_results(self.display_surface,self.inicio,self.contador_palomas,self.contador_ecuaciones,fin,self.new_max_level,self.meta,self.nivel_dificultad)
		elif self.player.sprite.rect.top > screen_height:
			self.player.sprite.get_damage()
			self.player.sprite.direction.y = -40
			self.caidas += 1
		if self.check_game_over():
			fin = time.time()
			self.create_results(self.display_surface,self.inicio,self.contador_palomas,self.contador_ecuaciones,fin,self.new_max_level,self.meta,self.nivel_dificultad)

	def check_win(self):
		if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
			self.meta = True
			fin = time.time()
			self.create_results(self.display_surface,self.inicio,self.contador_palomas,self.contador_ecuaciones,fin,self.new_max_level,self.meta,self.nivel_dificultad)

	def check_enemy_collisions(self):
		enemy_collisions  = pygame.sprite.spritecollide(self.player.sprite,self.enemy_sprites,False)

		if enemy_collisions:
			for enemy in enemy_collisions:
				enemy_center = enemy.rect.centery
				enemy_top = enemy.rect.top 
				player_bottom = self.player.sprite.rect.bottom
				if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
					self.player.sprite.direction.y = -15
					enemy.kill()
				else:
					self.player.sprite.get_damage()

	def run(self):
		fondo = pygame.image.load(levels[self.current_level]['background']).convert_alpha()
		fondo = pygame.transform.scale(fondo, (screen_width,screen_height)) 
		self.display_surface.blit(fondo,(0,0))

		self.scroll_x()

		self.horizontal_movement_collision(self.terrain_sprites.sprites())
		self.vertical_movement_collision(self.terrain_sprites.sprites())

		self.horizontal_movement_collision(self.respuestas_r_sprites.sprites())
		self.vertical_movement_collision(self.respuestas_r_sprites.sprites())
		self.horizontal_movement_collision(self.respuestas_l_sprites.sprites())
		self.vertical_movement_collision(self.respuestas_l_sprites.sprites())

		self.display_surface.blit(self.calificacion,(screen_width/2,screen_height/2)) 	

		self.terrain_sprites.update(self.world_shift)
		self.terrain_sprites.draw(self.display_surface)

		self.ecuacion.update()
		self.ecuacion_group.draw(self.display_surface)

		self.respuestas_r_sprites.update(self.world_shift)
		self.respuestas_r_sprites.draw(self.display_surface)

		self.respuestas_l_sprites.update(self.world_shift)
		self.respuestas_l_sprites.draw(self.display_surface)

		self.enemy_sprites.update(self.world_shift)
		self.enemy_sprites.draw(self.display_surface)
		self.enemy_collision_reverse()

		self.constrains_sprites.update(self.world_shift)

		self.player.update()
		self.player.draw(self.display_surface)
		self.goal.update(self.world_shift)
		self.goal.draw(self.display_surface)

		self.check_death()
		self.check_win()
		self.check_enemy_collisions()


