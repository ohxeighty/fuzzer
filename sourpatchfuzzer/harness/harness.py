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

    def monitor(self, pid, r_pipe):
        child_data = os.read(r_pipe, 5096)
        if(child_data):
            # Child threw error
            print(child_data) 
        os.close(r_pipe)

    def spawn_child(self, stdout, w_pipe):
        # Handle actual process creation

        # Tracee should call TRACEME
        ptrace.ptrace_traceme()

        # If we don't want STDOUT, dup2 the FDs to point to devnull  
        if not stdout:  
            with open(os.devnull, "wb") as devnull:
                os.dup2(devnull.fileno(), 1)
                os.dup2(1, 2) 
        try:
            os.execv(self.binary, self.arguments)  
        except: 
            # Error occured - write to parent. 
            os.write(w_pipe, sys.exc_info())

        os.close(w_pipe)
            
    def spawn_process(self,stdout=True):
        # Fork overhead in python3? 
        # Might want to migrate this out to a shared lib.

        # Note that we copy over our current environment. 
        # Might want to tweak this later. 

        # Setup pipe and fork. 
        r_pipe, w_pipe = os.pipe()
        pid = os.fork()

        
        if pid: 
            # Parent
            os.close(w_pipe)
            self.monitor(pid, r_pipe)
            self.pid = pid 
            return pid  
        else:
            os.close(r_pipe)
            self.spawn_child(stdout, w_pipe)
    
    """
    Functions to handle ptrace business. 
    """

    def cont(self):
        ptrace.ptrace_continue(self.pid)
