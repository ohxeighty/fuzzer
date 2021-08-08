from random import randint, randrange, choice
import parser

class Mutator:
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """

    def __init__(self, sample=None, min=1, max=5):
        if sample is not None:
            self.data = sample
        self.population = [sample]
        self.min = min
        self.max = max
        return

    # =====================================================
    # Filetype: data/plaintext
    # Main strategies: kitchen sink

    def single_mutate(self):
        if len(self.population) >= 1:
            output = choice(self.population)
        else:
            output = self.data
        tries = randint(self.min, self.max)
        for i in range(0, tries):
            output = self.mutate(output)
        return output

    def complex_mutate(self, invalid_chance = 10):
        #print(self.population)
        output = self.single_mutate()
        if randint(1,100) <= invalid_chance:
            complex = choice([self.duplicate, self.insert_special])
            return complex(output)
        return output


    # ====================================================== 
    def insert_special(self, s):
        special = [b'\0',b'\n',b'%p',b'%n',b'%s',b'\r',b'\b',b'\t',b'\f',b'\\',b'\x7f',b'\xff']
        pos = randint(0, len(s))
        if isinstance(s, str):
            randchar = chr(choice(special))
        else:
            randchar = choice(special)
        return s[:pos] + randchar + s[pos:]       

    def duplicate(self, s):
        return s*2

    # Population controls:
    def reset(self):
        self.population = [self.data]
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

    # ===================================================================
    # list of mutations:
    # All of these mutations are modified from the fuzzing book
    # see: https://www.fuzzingbook.org/html/MutationFuzzer.html
    def insert_random(self, s):
        pos = 0
        if len(s) >= 2 :
            pos = randint(0, len(s)-1)

        if isinstance(s, str):
            randchar = chr(randrange(32,127))
        else:
            randchar = bytes((chr(randrange(32,127))), encoding='utf8')
        #print("at {}, string is {}, adding {}".format(pos, s, randchar))
        return s[:pos] + randchar + s[pos:]
    
    def replace_random(self,s):
        if len(s) >= 2 :
            pos = randint(0, len(s)-1)

            if isinstance(s, str):
                randchar = chr(randrange(32,127))
            else:
                randchar = bytes((chr(randrange(32, 127))), encoding='utf8')
            return s[:pos]+randchar+s[pos:]

    def delete_random(self, s):
        if len(s) >= 2 :
            pos = randint(0, len(s)-1)
            #print("deleting pos {} of {}".format(pos, s))
            return s[:pos]+s[pos+1:]
        return s

    def flip_random_bit(self, s):
        if s=="" or s ==b'':
            return s
        pos = 0
        if len(s) >= 2 :
            pos = randint(0, len(s)-1)
        c = s[pos]
        bit = 1<<randint(0,6)
        if isinstance(s, str):
            new = chr(ord(c)^bit)
        else:
            new = bytes((chr(c^bit)),encoding='utf8')
        #print("flipping {} of {} to {}".format(pos, s, new))
        return s[:pos]+new+s[pos+1:]

    def mutate(self, s): # Expects a bytestring or string
        mutators = [self.insert_random, self.delete_random, self.flip_random_bit, self.replace_random]
        pick = choice(mutators)
        return pick(s)
