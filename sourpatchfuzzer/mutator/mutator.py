from random import randint, randrange, choice
import parser

class Mutator:
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """

    def __init__(self, sample, min=2, max=10):
        self.population = sample
        self.min = min
        self.max = max
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

