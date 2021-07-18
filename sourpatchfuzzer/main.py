#!/usr/bin/env python3

import harness
from mutator import Mutator, JsonMutator, CsvMutator
from parser import SampleParser
from argparse import ArgumentParser
from os.path import isfile
import os 
from sys import exit, argv
import time 
import ptrace 
import signal

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

    # PLACEHOLDER
    # Check magic bytes / struct of sample input -> make best guess for input format
    # This should be moved into mutation logic -> this is a shortcut for midpoint
    try:
        # move to mutator later
        sample_processed = SampleParser(sample)
        mutations = JsonMutator(sample_processed.data, min=2, max=10)
    except:
        # midpoint, csv
        mutations = CsvMutator(sample, min=2, max=10)

    


    # can pass this as data:
    # mutations.generate_mutation
    # or run generate_mutation for several iterations, and pass in mutations.population, a list of mutated inputs
 
    # Loop for whole timelimit 
    # In future - try multiple strategies in time limit
    while(1):

        # in future, call parent method -> give me a mutation.. 
        current_input = mutations.single_mutate()

        print(current_input)
        prog = harness.Harness(binary)
        # The spawned process should be stopped.  
        pid, status = prog.spawn_process(stdout=True)
        prog.cont()

        prog.send(current_input) 

        # simulate EOF 
        prog.close_input() 
        # why in the everloving fuck does RESIZING A TERMINAL alter the behaviour of waitpid ????????
        # sigwinch. thats why. 

        while(1):
            # sigsegv doesn't count as a termination signal.
            # since it gets caught by ptrace (only sigkill goes through ptrace) 
            # WSTOPSIG == 11 == SIGSEGV -> segfault
            pid, status = prog.wait()
            if(os.WIFSTOPPED(status) and (os.WSTOPSIG(status) == signal.SIGSEGV)):
                # Placeholder -> Need to create file with crash input and integrate 
                # fuzzing engine. 
                print("Input crashed program with signal: {}".format(os.WSTOPSIG(status)))
                with open("bad.txt", "ab+") as f:
                    # write the byte string
                    # since most formats have newlines in them
                    f.write(str(current_input).encode("unicode-escape") + b"\n")
                break
            elif(os.WIFEXITED(status)):
                break
            prog.cont()




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
    
    # enforce absolute
    args.binary = os.path.abspath(args.binary)
    args.sample = os.path.abspath(args.sample)

    fuzz(args.binary, args.sample)
