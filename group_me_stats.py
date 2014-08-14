'''
Call format: 
	python group_me_stats.py [name of file containing access_token] [-option] [groupID]
	options:
		-g = prints id and name of all groups
		-f = prints texting frequency of each person
		-w = prints top 20 commonly used words
		-c = prints top 20 comments based on number of likes
*note that -g should not have a groupID parameter while all the others must have groupID param

'''

import requests, json, re, sys, optparse
from collections import defaultdict

def printGroupsAndID():
	''' Prints ID and name of all groups. '''

	url = '/groups'
	req = requests.get(base_url+url, params=params)
	if req.status_code == 200:
		print "\nPrinting All Groups (ID and Name)...\n"
		for message in req.json()['response']:
			print "ID = %s  Name = %s" % (message['id'], message['name'])
	else:
		print "Error: %s" % str(req)

def printTextingFrequency(groupID):
	''' Prints how many texts each person sent in the group specified by groupID. '''

	print "\nPrinting Texting Frequency for Each Person from Group %s...\n" % groupID
	url = '/groups/%s/messages' % groupID
	frequency = defaultdict(int)
	params['limit'] = 100 # Can't get more than 100 messages at a time.
	req = requests.get(base_url + url, params=params)
	
	while (req.status_code == 200): # Returns code 304 if no more messages to return.
		for message in req.json()['response']['messages']:
			frequency[message['name']] += 1
			latest_message_id = message['id']

		params['before_id'] = latest_message_id
		req = requests.get(base_url + url, params=params)

	if req.status_code == 304 or req.status_code == 200:
		frequency_list = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
		for person in frequency_list:
			if person[1] == 1:
				print "%s text from %s" % (person[1], person[0])
			else:
				print "%s texts from %s" % (person[1], person[0])
	else:
		print "Error: %s. Possibly invalid group ID." % str(req)

def printTopTwentyCommonlyUsedWords(groupID):
	''' Prints the top 20 commonly texted word in the group specified by groupID. '''

	print "\nPrinting Top Twenty Commonly Used Words from Group %s...\n" % groupID
	url = '/groups/%s/messages' % groupID
	top_words = defaultdict(int)
	params['limit'] = 100
	req = requests.get(base_url + url, params=params)

	while (req.status_code == 200): # Returns code 304 if no more messages to return.
		for message in req.json()['response']['messages']:
			if message['text'] is not None:
				words = re.compile('\w+').findall(message['text'])
				for word in words:
					top_words[word] += 1
			latest_message_id = message['id']

		params['before_id'] = latest_message_id
		req = requests.get(base_url + url, params=params)
	
	if req.status_code == 304 or req.status_code == 200:
		top_words_list = sorted(top_words.items(), key=lambda x:x[1], reverse=True)[:20]
		for word in top_words_list:
			print "\"%s\" - %s times." % (word[0], word[1])
	else:
		print "Error: %s. Possibly invalid group ID." % str(req)

def printTopTwentyComments(groupID):
	''' Prints the top 20 comments with the most likes. 
		Printing format example: 
			[# likes] - [name]: [text] [URL attachment]
	'''

	print "\nPrinting Top 20 Comments from Group %s...\n" % groupID
	url = '/groups/%s/messages' % groupID
	params['limit'] = 100
	req = requests.get(base_url + url, params=params)
	texts = defaultdict(list)

	while (req.status_code == 200):
		for message in req.json()['response']['messages']:
			number_of_likes = len(message['favorited_by'])
			if number_of_likes > 0:
				texts[message['id']] += [message['name']]
				texts[message['id']] += [number_of_likes]
				texts[message['id']] += [message['text']] if message['text'] is not None else []
				if len(message['attachments']) > 0 and 'url' in message['attachments'][0]:
					texts[message['id']] += [message['attachments'][0]['url']]
			latest_message_id = message['id']
		params['before_id'] = latest_message_id
		req = requests.get(base_url + url, params=params)
	if req.status_code == 304 or req.status_code == 200:
		texts_list = sorted(texts.items(), key=lambda x:x[1][1], reverse=True)[:20]
		for text in texts_list:
			if len(text[1]) == 4:
				if text[1][2][-4:] == '.mp4':
					print "%s likes - %s: \"%s\"" % (text[1][1], text[1][0], text[1][2])
				else:
					print "%s likes - %s: \"%s\" %s" % (text[1][1], text[1][0], text[1][2], text[1][3])
			elif len(text[1]) == 3:
				if text[1][2][:4] == 'http':
					print "%s likes - %s: %s" % (text[1][1], text[1][0], text[1][2])
				else:
					print "%s likes - %s: \"%s\"" % (text[1][1], text[1][0], text[1][2])
	else: 
		print "Error: %s. Possibly invalid group ID." % str(req)

if len(sys.argv) > 2:
	try:
		with open(sys.argv[1]) as f:
			data = f.read().rstrip()
			access_token = data
	except EnvironmentError:
		sys.exit("Invalid file. Try again.")

	params = {'token':access_token}
	base_url = 'https://api.groupme.com/v3'
	if len(sys.argv) == 3:
		if sys.argv[2] == '-g':
			printGroupsAndID()
		else:
			print "Invalid option %s. Expected -g." % sys.argv[2]
	elif len(sys.argv) == 4:
		optparser = optparse.OptionParser()
		optparser.add_option('-f','--frequency', action='store_true', default=False)
		optparser.add_option('-w','--words', action='store_true', default=False)
		optparser.add_option('-c','--comments', action='store_true', default=False)
		options, args = optparser.parse_args()
		if options.frequency:
			printTextingFrequency(sys.argv[3])
		elif options.words:
			printTopTwentyCommonlyUsedWords(sys.argv[3])
		elif options.comments:
			printTopTwentyComments(sys.argv[3])
		else:
			print "Invalid option."
