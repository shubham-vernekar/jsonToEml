from emlMaker import emlMaker
from datetime import datetime
import pytz # $ pip install pytz

headers = {
    "Thread-Topic": "This is testing",
    "Thread-Index": "AQHUyPgULHE6ESLirk6/klEiiMXuSw==",
    "Message-ID": "<A95740@MNA6368.namprd.prod.outlook.com>",
    "Accept-Language": "en-US",
    "Content-Language": "en-US",
}

bodyText = """Hi,
This is a test message.
Thanks"""

bodyHTML = """<html lang="en" dir="ltr">
  <body>
      <p style="color:#4f2bef; font-weight: bold;">Hi,<br>
        This is a test message.<br>This is a test message.<br>This is a test message.<br>This is a test message.<br>This is a test message.<br>
        Thanks
      </p>
  </body>
</html>"""

attachments = [
    r"C:\Users\vernekar_s\Downloads\sample.pdf",
]

emailTo = '"sample@gmail.com" <sample@gmail.com>'
emailFrom = "Ram <ram@sample.com>"
subject = "Sample Subject"
timestamp = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%a, %d %b %Y %H:%M:%S %z")

x = emlMaker()
x.generateEML(headers, bodyText, bodyHTML, attachments, emailTo, emailFrom, subject, timestamp)
