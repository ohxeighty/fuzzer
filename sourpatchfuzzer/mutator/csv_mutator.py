from random import randint, randrange, choice
import string
import parser
import csv
import mutator

# MAKE REPRODUCIBLE -> DUMP RAND SEED 

# When we have time -> extend into object oriented
# parent vanilla mutator

class CsvMutator(mutator.Mutator):
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """
    def __init__(self, sample_processed, min=2, max=10): 
        # By convention, header is the first row 
        self.csv_list = sample_processed 
        self.csv_headers = list(self.csv_list[0].keys())
        self.newline = "\n"
        self.delimiter = ","
        mutator.Mutator.__init__(self,min,max)
        return

    # ==================================================================
    def field_single_mutate(self):
        mutated_list = self.csv_list.copy()
        rand_row = randrange(0, len(self.csv_list)) 
        rand_key = choice(self.csv_headers)
    
        mutated_list[rand_row][rand_key] = self.mutate(self.csv_list[rand_row][rand_key])
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


