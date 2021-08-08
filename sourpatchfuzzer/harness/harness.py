import ctypes
import sys
import os
import signal
import ptrace

# big fat chunky angr
# if bothered, please just pull the logic we need for creating our BBV
import angr

# 32 bit user reg struct
# see /usr/include/sys/user.h
# after much fucking pain, it turns out the below struct
# isnt correct in x86 mode when on x64 machine????
# looks like we still use extended register set...
#class user_regs_struct(ctypes.Structure):
#   _fields_ = [
#       ("ebx", ctypes.c_long),
#       ("ecx", ctypes.c_long),
#       ("edx", ctypes.c_long),
#       ("esi", ctypes.c_long),
#       ("edi", ctypes.c_long),
#       ("ebp", ctypes.c_long),
#       ("eax", ctypes.c_long),
#       ("xds", ctypes.c_long),
#       ("xes", ctypes.c_long),
#       ("xfs", ctypes.c_long),
#       ("xgs", ctypes.c_long),
#       ("orig_eax", ctypes.c_long),
#       ("eip", ctypes.c_long),
#       ("xcs", ctypes.c_long),
#       ("eflags", ctypes.c_long),
#       ("esp", ctypes.c_long),
#       ("xss", ctypes.c_long),
#   ]

class user_regs_struct(ctypes.Structure):
    _fields_ = [
        ("r15", ctypes.c_ulonglong),
        ("r14", ctypes.c_ulonglong),
        ("r13", ctypes.c_ulonglong),
        ("r12", ctypes.c_ulonglong),
        ("rbp", ctypes.c_ulonglong),
        ("rbx", ctypes.c_ulonglong),
        ("r11", ctypes.c_ulonglong),
        ("r10", ctypes.c_ulonglong),
        ("r9", ctypes.c_ulonglong),
        ("r8", ctypes.c_ulonglong),
        ("rax", ctypes.c_ulonglong),
        ("rcx", ctypes.c_ulonglong),
        ("rdx", ctypes.c_ulonglong),
        ("rsi", ctypes.c_ulonglong),
        ("rdi", ctypes.c_ulonglong),
        ("orig_rax", ctypes.c_ulonglong),
        # dont worry, im just as confused as you
        ("eip", ctypes.c_ulonglong),
        ("cs", ctypes.c_ulonglong),
        ("eflags", ctypes.c_ulonglong),
        ("rsp", ctypes.c_ulonglong),
        ("ss", ctypes.c_ulonglong),
        ("fs_base", ctypes.c_ulonglong),
        ("gs_base", ctypes.c_ulonglong),
        ("ds", ctypes.c_ulonglong),
        ("es", ctypes.c_ulonglong),
        ("fs", ctypes.c_ulonglong),
        ("gs", ctypes.c_ulonglong),
    ]

# https://googleprojectzero.blogspot.com/2020/04/fuzzing-imageio.html
# also other funcs we dont care to cover
# kind of useless since these symbols don't get loaded. FIX LATER. 
skip_setup_funcs =  ['__libc_csu_init', 
                     '__libc_csu_fini', 
                     '_fini',
                     '_di_fini',
                     '__do_global_dtors_aux',
                     '_start',
                     '_init',
                     'register_tm_clones',
                     'deregister_tm_clones',
                     'frame_dummy',]

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


        # some nice stats
        self.crash_eips = []
        self.iterations = 0 

        # our hashmap of addresses -> original instruction 
        # that keeps track of our persistent breakpoints
        # from run to run
        self.breakpoints = dict() 

        # x86 registers
        self.registers = user_regs_struct() 

        # hokay, now we use angr to extract our basic block vector which we use for code coverage
        self.angr_project = angr.Project(binary, load_options={'auto_load_libs': False})

        # create networkx control flow graph
        self.cfg = self.angr_project.analyses.CFGFast()
        self.cfg.normalize()
        
        self.bbv = []
        for node in self.cfg.functions.values():
            #print(self.cfg.functions[0x8049289])
            # ignore some functions
            if not node.name.startswith("__"):
                # we dont care about externs
                symbol = self.angr_project.loader.find_symbol(node.addr)
                # drop some setup funcs
                if symbol:
                    # cle identified as extern
                    if not symbol.owner.is_main_bin:
                        continue 
                    if symbol.is_import:
                        continue
                    if symbol.name in skip_setup_funcs:
                        continue
                    for block in node.blocks:
                        self.bbv.append(block.addr)
                        # initialise breakpoints 
                        self.breakpoints[block.addr] = 0 

    def populate_breakpoints(self):
        # pretty sure the process has to be stopped 
        for addr in self.breakpoints.keys(): 
            #print("Adding breakpoint at {}".format(hex(addr)))
            self.breakp(addr)
    
    def breakpoint_status(self):
        print("Current Coverage: {}/{}".format(len(self.bbv)-len(self.breakpoints),len(self.bbv)))

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

        # wait for child to reach start 
        # since exec means child is sent a SIGTRAP
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
        # print("Tracee starting to exec")
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
    # i legit can't tell why peek is giving me back 64 bit wide words...
    # https://stackoverflow.com/questions/23131773/how-can-i-insert-int3-with-ptrace-in-ubuntu-x64

    def peek(self, addr):
        #print("Peeking at {}".format(hex(addr)))
        val = ptrace.ptrace_peek(self.pid, ctypes.c_void_p(addr))
        #print(hex(val))
        return val
    
    # write word
    # ctypes should translate a python bytestring to a char* 
    # we would rather void * 
    def poke(self, addr, data):
        #print("Poking {} at {}".format(hex(data), hex(addr)))
        ptrace.ptrace_poke(self.pid, ctypes.c_void_p(addr), ctypes.c_void_p(data))

    # read regs into struct
    def getregs(self):
        ptrace.ptrace_getregs(self.pid, ctypes.byref(self.registers))
    
    # write struct regs into actual regs
    def setregs(self):
        ptrace.ptrace_setregs(self.pid, ctypes.byref(self.registers))

    # more reading https://eli.thegreenplace.net/2011/01/27/how-debuggers-work-part-2-breakpoints
    # break = \xCC
    # Assume little endian -> we read word at addr, then replace LSB with break
    # write back

    # since we need to store the instruction we overwrite, we keep a dictionary (hash map)
    # of addr -> original instructions.
   
    # also not sure if adjacent breakpoints will create 
    # a fucky wucky if we, say, restore the breakpoint that was placed first (since
    # it would restore the word to a state before the second breakpoint?)

    # deal with it if we come to it
    def breakp(self, addr):
        # peek to grab original word @ addr
        original = self.peek(addr) 
        if(original == -1 and (ctypes.get_errno() != 0)):
            print("uh oh - peek fucked up")
        breakpoint = ((original & 0xFFFFFFFFFFFFFF00) | 0xCC) 
        # poke addr with new value
        self.poke(addr, breakpoint)  

        # update hashmap
        # we only store the byte that we've overwritten
        self.breakpoints[addr] = (original & 0xFF)
    
    # ALSO - when we hit a break ip still increments, so, when we 
    # hit the breakpoint we need to decrement ip, restore the original instruction
    # then continue (or single step then write bp again if we're not removing it)
 
    def restore_current_bp(self):
        self.getregs()
        self.registers.eip -= 1 
        #print("Breakpoint @ {}".format(hex(self.registers.eip)))
        #print(self.angr_project.loader.find_symbol(self.registers.eip))

        #print("original val: {}".format(hex(self.breakpoints[self.registers.eip])))

        # reads what currently here 
        current = self.peek(self.registers.eip)
        # then mask appropriately
        original = (current & 0xFFFFFFFFFFFFFF00) | self.breakpoints[self.registers.eip]

        #print("will rewrite with: {}".format(hex(original)))
        self.poke(self.registers.eip, original)
        self.setregs()

        # We now remove this bp from the persistent breakpoints list
        self.breakpoints.pop(self.registers.eip)
        

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
