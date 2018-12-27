import sys
import socket
import pickle
import numpy
from enum import Enum

# Parent class for other pieces.
class Piece:
	def __init__(self, size, horizontal):
		self.size = size
		self.horizontal = horizontal

class Carrier(Piece):
	sign = "C"
	name = "Carrier"
	size = 5
	def __init__(self, horizontal):
		Piece.__init__(self, Carrier.size, horizontal)

class Battleship(Piece):
	sign = "B"
	name = "Battleship"
	size = 4
	def __init__(self, horizontal):
		Piece.__init__(self, Battleship.size, horizontal)

class Submarine(Piece):
	name = "Submarine"
	sign = "S"
	size = 3
	def __init__(self, horizontal):
		Piece.__init__(self, Submarine.size, horizontal)

class Destroyer(Piece):
	name = "Destroyer"
	sign = "D"
	size = 2
	def __init__(self, horizontal):
		Piece.__init__(self, Destroyer.size, horizontal)


class Player:
	# All pieces every player must place on board
	pieces = [Carrier, Battleship, Submarine, Destroyer]

	def __init__(self):
		self.isTurn = False			#	Turn to play
		self.unitCount = None		#	Number of pieces as grid units.
		self.unitsLeft = None		#	Total units - Shot units
		self.totalHits = 0			#	Number of successful hits
		self.grid = numpy.zeros(shape=(10,10))
		self.piecesPlaced = []	#	To avoid placing the same units.
	
	def placePiece(self, piece, position):
		if self.checkPosition(piece, position) and self.checkPieceRepetition(piece):
			if piece.horizontal:
				for y in range(position[1], position[1] + piece.size):
					self.grid[position[0], y] = 1
			else:
				for x in range(position[0], position[0] + piece.size):
					self.grid[x, position[1]] = 1
			self.piecesPlaced.append(type(piece))

	# Check if occuppied or out of grid boundaries.
	def checkPosition(self, piece, position):
		if piece.horizontal:
			if (position[1] + piece.size) >= numpy.size(self.grid,0):
				print("Piece is outside of the grid boundaries")
				return False
			for x in range(position[1], position[1] + piece.size):
				if self.grid[position[0], x] != 0:
					print("Area occupied")
					return False
		else:
			if (position[0] + piece.size) >= numpy.size(self.grid,1):
				print("Piece is outside of the grid boundaries")
				return False
			for y in range(position[0], position[0] + piece.size):
				if self.grid[y, position[1]] != 0:
					print("Area occupied")
					return False
		return True

	# Check if any piece of same type is already placed.
	def checkPieceRepetition(self, piece):
		if self.piecesPlaced.count(type(piece)) == 0:
			return True
		else:
			print("This type of piece has already been placed.")
			return False

	# Returns the total number of squares occupied by the pieces.
	def countUnits(self):
		count = 0
		for piece in self.piecesPlaced:
			count += piece.size
		return count
	
	# Place pieces one by one via user input.
	def initBoard(self):
		for piece in Player.pieces:
			while self.piecesPlaced.count(piece) == 0:
				print("\nPlace ", piece.name, "(", piece.size, ") on grid.")
				pos = self.getPosInput()
				self.placePiece(piece(pos[2]), (pos[0], pos[1]))
			displayGrid(self.grid)
		self.unitsLeft = self.countUnits()
		self.unitCount = self.countUnits()

	# Get position input for piece placement. (eg. 5,5,V)
	# H: Horizontal V: Vertical
	def getPosInput(self):
		while True:
			raw = input("Enter position as row,column,alignment: ")
			position = raw.split(',')
			
			if len(position) != 3:
				print("Invalid position format.")
				continue

			try:
				position[0] = int(position[0])
				position[1] = int(position[1])
			except: 
				print("First two inputs must be an integer.")
				continue
		
			if position[2] == "H" or position[2] == "h":
				position[2] = True
			elif position[2] == "V" or position[2] == "v":
				position[2] = False
			else:
				print("Last input must be H or V")
				continue
			break
		return position
	
	# Get shot position input (eg. 5,5)
	def getShotInput(self):
		while True:
			raw = input("Enter the shot coordinates as row,column: ")
			position = raw.split(',')
			
			if len(position) != 2:
				print("Invalid position format.")
				continue

			try:
				position[0] = int(position[0])
				position[1] = int(position[1])
			except: 
				print("Inputs must be an integer.")
				continue

			if position[0] > 9 or position[1] > 9:
				print("Position outside of the grid")
			break
		return position
	
# End of classes

#	Colorfully display grid
def displayGrid(grid):
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
		print("\n")

# Handles shot send/recv operations.
def shootByTurns(player, connection, hostName,opponentName):
	isGameOver = False
	opponentGrid = numpy.zeros(shape=(10,10))

	while not(isGameOver):
		while player.isTurn and not(isGameOver):
			# Get shoot position from player.
			shotPos = player.getShotInput()

			# Send position to opponent.
			connection.send(pickle.dumps(shotPos))

			# Opponent sends back whether the sent position was a hit or not.
			hitOrMiss = pickle.loads(connection.recv(1024))

			# If it is a hit player gets to shoot one more time.
			if hitOrMiss == 1:
				opponentGrid[shotPos[0]][shotPos[1]] = 8
				print("\n", opponentName, "'s Grid", "\n", sep="")
				displayGrid(opponentGrid)
				player.totalHits += 1
				if player.totalHits >= player.unitCount:
					print(hostName, " won!")
					isGameOver = True
					player.isTurn = False
				continue
			elif hitOrMiss == 0: 
				# If it's not a hit, player's turn ends.
				opponentGrid[shotPos[0]][shotPos[1]] = 4
				player.isTurn = False
				print("\n", opponentName, "'s Grid", "\n", sep="")
				displayGrid(opponentGrid)
				print("\nWaiting for ", opponentName, ".\n", sep="")
			else:
				print("Shot already made.")
				continue
			
		while not(player.isTurn) and not(isGameOver):
			shotRecieved = pickle.loads(connection.recv(1024))
			
			# Check if shot made by opponent was a hit or not, send back the result.
			if player.grid[shotRecieved[0]][shotRecieved[1]] == 1:
				player.grid[shotRecieved[0]][shotRecieved[1]] = 8
				player.unitsLeft -= 1
				if player.unitsLeft <= 0:
					print(hostName,"lost!")
					isGameOver = True
				connection.send(pickle.dumps(1))
			elif player.grid[shotRecieved[0]][shotRecieved[1]] == 4:
				connection.send(pickle.dumps(2))
			elif player.grid[shotRecieved[0]][shotRecieved[1]] == 8:
				connection.send(pickle.dumps(2))
			else:
				# If it's not a hit, player's turn begins.
				player.grid[shotRecieved[0]][shotRecieved[1]] = 4
				connection.send(pickle.dumps(0))
				player.isTurn = True
			print("\n", hostName,"'s Grid", "\n", sep="")
			displayGrid(player.grid)

# Handling the command line arguments
isHost = False 
if len(sys.argv) == 2:
	isHost = True
	port = int(sys.argv[1])
elif len(sys.argv) == 3:
	hostIP = sys.argv[1]
	port = int(sys.argv[2])
else:
	print("Invalid arguments.")
	sys.exit()

hostName = input("Please enter your name: ")
opponentName = None

# Host player
if(isHost):
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.bind((socket.gethostname(), port))
	serverSocket.listen(1)

	print("Waiting for player...\n")
	(connection, clientAddress) = serverSocket.accept()

	connection.send(pickle.dumps(hostName))
	opponentName = pickle.loads(connection.recv(1024))

	print("Player connected! Address:", clientAddress, "\n")
	print("Opponent name:", opponentName, "\n")

	hostPlayer = Player()
	hostPlayer.initBoard()
	hostPlayer.isTurn = True

	shootByTurns(hostPlayer, connection, hostName, opponentName)
	connection.close()
else:
# Client player
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverAddress = hostIP, port
	clientSocket.connect(serverAddress)

	clientSocket.send(pickle.dumps(hostName))
	opponentName = pickle.loads(clientSocket.recv(1024))
	
	print("Player connected! Address:", serverAddress, "\n")
	print("Opponent name:", opponentName, "\n")

	clientPlayer = Player()
	clientPlayer.initBoard()

	shootByTurns(clientPlayer, clientSocket, hostName, opponentName)
	clientSocket.close()
