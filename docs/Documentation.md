actual docs :) 

# How Our Fuzzer Works
Our fuzzer is comprised of several main components: 

## Main Interface
The parent script is responsible for parsing user input, attaching the harness and driving the mutator 

## Mutator module
The mutator module provides the mutators for supported structured file formats along with a generic mutator. The mutator takes in **code coverage** (supplied by the harness) as feedback to tune its corpus of inputs. 
### Mutators
Due to ~~extremely poor time management~~ temporal anomalies, high level fuzzing strategies were not completely implemented (specifically - survival of the fittest fuzzing strategies). Our corpus however does receive feedback in the form of code coverage; with inputs that increase the code coverage being added back to the corpus. 

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
- Perform any generic mutations on the field's contents

The JSON mutator also supports structural mutations to the JSON file. Currently, the following mutations to the JSON structure are supported:
- Duplicate a random line in the input file
- Swap single quotes in a random line with double quotes and vice versa
- Perform any generic mutations on random lines

Our CSV mutator disassembles the sample input using a csv library into fields. Fields are then mutated at random individually. Our main strategy for mutating CSV input files is to mutate individual fields at random. We currently support the following mutations:
- Perform any generic mutations on the field's contents
- Completely randomise the contents of every field in a row
- Append rows consisting of random data into the CSV
- Replace an entire row with a random string

Our JPG mutator dissasssembles the sample input into a list of JPG segments using custom code. Each segment may be randomly mutated before being repacked into something resembling a valid JPG file. We currently support the following mutations for JPG:
- Perform any generic mutations on the segment header bytes, segment length bytes or segment content bytes
- Swap the position of one segment with another at random

Our XML mutator disassembles the sample input into an element tree. We support the following mutations to each element of the tree:
- Replace the element with a random string which may or may not contain special characters


## Harness
The harness implements the low level instrumentation (code coverage + signal handling) of the binary along with any necessary IO. 

### Technical Overview
**something awesome? :) ** - low level instrumentation and harness is all custom work; ptrace is ~~torture~~ fun!*

* Captures crash signal (type of crash)
* Code coverage at basic block level (see below)
* Does not touch disk
* Does **not** have in memory resetting (see improvements)
* Collects telemetry (iterations, crashes)
	* Capability to dump userland (registers, memory) at time of crash
* Uses code coverage + iterations to detect infinite loops (resets population -> we've hit some sort of dead end as far as we're concerned)

Instrumentation of the binary is accomplished primarily through invocations of ptrace (pulled from libc with ctypes). 

To spawn the victim, the harness forks: the child indicates it should be traced with `PTRACE_TRACEME` and disables ASLR (by calling `personality(ADDR_NO_RANDOMIZE)`) before execv'ing the target binary while the parent waits until `SIGTRAP` is received - indicating that the child is now waiting to continue from its entrypoint. From here, the harness can pass control back up to the main fuzzing loop. 

This tracing layer allows the parent (i.e. the fuzzer) to inject and intercept signals (importantly, `SIGTRAP` for breakpoints & `SIGSEGV` for segmentation faults) and perform all other instrumentation primitives as detailed in the `ptrace(2)` man page. The harness also (necessarily..) provides IO through a pipe to the STDIN of the child. The child's STDOUT is by default sent to `/dev/null`. 

Specifically, we use make use of angr's control flow graph (represented as a NetworkX object) to create a **basic block vector** (where a basic block is a continuous block of assembly code without any control structures like `jmp` or `call`). After filtering these blocks (for example, we don't care about symbols that resolve externally to say, libc, or generic constructor / destructor functions such as `register_tm_clones`) we can then add breakpoints (implemented with `int 3` software breakpoints - the LSB of instruction @ the block is swapped with `\xcc` ) to the start of each basic block (that persist through multiple runs) that are removed when hit; thereby serving as an indicator of code coverage (which is fed back up to the mutator). 

# Capabilities
Capable of fuzzing supported structured formats + generic plaintext inputs. Will generally hit memory corruption vulnerabilities (buffer overflows, format str vulnerabilities) along with simple logic errors (e.g. poor handling of negative numbers, incorrect type casting). 

Demonstrated with several test binaries. 

# Improvements

**In future, we should allow the harness to restart the binary in memory by restoring userland registers and jumping back to `_start` - (i.e. akin to GDB's checkpoint functionality). the major obstacle in implementing this was time (if its not the due date its not the do date...) & programmatically identifying offsets to user controlled data to save (e.g. by pulling from /proc/{pid}/mem). Avoiding all the expensive back and forth to the kernel (disk io, memory paging...) that is performed before we even hit main would dramatically increase performance.**

**The harness is also hard coded to support x86 binaries running on a x64 machine (ctypes sizes, bitwise logic, word bit width...).** 

**As a side note - ran into a problem when trying to record unique crashes via EIP at crashtime. Some of our mutations resulted in memory corruption... of EIP. Probably a good idea to record an old IP (should be cheap)...** More cheap metrics that indicate stagnation are usually a good thing - helps us baseline our fuzzing and allows us to feed it into a higher level strategy. Also lets us know when to hard reset back to the first generation (e.g. in the off chance we've reached substantial code coverage into a dead end). 

**As mentioned - lack of a higher level fuzzing strategy.**

**Generally speaking - a lot of the code is non-performant boilerplate POC. This is definitely not because we picked the assignment back up a day before the due date. Additionally - codebase is poorly organised (mutators should be inherited, etc)**

**I would also like to remove reliance upon angr's basic block creation algos; but that would require some extensive reading.**

# Bonus Marks
Completely custom harness built from ptrace primitives? (Aside from pulling angr's basic block traversal algorithms.). This assignment was an interesting deep dive into process signalling and tracing. 


