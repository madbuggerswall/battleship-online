import numpy

grid = numpy.zeros(shape=(10,10))
grid[4][5] = 4
grid[4][7] = 8
grid[1][1] = 1
print(grid)

def displayGrid():
	for col in range (0, grid.shape[1]):
		print("  ", col, end='')
	print()
	for row in range(0, grid.shape[0]):
		print(row, end=": ")
		for col in range (0, grid.shape[1]):
			if grid[row][col] == 0:
				print("\x1b[0;37;44m"," ", "\x1b[0m" ,end=' ')
			if grid[row][col] == 1:
				print("\x1b[0;37;47m"," ", "\x1b[0m" ,end=' ')
			if grid[row][col] == 4:
				print("\x1b[0;37;41m","X", "\x1b[0m" ,end=' ')
			if grid[row][col] == 8:
				print("\x1b[0;37;42m","H", "\x1b[0m" ,end=' ')
		print()
		print()
		
displayGrid()