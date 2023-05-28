# TONE

This is a repository for a CPU based on one instruction set (OISC).



## Introduction

We adopt `SUBLEQ` as only one instruction in this computing system, which can be proved to be Turing Complete. The instruction format is shown below. 

```
SUBLEQ A,B,C
```

The `SUBLEQ` instruction subtracts the contents at address B from the contents at address A, stores the result at address A, and then, if the result is not positive, transfers control to address C. Its pseudo code is shown below.

```
Instruction subleq a,b,c :
    Mem[a] = Mem[a] - Mem[b]
    if (Mem[a] ≤ 0)
        goto c
```



## Reference

[One-instruction set computer - Wikipedia](https://en.wikipedia.org/wiki/One-instruction_set_computer)
