# fuzzer
## Capabilities
Currently, our fuzzer is capable of:
- fuzzing json inputs using basic mutation strategies, including:
	- setting fields to NULL
	- replacing fields with large numbers and random strings
	- swapping data types in fields
- fuzzing csv inputs (hopefully) using basic mutation strategies, including:
	- mutating rows with garbage
	- adding garbage rows 
- fuzzing jpg (hopefully) using basic mutation strategies, including:
	- mutating sections and section metadata with garbage
	- swapping sections 
- and generally, mutating inputs in these fashions:
	- removing bytes
	- adding bytes
	- flipping bits in bytes

## Design
Our fuzzer is composed of several major components:
- harness: handles loading, i/o and signal/crash management
- mutator: takes in input from the parser and mutates it to create possibly adversarial input for the harness
As of now, each format has its own subclass mutator which handles parsing samples into fields and mutating individual fields. There is no coverage measurement yet.

See the `docs` directory for future design notes (current baseline plan is evolutionary fuzzer with code coverage serving as the natural selection metric). 

Most of the existing code is boilerplate PoC that needs to be refactored into consistent classes & methods. 

### Harness
Our custom harness uses ptrace (pulled from libc @ assumed path `/lib/x86_64-linux-gnu/libc.so.6`) to trace the target binary and watch for signals (including crashes). In future, this will enable fine tuned interrogation of the target binary and code coverage feedback (i.e. typical "debugger" capabilities implemented with ptrace methods).  

The target binary is spawned under a child process with fork + exec.

Two pipes are created for IO: one pipe sends data from the harness into STDIN and the other pipe is used to communicate errors/crashes (when spawning) back up to the harness.

### Mutators
- The JSON mutator disassembles the sample input using a json library into fields
- Each field is individually and randomly mutated depending on what type of data the field is
- The possible mutations are:
	- Set a field to null
	- Set a field to a very large int
	- Set a field to a random string
	- If possible, replace a string with its integer representation, and vice versa
	- Manipulate an integer up or down randomly

- The CSV mutator disassembles the sample input using a csv library into fields
- Each field may be randomly mutated before being repacked
The possible mutations are:
	- Mutate a random field generally
	- Append new rows of random strings
	- Replace existing rows with random strings

- The JPG mutator disassembles the sample input using the standard JPG file format into fields
- Each field may be randomly mutated before being repacked
	- Mutate a random field generally
	- Swap the position of one field with another at random