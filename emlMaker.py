import os
import string
import random
import base64
import re
from mimetypes import MimeTypes


def b64Size(b64string):
    """
        Calcuate filesize of a base64 encoded file
    """
    return (len(b64string) * 3) / 4 - b64string.count('=', -2)


class emlMaker:
    """
        Generates an EML file from the JSON passed
    """

    def __init__(self):
        pass

    def generateEML(self, data, output_file):
        """
            Generate EML data
        """

        # Extact field from JSON if available
        headers = data.get("headers", [])
        body_text = data.get("text", "")
        body_html = data.get("html", "")
        attachments = data.get("attachments", [])
        email_from = data.get("from", {})
        email_to = data.get("to", [])
        cc = data.get("cc", [])
        bcc = data.get("bcc", [])
        subject = data.get("subject", "")
        timestamp = data.get("date", "")

        eml_string = ""

        # Write all the headers
        for key in headers:
            if isinstance(headers[key], list):
                for i in headers[key]:
                    eml_string += "{}: {}".format(key, i) + "\n"
            else:
                eml_string += "{}: {}".format(key, headers[key]) + "\n"

        if email_from:
            eml_string += "From: {}\n".format(self.writeNameEmail([email_from]))
        if email_to:
            eml_string += "To: {}\n".format(self.writeNameEmail(email_to))
        if cc:
            eml_string += "Cc: {}\n".format(self.writeNameEmail(cc))
        if bcc:
            eml_string += "Bcc: {}\n".format(self.writeNameEmail(bcc))
        if subject:
            eml_string += "Subject: {}\n".format(subject)
        if timestamp:
            eml_string += "Date: {}\n".format(timestamp)

        if len(attachments) < 0:
            content_type = "multipart/mixed"
        else:
            content_type = "multipart/related"

        eml_string += "Content-Type: {}; ".format(content_type)

        # Generate boundary
        boundary = self.generateBoundary(55)
        eml_string += 'boundary="{}" \nMIME-Version: 1.0\n\n'.format("_004" + boundary)

        # Add email body in text and in html
        if body_text or body_html:
            eml_string += '--{}\nContent-Type: multipart/alternative;\n\tboundary="{}"\n'.format(
                "_004" + boundary, "_000" + boundary)

            if body_text:
                eml_string += '\n--{}\nContent-Type: text/plain; charset="iso-8859-1"'.format("_000" + boundary) +
                '\nContent-Transfer-Encoding: quoted-printable\n'

                eml_string += '\n{}\n'.format(body_text)

            if body_html:
                eml_string += '\n--{}\nContent-Type: text/html; charset="iso-8859-1"'.format("_000" + boundary) +
                '\nContent-Transfer-Encoding: quoted-printable\n'

                eml_string += '\n{}\n'.format(self.trimLargeLines(
                    body_html.replace("=", "=3D"), 75, "=\n"))

            eml_string += "\n--{}--\n".format("_000" + boundary)

        # Add attachments to the email
        for attachment in attachments:
            # Read file from disk
            if attachment.get("filename", False):
                filename = attachment.get("filename", "")
                basename = os.path.basename(filename)
                with open(filename, 'rb') as file:
                    base64Data = base64.b64encode(file.read())
                    base64Data = self.trimLargeLines(base64Data.decode('utf-8'), 76, "\n")
                fileSize = os.path.getsize(filename)
            else:
                # File already in base64
                basename = attachment.get("name", "")
                base64Data = self.trimLargeLines(attachment.get("raw", ""), 76, "\n")
                fileSize = int(b64Size(base64Data))

            # Find the file type of the attachment
            mimeType = MimeTypes().guess_type(basename)[0]

            eml_string += '\n--{}\nContent-Type: {}; name="{}"\nContent-Description: {}\n\
Content-Disposition: attachment; filename="{}"; size={}\nContent-Transfer-Encoding: \
base64\n\n'.format("_004" + boundary, mimeType, basename, basename, basename, fileSize)
            eml_string += "{}\n".format(base64Data)

        eml_string += "\n--{}--\n".format("_004" + boundary)

        # Write eml to file
        self.writeFile(eml_string, output_file)

    def trimLargeLines(self, data, length, key="\n"):
        """
            Adds a new line in case a line is too long
            length = max length of the line
        """
        # Find positions of new lines
        new_lines = [0] + [match.start() for match in re.finditer(r"\n", data)] + [len(data)]

        split_pts = []
        last_pt = 0
        result = ""
        for k in range(len(new_lines)-1):
            diff = new_lines[k+1] - new_lines[k]
            delta = 0
            # if distance between two new lines is larger than the max length
            while diff >= length:
                diff -= length
                delta += length
                new_pt = new_lines[k] + delta
                if data[last_pt:new_pt].isspace():
                    result += data[last_pt:new_pt] + "\n"
                else:
                    result += data[last_pt:new_pt] + key

                last_pt = new_pt

        result += data[last_pt:]
        return result

    def writeNameEmail(self, data):
        """
            Insert name and email ID in eml format
        """
        result = ""
        for i in data:
            name = i.get("name", "")
            email = i.get("email", "")
            if name:
                result += '{} <{}>; '.format(name, email)
            else:
                result += '"{}" <{}>; '.format(email, email)
        return result[:-2]

    def generateBoundary(self, string_length=10):
        """
            Generates a random string to be used as boundary
        """
        letters = string.ascii_uppercase + string.digits*2
        return "_" + ''.join(random.choice(letters) for i in range(string_length)) + "_"

    def writeFile(self, eml_string, output_file):
        """
            Export the eml string to a file
        """
        with open(output_file, 'w') as wFile:
            wFile.write(eml_string)
