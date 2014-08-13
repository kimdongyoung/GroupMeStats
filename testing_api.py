import requests, json, re
from collections import defaultdict

# Get number of groupme messages for each user
# Get top word said in the groupme
# Most frequently said word by each person.

access_token = 'c3e245d004a5013206260270db3b2a1e' # Taken directly from the applications page.
base_url = 'https://api.groupme.com/v3'
PADT_groupID = '5621136'
ROOMMATES_groupID = '5663412'

# Return a frequency dictionary with key=name, value=number of messages
# Also return a dictionary of the top ten most used word
def test(groupID, count):
	url = '/groups/%s/messages' % groupID
	params = {'token':access_token}
	num = 0
	frequency = defaultdict(int)
	top_words = defaultdict(int)

	while (count > 0):
		params['limit'] = count if count < 100 else 100
		req = requests.get(base_url + url, params=params)
		
		if (req.status_code == 304):
			break # No more messages; exit.

		for message in req.json()['response']['messages']:
			# print "%s: \"%s\"" % (message['name'], message['text'])
			frequency[message['name']] += 1
			if message['text'] is not None:
				words = re.compile('\w+').findall(message['text'])
				for word in words:
					top_words[word] += 1
			latest_message_id = message['id']

		params['before_id'] = latest_message_id		
		count -= 100
	
	frequency_list = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
	top_words_list = sorted(top_words.items(), key=lambda x:x[1], reverse=True)[:25]

	for person in frequency_list:
		print "%s texted %s times." % (person[0], person[1])
	for word in top_words_list:
		print "\"%s\" was said %s times." % (word[0], word[1])

test(PADT_groupID, 8285)

#8285 messages in PADT GroupMe
