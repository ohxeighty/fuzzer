from random import randint, randrange, choice
import string
import parser
import json

# MAKE REPRODUCIBLE -> DUMP RAND SEED 

# When we have time -> extend into object oriented
# parent vanilla mutator

class JsonMutator:
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """

    def __init__(self, sample, min=2, max=10): 
        self.json_dict = json.loads(sample) 
        self.min = min
        self.max = max
        self.population = []
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

    def mutate(self, s):
        mutators = [self.insert_random, self.delete_random, self.flip_random_bit]
        pick = choice(mutators)
        return pick(s)

    # TEMPORARY
    
    # GENERIC MUTATORS
    def field_null(self, s):
        return None
    
    def field_rand_str(self, s):
        return "".join(choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(10))

    def field_large_int_random(self, i):
        return randint(-9223372036854775808, 9223372036854775807)


    # INT FIELD MUTATORS

    def field_local_int_random(self, i):
        return randint(i-100, i+100)

    def field_replace_int_with_str(self, i):
        return str(i)

    # STRING FIELD MUTATORS
    def field_replace_str_with_int(self, s):
        try:
            return int(s)
        except:
            return 0 

    
    # LIST MUTATORS

    # PLACEHOLDER -> SINGLE FIELD MUTATION
    def single_mutate(self):
        rand_key = choice(list(self.json_dict.keys()))

        mutated_json = self.json_dict.copy()
        mutators = [self.field_null, self.field_large_int_random, self.field_rand_str]
        # Replace with grammar implementation later. THis is for midpoint.
        # Try mutate based on type
        if type(self.json_dict[rand_key]) == int:
            mutators += [self.field_local_int_random, self.field_replace_int_with_str]
        elif type(self.json_dict[rand_key]) == str:
            mutators += [self.field_replace_str_with_int]

        mutated_json[rand_key] = choice(mutators)(self.json_dict[rand_key])

        return json.dumps(mutated_json).encode("utf-8")
