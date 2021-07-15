import harness
binls = harness.Harness(["/bin/ls","-al","/root"])
binls.spawn_process()
binls.cont()

