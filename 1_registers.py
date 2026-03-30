# ============================================================
#  Step 1 — Register File
#
#  A register file is just a list of 8 slots.
#  Each slot holds one 4-bit number (0 to 15).
#
#  Two rules:
#    1. x0 is always 0. Writing to it does nothing.
#    2. Values wrap at 4 bits. 16 becomes 0, 17 becomes 1, etc.
# ============================================================


MASK = 0xF

class Registers:
    
    def __init__(self):
        
        """ There are 8 registers, each initialized to 0. """
        self.reg = [0]*8
    
    def read(self, index: int):
        """ read and return the value of register index. """
        return self.reg[index]
    
    def write(self, index: int, value: int):
        """ write value to register index. """
        if index == 0:
            return
        self.reg[index] = value & MASK
        
    def show(self):
        """Print all registers in a readable way."""
        print("Registers:")
        for i, v in enumerate(self.reg):
            marker = " <- always 0" if i == 0 else ""
            print(f"  x{i} = {v:2d}  ({v:04b}){marker}")


 
regs = Registers()
 
# Write some values
regs.write(1, 5)    # x1 = 5
regs.write(2, 9)    # x2 = 9
regs.write(3, 15)   # x3 = 15  (max 4-bit value)
regs.write(4, 16)   # x4 = 16  → wraps to 0
regs.write(5, 19)   # x5 = 19  → wraps to 3  (19 & 0xF = 3)
regs.write(0, 99)   # x0 = 99  → ignored, x0 stays 0
 
regs.show()
 
# Read back
print()
print(f"x1 + x2 = {regs.read(1) + regs.read(2)}")