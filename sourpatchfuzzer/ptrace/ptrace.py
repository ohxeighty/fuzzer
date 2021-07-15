import ctypes
import sys
import os 

"""
Ptrace bindings. 
"""

PTRACE_TRACEME	  = 0
PTRACE_PEEKTEXT   = 1
PTRACE_PEEKDATA   = 2
PTRACE_POKETEXT   = 4
PTRACE_POKEDATA   = 5
PTRACE_CONT		  = 7
PTRACE_KILL		  = 8
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS	  = 12
PTRACE_SETREGS	  = 13
PTRACE_ATTACH	  = 16
PTRACE_DETACH	  = 17

libc = ctypes.CDLL('/lib/x86_64-linux-gnu/libc.so.6')
libc.ptrace.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_void_p]
libc.ptrace.restype = ctypes.c_uint64

# man ptrace
# long ptrace(enum __ptrace_request request, pid_t pid, void *addr, void *data);
def ptrace_traceme(): 
	"""
	PTRACE_TRACEME
	Indicate that this process is to be traced by its parent. A process probably shouldn't make this request if its parent isn't expecting to trace it. (pid, addr, and data are ignored.)
	"""
	libc.ptrace(PTRACE_TRACEME, 0, 0, 0) 

def ptrace_attach(pid):
	# tracee is sent a SIGSTOP	
	libc.ptrace(PTRACE_ATTACH, pid, 0, 0) 

def ptrace_continue(pid, signal=0):
	# If data != 0, it is the number of a signal to be delivered to tracee
	libc.ptrace(PTRACE_CONT, pid, 0, signal)
