import harness
<<<<<<< HEAD
from argparse import ArgumentParser
from os.path import isfile
from sys import exit, argv

"""
So this is what I think our code flow should look like:
    main gets the binary and sample file
    -> sample file is sent to parser
    <- returns one or a list of bytes that are valid inputs
    -> valid inputs are sent to one or more mutators
    
    ## then one of two options:
    ## either 1:
    <- mutated inputs are returned, along with a value for reach
    -> mutated inputs are sent from main
    ## or 2:
    -> mutator sends inputs automatically adding pop using reach

    1 is probably good enough for midpoint check-in
    2 might be necessary for more complicated fuzzing techniques
"""
def fuzz(binary, sample):
    binls = harness.Harness(binary, sample) # not how this works - pls fix
    binls.spawn_process()
    binls.cont()
    binls.send(b"{}")




if __name__ == '__main__':
    parser = ArgumentParser(description='a warm and fuzzy feeling')
    parser.add_argument('binary', help='binary to fuzz through')
    parser.add_argument('sample', help='sample valid input for binary')
    args = parser.parse_args()
    
    if not isfile(args.binary):
        print('"{}" not found!'.format(args.binary))
        exit(-1)
    elif not isfile(args.sample):
        print('"{}" not found!'.format(args.sample))
        exit(-1)
    
    fuzz(args.binary, args.sample)
