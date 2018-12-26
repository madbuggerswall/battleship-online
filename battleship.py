import socket
import numpy
import sys

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

	pieces = [Carrier, Battleship, Submarine, Destroyer]

	def __init__(self):
		self.isConnected = False
		self.isReady = False
		self.grid = numpy.zeros(shape=(10,10))
		self.piecesPlaced = []
	
	def placePiece(self, piece, position):
		if self.checkPosition(piece, position) and self.checkPieces(piece):
			if piece.horizontal:
				for y in range(position[1], position[1] + piece.size):
					self.grid[position[0], y] = 1
			else:
				for x in range(position[0], position[0] + piece.size):
					self.grid[x, position[1]] = 1
			self.piecesPlaced.append(type(piece))


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

	def checkPieces(self, piece):
		if self.piecesPlaced.count(type(piece)) == 0:
			return True
		else:
			print("This type of piece has already been placed.")
			return False
		#  return self.piecesPlaced.count(type(piece)) == 0
	
	def initBoard(self):
		for piece in Player.pieces:
			while self.piecesPlaced.count(piece) == 0:
				print("Place ", piece.name, "(", piece.size, ") on grid")
				pos = self.getPosInput()
				self.placePiece(piece(pos[2]), (pos[0], pos[1]))
			print(self.grid)

	def getPosInput(self):
		isValid = False
		while not(isValid):
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
		
			if position[2] == "H":
				position[2] = True
			elif position[2] == "V":
				position[2] = False
			else:
				print("Last input must be H or V")
				continue
			isValid = True
		return position

class Game:
	pass

	
if len(sys.argv) == 2:
	isHost = True
	port = int(sys.argv[1])
elif len(sys.argv) == 3:
	hostIP = sys.argv[1]
	port = int(sys.argv[2])
else:
	print("Invalid arguments.")
	sys.exit()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((socket.gethostname(), port))
serverSocket.listen(1)

(clientSocket, clientAddress) = serverSocket.accept()
print("Player connected! Address: ", clientAddress)

player = Player()
player.initBoard()


# while True:
# 	clientSocket.sendall(b"Hello client")
# 	clientSocket.recv(1024)
# clientSocket.close()


