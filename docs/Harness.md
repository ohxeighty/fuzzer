Do first. Look at how we can collect code coverage. 


# C Bindings
Take advantage of C for low level ops. 
```python
from ctypes import cdll

lib = cdll.LoadLibrary("blah.so")

...

```