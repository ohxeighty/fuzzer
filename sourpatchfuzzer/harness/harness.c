#include <harness.h>
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

// Refer to docs for strategies on mitigating harness overhead. Mainly 
// revolves around avoiding disk touch & keeping the ELF in memory (which
// is fairly difficult to implement from scratch). 

// For now, just pipe->fork->exec 
// Haven't profiled the performance gain so this is all guesswork.

pid_t pid = 0;
int pipefd[2]; 
