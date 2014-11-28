import xml.sax
import csv

PG = True
if (PG):
  ENCODING = "utf-8"
else:
  ENCODING = "latin_1"

class TaxonomyHandler(xml.sax.handler.ContentHandler):
  """produces csv files from taxonomy.xml"""
  def __init__(self):
    self.elements = {
      "name": 0,
      "externalTerm": 0,
      "oldCode": 0,
      "seeAlso": 0,
      "useReference": 0,
      "definition": 0,
      "createdDate": 0,
      "lastModifiedDate": 0}
    self.values = {
      "code": "",
      "name": "",
      "externalTerm": "",
      "oldCode": "",
      "seeAlso": "",
      "useReference": "",
      "definition": "",
      "createdDate": "",
      "lastModifiedDate": ""}
    self.release_date = ""
    self.taxonomy = csv.writer(open("taxonomy.csv", "w"), quoting=2)
    self.old_codes = csv.writer(open("old_codes.csv", "w"), quoting=2)
    self.see_also = csv.writer(open("see_also.csv", "w"), quoting=2)
    self.details = csv.writer(open("details.csv", "w"), quoting=2)
    self.release = csv.writer(open("release.csv", "w"), quoting=2)

  def startElement(self, name, attributes):
    if name == "taxonomy":
      self.release_date = attributes["releaseDate"]
      self.release.writerow([self.release_date])
      print self.release_date
    if name == "record":
      for k in self.values.keys():
        self.values[k] = ""
        self.values["code"] = attributes["code"]
    else:
      if self.elements.get(name) == 0:
        self.elements[name] = 1

  def characters(self, data):
    if self.elements["name"]:
      if self.elements["externalTerm"] == 0:
        self.values["name"] += data
    else:
      for k, v in self.elements.iteritems():
        if v == 1:
          self.values[k] += data

  def endElement(self, name):
    if name == "externalTerm":
      self.elements["externalTerm"] = 0
    elif name == "name":
      if not self.elements["externalTerm"]:
        self.taxonomy.writerow([
          self.values["code"], 
          self.values["name"].encode(ENCODING, "backslashreplace"),
          "1",
          self.release_date])
    elif name == "oldCode":
      self.old_codes.writerow([
        self.values["code"],
        self.values["oldCode"],
        self.release_date])
      self.values["oldCode"] = ""
    elif name == "seeAlso":
      self.see_also.writerow([
        self.values["code"],
        self.values["seeAlso"],
        self.release_date])
      self.values["seeAlso"] = ""
    elif name == "useReference":
      self.taxonomy.writerow([
        self.values["code"],
        self.values["useReference"].encode(ENCODING, "backslashreplace"),
        "0",
        self.release_date])
      self.values["useReference"] = ""
    elif name == "lastModifiedDate":
      self.details.writerow([
        self.values["code"],
        " ".join(self.values["definition"].encode(ENCODING,"backslashreplace").splitlines()),
        self.values["createdDate"],
        self.values["lastModifiedDate"],
        self.release_date])
    if self.elements.get(name):
      self.elements[name] = 0

parser = xml.sax.make_parser()
handler = TaxonomyHandler()
parser.setContentHandler(handler)
parser.parse("taxonomy.xml")

