from random import randint, randrange, choice

class Mutator:
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """

    def __init__(self, min=2, max=10, sample):
        self.population = sample
        self.min = min
        self.max = max
        return

    def add_pop(self, pop):
        self.population.append(pop)
        return
        
    def mut_fuzz(self):
        # take a random base in our population
        candidate = choice(self.population)
        trials = randint(self.min, self.max) # fuzz random amount of times
        for i in range(trials):
            candidate = self.mutate(candidate)

        # TODO: couple of options here: 
        # return candidate
        # add_pop(candidate)
        # test for coverage, if it goes deeper, then add to population
    
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
        mutators = [insert_random, delete_random, flip_random_bit]
        pick = choice(mutators)
        return pick(s)

