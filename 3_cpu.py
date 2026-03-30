# ============================================================
#  Step 3 — The CPU
#
#  We wire the registers and ALU together.
#  The CPU reads instructions one at a time and executes them.
#
#  Instruction format (16 bits):
#
#  [15:12] opcode  — what to do        (4 bits)
#  [11:9]  rd      — where to store    (3 bits, register 0-7)
#  [8:6]   rs1     — first input       (3 bits, register 0-7)
#  [5:3]   rs2     — second input      (3 bits, register 0-7)
#  [2:0]   funct   — which ALU op      (3 bits)
#
#  Opcodes:
#    0  = R-type: rd = ALU(rs1, rs2)
#    1  = I-type: rd = ALU(rs1, immediate)   immediate is bits [5:0]
#   15  = HALT
# ============================================================


 
MASK = 0xF
 
# ALU ops (same as step 2)
ADD=0; SUB=1; AND=2; OR=3; XOR=4; SLT=5
OP_NAME = {0:"ADD",1:"SUB",2:"AND",3:"OR",4:"XOR",5:"SLT"}
 
# Opcodes
R_TYPE = 0
I_TYPE = 1
HALT   = 15
 
# ── Helpers to BUILD instructions (our tiny assembler) ───────
 
def r_instr(funct, rd, rs1, rs2):
    """Build an R-type instruction word."""
    return (R_TYPE << 12) | (rd << 9) | (rs1 << 6) | (rs2 << 3) | funct
 
def i_instr(funct, rd, rs1, imm):
    """Build an I-type instruction word (immediate in bits [5:0])."""
    return (I_TYPE << 12) | (rd << 9) | (rs1 << 6) | (imm & 0x3F)
 
def halt():
    """Build a HALT instruction."""
    return HALT << 12

# ── ALU (from step 2) ─────────────────────────────────────────
 
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
        
        # ── FETCH ────────────────────────────────────────────
        
        instr = self.mem[self.pc]
        self.pc += 1
        
        # ── DECODE ───────────────────────────────────────────
        
        opcode = (instr >> 12) & 0xF
        rd     = (instr >> 9)  & 0x7
        rs1    = (instr >> 6)  & 0x7
        rs2    = (instr >> 3)  & 0x7
        funct   = instr & 0x7
        imm = instr & 0x3F  # for I-type
        
        # ── EXECUTE ──────────────────────────────────────────
        
        if opcode == HALT:
            print("HALT encountered. Stopping CPU.")
            self.running = False
            return
        
        a = self.reg_read(rs1)
        
        if opcode == R_TYPE:
            b = self.reg_read(rs2)     # second input from register
            result = alu(a, b, funct)
            self.reg_write(rd, result)
            print(f"  R  x{rd} = x{rs1}({a}) {OP_NAME[funct]} x{rs2}({b}) = {result}   regs={self.regs}")
            
        elif opcode == I_TYPE:
            b = imm & MASK
            result = alu(a, b, ADD)
            self.reg_write(rd, result)
            print(f"  I  x{rd} = x{rs1}({a}) {OP_NAME[funct]} {imm} = {result}   regs={self.regs}")
            
    def run(self):
        """Run until HALT."""
        
        print(f"{'Cycle':<6} instruction")
        print("-" * 60)
        cycle = 0
        while self.running and cycle < 100:
            print(f"  {cycle:<4}", end="")
            self.step()
            cycle += 1
            
program = [
    i_instr(ADD, rd=1, rs1=0, imm=7),
    i_instr(ADD, rd=2, rs1=0, imm=3),
    r_instr(AND, rd=3, rs1=1, rs2=2),
    r_instr(OR,  rd=4, rs1=1, rs2=2),
    r_instr(XOR, rd=5, rs1=1, rs2=2),
    halt(),
]

print("Program:")
for i, instr in enumerate(program):
    print(f"  {i:02d}: {instr:016b}")
 
cpu = CPU(program)
cpu.run()
 
print()
print("Final registers:")
for i, v in enumerate(cpu.regs):
    print(f"  x{i} = {v}")                                                             