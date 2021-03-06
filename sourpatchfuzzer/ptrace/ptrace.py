import ctypes, ctypes.util
import sys
import os 

"""
Ptrace bindings. 
Note that the constants are pulled from my machine (Linux). 
Should match deployment machine.
In theory we could dynamically populate them, but its a lot of work.
"""

PTRACE_TRACEME	  = 0x0
PTRACE_PEEKTEXT   = 0x1
PTRACE_PEEKDATA   = 0x2
PTRACE_POKETEXT   = 0x4
PTRACE_POKEDATA   = 0x5
PTRACE_CONT		  = 0x7
PTRACE_KILL		  = 0x8
PTRACE_SINGLESTEP = 0x9
PTRACE_GETREGS	  = 0xC
PTRACE_SETREGS	  = 0xD
PTRACE_ATTACH	  = 0x10
PTRACE_DETACH	  = 0x11
PTRACE_SETOPTIONS = 0x4200

# Options
PTRACE_O_TRACESYSGOOD = 0x00000001
PTRACE_O_TRACEFORK = 0x00000002
PTRACE_O_TRACEVFORK = 0x00000004
PTRACE_O_TRACECLONE = 0x00000008
PTRACE_O_TRACEEXEC = 0x00000010
PTRACE_O_TRACEVFORKDONE = 0x00000020
PTRACE_O_TRACEEXIT = 0x00000040

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
libc.ptrace.argtypes = [ctypes.c_uint64, ctypes.c_uint64, ctypes.c_void_p, ctypes.c_void_p]
# long long unsigned
libc.ptrace.restype = ctypes.c_uint64

# argtypes for persona 
libc.syscall.argtypes = [ctypes.c_long, ctypes.c_ulong]
libc.syscall.restype = ctypes.c_uint64
# also export method for personality
# if bothered move this out later
# see /usr/include/sys/personality.h -> ADDR_NO_RANDOMIZE = 0x40000
# sys_personality = 135 
def personality_disable_aslr():
    libc.syscall(135, 0x40000)

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

def ptrace_setoptions(pid, options):
	for option in options:
		libc.ptrace(PTRACE_SETOPTIONS, pid, 0, option)

def ptrace_singlestep(pid):
	libc.ptrace(PTRACE_SINGLESTEP, pid, 0, 0)

def ptrace_peek(pid, addr):
    return libc.ptrace(PTRACE_PEEKTEXT, pid, addr, 0)

def ptrace_poke(pid, addr, data):
    libc.ptrace(PTRACE_POKETEXT, pid, addr, data)

def ptrace_getregs(pid, data):
    libc.ptrace(PTRACE_GETREGS, pid, 0, data)

def ptrace_setregs(pid, data):
    libc.ptrace(PTRACE_SETREGS, pid, 0, data)

def ptrace_detach(pid):
    libc.ptrace(PTRACE_DETACH, pid, 0, 0)
