# TONE DEMO

Here we will demonstrate how the TONE works through a "hello world" demo.

## 1. Work Flow

We build up a [demo soc](../rtl/soc_demo) comprises a CPU core, a memory unit and a led controller, here we will demonstrate the work flow of TONE.

##### Programming

Firstly, use C to write a barebone program, for example,

```c
# hello.c
void main() {
    int* led = (int*)0xffff0000;
    while (1) {
        int n = 2400;
        while (n--);
        *led += 1;
    }
}
```

##### Compilation flow

We use riscv toolchain to compile this C program.

```bash
riscv64-unknown-elf-gcc -c -march=rv32i -mabi=ilp32 -O0 -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles hello.c -o hello.o
```

We only need the code part of the output file, so we execute `objcopy` to intercept it.

```bash
riscv64-unknown-elf-objcopy -O binary -j .text hello.o hello.bin
```

Let us use `objdump` to see what's inside it.

```bash
riscv64-unknown-elf-objdump -D -M noaliases,numeric -b binary hello.bin -mriscv
```

```
hello.bin:     file format binary


Disassembly of section .data:

0000000000000000 <.data>:
   0:   riscv64-unknown-elf-objdump: unrecognized disassembler option: noaliases
fe010113                add     x2,x2,-32
   4:   00812e23                sw      x8,28(x2)
   8:   02010413                add     x8,x2,32
   c:   ffff07b7                lui     x15,0xffff0
  10:   fef42423                sw      x15,-24(x8)
  14:   000017b7                lui     x15,0x1
  18:   96078793                add     x15,x15,-1696 # 0x960
  1c:   fef42623                sw      x15,-20(x8)
  20:   00000013                nop
  24:   fec42783                lw      x15,-20(x8)
  28:   fff78713                add     x14,x15,-1
  2c:   fee42623                sw      x14,-20(x8)
  30:   fe079ae3                bnez    x15,0x24
  34:   fe842783                lw      x15,-24(x8)
  38:   0007a783                lw      x15,0(x15)
  3c:   00178713                add     x14,x15,1
  40:   fe842783                lw      x15,-24(x8)
  44:   00e7a023                sw      x14,0(x15)
  48:   fcdff06f                j       0x14
```

As you can see, the first few instructions are used to handle the stack frame, and the last few instructions are the function of our program. Now we need to write one piece of assembly code to initialize the stack frame for the program to work properly.

```assembly
# start.s
.text
.global main
lui x2,0x0001
call main

```

Then, compile this assembly program.

```bash
riscv64-unknown-elf-gcc -c -nostdlib start.s -o start.o
```

Next, concatenate two binary files.

```bash
riscv64-unknown-elf-ld -melf32lriscv hello.o start.o -o final.o
```

Finally, extract the code segment as we shown before.

```bash
riscv64-unknown-elf-objcopy -O binary final.o final.bin
```

##### Interpretation flow

You can get instruction to interpreter through `-h` or `--help`.

```bash
usage: run.py [-h] [-o OUTPUT] file

positional arguments:
  file                  select source binary file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        place target binary file
```

```bash
python ./interpreter/run.py ./demo/final.bin
```

After running this script, we can get text of executable binary `fpga.txt` and `micro-procedure.txt` in current directory to initialize FPGA memory.

## 2. Implementation on FPGA

Upload the RTL codes in `./rtl/core` and `./rtl/soc_demo` into your EDA, and choose the user constrain file in `./fpga/constrain/soc_demo` to run implementation, then program the bitstream to your FPGA board, done.
