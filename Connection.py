from pymongo import MongoClient

# username = ""
# password = ""
# host = ""
# client = MongoClient("mongodb://%s:%s@%s:27017" % (username, password, host))

class Connection():

	dbs = ['TopPlays', 'Beatmaps', 'TopPlayersAPI', 'TopPlayerScrape', 'TopPlayersCountry']
	db = None
	collection = None

	def __init__(self, localConnection):
		self.localConnection = localConnection

		if localConnection:
			self.client = MongoClient("mongodb://localhost:27017")

	@staticmethod
	def validDB(db):
		if db in Connection.dbs:
			return True
		else:
			return False

	@staticmethod
	def validCollection(collection):
		return True

	def setDB(self, db):
		if Connection.validDB(db):
			self.db = self.client[db]
			print("DB has been set to {}".format(db))
		else:
			return None

	def setCollection(self, collection):
		if Connection.validCollection(collection):
			pass
		else:
			return None

	# def testConnection(self):
	# 	try: 
	# 		db.command("serverStatus")
	# 	except Exception as e: 
	# 		print(e)
	# 	else: 
	# 		print("You are connected.")


connection = Connection(localConnection=True)
connection.setDB('Beatmaps')
connection.setCollection('Standard')
# print(connection)
db = connection.db  
collection = db.collection
exit()
