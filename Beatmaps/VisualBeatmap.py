import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict

from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client['Beatmaps']

modes = ['standard', 'taiko', 'catch', 'mania']



def getWedgeSizes(labels, series_data):
	""""""
	sizes = []
	series_data_counts = pd.DataFrame(series_data.value_counts())
	for label in labels:
		if label is None:
			continue
		else:
			percent = 100 * (series_data_counts.loc[label][0] / len(series_data))
			sizes.append(percent)

	return sizes



def truncateData(series_data):
	"""function combines data that is less than 1% frequent w/ 'other' category
	"""
	truncated_data = series_data
	# print(type(series_data))
	difficulty_data = series_data.unique()
	count_frequency = series_data.value_counts()
	for diff in difficulty_data:
		percent = 100 * (count_frequency[diff] / len(series_data))
		if percent < 2:
			truncated_data = truncated_data.replace(diff, 'other')
		else:
			pass

	return truncated_data



### map difficulty
# display count (num of beatmaps) on graph
# do for other difficulties
def graphDifficultyFrequency(mode, difficulty_field='difficultyrating'):
	"""
	@param mode (str) - 
	@param difficulty_field (str) (optional) - 
	"difficultyrating" -->  The amount of stars the map would have ingame and on the website
	"diff_size"        -->  Circle size value (CS)
	"diff_overall"     -->  Overall difficulty (OD)
	"diff_approach"    -->  Approach Rate (AR)
	"diff_drain"       -->  Healthdrain (HP)
	"""
	if mode not in modes:
		exit("Invalid mode parameter.")

	difficulty_fields = ['difficultyrating', 'diff_size', 'diff_overall', 'diff_approach', 'diff_drain']
	if difficulty_field not in difficulty_fields:
		exit("Invalid difficulty_field")

	field_difficulties = []
	collection = db[mode]
	for doc in collection.find({'approved': 1}):
		field_difficulties.append(doc[difficulty_field])


	if difficulty_field == 'difficultyrating':
		field_difficulties = pd.Series(field_difficulties, name="Star difficulty")
		field_difficulties = field_difficulties.sort_values(ascending=False)

		ax = sns.distplot(field_difficulties, kde=False)
		ax.set_title('Frequency of Star Difficulty for {}!osu'.format(mode))
		ax.set_ylabel('Number of Beatmaps')
		# ax.legend([121], labels=['Count'])

		ax.set_xticks(np.arange(0,10,0.5))
		ax.set_xticklabels(np.array(['0', '', '1', '', '2', '', '3', '', '4', '', '5', '', '6', '', '7', '', '8', '', '9']))

		plt.show()
	elif difficulty_field == 'diff_size':
		cs_data = pd.Series(field_difficulties)#, name="Circle Size")
		cs_data = truncateData(cs_data)

		# field_difficulties = field_difficulties.sort_values(ascending=False)
		
		### pie chart
		labels = cs_data.unique()
		sizes = getWedgeSizes(labels, cs_data)
		fig1, ax1 = plt.subplots()
		ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
		        shadow=True, startangle=90)
		ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

		plt.show()


		### histogram
		# ax = sns.distplot(field_difficulties, kde=False)
		# ax.set_title('Frequency of Circle Sizes (CS) for {}!osu'.format(mode))
		# ax.set_ylabel('Number of Beatmaps')
	elif difficulty_field == 'diff_overall':
		od_data = truncateData(pd.Series(field_difficulties))

		### pie chart
		# labels = od_data.unique()
		# sizes = getWedgeSizes(labels, od_data)

		# fig1, ax1 = plt.subplots()
		# ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
		#         shadow=True, startangle=90)
		# ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.


		### historgram
		ax = sns.distplot(field_difficulties, kde=False)
		ax.set_title('Frequency of Overall Difficult (OD) for {}!osu'.format(mode))
		ax.set_ylabel('Number of Beatmaps')
		# ax.legend([121], labels=['Count'])


		plt.show()
	elif difficulty_field == 'diff_approach':
		pass
	elif difficulty_field == 'diff_drain':
		pass


# graphDifficultyFrequency(mode='standard', difficulty_field='difficultyrating')


def graphPieFrequency(mode, field, approved_status=1):
	"""
	@param field (str) - 'genre_id' or 'language_id'
	"""
	if mode not in modes:
		exit("Invalid mode parameter.")

	if field not in ['genre_id', 'language_id']:
		exit("Invalid field parameter.")

	languages = ['any', 'other', 'english', 'japanese', 'chinese', 'instrumental', 'korean', 'french', 'german', 'swedish', 'spanish', 'italian']
	genres = ['any', 'unspecified', 'video_game', 'anime', 'rock', 'pop', 'other', 'novelty', None, 'hip_hop', 'electronic']
	
	frequency_data_count = defaultdict(int)
	collection = db[mode]
	for doc in collection.find({'approved': approved_status}):
		if field == 'genre_id':
			field_name = genres[ doc[field] ]
			frequency_data_count[field_name] += 1
		if field == 'language_id':
			field_name = languages[ doc[field] ]
			frequency_data_count[field_name] += 1

		

	if field == 'genre_id':
		frequency_data_percent = {}
		length = sum(frequency_data_count.values())
		wedge_sizes = [100 * (i/length) for i in frequency_data_count.values()]

		### adding percentage to labels
		labels = []
		for i, name in enumerate(frequency_data_count.keys()):
			label_name = name + ' ' + str(round(wedge_sizes[i], 1)) + r'%'
			labels.append(label_name)

		print(labels)
		fig, texts = plt.pie(wedge_sizes, shadow=False, startangle=90)
		plt.legend(fig, labels, loc='right')
		plt.axis('equal')
		# plt.tight_layout()


		plt.show()

	elif field == 'language_id':
		pass



# graphPieFrequency('standard', field='genre_id')


def getYearTick(year, series_data):
	""""""
	year_tick = None

	series_data = series_data.unique()
	for i, data in enumerate(series_data):
		if data[:4] == year:
			year_tick = i

	return year_tick


### beatmaps ranked per month
### look at sets vs. individual maps
### multiple graphs (per year)
def beatmapRankingFrequency(mode, time_frame='month', approved_status=1):
	"""
	"approved_date"    : "2013-07-02 01:01:12", // date ranked, in UTC
	"last_update"      : "2013-07-06 16:51:22", // last update date, in UTC. May be after approved_date if map was unranked and reranked.
	"""
	ranked_dates = []
	collection = db[mode]
	for doc in collection.find({'approved': approved_status}):
		approved_date = doc['approved_date'].split(' ')[0]
		ranked_dates.append(approved_date)

	years_data = [date[:4] for date in ranked_dates]

	if time_frame == 'year':
		### ranked maps per year
		years_data = [date[:4] for date in ranked_dates]
		years_data = pd.Categorical(years_data)
		years_data = pd.Series(years_data)

		print(years_data.head())

		ax = sns.countplot(x=years_data)

		ax.set_title("Ranked Beatmaps per Year for {}!osu".format(mode))
		ax.set_ylabel("Number of Beatmaps")
		ax.set_xlabel("Year")
		plt.show()

	elif time_frame == 'quarter':
		pass
	elif time_frame == 'month':
		months_data = [date[:7] for date in ranked_dates]
		months_data = pd.Categorical(months_data)
		months_data = pd.Series(months_data)

		print(months_data.head())

		ax = sns.countplot(x=months_data)

		ax.set_title("Ranked Beatmaps per Month for {}!osu".format(mode))
		ax.set_ylabel("Number of Beatmaps")
		ax.set_xlabel("Month")

		### formatting ticks
		# x_ticks = np.full(shape=137, fill_value='')
		# for year in sorted(set(years_data)):
		# 	year_tick = getYearTick(year, months_data)
		# 	print(year_tick, year)
		# 	x_ticks[year_tick] = year
		# ax.set_xticklabels(x_ticks)

		plt.setp( ax.xaxis.get_majorticklabels() )

		plt.show()
	else:
		exit("Invalid time frame parameter.")




beatmapRankingFrequency('standard', time_frame='year')