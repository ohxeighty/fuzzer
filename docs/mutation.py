from random import randint, randrange, choice
sample = "http://www.google.com/search?q=fuzzing"

"""
Mutation fuzzing: from a given *valid* input, create mutations. 
Greater likelihood of reaching more branches, since random fuzzing will often hit invalid input 
in programs that expect a specific input format.
"""

def insert_random(s):
    """
    Method 1: inserting random characters
    """
    pos = randint(0, len(s))
    randchar = chr(randrange(32, 127))
    return s[:pos] + randchar + s[pos:]

def delete_random(s):
    """
    Method 2: delete random character
    """
    if s == "":
        return s
    
    pos = randint(0, len(s)-1)
    return s[:pos] + s[pos+1:]

def flip_random_bit(s):
    """
    Method 3: flip a random bit in a random position
    """
    if s == "":
        return s
    pos = randint(0, len(s) - 1)
    c = s[pos]
    bit = 1 << randint(0,6)
    new_c = chr(ord(c)^bit)
    return s[:pos]+new_c+s[pos+1:]

"""
We can randomly pick a combination of the three basic mutations, and also choose multiple mutations
e.g. http:// -> ftp:// requires multiple mutations
"""

def mutate(s):
    """
    Perform a random mutation
    """
    mutators = [
        insert_random,
        delete_random,
        flip_random_bit
    ]
    mutator = choice(mutators)
    return mutator(s)

def fuzz(s):
    min = 2
    max = 10
    sample = s
    for i in range(min, max):
        sample = mutate(sample)
    return sample

print(fuzz(sample))

# From our list of sample inputs, we get the population
# Randomly pick input from the population, and mutate a random number of times.
# If we have coverage, we can use it to guide mutation
# Mutate *successful* inputs, where success is means reaching deeper in program execution or finding an new path, not just valid input
# if a new mutation is successful, add it to our population.