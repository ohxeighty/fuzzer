import sys
import os
import magic
import csv

class SampleParser:
    def __init__(self, sample):
        with open(sample, "rb") as f:
            self.sample = sample
            self.data = f.read()
            self.guess = magic.from_buffer(self.data)
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
