from random import randint, randrange, choice, randbytes
import string
import parser
import csv

# MAKE REPRODUCIBLE -> DUMP RAND SEED 

# When we have time -> extend into object oriented
# parent vanilla mutator

class CsvMutator:
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """

    def process_csv(self, s):
        with open(s, newline="") as f:
            reader = csv.DictReader(f)
            return [rows for rows in reader]

    def __init__(self, sample, min=2, max=10): 
        # By convention, header is the first row 
        self.csv_list = self.process_csv(sample) 
        self.csv_headers = list(self.csv_list[0].keys())
        self.min = min
        self.max = max
        self.population = []
        
        self.newline = "\n"
        self.delimiter = ","
        return


    def add_pop(self, pop):
        self.population.append(pop)
        return
        
    def print_population(self):
        print(self.population)
        return

    def generate_mutation(self):
        """
        Mutator.generate_mutation will spit out a mutated version of a random pop, then add it to the population. In the future: change the behaviour to add a population if coverage detects more branches.
        """
        # take a random base in our population
        candidate = choice(self.population)
        trials = randint(self.min, self.max) # fuzz random amount of times
        for i in range(trials):
            candidate = self.mutate(candidate)

        # TODO: couple of options here: 
        # return candidate
        # add_pop(candidate)
        # test for coverage, if it goes deeper, then add to population
        self.add_pop(candidate)
        return candidate 
    #

    # ===================================================================
    # list of mutations:
    # All of these mutations are from the fuzzing book
    # see: https://www.fuzzingbook.org/html/MutationFuzzer.html
    def insert_random(self, s):
        pos = randint(0, len(s))
        randchar = chr(randrange(32,127))
        return s[:pos] + randchar + s[pos:]

    def delete_random(self, s):
        if s == "":
            return s
        pos = randint(0, len(s)-1)
        return s[:pos]+s[pos+1:]

    def flip_random_bit(self, s):
        if s=="":
            return s
        pos = randint(0, len(s)-1)
        c = s[pos]
        bit = 1<<randint(0,6)
        new = chr(ord(c)^bit)
        return s[:pos]+new+s[pos+1:]

    def field_single_mutate(self):
        mutated_list = self.csv_list.copy()
        rand_row = randrange(0, len(self.csv_list)) 
        rand_key = choice(self.csv_headers)
        mutators = [self.insert_random, self.delete_random, self.flip_random_bit]
        
        mutated_list[rand_row][rand_key] = choice(mutators)(self.csv_list[rand_row][rand_key])
        return mutated_list
        

    def rand_str(self, n):
        return "".join(choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(n))

    def field_random_row(self):
        n = randrange(1,1000)
        mutated_list = self.csv_list.copy()
        rand_row = randrange(0, len(self.csv_list)) 
        mutated_list[rand_row] = dict(zip(self.csv_headers, [self.rand_str(n) for i in range(len(self.csv_headers))]))
        return mutated_list
        
    def field_append_rows(self):
        n = randrange(1,100)
        mutated_list = self.csv_list.copy()
        for i in range(n):
            mutated_list.append(dict(zip(self.csv_headers, [self.rand_str(10) for i in range(len(self.csv_headers))])))
        return mutated_list

    # Write CSV
    def csv_write(self, csv_list):
        # grab headers
        formatted = self.delimiter.join(list(csv_list[0].keys()))
        for row in csv_list[0:]:
            formatted += self.newline + self.delimiter.join(row.values())
        return formatted.encode("utf-8")
        
    # PLACEHOLDER -> SINGLE FIELD MUTATION
    def single_mutate(self):

        mutators = [self.field_random_row, self.field_append_rows, self.field_single_mutate]

        mutated_list = choice(mutators)()
        return self.csv_write(mutated_list)


