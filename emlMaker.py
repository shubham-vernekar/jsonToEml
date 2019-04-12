import os
import string
import random
import base64
from mimetypes import MimeTypes
import re

def generateBoundary(stringLength=10):
    letters = string.ascii_uppercase + string.digits*2
    return "_" + ''.join(random.choice(letters) for i in range(stringLength)) + "_"

def trimString(data, key, length):
    result = ""
    x = [0] + [match.start() for match in re.finditer(r"\n",data)] + [len(data)]

    locs = []
    for k in range(len(x)-1):
        diff = x[k+1] - x[k]
        delta = 0
        while diff >= length :
            diff -= length
            delta += length
            splitPoint = x[k] + delta
            locs.append(splitPoint)

    if locs:
        ans = data[:locs[0]] + key
        for k in range(len(locs)-1):
            if data[locs[k]:locs[k+1]].isspace():
                ans += data[locs[k]:locs[k+1]] + "\n"
            else:
                ans += data[locs[k]:locs[k+1]] + key

        ans += data[locs[k+1]:]
        return ans

    return data

def nameIDFormat(data):
    result = ""
    for i in data:
        name = i.get("name", "")
        email = i.get("email", "")
        if name:
            result += '{} <{}>; '.format(name,email)
        else:
            result += '"{}" <{}>; '.format(email,email)
    return result[:-2]

def b64Size(b64string):
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)

class emlMaker:
    def __init__(self):
        pass

    def generateEML(self, data, outputFile):

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
            emlString += "From: {}\n".format(nameIDFormat([emailFrom]))
        if emailTo:
            emlString += "To: {}\n".format(nameIDFormat(emailTo))
        if cc:
            emlString += "Cc: {}\n".format(nameIDFormat(cc))
        if bcc:
            emlString += "Bcc: {}\n".format(nameIDFormat(bcc))
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
            if attachment.get("filename",False):
                filename = attachment.get("filename","")
                basename = os.path.basename(filename)
                with open(filename,'rb') as file:
                    base64Data = base64.b64encode(file.read())
                    base64Data = trimString(base64Data.decode('utf-8'), "\n", 76)
                fileSize = os.path.getsize(filename)
            else:
                basename = attachment.get("name","")
                base64Data = trimString(attachment.get("raw",""), "\n", 76)
                fileSize = int(b64Size(base64Data))

            mimeType = MimeTypes().guess_type(basename)[0]

            emlString += '\n--{}\nContent-Type: {}; name="{}"\nContent-Description: {}\n\
Content-Disposition: attachment; filename="{}"; size={}\nContent-Transfer-Encoding: base64\n\n'.format("_004" + boundary,mimeType,basename,basename,basename,fileSize)
            emlString += "{}\n".format(base64Data)

        emlString += "\n--{}--\n".format("_004" + boundary)

        with open(outputFile,'w') as wFile:
            wFile.write(emlString)
