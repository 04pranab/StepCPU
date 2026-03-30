# ============================================================
#  Step 2 — ALU  (Arithmetic Logic Unit)
#
#  Takes two 4-bit inputs A and B,
#  takes an operation code (which math to do),
#  returns one 4-bit result.
#
#  That's the entire spec.
# ============================================================

MASK = 0xF

# Operation codes — just constants we made up.
# These numbers will later live inside instruction words.
ADD = 0   # A + B
SUB = 1   # A - B
AND = 2   # A & B  (bitwise)
OR  = 3   # A | B  (bitwise)
XOR = 4   # A ^ B  (bitwise)
SLT = 5   # 1 if A < B, else 0  (Set Less Than)

# Names for printing
OP_NAMES = {ADD:"ADD", SUB:"SUB", AND:"AND", OR:"OR", XOR:"XOR", SLT:"SLT"}

def alu(a: int, b: int, op: int) -> int:
    
    """Do opperation on 2 4-bit inputs and return a 4-bit result always."""
    
    a = a & MASK
    b = b & MASK
    
    if op == ADD:
        return (a + b) & MASK   # wrap at 4 bits 
    if op == SUB:
        return (a - b) & MASK   # wrap at 4 bits
    if op == AND:
        return a & b
    if op == OR:
        return a | b
    if op == XOR:
        return a ^ b    
    if op == SLT:
        return 1 if a < b else 0
    raise ValueError(f"Unknown ALU operation code: {op}")

print("ALU test:")
print(f"  5 ADD  3  = {alu(5, 3, ADD)}")     # 8
print(f"  9 SUB  4  = {alu(9, 4, SUB)}")     # 5
print(f" 15 ADD  1  = {alu(15,1, ADD)}")     # 0  (overflow wraps)
print(f"  3 SUB  7  = {alu(3, 7, SUB)}")     # 12 (underflow wraps)
print(f"  6 AND  3  = {alu(6, 3, AND)}")     # 2
print(f"  5 OR   3  = {alu(5, 3, OR)}")      # 7
print(f"  3 SLT  7  = {alu(3, 7, SLT)}")    # 1  (3 < 7 is true)
print(f"  9 SLT  3  = {alu(9, 3, SLT)}")    # 0  (9 < 3 is false)
 
# Show the wrap-around clearly
print()
print("Overflow behaviour:")
for a, b in [(14,1),(14,2),(14,3),(15,1)]:
    raw = a + b
    result = alu(a, b, ADD)
    print(f"  {a} + {b} = {raw} raw  ->  {result} after 4-bit clamp")