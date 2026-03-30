# ============================================================
#  Step 4 — CPU with Branches  (fixed)
#
#  We add a new instruction type: B-type (branch).
#  Only two things changed from step 3:
#    1. New b_instr() encoder
#    2. New BRANCH block in the execute stage
#
#  THE CONTRACT:
#
#  R-type:  opcode[15:12] | rd[11:9] | rs1[8:6] | rs2[5:3] | funct[2:0]
#  I-type:  opcode[15:12] | rd[11:9] | rs1[8:6] | imm[5:0]
#  B-type:  opcode[15:12] | rs1[11:9]| rs2[8:6] | cond[5:4]| offset[3:0]
#
#  No field overlaps. Encoder writes, decoder reads. Same positions.
# ============================================================
 
MASK = 0xF
 
# ALU ops
ADD=0; SUB=1; AND=2; OR=3; XOR=4; SLT=5
OP_NAME = {0:"ADD",1:"SUB",2:"AND",3:"OR",4:"XOR",5:"SLT"}
 
# Opcodes
R_TYPE = 0
I_TYPE = 1
BRANCH = 4
HALT   = 15
 
# Branch conditions
BEQ=0; BNE=1; BLT=2
COND_NAME = {0:"BEQ",1:"BNE",2:"BLT"}

 
# ── Encoders — follow THE CONTRACT exactly ───────────────────
 
def r_instr(funct, rd, rs1, rs2):
    # [15:12]=opcode [11:9]=rd [8:6]=rs1 [5:3]=rs2 [2:0]=funct
    return (R_TYPE << 12) | (rd << 9) | (rs1 << 6) | (rs2 << 3) | funct
 
def i_instr(rd, rs1, imm):
    # [15:12]=opcode [11:9]=rd [8:6]=rs1 [5:0]=imm
    return (I_TYPE << 12) | (rd << 9) | (rs1 << 6) | (imm & 0x3F)
 
def b_instr(cond, rs1, rs2, offset):
    # [15:12]=opcode [11:9]=rs1 [8:6]=rs2 [5:4]=cond [3:0]=offset
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
    """4-bit unsigned → signed  (-8 to +7)."""
    v = v & 0xF
    return v - 16 if v & 0x8 else v
 
# ── The CPU ───────────────────────────────────────────────────

class CPU:
    def __init__(self, program):
        self.mem = program 
        self.regs = [0]*8
        self.running = True
        self.pc = 0        
    
    def reg_read(self, index):
        return self.regs[index]

    def reg_write(self, index, value):
        if index == 0:
            return
        self.regs[index] = value & MASK

    def step(self):
        instr      = self.mem[self.pc]
        current_pc = self.pc
        self.pc   += 1
 
        # ── DECODE — follow THE CONTRACT ─────────────────────
        opcode = (instr >> 12) & 0xF
        
        if opcode == R_TYPE:
            rd    = (instr >> 9) & 0x7
            rs1   = (instr >> 6) & 0x7
            rs2   = (instr >> 3) & 0x7
            funct = (instr >> 0) & 0x7
            a, b  = self.reg_read(rs1), self.reg_read(rs2)
            result = alu(a, b, funct)
            self.reg_write(rd, result)
            print(f"  [{current_pc}]  {OP_NAME[funct]}   x{rd} = x{rs1}({a}) {OP_NAME[funct]} x{rs2}({b}) = {result}   {self.regs}")
 
        elif opcode == I_TYPE:
            rd    = (instr >> 9) & 0x7
            rs1   = (instr >> 6) & 0x7
            imm   = instr & 0x3F
            a     = self.reg_read(rs1)
            result = alu(a, imm & MASK, ADD)
            self.reg_write(rd, result)
            print(f"  [{current_pc}]  ADDI  x{rd} = x{rs1}({a}) + {imm} = {result}   {self.regs}")
 
        elif opcode == BRANCH:
            rs1    = (instr >> 9) & 0x7
            rs2    = (instr >> 6) & 0x7
            cond   = (instr >> 4) & 0x3
            offset = sign_extend_4(instr & 0xF)
            a, b   = self.reg_read(rs1), self.reg_read(rs2)
            name   = COND_NAME[cond]
 
            taken = False
            if   cond == BEQ: taken = (a == b)
            elif cond == BNE: taken = (a != b)
            elif cond == BLT: taken = (a <  b)
 
            if taken:
                self.pc = current_pc + offset
                print(f"  [{current_pc}]  {name}   x{rs1}({a}) x{rs2}({b}) TAKEN → PC={self.pc}   {self.regs}")
            else:
                print(f"  [{current_pc}]  {name}   x{rs1}({a}) x{rs2}({b}) not taken   {self.regs}")
 
        elif opcode == HALT:
            self.running = False
            print(f"  [{current_pc}]  HALT   regs={self.regs}")
