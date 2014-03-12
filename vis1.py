import pygame
pygame.init()
import math
import sys
import random
try:
	import psyco
	psyco.full()
except ImportError:
	print 'Psyco not installed, the program will just run slower'

class Tile(object):
	
	def __init__(self, list):
		self.list = list
	
	def __getitem__(self, x):
		return self.list.__getitem__(x)
	
	def __setitem__(self, x, y):
		return self.list.__setitem__(x,y)
	
	def __len__(self):
		return len(self.list)

class World(object):
	
	def __init__(self, size):
		self.size = size
		self.rows = size[1]
		self.columns = size[0]
		## MAKE THE TILES (pixels)
		# The definition of a tile is a sequence of the following:
		# red (0-255), green (0-255), blue (0-255), x, y, changed, food, pheremone, index, above index, below index, left index, right index
		print 'MAKING TILES'
		self.grid = []
		count = 0
		for c in range(self.columns):
			for r in range(self.rows):
				self.grid.append([255, 255, 255, c, r, 1, 0, 0, count, -1, -1, -1, -1])
				count += 1
		# Set neighbours
		for t in self.grid:
			if count % 500 == 0:
				print str(count)
			count -= 1
			# down
			if t[8] % self.rows:
				t[10] = t[8]-1
			else:
				t[10] = t[8]+1
			# up
			if (t[8] + 1) % self.rows:
				t[9] = t[8]+1
			else:
				t[9] = t[8]-1
			# left
			if t[8] >= self.rows:
				t[11] = t[8] - self.rows
			else:
				t[11] = t[8] + self.rows
			#right
			if t[8] < self.rows * (self.columns - 1):
				t[12] = t[8] + self.rows
			else:
				t[12] = t[8] - self.rows
					
		print 'MADE TILES'
		self.to_draw = self.grid
		self.screen = pygame.display.set_mode(self.size)
		self.array = pygame.surfarray.pixels3d(self.screen)

	def get_draw(self, tile):
		if tile[5]:
			return True
		else:
			return False

	def draw(self):
		def draw_changed(t):
			self.array[t[3]][t[4]] = t[:3]
			t[5] = 0
		print str(len(self.to_draw))
		map(draw_changed, self.to_draw)
		#map(draw_changed, filter(self.get_draw, self.grid))
		self.to_draw = []	
	
	def check(self, tile):
		if tile[5] > 0 or tile[6] > 0 or tile[7] > 0:
			return True
		else:
			return False
	
	def tick(self):
		for t in filter(self.check, self.grid):
			t[6] *= 1.001
			if t[6] > 255:
				frac = t[6] / 5
				t[6] = frac
				try:
					self.grid[t[9]][6] += frac
				except:
					pass
				try:
					self.grid[t[10]][6] += frac
				except:
					pass
				try:
					self.grid[t[11]][6] += frac
				except:
					pass
				try:
					self.grid[t[12]][6] += frac
				except:
					pass

			t[7] *= 0.9
			t[5] = 1
			self.to_draw.append(t)
			t[0] = max(0, 255 - ((t[6]+t[7])/2))
			t[1] = max(0, 255 - (t[7]/2))
			t[2] = max(0, 255 - (t[6]/2))
	
	def get_tile(self, position):
		if position[0] < 0 or position[1] < 0 \
			or position[0] >= self.columns or position[1] >= self.rows:
			raise IndexError()
		for x, t in enumerate(self.grid):
			if t[3] == position[0] and t[4] == position[1]:
				return x

class Ant(object):
	
	def __init__(self, hill, tile):
		self.hill = hill
		self.tile = tile
		self.bias = (10,1)	# The bias is (number for, number against) following a pheremone trail
		self.bias_list = [1 for x in range(self.bias[0])]+[0 for x in range(self.bias[1])]
		self.food = False
	
	def move(self, world):
		"""Make this ant take a step."""
		# Mark the current tile as needing a redraw
		world.grid[self.tile][5] = 1
		tile = world.grid[self.tile]
		hilltile = world.grid[self.hill.tile]
		world.to_draw.append(world.grid[self.tile])
		# Reset colours
		world.grid[self.tile][0] = 255 - ((tile[6]+tile[7])/2)
		world.grid[self.tile][1] = 255 - (tile[7]/2)
		world.grid[self.tile][2] = 255 - (tile[6]/2)
		# Find neighbours
		left = world.grid[tile[11]]
		down = world.grid[tile[10]]
		right = world.grid[tile[12]]
		up = world.grid[tile[9]]

		# If we're carrying food then we need to move towards the
		# anthill
		if self.food:
			# Add some pheremone to this tile
			world.grid[self.tile][7] += 50
			# If we're above the anthill
			if tile[4] > hilltile[4]:
				# and to the right of it
				if tile[3] > hilltile[3]:
					if left[7] > 0 and down[7] == 0:
						self.tile = left[8]
					elif right[7] == 0 and down[7] > 0:
						self.tile = down[8]
					else:
						# then go either left or down (50/50 chance each)
						if random.randint(0,1):
							self.tile = left[8]
						else:
							self.tile = down[8]
				# and to the left of it
				elif tile[3] < hilltile[3]:
					if right[7] > 0 and down[7] == 0:
						self.tile = right[8]
					elif right[7] == 0 and down[7] > 0:
						self.tile = down[8]
					else:
						# then go either right or down (50/50 chance each)
						if random.randint(0,1):
							self.tile = right[8]
						else:
							self.tile = down[8]
				# and centred on it
				else:
					# then move down
					self.tile = down[8]
			# If we're below the anthill
			elif tile[4] < hilltile[4]:
				# and to the right of it
				if tile[3] > hilltile[3]:
					if left[7] > 0 and up[7] == 0:
						self.tile = left[8]
					elif left[7] == 0 and up[7] > 0:
						self.tile = up[8]
					else:
						# then either go left or up (50/50 chance each)
						if random.randint(0,1):
							self.tile = left[8]
						else:
							self.tile = up[8]
				# and we're to the left of it
				elif tile[3] < hilltile[3]:
					if right[7] > 0 and up[7] == 0:
						self.tile = right[8]
					elif right[7] == 0 and up[7] > 0:
						self.tile = up[8]
					else:
						# then either go right or up (50/50 chance each)
						if random.randint(0,1):
							self.tile = right[8]
						else:
							self.tile = up[8]
				# or we're centred on it
				else:
					self.tile = up[8]
			# If we're at the same height as the anthill
			else:
				# and right of it
				if tile[3] > hilltile[3]:
					# then move left
					self.tile = left[8]
				# or left of it
				elif tile[3] < hilltile[3]:
					# then move right
					self.tile = right[8]
				# or in the same place as it
				else:
					# give our food to the anthill
					self.hill.size += 2
					self.food = False
		else:
			if tile[7] > 0:
				#bias-list = [1 for x in range(self.bias[0]*int(self.tile.pheremone))]+[
				if self.bias_list[random.randint(0, len(self.bias_list) - 1)]:
					poss = []
					if tile[3] > hilltile[3]:
						# We're on the right of the hill
						poss.append(right[8])
					elif tile[3] < hilltile[3]:
						# We're on the left of the hill
						poss.append(left[8])
					if tile[4] > hilltile[4]:
						# We're above the hill
						poss.append(up[8])
					elif tile[4] < hilltile[4]:
						# We're below the hill:
						poss.append(down[8])
					if len(poss) == 0:
						self.tile = [up[8], down[8], left[8], right[8]][random.randint(0, 3)]
						return
					else:
						self.tile = poss[random.randint(0, len(poss)-1)]
						return
			self.tile = [up[8], down[8], left[8], right[8]][random.randint(0, 3)]
	
	def tick(self, world):
		if self.food:
			self.move(world)
		else:
			if world.grid[self.tile][6] > 0:
				self.food = True
				world.grid[self.tile][6] -= 1
			else:
				self.move(world)
		
class Anthill(object):
	
	def __init__(self, world, tile, size):
		self.world = world
		self.tile = tile
		self.size = size
		self.ants = []
		
	def radius(self):
		return (self.size/math.pi)**0.5
	
	def draw(self, screen):
		pygame.draw.circle(screen, (128, 64, 0), self.centre(), int(self.radius()))
		for ant in self.ants:
			self.world.to_draw.append(self.world.grid[ant.tile])
			self.world.grid[ant.tile][0] = self.world.grid[ant.tile][1] = self.world.grid[ant.tile][2] = 0

	def centre(self):
		return (world.grid[self.tile][3], \
			world.grid[self.tile][4])
	
	def tick(self):
		for ant in self.ants:
			ant.tick(self.world)
			ant.move(self.world)
		if self.size > 200:
			self.ants.append(Ant(self, self.tile))
			self.size -= 2
		


if __name__ == '__main__':
	size = (320, 240)
	world = World(size)
	hill = Anthill(world, world.get_tile((size[0]/2, size[1]/2)), 250)
	count = 0
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
		if pygame.mouse.get_pressed()[0]:
			world.grid[world.get_tile(pygame.mouse.get_pos())][6] += 50
		world.tick()
		world.draw()
		hill.tick()
		hill.draw(world.screen)
		#sys.stdout.write('.')
		#sys.stdout.flush()
		if count % 10:
			pygame.display.update()
			count = 0
		count += 1
