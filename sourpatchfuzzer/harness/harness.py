import subprocess
import ctypes
import sys
import os
import ptrace

class Harness:
    """
    Binary harness. 
    """

    def __init__(self, argv):
        # In future, it would be ideal to load the ELF and keep it in memory,
        # size permitting -> less disk IO. 
        
        # We would need a BFD lib or other way to execute an image from memory.
        # For now, just execve. I'm sure disk caching optimisations are fine... 
        self.binary = argv[0]
        self.arguments = argv[1:]
        self.pid = -1 

        self.er_pipe = None
        self.ew_pipe = None
        self.ir_pipe = None
        self.iw_pipe = None
 
    def monitor(self, stdin):
        os.write(self.iw_pipe, stdin)
        child_data = os.read(self.er_pipe, 5096)
        if(child_data):
            # Child threw error
            print(child_data) 
        os.close(self.er_pipe)

    def spawn_child(self, stdout):
        # Handle actual process creation

        # Tracee should call TRACEME
        ptrace.ptrace_traceme()
        
        # Point pipe to stdin
        os.dup2(self.ir_pipe, 0)

        # If we don't want STDOUT, dup2 the FDs to point to devnull  
        if not stdout:  
            with open(os.devnull, "wb") as devnull:
                os.dup2(devnull.fileno(), 1)
                os.dup2(1, 2) 
        
    
        try:
            if self.arguments != []:
                os.execl(self.binary, self.arguments)  
            else:
                os.execl(self.binary, [" "])
        except: 
            # Error occured - write to parent. 
            os.write(self.ew_pipe, sys.exc_info())

        os.close(self.ew_pipe)
            
    def spawn_process(self, stdout=True, stdin=b""):
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
        self.er_pipe, self.ew_pipe = os.pipe()
        self.ir_pipe, self.iw_pipe = os.pipe() 

        # Fork 
        pid = os.fork()

         
        if pid: 
            # Parent
            os.close(self.ew_pipe)
            os.close(self.ir_pipe)

            self.pid = pid 
            self.monitor(stdin)
            return pid  
        else:
            os.close(self.er_pipe)
            os.close(self.iw_pipe)

            self.spawn_child(stdout)
          
    """
    Functions to interact with traced process..
    """

    def cont(self):
        ptrace.ptrace_continue(self.pid)

    def wait(self):
        # While being traced, the child will stop each time it gets a signal.
        # Parent will be notified at next call to waitpid.
        os.waitpid(self.pid)
    
    def send(self, stdin):
        os.write(self.iw_pipe, stdin)
