import sys
import os
import magic
import csv
import xml.etree.ElementTree as ET
import parser.jpg as jpg

class SampleParser:
    def __init__(self, sample):
        with open(sample, "rb") as f:
            self.sample = sample
            self.data = f.read()
            #mage = magic.Magic(magic_file="parser/magic.mgc")
            mage = magic.Magic()
            self.guess = mage.from_buffer(self.data)
            if "JFIF" in self.guess:
                self.guess = "JFIF"
            elif "JSON" in self.guess:
                self.guess = "JSON"
            elif "CSV" in self.guess:
                self.guess = "CSV"
            elif "XML" in self.guess:
                self.guess = "XML"

        # for now, store everything in bulk in sample_data
        # in the future, we want to be able to break up our sample data into more useful information to pass to other modules
        # e.g. grab headers, determine data type (if we want to hardcode fuzzing options for input like xml)
        return

    def print_sample(self):
        print(self.data)
        return

    def csv(self):
        with open(self.sample, newline="") as f:
            reader = csv.DictReader(f)
            return [rows for rows in reader]

    def xml(self):
        tree = ET.parse(self.sample)
        return tree

    def jpg(self):
        dissected = jpg.Jpg(self.data)
        return dissected
