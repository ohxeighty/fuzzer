actual docs :) 

# How Our Fuzzer Works
Our fuzzer is comprised of several main components: 
## Main Interface
The parent script is responsible for parsing user input, attaching the harness and driving the mutator 
## Mutator module
The mutator module provides the mutators for supported structured file formats along with a generic mutator. The mutator takes in code coverage (supplied by the harness) as feedback to tune its corpus of inputs. 
## Harness
The harness implements the low level instrumentation of the binary along with any necessary IO. Instrumentation of the binary is 

