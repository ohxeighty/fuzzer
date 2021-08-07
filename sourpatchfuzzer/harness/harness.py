import ctypes
import sys
import os
import signal
import ptrace

# big fat chunky angr
# if bothered, please just pull the logic we need for creating our BBV
import angr

class Harness:
    """
    Binary harness. 
    """

    def __init__(self, binary, arguments=[]):
        # current optimisation strategy: 
        # breakpoint at libc entry point and catch exit -> save userland registers at entry
        # restore at entry point "checkpoint" with same userland state blah blah
        # probably saves on a lot of syscalls before we get to execution proper

        # but this requires us to restore writable memory pages
        # we COULD do this by reading /proc/$pid/mem ...
        # but for this to be efficient we would need to tailor offsets to save memory from 
        # otherwise we'd be holding onto the entire proc memory 

        # in an ideal world, we'd do some program assisted tweaking for each binary
        # i.e. locating a suitable "start" after most disk io finishes up 
        # and an "end" after all code which touches data tainted by user input finishes up

        # reading for _start -> main
        # http://dbp-consulting.com/tutorials/debugging/linuxProgramStartup.html

        # For now, just execve. I'm sure disk caching optimisations are fine... 
        self.binary = binary
        # By convention, argv0 is the invoked bin
        self.arguments = arguments 
        self.pid = -1 

        self.ir_pipe = None
        self.iw_pipe = None
        
        ## our hashmap of addresses -> original instruction 
        ## that keeps track of our breakpoints
        #self.breakpoints = dict() 

        ## hokay, now we use angr to extract our basic block vector which we use for code coverage
        #self.angr_project = angr.Project(binary, auto_load_libs=False)
        ## create networkx control flow graph
        #self.cfg = self.angr_project.analyses.CFGFast()
        #self.cfg.normalize()
        #
        #self.bbv = []
        #for node in self.cfg.functions.values():
        #    # internals
        #    if not node.name.startswith("__"):
        #        self.bbv += node.blocks
    def monitor(self):
        #child_data = os.read(self.er_pipe, 5096)
        
        #if(child_data):
        #    # Child threw error
        #    print(child_data) 
        
        # os.close(self.er_pipe)
        # Wait for tracee
        # Why the fuck does .waitpid cause the child to continue?? 
        # pid, status = os.waitpid(self.pid, 0)
        #print("Monitor entry")
        return self.wait()

        #ptrace.ptrace_continue(self.pid) 

    def spawn_child(self, stdout):
        # Handle actual process creation

 
        # Point pipe to stdin
        os.dup2(self.ir_pipe, 0)

        # If we don't want STDOUT, dup2 the FDs to point to devnull  
        if not stdout:  
            with open(os.devnull, "wb") as devnull:
                os.dup2(devnull.fileno(), 1)
                os.dup2(1, 2) 
 
        # Tracee should call TRACEME
        ptrace.ptrace_traceme() 

        # Disable ASLR
        # see /usr/include/sys/personality.h 
        # sys_personality = 135 
        ptrace.personality_disable_aslr()  

        # Set ptrace options
        # Stop tracee at exit
        # ptrace.ptrace_setoptions(self.pid, [ptrace.PTRACE_O_TRACEEXIT])  
         
        # Pause before execv
        # os.kill(os.getpid(), signal.SIGSTOP)
        #print("Tracee starting to exec")
        if self.arguments != []:
            os.execvp(self.binary, [self.binary]+self.arguments)  
        else:
            os.execvp(self.binary, [self.binary])
            
    def spawn_process(self, stdout=True):
        """
        Parameters:
            stdin: Byte string that is initially sent to stdin of child.
        """
        # Fork overhead in python3? 
        # Might want to migrate this out to a shared lib.

        # Note that we copy over our current environment. 
        # Might want to tweak this later. 

        # Parent writes input to child. 
        self.ir_pipe, self.iw_pipe = os.pipe() 

        # Fork 
        self.pid = os.fork()
          
        if self.pid: 
            # Parent
            os.close(self.ir_pipe)

            return self.monitor() 
        else:
            # Child
            os.close(self.iw_pipe)

            self.spawn_child(stdout)
          
    """
    Functions to interact with traced process..
    """

    def cont(self):
        ptrace.ptrace_continue(self.pid)

    def step(self):
        ptrace.ptrace_singlestep(self.pid)

    # read word
    def peek(self, addr):
        return ctypes.c_ulong(ptrace.ptrace_peek(self.pid, ctypes.c_void_p(addr)))
    
    # write word
    # ctypes should translate a python bytestring to a char* 
    # we would rather void * 
    def poke(self, addr, data):
        ptrace.ptrace_poke(self.pid, ctypes.c_void_p(addr), ctypes.c_void_p(data))
    # more reading https://eli.thegreenplace.net/2011/01/27/how-debuggers-work-part-2-breakpoints
    # break = \xCC
    # Assume little endian -> we read word at addr, then replace LSB with break
    # write back

    # since we need to store the instruction we overwrite, we keep a dictionary (hash map)
    # of addr -> original instructions.

    # ALSO - when we hit a break ip still increments, so, when we 
    # hit the breakpoint we need to decrement ip, restore the original instruction
    # then continue (or single step then write bp again if we're not removing it)

    # REMINDER - We (mostly) care about x86 -> word = 32 bits
   
    # also not sure if adjacent breakpoints will create 
    # a fucky wucky if we, say, restore the breakpoint that was placed first (since
    # it would restore the word to a state before the second breakpoint?)

    # deal with it if we come to it
    def breakp(self, addr):
        # already breakpointed?
        if addr in self.breakpoints.keys:
            print("uh oh, addr already breakpointed, stinky!")
            return

        # peek to grab original word @ addr
        original = self.peek(addr) 
        
        breakpoint = ctypes.c_ulong((original & 0xFFFFFF00) | 0xCC) 
        # poke addr with new value
        self.poke(addr, breakpoint)  

        # update hashmap
        self.breakpoints[addr] = original  

    def wait(self, flags=0):
        # While being traced, the child will stop each time it gets a signal.
        # Parent will be notified at next call to waitpid.
        return os.waitpid(self.pid, flags)
    
    def send(self, stdin, newline=None):
        if newline:
            stdin += newline
        os.write(self.iw_pipe, stdin)
    
    # "EOF" -> no simulated tty, cant send end of transmission.
    def close_input(self):
        os.close(self.iw_pipe)
