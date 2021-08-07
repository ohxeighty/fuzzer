from random import randint, randrange, choice
import string
import parser
import json
import mutator

# MAKE REPRODUCIBLE -> DUMP RAND SEED 

# When we have time -> extend into object oriented
# parent vanilla mutator

class JsonMutator(mutator.Mutator):
    """
    Mutator(min, max, sample input)
    creates a list Mutator.population of mutated inputs to be passed into the binary
    
    Do we pass in input here, or provide the input to the harness? Ideally we want to be able to tell this class coverage information for better pop development
    """

    def __init__(self, sample, min=2, max=10): 
        self.json_dict = json.loads(sample) 
        mutator.Mutator.__init__(self, None, min, max)
        return
       # TEMPORARY
    
    # ================================================================
    # Filetype: JSON
    # Main strategies: single field mutation, corrupting structure of input

    def single_mutate(self):
        rand_key = choice(list(self.json_dict.keys()))
        mutated_json = self.json_dict.copy()
        mutators = [self.field_null, self.field_large_int_random, self.field_rand_str]
        # Try mutate based on type
        if type(self.json_dict[rand_key]) == int:
            mutators += [self.field_local_int_random, self.field_replace_int_with_str]
        elif type(self.json_dict[rand_key]) == str:
            mutators += [self.field_replace_str_with_int]

        mutated_json[rand_key] = choice(mutators)(self.json_dict[rand_key])
        return json.dumps(mutated_json).encode("utf-8")

    def complex_mutate(self, invalid_chance = 40):
    # We should try things in 2 stages: mutating fields, then mutating structure
        tries = randint(self.min, self.max)
        for i in range(0, tries):
            self.json_dict = json.loads(self.single_mutate())
        if randint(1, 100) <= invalid_chance: # chance to invalidate. 40% by default
            decomposed = self.single_mutate().split(b',')

            randfield = randint(0, len(decomposed)-1)
            for i in range(0, tries):
                decomposed = self.invalidator(decomposed)
            return b','.join(self.invalidator(decomposed))
        else:
            return self.single_mutate()

    # =================================================================

    # ADD INVALID JSON MUTATORS:
    # duplicate keys, single quote keys, straight up invalid stuff
    def invalidator(self, l):
        invalidators = [self.structure_duplicate, self.structure_requote, self.structure_chaos]
        pick = choice(invalidators)
        return pick(l)
    
    def structure_duplicate(self, l):
        l.append(l[randint(0,len(l)-1)])
        return l
    
    def structure_requote(self, l, all_chance = 10): # swap quotes of a random row
        former = b'"'
        latter = b"'"
        if latter in l[0]:
            former = b"'"
            latter = b'"'
        if randint(1, 100) <= all_chance: # 1 in 10 chance by default to swap all
            count = 0
            for i in l:
                l[count] = i.replace(former,latter)
                count += 1
        else:
            new = randint(0, len(l)-1)
            l[new] = l[new].replace(former, latter)
        return l

    def structure_chaos(self, l): # hahahahahahahahahahahahaHAHAHAHAHAHA
        rand_row = randint(0, len(l)-1)
        l[rand_row] = self.mutate(l[rand_row])
        return l


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

        

