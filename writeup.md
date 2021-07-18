# fuzzer
## Capabilities
Currently, our fuzzer is capable of:
- fuzzing json inputs using basic mutation strategies, including:
	- setting fields to NULL
	- replacing fields with large numbers
	- swapping data types in fields
- fuzzing csv inputs (hopefully) using basic mutation strategies, including:
	- mutate single fields
	- add rows
- and generally, mutating inputs in these fashions:
	- removing bytes
	- adding bytes
	- flipping bits in bytes
## Design
Our fuzzer is composed of several major components:
- harness: handles loading, i/o and crash management
- mutator: takes in input from the parser and mutates it to create possibly adversarial input for the harness
As of currently, each format has its own subclass mutator which handles parsing samples into fields and mutating individual fields. There is no coverage measurement yet.
### Harness
Our harness uses ptrace to trace the target binary and watch for crashes. 
The harness initialises two pipes: one pipe sends data into STDIN and the other pipe is used to communicate errors/crashes back up to the harness.
Binaries are executed by initially loading the binary, then forking to run our mutated input. 
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
- Each field is individually and randomly mutated before being repacked by csv
The possible mutations are:
	- Mutate a random field generally
	- Append new rows of random strings
	- Replace existing rows with random strings
