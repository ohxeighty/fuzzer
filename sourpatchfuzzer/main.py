#!/usr/bin/env python3

import harness
from mutator import Mutator, JsonMutator, CsvMutator, JpgMutator, XmlMutator
from parser import SampleParser
from argparse import ArgumentParser
from os.path import isfile
import os 
from sys import exit, argv
import time 
import ptrace 
import signal
from functools import partial

TIME_LIMIT = 60*3

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
def fuzz(binary, sample, verbose, prog):
    """
    block based code coverage? edge coverage is hard and requires actual... algorithms (and source)
    and if we got X amount of time without new coverage, we start from scratch? (bandaid 
    fix for when we get a bad evolution path...) 

    I'm fairly certain using ANGR's factory module to grab a basic block vector is within the DIY scope. 
    """
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
            'JSON' : lambda sample_processed:JsonMutator(sample_processed.data, min=2, max=10),
            'CSV': lambda sample_processed:CsvMutator(sample_processed.csv(), min=2, max=10),
            'JFIF': lambda sample_processed:JpgMutator(sample_processed.jpg(), min=2, max=10),
            'XML': lambda sample_processed:XmlMutator(sample_processed.xml(), min=2, max=10),
            'HTML document, ASCII text': lambda sample_processed:XmlMutator(sample_processed.xml(), min=2, max=10)
            }[sample_processed.guess](sample_processed)
    except KeyError as e:
        print('Unmatched data type: {}, defaulting to generic mutator'.format(e))
        mutations = Mutator(sample_processed.data)
        # need a default: ascii
    except Exception as e:
        print("mutator fucked up: {}".format(e))
    
    print('Running fuzzer with a {} second limit...'.format(TIME_LIMIT))

    # nevermind
    strategy = mutations.complex_mutate
    
    # Loop for whole timelimit 
    # In future - try multiple strategies in time limit
    cov = float(0)
    while(1):
        prog.iterations += 1 


        # in future, call parent method -> give me a mutation..     
        current_input = strategy()

        # Spawn process - should be stopped after exec. 
        pid, status = prog.spawn_process(stdout=False)
        prog.getregs()
        # Now that the process has been spawned, we can populate the breakpoints
        prog.populate_breakpoints()
        if verbose:
            print(strategy)
            print(current_input)
            print("pid {}".format(pid))
        prog.getregs()
        # Now that the process has been spawned, we can populate the breakpoints
        prog.populate_breakpoints()
        #prog.breakpoint_status()

        # Start the process proper 
        prog.cont()
        prog.send(current_input) 

        # simulate EOF 
        prog.close_input() 
        # why in the everloving fuck does RESIZING A TERMINAL alter the behaviour of waitpid ????????
        # sigwinch. thats why. 
        
        print("coverage: {}, this run: {}".format(prog.coverage(), cov))
        if prog.coverage() > cov:
            cov = prog.coverage()
            print(cov)
            mutations.add_pop(current_input)
        # Wait for something to happen. 
        while(1):
            # sigsegv doesn't count as a termination signal.
            # since it gets caught by ptrace (only sigkill goes through ptrace) 
            # WSTOPSIG == 11 == SIGSEGV -> segfault

                

            pid, status = prog.wait()
            if(os.WIFSTOPPED(status) and (os.WSTOPSIG(status) == signal.SIGSEGV)):
                # Placeholder -> Need to create file with crash input and integrate 
                # fuzzing engine. 

                # Update stats
                prog.getregs()
                prog.crash_eips.append(prog.registers.eip) 
                #if verbose:
                #    print("Input crashed program with signal: {}".format(os.WSTOPSIG(status)))

                with open("bad.txt", "ab+") as f:
                    # write the byte string
                    # since most formats have newlines in them
                    f.write(str(current_input).encode("unicode-escape") + b"\n")
                break
            # we have hit one of our basic block breakpoints
            elif(os.WIFSTOPPED(status) and (os.WSTOPSIG(status) == signal.SIGTRAP)):
                # we need to decrement eip, replace the breakpoint with its saved value
                prog.restore_current_bp() 

            elif(os.WIFEXITED(status)):
                break

            #prog.step()
            prog.cont()

def timeout(num, stack, prog):
    print("=========================================")
    print("Time limit reached: {} arbitrary time units".format(TIME_LIMIT))
    print("Faulting inputs have been logged to bad.txt")
    print("You look nice today :)")
    # We could put a neat summary here

    print("Total crashes: {}".format(len(prog.crash_eips)))
    # sometimes, buffer overflow or other memory corruption means we cannot read EIP reliably
    # :) 
    #print("Unique crashes: {}".format(len(set(prog.crash_eips))))
    print("Total iterations: {}".format(prog.iterations))

    exit(0)


if __name__ == '__main__':
    parser = ArgumentParser(description='a warm and fuzzy feeling')
    parser.add_argument('binary', help='binary to fuzz through')
    parser.add_argument('sample', help='sample valid input for binary')
    parser.add_argument('-v','--verbose', help='show all generated output', action="store_true", default=False)
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
    
    # Setup harness
    prog = harness.Harness(args.binary)
    
    ## set a timer for 3 minutes
    signal.signal(signal.SIGALRM, partial(timeout, prog=prog))
    #signal.signal(signal.SIGALRM, timeout)
    signal.alarm(TIME_LIMIT)
    
    fuzz(args.binary, args.sample, args.verbose, prog)
