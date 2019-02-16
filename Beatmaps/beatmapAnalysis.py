import json
from pprint import pprint
from pymongo import MongoClient
from collections import defaultdict, Counter
from operator import itemgetter

client = MongoClient("mongodb://localhost:27017")
db = client['Beatmaps']


### find each approved status
# 4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
def getCounts(collection):
	loved_count     = collection.count_documents({"approved": 4})
	qualified_count = collection.count_documents({"approved": 3})
	approved_count  = collection.count_documents({"approved": 2})
	ranked_count    = collection.count_documents({"approved": 1})
	pending_count   = collection.count_documents({"approved": 0})
	WIP_count       = collection.count_documents({"approved": -1})
	graveyard_count = collection.count_documents({"approved": -2})
	total_count     = collection.count_documents({})
	### sum check
	total_check = loved_count + qualified_count + approved_count + ranked_count + pending_count + WIP_count + graveyard_count
	if total_check != total_count:
		raise ValueError("Total is comming out wrong.")

	return """
	Loved Count:      %s
	Qualified Count:  %s
	Approved Count:   %s
	Ranked Count:     %s
	Pending Count:    %s
	WIP Count:        %s
	Graveyard Count:  %s
	Total Count:      %s
	""" % (loved_count, qualified_count, approved_count, ranked_count, pending_count, WIP_count, graveyard_count, total_count)


# print(getCounts(db['standard']))

##### USE NLTK
# def getVersionData(collection, approved_status=1):
# 	""" function to find version data
# 	"""
# 	# 'light'

# 	version_data_cursor = collection.find({'approved': approved_status}) 
# 		# projection={'version': 1, '_id': 0})
	
# 	version_data = [doc['version'] for doc in version_data_cursor]
# 	# print(version_data)

# 	difficulties = ['easy', 'normal', 'hard', 'insane', 'extra', 'extreme', 'expert', 
# 	'advanced', 'ultra', 'lunatic', 'hyper', 'standard', 'master', 'simple', 'special', 'forever', 
# 	'ultimate', 'another', 'beginner', 'difficult', 'challen', 'heavy', 'calm', 'belief', 
# 	'marathon', 'light', 'medium', 'basic', 'exhaust', 'novice', 'kagerou', 'peace',
# 	'infinite', 'relax', 'tough', 'nightmare', 'supreme', 'dangerous', 'safe', 'kantan', 
# 	'maximum',
# 	'intermediate']
# 	difficulty_dict = defaultdict(int)
# 	unknowns = []
# 	for ver in version_data:
# 		for diff in difficulties:
# 			if diff in ver.lower():
# 				difficulty_dict[diff] += 1
# 				break
# 			else:
# 				if diff == 'intermediate':
# 					unknowns.append(ver)
# 					difficulty_dict['None'] += 1


# 	pprint(sorted(unknowns))
# 	print()
# 	pprint(difficulty_dict)
# 	print(len(version_data))


def getDiffData(collection, diff, approved_status=1):
	"""
	# "diff_size"        : "4",           // Circle size value (CS)
	# "diff_overall"     : "6",           // Overall difficulty (OD)
	# "diff_approach"    : "7",           // Approach Rate (AR)
	# "diff_drain"       : "6",           // Healthdrain (HP)
	"""
	diff_data = []
	diff_data_cursor = collection.find({'approved': approved_status})

	diff_data = [doc[diff] for doc in diff_data_cursor]
	diff_data_count = Counter(diff_data)

	#print(diff_data)
	print(max(diff_data))
	print(min(diff_data))
	pprint(diff_data_count)
	print()


# getDiffData(collection=db['standard'], diff='diff_size')
# exit()



def getGenreData(collection, approved_status=1):
	""" function to find the frequency of genre of beatmap for a specified collection
	 0 = any, 1 = unspecified, 2 = video game, 3 = anime,
	 4 = rock, 5 = pop, 6 = other, 7 = novelty, 9 = hip hop, 
	 10 = electronic (note that there's no 8)
	"""
	# print("===== GENRE DATA =====")
	count_dict = {}
	total_check = 0
	genres = ['any', 'unspecified', 'video_game', 'anime', 'rock', 'pop', 'other', 'novelty', None, 'hip_hop', 'electronic']
	for genre in genres:
		if genre is not None:
			index = genres.index(genre)
			count = collection.count_documents({'approved': approved_status, 'genre_id': index})
			count_dict[genre] = count
			total_check += count

	total_count = collection.count_documents({'approved': approved_status})
	count_dict['total_count'] = total_count 
	count_dict['total_count_check'] = total_check

	return count_dict



def getLangData(collection, approved_status=1):
	""" function to find the frequency of langauge of beatmap for a specified collection
	0 = any, 1 = other, 2 = english, 3 = japanese, 
	4 = chinese, 5 = instrumental, 6 = korean, 7 = french, 
	8 = german, 9 = swedish, 10 = spanish, 11 = italian
	"""
	# print("===== LANGUAGE DATA =====")
	count_dict = {}
	total_check = 0
	languages = ['any', 'other', 'english', 'japanese', 'chinese', 'instrumental', 'korean', 'french', 'german', 'swedish', 'spanish', 'italian']
	for lang in languages:
		index = languages.index(lang)
		count = collection.count_documents({'approved': approved_status, 'language_id': index})
		count_dict[lang] = count
		total_check += count
	
	total_count = collection.count_documents({'approved': approved_status})
	count_dict['total_count'] = total_count 
	count_dict['total_count_check'] = total_check

	return count_dict



# pprint(getGenreData(collection=db['standard']))
# print()
# pprint(getLangData(collection=db['standard']))


def getSort(collection, field, approved_status=1, amount=10):
	"""
	one edge-case: when field == favourite_count; you can only favourite a beatmapset not a specific beatmap
	"""
	ascending_cursor = collection.aggregate([
		{"$match": {"approved": 1}},
		{"$sort": {field: -1}} ], 
		allowDiskUse=True)
	descending_cursor = collection.aggregate([
		{"$match": {"approved": 1}},
		{"$sort": {field: 1}} ], 
		allowDiskUse=True)

	if field == "favourite_count": # edge-case
		greatest = []
		for doc in ascending_cursor:
			if amount > 0: # amount will decrease each time a doc is appended to greatest
				current_beatmapsets = [i['beatmapset_id'] for i in greatest]
				if doc['beatmapset_id'] not in current_beatmapsets:
					greatest.append(doc)
					amount -= 1
		least = [] # doesn't really matter
	else: # normal
		greatest = list(ascending_cursor)[:amount] # gets the top 10 (or however many amount) docs
		least = list(descending_cursor)[:amount]

	return [greatest, least]


# build on to this function
# get all beatmapdata for each map, get username
def getCreatorData(collection, approved_status=1, amount=25):
	"""
	function finds the creaters with the most maps
	"""
	### see if each set contains 1 single unique id
	### limit to one map per beatmapset?
	creator_data = {'set_count': [], 'map_count': []}
	creator_count_set = defaultdict(int) # counts 1 per set
	creator_count_map = defaultdict(int) # counts 1 per map
	used_beatmapsets = []
	for doc in collection.find({'approved': approved_status}):
		beatmap_set = doc['beatmapset_id']
		creator_id = doc['creator_id']
		if beatmap_set not in used_beatmapsets:
			used_beatmapsets.append(beatmap_set)
			creator_count_set[creator_id] += 1

		creator_count_map[creator_id] += 1

	amount_copy = amount

	### set_count
	for creator, count in sorted(creator_count_set.items(), key=itemgetter(1), reverse=True):
		if amount > 0:
			creator_data['set_count'].append({creator: count})
			amount -= 1
		else:
			break

	### map_count
	for creator, count in sorted(creator_count_map.items(), key=itemgetter(1), reverse=True):
		if amount_copy > 0:
			creator_data['map_count'].append({creator: count})
			amount_copy -= 1
		else:
			break

	return creator_data



def updateAll():
	"""
	writes all analysis data to files
	"""
	client = MongoClient("mongodb://localhost:27017")
	db = client['Beatmaps']

	fields = ['difficultyrating', 'total_length', 'hit_length', 
	'diff_size', 'diff_overall', 'diff_drain', 'diff_approach',
	'max_combo', 'favourite_count', 'playcount', 'passcount']


	modes = ['standard', 'taiko', 'catch', 'mania']
	for mode in modes:
		collection = db[mode]

		### genre data
		genre_file = 'beatmap_data/' + mode + '/' + 'genre' + '.json'
		with open(genre_file, 'w+') as fo:
			genre_data = getGenreData(collection=collection)
			json.dump(genre_data, fo, indent=4)
		print("Finished writing genre data to file! ({})".format(mode))

		### language data
		lang_file = 'beatmap_data/' + mode + '/' + 'language' + '.json'
		with open(lang_file, 'w+') as fo:
			lang_data = getLangData(collection=collection)
			json.dump(lang_data, fo, indent=4)
		print("Finsihed writing lang data to file! ({})".format(mode))

		### creator data
		creator_file = 'beatmap_data/' + mode + '/' + 'creators' + '.json'
		with open(creator_file, 'w+') as fo:
			creator_data = getCreatorData(collection=collection)
			json.dump(creator_data, fo, indent=4)
		print("Finsihed writing creator data to file! ({})".format(mode))

		### the fields ('difficultyrating', 'total_length', 'max_combo', 'favourite_count', 'playcount', 'passcount')
		for field in fields:
			# either both ascending & desending, or just ascending
			if 'count' in field: # this means we only need the ascended (greatest) from the sort (favourite_count, playcount, passcount)
				### file path and name
				file = 'beatmap_data/' + mode + '/' + field + '.json'

				### assigning data
				max_data = getSort(collection=collection, field=field)[0]

				### removing '_id' key (b/c of TypeError: Object of type ObjectId is not JSON serializable)
				for i in range(len(max_data)):
					del max_data[i]['_id']

				data_dict = {'max_data': max_data}

				### writing data to file
				with open(file, 'w+') as fo:
					json.dump(data_dict, fo, indent=4)
				print("Finished writing {} data to file! ({})".format(field, mode))
			else:
				### file path and name
				file = 'beatmap_data/' + mode + '/' + field + '.json'

				### assigning data
				max_data = getSort(collection=collection, field=field)[0]
				min_data = getSort(collection=collection, field=field)[1]

				### removing '_id' key
				for i in range(len(max_data)):
					del max_data[i]['_id']

				for i in range(len(min_data)):
					del min_data[i]['_id']

				data_dict = {'max_data': max_data, 'min_data': min_data}

				### writing data to file
				with open(file, 'w+') as fo:
					json.dump(data_dict, fo, indent=4)
				print("Finished writing {} data to file! ({})".format(field, mode))


	print("Done writing all data to files!!!")


if __name__ == "__main__":
	updateAll()



############### 
# ---- RANKED MAPS -----
# difficulty rating (stars {float})
# 	- most difficult maps
# 	- least difficult maps
# length & hit_length (seconds)
# 	- longest maps
#	- shortst maps
# combo (int)
# 	- longest combo maps
# 	- shortest combo maps
# favourite count (int)
# 	- most favourited maps
# play count (int)	
#	- most played maps
# pass count (int)
#	- most passed maps
# creator (str)
#	- creator with the most maps


# TODO'S
# version frequency (regx normal, easy, etc) (USE NLTK)
# difficulty frequency (pie charts, histograms)
	# "diff_size"        : "4",           // Circle size value (CS)
	# "diff_overall"     : "6",           // Overall difficulty (OD)
	# "diff_approach"    : "7",           // Approach Rate (AR)
	# "diff_drain"       : "6",           // Healthdrain (HP)
# bpm frequency (x-y plot, piechart? histo?)
# language / genre / creator / etc frequency (pie charts)
# approved beatmaps per month / year
# analyze 'tags'



# bpm_data = getSort(db.standard, "bpm")
# hightest_bpm_maps = bpm_data[0]
# lowest_bpm_maps = bpm_data[1]
# pprint(lowest_bpm_maps[0])