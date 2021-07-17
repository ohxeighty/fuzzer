import ctypes
import sys
import os
import signal
import ptrace

class Harness:
    """
    Binary harness. 
    """

    def __init__(self, binary, arguments=[]):
        # In future, it would be ideal to load the ELF and keep it in memory,
        # size permitting -> less disk IO. 
        
        # We would need a BFD lib or other way to execute an image from memory.
        # For now, just execve. I'm sure disk caching optimisations are fine... 
        self.binary = binary
        # By convention, argv0 is the invoked bin
        self.arguments = arguments 
        self.pid = -1 

        #self.er_pipe = None
        #self.ew_pipe = None
        self.ir_pipe = None
        self.iw_pipe = None
 
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

        # Two pipes; child writes errors to parent.
        # Parent writes input to child. 
        #self.er_pipe, self.ew_pipe = os.pipe()
        self.ir_pipe, self.iw_pipe = os.pipe() 

        # Fork 
        self.pid = os.fork()
          
        if self.pid: 
            # Parent
            #os.close(self.ew_pipe)
            os.close(self.ir_pipe)

            return self.monitor() 
        else:
            # Child
            #os.close(self.er_pipe)
            os.close(self.iw_pipe)

            self.spawn_child(stdout)
          
    """
    Functions to interact with traced process..
    """

    def cont(self):
        ptrace.ptrace_continue(self.pid)

    def step(self):
        ptrace.ptrace_singlestep(self.pid)

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
