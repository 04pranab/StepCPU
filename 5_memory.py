# ============================================================
#  Step 5 — CPU with Memory
#
#  What's new vs step 4:
#    - self.mem  : 16-cell data memory, separate from program
#    - LOAD      : rd = mem[rs1 + offset]
#    - STORE     : mem[rs1 + offset] = rs2
#
#  THE CONTRACT (updated):
#
#  R-type:  opcode[15:12] | rd[11:9]  | rs1[8:6] | rs2[5:3] | funct[2:0]
#  I-type:  opcode[15:12] | rd[11:9]  | rs1[8:6] | imm[5:0]
#  B-type:  opcode[15:12] | rs1[11:9] | rs2[8:6] | cond[5:4]| offset[3:0]
#  L-type:  opcode[15:12] | rd[11:9]  | rs1[8:6] | offset[5:3] (LOAD)
#  S-type:  opcode[15:12] | rs2[11:9] | rs1[8:6] | offset[5:3] (STORE)
# ============================================================

MASK    = 0xF
MEM_SIZE = 16

# ALU ops
ADD=0; SUB=1; AND=2; OR=3; XOR=4; SLT=5
OP_NAME = {0:"ADD",1:"SUB",2:"AND",3:"OR",4:"XOR",5:"SLT"}

# Opcodes
R_TYPE = 0
I_TYPE = 1
LOAD   = 2  
STORE  = 3  
BRANCH = 4
HALT   = 15

# Branch conditions
BEQ=0; BNE=1; BLT=2
COND_NAME = {0:"BEQ",1:"BNE",2:"BLT"}


# ── Encoders ─────────────────────────────────────────────────

def r_instr(funct, rd, rs1, rs2):
    return (R_TYPE << 12) | (rd << 9) | (rs1 << 6) | (rs2 << 3) | funct

def i_instr(rd, rs1, imm):
    return (I_TYPE << 12) | (rd << 9) | (rs1 << 6) | (imm & 0x3F)

def load(rd, rs1, offset):              
    # rd = mem[rs1 + offset]
    # offset sits in bits [5:3]  (3 bits → 0 to 7)
    return (LOAD << 12) | (rd << 9) | (rs1 << 6) | ((offset & 0x7) << 3)

def store(rs2, rs1, offset):            
    # mem[rs1 + offset] = rs2
    # rs2 goes where rd usually lives (bits [11:9])
    # offset sits in bits [5:3]
    return (STORE << 12) | (rs2 << 9) | (rs1 << 6) | ((offset & 0x7) << 3)

def b_instr(cond, rs1, rs2, offset):
    return (BRANCH << 12) | (rs1 << 9) | (rs2 << 6) | (cond << 4) | (offset & 0xF)

def halt():
    return HALT << 12


# ── ALU ───────────────────────────────────────────────────────

def alu(a, b, op):
    a, b = a & MASK, b & MASK
    if   op == ADD: result = a + b
    elif op == SUB: result = a - b
    elif op == AND: result = a & b
    elif op == OR:  result = a | b
    elif op == XOR: result = a ^ b
    elif op == SLT: result = 1 if a < b else 0
    else: raise ValueError(f"bad op {op}")
    return result & MASK

def sign_extend_4(v):
    v = v & 0xF
    return v - 16 if v & 0x8 else v


# ── CPU ───────────────────────────────────────────────────────

class CPU:

    def __init__(self, program, data=None):
        self.prog    = program
        self.mem     = [0] * MEM_SIZE        # data memory, all zeros
        self.regs    = [0] * 8
        self.pc      = 0
        self.running = True

        # optionally pre-load data memory
        if data:
            for i, v in enumerate(data):
                self.mem[i] = v & MASK

    def rr(self, i): return self.regs[i] & MASK
    def rw(self, i, v):
        if i != 0: self.regs[i] = v & MASK

    def show_mem(self):
        print("  Memory:", end="")
        for i, v in enumerate(self.mem):
            if v != 0:
                print(f"  [{i}]={v}", end="")
        print()

    def step(self):
        instr      = self.prog[self.pc]
        cur        = self.pc
        self.pc   += 1
        opcode     = (instr >> 12) & 0xF

        if opcode == R_TYPE:
            rd    = (instr >> 9) & 0x7
            rs1   = (instr >> 6) & 0x7
            rs2   = (instr >> 3) & 0x7
            funct = (instr >> 0) & 0x7
            a, b  = self.rr(rs1), self.rr(rs2)
            result = alu(a, b, funct)
            self.rw(rd, result)
            print(f"  [{cur}]  {OP_NAME[funct]:<4}  x{rd} = x{rs1}({a}) {OP_NAME[funct]} x{rs2}({b}) = {result}")

        elif opcode == I_TYPE:
            rd    = (instr >> 9) & 0x7
            rs1   = (instr >> 6) & 0x7
            imm   = instr & 0x3F
            result = alu(self.rr(rs1), imm & MASK, ADD)
            self.rw(rd, result)
            print(f"  [{cur}]  ADDI  x{rd} = x{rs1}({self.rr(rd)}) + {imm} = {result}")

        elif opcode == LOAD:                             
            rd     = (instr >> 9) & 0x7
            rs1    = (instr >> 6) & 0x7
            offset = (instr >> 3) & 0x7
            addr   = (self.rr(rs1) + offset) & MASK
            value  = self.mem[addr]
            self.rw(rd, value)
            print(f"  [{cur}]  LOAD  x{rd} = mem[x{rs1}({self.rr(rs1)})+{offset}] = mem[{addr}] = {value}")

        elif opcode == STORE:                            
            rs2    = (instr >> 9) & 0x7
            rs1    = (instr >> 6) & 0x7
            offset = (instr >> 3) & 0x7
            addr   = (self.rr(rs1) + offset) & MASK
            value  = self.rr(rs2)
            self.mem[addr] = value
            print(f"  [{cur}]  STORE mem[x{rs1}({self.rr(rs1)})+{offset}] = mem[{addr}] ← x{rs2}({value})")

        elif opcode == BRANCH:
            rs1    = (instr >> 9) & 0x7
            rs2    = (instr >> 6) & 0x7
            cond   = (instr >> 4) & 0x3
            offset = sign_extend_4(instr & 0xF)
            a, b   = self.rr(rs1), self.rr(rs2)
            name   = COND_NAME.get(cond, f"BR{cond}")
            taken  = False
            if   cond == BEQ: taken = (a == b)
            elif cond == BNE: taken = (a != b)
            elif cond == BLT: taken = (a <  b)
            else: print(f"  [!] unknown cond={cond}")
            if taken:
                self.pc = cur + offset
                print(f"  [{cur}]  {name}   x{rs1}({a}) x{rs2}({b}) TAKEN → PC={self.pc}")
            else:
                print(f"  [{cur}]  {name}   x{rs1}({a}) x{rs2}({b}) not taken")

        elif opcode == HALT:
            self.running = False
            print(f"  [{cur}]  HALT")

        else:
            print(f"  [{cur}]  ??? unknown opcode {opcode}")
            self.running = False

    def run(self, max_cycles=60):
        print(f"  {'PC':<5}  instruction")
        print("  " + "-" * 50)
        for _ in range(max_cycles):
            if not self.running: break
            self.step()
        if self.running:
            print(f"  [!] stopped at {max_cycles} cycles")


# ══════════════════════════════════════════════════════════════
#  Demo 1 — store two values, load them back, add them
# ══════════════════════════════════════════════════════════════

print("=" * 52)
print("Demo 1 — store values in memory, load and add them")
print("=" * 52)

prog1 = [
    i_instr(rd=1, rs1=0, imm=6),     # 0: x1 = 6
    i_instr(rd=2, rs1=0, imm=9),     # 1: x2 = 9
    store(rs2=1, rs1=0, offset=0),   # 2: mem[0] = x1 (store 6)
    store(rs2=2, rs1=0, offset=1),   # 3: mem[1] = x2 (store 9)
    load(rd=3, rs1=0, offset=0),     # 4: x3 = mem[0] (load 6)
    load(rd=4, rs1=0, offset=1),     # 5: x4 = mem[1] (load 9)
    r_instr(ADD, rd=5, rs1=3, rs2=4),# 6: x5 = x3 + x4
    store(rs2 = 5, rs1=0, offset=3),    
    halt(),                          
]

cpu1 = CPU(prog1)
cpu1.run()
cpu1.show_mem()
print(f"  Regs: {cpu1.regs}")


# ══════════════════════════════════════════════════════════════
#  Demo 2 — sum an array in memory
#  mem = [3, 5, 2, 4, 1]  →  x1 should = 15
# ══════════════════════════════════════════════════════════════

print()
print("=" * 52)
print("Demo 2 — sum array [3,5,2,4,1] stored in memory")
print("=" * 52)

# Plan:
#   x1 = accumulator (sum), starts 0
#   x2 = index (address), starts 0
#   x3 = limit  = 5
#   x4 = step   = 1
#   x5 = temp (loaded value)
#
#   loop:
#     x5 = mem[x2]       load next element
#     x1 = x1 + x5       add to sum
#     x2 = x2 + x4       advance index
#     if x2 < x3: loop

prog2 = [
    i_instr(rd=1, rs1=0, imm=0),      # 0: x1 = 0  (sum)
    i_instr(rd=2, rs1=0, imm=0),      # 1: x2 = 0  (index)
    i_instr(rd=3, rs1=0, imm=5),      # 2: x3 = 5  (limit)
    i_instr(rd=4, rs1=0, imm=1),      # 3: x4 = 1  (step)
    # loop top — addr 4
    load(rd=5, rs1=2, offset=0),      # 4: x5 = mem[x2]
    r_instr(ADD, rd=1, rs1=1, rs2=5), # 5: x1 = x1 + x5
    r_instr(ADD, rd=2, rs1=2, rs2=4), # 6: x2 = x2 + 1
    b_instr(BLT, rs1=2, rs2=3, offset=-3), # 7: if x2<5 → back to addr 4
    halt(),                            # 8
]

data = [3, 5, 2, 4, 1]   # array in memory
cpu2 = CPU(prog2, data=data)
cpu2.run()
print(f"  Sum = x1 = {cpu2.regs[1]}  (expected 15)")