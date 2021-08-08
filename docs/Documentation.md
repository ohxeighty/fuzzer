actual docs :) 

# How Our Fuzzer Works
Our fuzzer is comprised of several main components: 
## Main Interface
The parent script is responsible for parsing user input, attaching the harness and driving the mutator 

## Mutator module
The mutator module provides the mutators for supported structured file formats along with a generic mutator. The mutator takes in code coverage (supplied by the harness) as feedback to tune its corpus of inputs. 

## Harness
The harness implements the low level instrumentation (code coverage + signal handling) of the binary along with any necessary IO. 

### Technical Overview
**something awesome? :) ** - low level instrumentation and harness is all custom work; ptrace is ~~torture~~ fun!*

Instrumentation of the binary is accomplished primarily through invocations of ptrace (pulled from libc with ctypes). 

To spawn the victim, the harness forks: the child indicates it should be traced with `PTRACE_TRACEME` and disables ASLR (by calling `personality(ADDR_NO_RANDOMIZE)`) before execv'ing the target binary while the parent waits until `SIGTRAP` is received - indicating that the child is now waiting to continue from its entrypoint. From here, the harness can pass control back up to the main fuzzing loop. 

**In future, we should allow the harness to restart the binary in memory by restoring userland registers and jumping back to `_start` - (i.e. akin to GDB's checkpoint functionality). the major obstacle in implementing this was time (if its not the due date its not the do date...) & programmatically identifying offsets to user controlled data to save (e.g. by pulling from /proc/{pid}/mem). Avoiding all the expensive back and forth to the kernel (disk io, memory paging...) that is performed before we even hit main would dramatically increase performance.**

This tracing layer allows the parent (i.e. the fuzzer) to inject and intercept signals (importantly, `SIGTRAP` for breakpoints & `SIGSEGV` for segmentation faults) and perform all other instrumentation primitives as detailed in the `ptrace(2)` man page. The harness also (necessarily..) provides IO through a pipe to the STDIN of the child. The child's STDOUT is by default sent to `/dev/null`. 

Specifically, we use make use of angr's control flow graph (represented as a NetworkX object) to create a **basic block vector** (where a basic block is a continuous block of assembly code without any control structures like `jmp` or `call`). After filtering these blocks (for example, we don't care about symbols that resolve externally to say, libc, or generic constructor / destructor functions such as `register_tm_clones`) we can then add breakpoints (implemented with `int 3` software breakpoints - the LSB of instruction @ the block is swapped with `\xcc` ) to the start of each basic block (that persist through multiple runs) that are removed when hit; thereby serving as an indicator of code coverage (which is fed back up to the mutator). 

**As a side note - ran into a problem when trying to record unique crashes via EIP at crashtime. Some of our mutations resulted in memory corruption... of EIP. Probably a good idea to record an old IP (should be cheap)...**
