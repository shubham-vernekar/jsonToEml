import os
import string
import random
import base64
from mimetypes import MimeTypes

def generateBoundary(stringLength=10):
    letters = string.ascii_uppercase + string.digits*2
    return "_" + ''.join(random.choice(letters) for i in range(stringLength)) + "_"

def trimString(data, key, length):
    ans = ""
    count = 0
    for char in data:
        ans += char
        count += 1

        if count >= length:
            ans += key
            count = 0

        if char == "\n":
            count = 0

    return ans

class emlMaker:
    def __init__(self):
        pass

    def generateEML(self, data):
        # headers=[], bodyText="", bodyHTML="", attachments=[], emailTo="", emailFrom="", subject="", timestamp=""
        headers = data.get("headers",[])
        bodyText = data.get("text","")
        bodyHTML = data.get("html","")
        attachments = data.get("attachments",[])
        emailFrom = data.get("from",{})
        emailTo = data.get("to",[])
        cc = data.get("cc",[])
        bcc = data.get("bcc",[])
        subject = data.get("subject","")
        timestamp = data.get("date","")

        emlString = ""

        for key in headers:
            if isinstance(headers[key], list):
                for i in headers[key]:
                    emlString += "{}: {}".format(key, i) + "\n"
            else:
                emlString += "{}: {}".format(key, headers[key]) + "\n"

        if emailFrom:
            emlString += "From: {}\n".format(emailFrom)
        if emailTo:
            emlString += "To: {}\n".format(emailTo)
        if subject:
            emlString += "Subject: {}\n".format(subject)
        if timestamp:
            emlString += "Date: {}\n".format(timestamp)

        if len(attachments) <0 :
            contentType = "multipart/mixed"
        else:
            contentType = "multipart/related"

        emlString += "Content-Type: {}; ".format(contentType)
        boundary = generateBoundary(55)

        emlString += 'boundary="{}" \nMIME-Version: 1.0\n\n'.format("_004" + boundary)
        if bodyText or bodyHTML:
            emlString += '--{}\nContent-Type: multipart/alternative;\n\tboundary="{}"\n'.format("_004" + boundary, "_000" + boundary)

            if bodyText:
                emlString += '\n--{}\nContent-Type: text/plain; charset="iso-8859-1"\nContent-Transfer-Encoding: quoted-printable\n'.format("_000" + boundary)
                emlString += '\n{}\n'.format(bodyText)

            if bodyHTML:
                emlString += '\n--{}\nContent-Type: text/html; charset="iso-8859-1"\nContent-Transfer-Encoding: quoted-printable\n'.format("_000" + boundary)
                emlString += '\n{}\n'.format(trimString(bodyHTML.replace("=","=3D"), "=\n", 75))

            emlString += "\n--{}--\n".format("_000" + boundary)

        for attachment in attachments:
            filename = os.path.basename(attachment)
            with open(attachment,'rb') as file:
                base64Data = base64.b64encode(file.read())
                base64Data = trimString(base64Data.decode('utf-8'), "\n", 76)

            mimeType = MimeTypes().guess_type(attachment)[0]
            fileSize = os.path.getsize(attachment)

            emlString += '\n--{}\nContent-Type: {}; name="{}"\nContent-Description: {}\n\
Content-Disposition: attachment; filename="{}"; size={}\nContent-Transfer-Encoding: base64\n\n'.format("_004" + boundary,mimeType,filename,filename,filename,fileSize)
            emlString += "{}\n".format(base64Data)

        emlString += "\n--{}--\n".format("_004" + boundary)

        with open('test.eml','w') as wFile:
            wFile.write(emlString)
