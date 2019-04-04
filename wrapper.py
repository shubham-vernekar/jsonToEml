from emlMaker import emlMaker
from datetime import datetime
import pytz # $ pip install pytz

jsonData = {
	'headers': {
		'Message-ID': '<A95740@MNA6368.namprd.prod.outlook.com>',
		'Accept-Language': 'en-US',
		'Content-Language': 'en-US'
	},
	'from': {
		'name': 'Ram',
		'email': 'ram@sample.com'
	},
	'to': [{
		'email': 'sample@gmail.com'
	}],
	'cc': [{
		'name': 'Sam',
		'email': 'sam@gmail.com'
	}],
	'bcc': [{
		'email': 'one@gmail.com'
	}, {
		'email': 'two@gmail.com'
	}],
	'subject': 'Sample Subject',
	'date': 'Tue, 02 Apr 2019 15:53:39 +0530',
	'text': 'Hi,\nThis is a test message.\nThanks',
	'html': """<html lang="en" dir="ltr">
                  <body>
                      <p style="color:#4f2bef; font-weight: bold;">Hi,<br>
                        This is a test message.<br>This is a test message..<br>This is a test message..<br>This is a test message..<br>This is a test message..<br>This is a test message..<br>
                        Thanks
                      </p>
                  </body>
                </html>""",
	'attachments': [{
		'filename': 'D:\\EMLMaker\\sampleAttachments\\myself.jpg'
	}, {
		'name': 'sample.txt',
		'raw': 'SGVsbG8sIApUaGlzIGlzIGEgc2FtcGxlIHR4dCBmaWxl'
	}]
}


outputFile = "test.eml"
x = emlMaker()

import time

st = time.time()
for i in range(100):
	x.generateEML(jsonData,outputFile)
	quit()
et = time.time()-st

print ("Total time = ",et)
print ("Speed (rec/sec) = ", 100/et)
