def getAccuracy(mode, count_dict):
	""" function manually calculates the accuracy of a play, given its mode
	and (count_dict), each mode is specific and unique in the way accuracy is calculated
	also the API variable naming really doesn't help and can be confusing 
	# formulas from https://osu.ppy.sh/help/wiki/Accuracy
	"""
	num_0 = int(count_dict["countmiss"])
	num_50 = int(count_dict["count50"])
	num_100 = int(count_dict["count100"])
	num_300 = int(count_dict["count300"])
	num_katu = int(count_dict["countkatu"])
	num_geki = int(count_dict["countgeki"])

	if mode == 0: # standard osu!
		numerator = (50 * num_50) + (100 * num_100) + (300 * num_300)
		denominator = 300 * (num_0 + num_50 + num_100 + num_300)
		accuracy = numerator / denominator
		return accuracy
	elif mode == 1: # taiko
		numerator = (0.5 * num_100) + (num_300)
		denominator = (num_0 + num_100 + num_300)
		accuracy = numerator / denominator
		return accuracy
	elif mode == 2: # catch
		"""Note for API users: To calculate the accuracy in osu!catch,
		 number of droplets are under count50 and number of missed droplets are under countkatu."""
		numerator = num_50 + num_100 + num_300
		denominator = num_katu + num_0 + num_50 + num_100 + num_300
		accuracy = numerator / denominator
		return accuracy
	elif mode == 3: # mania
		numerator = (50 * num_50) + (100 * num_100) + (200 * num_katu) + (300 * (num_300 + num_geki))
		denominator = (300 * (num_0 + num_50 + num_100 + num_katu + num_300 + num_geki))
		accuracy = numerator / denominator
		return accuracy