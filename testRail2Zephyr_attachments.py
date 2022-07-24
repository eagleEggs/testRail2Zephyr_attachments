import requests
import json


TRUN = ""
TRPW = ""
zAPIKey = ""
zFolder = ""  # folder name in Z
testRun = ''  # test run from TR
saveLoc = ""
trEndpoint = ""  # no trailing slash
zEndpoint = ""  # no trailing slash
zProject = "" # z project ID

def trPull(TRUN, TRPW, zAPIKey, testRun):
	
	# PULL INIT TR DATA
	testsFromRun = requests.get(('{}/get_tests/'.format(trEndpoint) + testRun), auth=(TRUN, TRPW))
	tests = testsFromRun.json()

	# PULL INIT Z DATA
	zSession = requests.Session()
	zSession.headers.update({'Authorization': 'Bearer {}'.format(zAPIKey)})
	zResponse = zSession.get('{}/testcase/search/?query=projectKey%20=%20%22{}%22%20AND%20folder%20=%20%22/{}%22'.format(zEndpoint, zProject, zFolder), verify=False)

	# print(tests['tests'])
	for i in tests['tests']:
		print("TEST ID: {}".format(i['id']))
		print("CASE ID: {}".format(i['case_id']))
		print("RUN ID: {}".format(i['run_id']))
		print("TITLE: {}".format(i['title']))
		
		#GET ATTACHMENT FOR CURRENT TEST:
		print("Querying Attachment...")
		att = requests.get(('{}/get_attachments_for_test/'.format(trEndpoint) + str(i['id'])), auth=(TRUN, TRPW))
		atts = att.json()
		for x in atts:
			print("ATTACHMENT ID FOR TEST {}: {}".format(x['id'], x['filename']))
			print("Downloading Attachment...")
			getAtt = requests.get(('{}/get_attachment/{}'.format(trEndpoint, x['id'])), auth=(TRUN, TRPW))
			print("Attachment Request Status Code: {}".format(getAtt.status_code))
			if getAtt.status_code == 200:
				hasAtt = True
				fileName = "{}/{}".format(saveLoc, x['filename'])
				with open(fileName, "wb") as f:
					print("Saving Attachment...")
					f.write(getAtt.content)

				# push to Zephyr mid loop:
				list = zResponse.content
				print(zResponse)
				print(list.decode('utf-8'))
				decList = list.decode('utf-8')
				decListDict = json.loads(decList)
				print(decListDict)

				for y in decListDict:
					print(y['name'])
					if y['name'] == i['title']:
						print("FOUND NAME MATCH")
						payload = {}
						files = [('file', (fileName, open('{}'.format(fileName), 'rb'), 'image/jpeg'))]
						zResponses = zSession.post(
						url='{}/testcase/{}/attachments'.format(zEndpoint, y['key']),
							data=payload,
							files=files,
							verify=False)

						print(zResponses)
					
					print(y['key'])

				print(zResponses.status_code)
				
			else:
				print("No Attachment for Test {}".format(i['id']))
				
		print("     ")


trPull(TRUN, TRPW, zAPIKey, testRun)

