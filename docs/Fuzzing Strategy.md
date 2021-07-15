# Mutation Based
* Identify format
* Formulate input and mutate via a method
* If mutant covers new code, add to corpus 
* Repeat

i.e. genetic evolution with code coverage as natural selection metric

# Structured Fuzzing
* Input aware



# Reading
LLVM SanitizerCoverage
Dynamic Binary Instrumentation (PIN) 

Look at other fuzzers like AFL, libFuzzer, Honggfuzz
https://arxiv.org/pdf/1812.11875.pdf



# Test Case Reduction
When we get a crash, we want to reduce the input down to the minimum length & complexity that will trigger that crash.

