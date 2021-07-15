Do first. Look at how we can collect code coverage. 

# C Bindings
Take advantage of C for low level ops. 
```python
from ctypes import cdll

lib = cdll.LoadLibrary("blah.so")

...

```

# Strategies for Reducing Instrumentation Overhead
C Harness? Ctypes. 
* Load ELF into memory and run. Hard because we have to parse the ELF (Or get a BFD lib to do it) then handle relocations. Does it even increase performance that much? So many optimisations for disk caching... 
	* Extension: Saving process state in memory then jumping back to that so we don't have to restart the process and go through initialization, resolving relocations ...
		* This is even harder with the requirement **to not touch disk.** ???
		* We could outsource this to rigorous frameworks. (DMTCP, CRIU...)
			* These touch disk. Also a lot of overhead so... kind of defeats the purpose. 
* Avoid touching disk at all, aside from reads.


# PTrace
Ptrace for code injection and primitive debugging. Probably how we're going to implement instrumentation. 
https://ancat.github.io/python/2019/01/01/python-ptrace.html


# Preload
Preload sys libraries and replace functions? (i.e. read and stuff...)



 