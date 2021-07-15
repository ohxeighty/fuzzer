import harness
binls = harness.Harness(["/tmp/json1"])
binls.spawn_process()
binls.cont()
binls.send(b"{}")


