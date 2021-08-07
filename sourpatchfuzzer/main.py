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

TIME_LIMIT = 5 #60*3

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
def fuzz(binary, sample, verbose):

    # PLACEHOLDER
    # Check magic bytes / struct of sample input -> make best guess for input format
    # This should be moved into mutation logic -> this is a shortcut for midpoint
    sample_processed = SampleParser(sample)
    
    try:
    # data: that one plaintext file
    # ASCII text: plaintext
    # JSON data: json
    # CSV text: csv
    # HTML document, ASCII text: xml2

        mutations = { # walmart switch statement
            'JSON data' : lambda sample_processed:JsonMutator(sample_processed.data, min=2, max=10),
            'CSV text': lambda sample_processed:CsvMutator(sample_processed.csv(), min=2, max=10)
            }[sample_processed.guess](sample_processed)
    except KeyError as e:
        print('Unmatched data type: {}, defaulting to generic mutator'.format(e))
        mutations = Mutator(sample_processed)
        # need a default: ascii
    except Exception as e:
        print("mutator fucked up: {}".format(e))
    
    print('Running fuzzer with a {} second limit...'.format(TIME_LIMIT))

    # Some inkling of a strategy handler
    if hasattr(mutations, 'complex_mutate'):
        strategy = mutations.complex_mutate
    else:
        strategy = mutations.single_mutate
    
    # Loop for whole timelimit 
    # In future - try multiple strategies in time limit
    while(1):

        # in future, call parent method -> give me a mutation.. 
        
        current_input = strategy()

        if verbose:
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

def timeout(num, stack):
    print("=========================================")
    print("Time limit reached: {}".format(TIME_LIMIT))
    print("You look nice today!")
    # We could put a neat summary here
    exit(0)


if __name__ == '__main__':
    parser = ArgumentParser(description='a warm and fuzzy feeling')
    parser.add_argument('binary', help='binary to fuzz through')
    parser.add_argument('sample', help='sample valid input for binary')
    parser.add_argument('-v','--verbose', help='show all generated output', action="store_true")
    args = parser.parse_args()
    if os.path.exists("bad.txt"):
        os.remove("bad.txt")
    
    if not isfile(args.binary):
        print('"{}" not found!'.format(args.binary))
        exit(-1)
    elif not isfile(args.sample):
        print('"{}" not found!'.format(args.sample))
        exit(-1)
    
    # enforce absolute
    args.binary = os.path.abspath(args.binary)
    args.sample = os.path.abspath(args.sample)
    
    # set a timer for 3 minutes
    #signal.signal(signal.SIGALRM, timeout)
    signal.alarm(TIME_LIMIT)

    fuzz(args.binary, args.sample, args.verbose)
