import sys
import socket
import pickle
import numpy

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
		
			if position[2] == "H":
				position[2] = True
			elif position[2] == "V":
				position[2] = False
			else:
				print("Last input must be H or V")
				continue
			break
		return position

	def shoot(self):
		pass

	def getShotInput(self):
		while True:
			raw = input("Enter the shot coordinates as row,column")
			position = raw.split(',')
			
			if len(position) != 3:
				print("Invalid position format.")
				continue

			if position[0] > 9 or position[1] > 9:
				print("Position outside of the grid")

			try:
				position[0] = int(position[0])
				position[1] = int(position[1])
			except: 
				print("Inputs must be an integer.")
				continue
			break
		return position

class GameSession:

	def __init__(self):
		self.hostReady = False
		self.clientReady = False

		self.hostUnits = 14
		self.clientUnits = 14

		self.hostGrid = numpy.zeros(shape=(10,10))
		self.clientGrid = numpy.zeros(shape=(10,10))


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

piece = Piece(10, False)
pieceData = pickle.dumps(piece)

gameSession = GameSession()

if(isHost):
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.bind((socket.gethostname(), port))
	serverSocket.listen(1)

	print("Waiting for player...")
	(connection, clientAddress) = serverSocket.accept()
	print("Player connected! Address: ", clientAddress)

	hostPlayer = Player()
	hostPlayer.initBoard()
	gameSession.hostReady = True
	gameSessionData = pickle.dumps(gameSession)
	connection.send(gameSessionData)
	gameSessionData = connection.recv(1024)
	gameSession = pickle.loads(gameSessionData)

	print(gameSession.hostReady)
	print(gameSession.clientReady)

	while True:
		connection.send(pieceData)
		connection.recv(1024)
	connection.close()
else:
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverAddress = hostIP, port
	clientSocket.connect(serverAddress)

	clientPlayer = Player()
	clientPlayer.initBoard()
	gameSession.clientReady = True
	gameSessionData = pickle.dumps(gameSession)
	clientSocket.send(gameSessionData)
	gameSessionData = clientSocket.recv(1024)
	gameSession = pickle.loads(gameSessionData)

	print(gameSession.hostReady)
	print(gameSession.clientReady)

	# while True:
	# 	dataRecieved = clientSocket.recv(1024)
	# 	dataInstance = pickle.loads(dataRecieved)
	# 	print(dataInstance.size)
	# 	print(type(dataInstance))
