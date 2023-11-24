import pygame
from game_data import *

class Node(pygame.sprite.Sprite):
	def __init__(self,pos,status,icon_speed,path):
		super().__init__()
		self.image = pygame.image.load(path).convert_alpha()
		self.image = pygame.transform.scale(self.image, (200,150))
		if status == 'available':	
			self.status = 'available'
		else:
			self.status = 'locked'	
		self.rect = self.image.get_rect(center = pos)

		self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed/2),self.rect.centery - (icon_speed/2),icon_speed,icon_speed)

	def update(self):
		if self.status == 'locked':
			tint_surf = self.image.copy()
			tint_surf.fill('blue',None,pygame.BLEND_RGBA_MULT)
			self.image.blit(tint_surf,(0,0))
		

class Icon(pygame.sprite.Sprite):
	def __init__(self,pos):
		super().__init__()
		self.pos = pos		
		self.image = pygame.image.load('imagenes/manzana.png').convert_alpha()
		self.image = pygame.transform.scale(self.image, (60,60))
		#self.image.fill('blue')
		self.rect = self.image.get_rect(center = pos)
	
	def update(self):
		self.rect.center = self.pos

class Overworld:
	def __init__(self, start_level,max_level,surface,create_level,create_dificultad,nivel_dificultad):
		self.display_surface = surface
		self.max_level = max_level
		self.current_level = start_level
		self.create_level = create_level
		self.create_dificultad = create_dificultad
		self.nivel_dificultad = nivel_dificultad

		#movement logic
		self.moving = False
		self.move_direction = pygame.math.Vector2(0,0)
		self.speed = 8

		#sprites
		self.setup_nodes()
		self.setup_icon()

	def setup_nodes(self):
		self.nodes = pygame.sprite.Group()
		
		for index, node_data in enumerate(levels.values()):
			if index <= self.max_level:
				node_sprite = Node(node_data['node_pos'],'available',self.speed,node_data['node_graphics'])
			else:
				node_sprite = Node(node_data['node_pos'],'locked',self.speed,node_data['node_graphics'])	
			self.nodes.add(node_sprite)

	def draw_paths(self):
		if self.max_level > 0:
			points = [node['node_pos'] for index,node in enumerate(levels.values()) if index<=self.max_level]
			pygame.draw.lines(self.display_surface,'red', False, points,10)
		else:
			pass

	def setup_icon(self):
		self.icon = pygame.sprite.GroupSingle()
		icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)	
		self.icon.add(icon_sprite)

	def input(self):
		keys = pygame.key.get_pressed()
		
		if not self.moving:
			if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
				self.move_direction = self.get_movement_data('next')
				self.current_level += 1
				self.moving = True
			elif keys[pygame.K_LEFT] and self.current_level > 0:
				self.move_direction = self.get_movement_data('previous')
				self.current_level -= 1	
				self.moving = True
			elif keys[pygame.K_SPACE]:
				self.create_level(self.current_level,self.nivel_dificultad)
			elif keys[pygame.K_r]:
				self.create_dificultad()		

	def get_movement_data(self,target):
		start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)
		
		if target == 'next':
			end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
		else:
			end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)

		return (end - start).normalize()

	def update_icon_pos(self):
		if self.moving and self.move_direction:
			self.icon.sprite.pos += self.move_direction * self.speed
			target_node = self.nodes.sprites()[self.current_level]
			if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
				self.moving = False
				self.move_direction = pygame.math.Vector2(0,0)
			#self.icon.sprite.rect.center = self.nodes.sprites()[self.current_level].rect.center

	def run(self):
		self.main_font = pygame.font.SysFont("tahoma", 40)
		#instrucciones1 = self.main_font.render('Presiona [SPACE] para seleccionar nivel y muevete con [LEFT] y [RIGHT]',0,'black')
		#instrucciones1_rect = instrucciones1.get_rect(center=(screen_width/2,60))
		instrucciones2 = self.main_font.render('Regresar con [R]',0,'white')
		instrucciones2_rect = instrucciones2.get_rect(center=(screen_width/2,screen_height-100))
		#instrucciones3 = self.main_font.render('Para avanzar de nivel: ¡Llega al final y ten 5 respuestas correctas!',0,'black')
		#instrucciones3_rect = instrucciones3.get_rect(center=(screen_width/2,screen_height-50))
		fondo = pygame.image.load("imagenes/fondos/mapa2.jpeg").convert_alpha()
		fondo = pygame.transform.scale(fondo, (screen_width,screen_height)) 
		self.display_surface.blit(fondo,(0,0))
		#self.display_surface.blit(instrucciones1,instrucciones1_rect)
		self.display_surface.blit(instrucciones2,instrucciones2_rect)
		#self.display_surface.blit(instrucciones3,instrucciones3_rect)
		self.input()
		self.update_icon_pos()
		self.icon.update()
		self.draw_paths()		
		self.nodes.draw(self.display_surface)
		self.nodes.update()
		self.icon.draw(self.display_surface)
			