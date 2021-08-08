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
Our mutator consists of a generic mutator and several filetype-specific mutators. Our basic generic mutation strategy includes the following possible mutations:
- Delete random bytes in the input file
- Insert random bytes into the input file
- Flip random bits in the input file
- Insert special characters (such as null bytes, line breaks and format strings) into the input file
- Return the input file but duplicated to an absurd length

We currently support the following specific mutators:
- CSV
- JPG
- JSON
- XML

Our JSON mutator disassembles the sample input using a json library into fields. Our main strategies for mutating JSON input files is to mutate individual fields at random, depending on what type of data the field is supposed to be, and to corrupt the overall structure of the JSON file. The JSON specific mutator supports the following mutations to field contents:
- Set a random field's contents to null
- Set a random field's contents to a very large integer
- Set a random field's contents to a random string
- If the field selected is an integer, change the integer to a random value
- Replace a field's contents with data of a different type

The JSON mutator also supports structural mutations to the JSON file. Currently, the following mutations to the JSON structure are supported:
- Duplicate a random line in the input file
- Swap single quotes in a random line with double quotes and vice versa
- Perform any generic mutations on random lines

Our CSV mutator disassembles the sample input using a csv library into fields. Fields are then mutated at random individually. Our main strategy for mutating CSV input files is to mutate individual fields at random. mutator disassembles the sample input using a csv library into fields
- Each field may be randomly mutated before being repacked
- The possible mutations are:
	- Mutate a random field generally
	- Append new rows of random strings
	- Replace existing rows with random strings

The JPG mutator disassembles the sample input using the standard JPG file format into a list of structures. Each field may be randomly mutated before being repacked into something resembling a valid JPG file.
	- Mutate a random field generally
	- Swap the position of one field with another at random