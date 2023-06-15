import pygame, sys
from settings import *
from level import Level
from overworld import Overworld

class Game:
	def __init__(self):
		self.max_level = 2
		self.overworld = Overworld(0,self.max_level,screen)

	def run(self):
		self.overworld.run()	

pygame.init()
pygame.display.set_caption("Mathison begins")
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
level0 = Level(level_map0,screen,number_level0)

game = Game()

#level2 = Level(level_map2,screen)
fondo = pygame.image.load("imagenes/cyberpunk.jpeg").convert_alpha()
fondo = pygame.transform.scale(fondo, (screen_width,screen_height))
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	#screen.fill((204,255,255))
	screen.blit(fondo,(0,0))
	#game.run()
	level0.run()

	pygame.display.update()
	clock.tick(60)	

