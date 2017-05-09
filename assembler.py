# assembler.py
# Benjamin Parfitt, Dec 9, 2016

import sys
sym_table = {}
offset_list = {}
true_offset = 0
# Data structure to hold the mnemonics used and their information
class Mnemonic:
    def __init__(self, _type, _format, _opcode, _operands):
        self._type = _type
        self._format = _format
        self._opcode = _opcode
        self._operands = _operands
# Dictionary containing the mnemonics of the SIC/XE language
mnemons = {
    'ADD':   Mnemonic('i', 3, 0x18, 'm'),
    'ADDR':  Mnemonic('i', 2, 0x90, 'r1,r2'),
    'AND':   Mnemonic('i', 3, 0x40, 'm'),
    'CLEAR': Mnemonic('i', 2, 0xB4, 'r1'),
    'COMP':  Mnemonic('i', 3, 0x28, 'm'),
    'COMPR': Mnemonic('i', 2, 0xA0, 'r1,r2'),
    'DIV':   Mnemonic('i', 3, 0x24, 'r1,r2'),
    'DIVR':  Mnemonic('i', 2, 0x9C, 'r1,r2'),
    'HIO':   Mnemonic('i', 1, 0xF4, ''),
    'J':     Mnemonic('i', 3, 0x3C, 'm'),
    'JEQ':   Mnemonic('i', 3, 0x30, 'm'),
    'JGT':   Mnemonic('i', 3, 0x34, 'm'),
    'JLT':   Mnemonic('i', 3, 0x38, 'm'),
    'JSUB':  Mnemonic('i', 3, 0x48, 'm'),
    'LDA':   Mnemonic('i', 3, 0x00, 'm'),
    'LDB':   Mnemonic('i', 3, 0x68, 'm'),
    'LDCH':  Mnemonic('i', 3, 0x50, 'm'),
    'LDF':   Mnemonic('i', 3, 0x70, 'm'),
    'LDL':   Mnemonic('i', 3, 0x08, 'm'),
    'LDS':   Mnemonic('i', 3, 0x6C, 'm'),
    'LDT':   Mnemonic('i', 3, 0x74, 'm'),
    'LDX':   Mnemonic('i', 3, 0x04, 'm'),
    'LPS':   Mnemonic('i', 3, 0xD0, 'm'),
    'MUL':   Mnemonic('i', 3, 0x20, 'm'),
    'MULR':  Mnemonic('i', 2, 0x98, 'r1,r2'),
    'OR':    Mnemonic('i', 3, 0x44, 'm'),
    'RD':    Mnemonic('i', 3, 0xD8, 'm'),
    'RMO':   Mnemonic('i', 2, 0xAC, 'r1,r2'),
    'RSUB':  Mnemonic('i', 3, 0x4C, ''),
    'SHIFTL':Mnemonic('i', 2, 0xA4, 'r1,n'),
    'SHIFTR':Mnemonic('i', 2, 0xA8, 'r1,n'),
    'SIO':   Mnemonic('i', 1, 0xF0, ''),
    'SSK':   Mnemonic('i', 3, 0xEC, 'm'),
    'STA':   Mnemonic('i', 3, 0x0C, 'm'),
    'STB':   Mnemonic('i', 3, 0x78, 'm'),
    'STCH':  Mnemonic('i', 3, 0x54, 'm'),
    'STI':   Mnemonic('i', 3, 0xD4, 'm'),
    'STL':   Mnemonic('i', 3, 0x14, 'm'),
    'STS':   Mnemonic('i', 3, 0x7C, 'm'),
    'STSW':  Mnemonic('i', 3, 0xE8, 'm'),
    'STT':   Mnemonic('i', 3, 0x84, 'm'),
    'STX':   Mnemonic('i', 3, 0x10, 'm'),
    'SUB':   Mnemonic('i', 3, 0x1C, 'm'),
    'SUBR':  Mnemonic('i', 2, 0x94, 'r1,r2'),
    'SVC':   Mnemonic('i', 2, 0xB0, 'n'),
    'TD':    Mnemonic('i', 3, 0xE0, 'm'),
    'TIO':   Mnemonic('i', 1, 0xF8, ''),
    'TIX':   Mnemonic('i', 3, 0x2C, 'm'),
    'TIXR':  Mnemonic('i', 2, 0xB8, 'm'),
    'WD':    Mnemonic('i', 3, 0xDC, 'm'),
    'BYTE':  Mnemonic('r', 1, 0, 'm'),
    'WORD':  Mnemonic('r', 3, 0, 'm'),
    'RESB':  Mnemonic('r', 1, 0, 0),
    'RESW':  Mnemonic('r', 3, 0, 0),
    'START': Mnemonic('a', 1, 0, 0),
    'END':   Mnemonic('a', 0, 0, 0),
    'BASE':  Mnemonic('b', 0, 0, 0)
}
# Used to display error messages if errors occur.
def error(message = "Error"):
    print(message)
    sys.exit()
# Used to edit strings(since they are immutable in python)
def chg_str(string, pos, item):
    nwstr = ''
    for i in range(len(string)):
        if i == pos:
            nwstr+=item
        else:
            nwstr+=string[i]
    return nwstr
# Removes the + so the mnemonic can be used when indexing the dictionary
def base_mn(string):
    if (string[0] == '+'):
        return string [1:]
    return string
# Used in pass one to determine the value to add to the offset
def instr_len(mnemonic):
    if (mnemons[base_mn(mnemonic)]._format == 3):
        if (mnemonic[0] == '+'):
            offset = 4
        else:
            offset = 3
    elif (mnemons[mnemonic]._format == 2):
        offset = 2
    else:
        offset = 1
    return offset
# Used in pass one to handle data declarations
def data_dec(mnemonic, operand):
    if (mnemonic[0] == 'R'):
        return int(operand)*mnemons[mnemonic]._format
    elif (mnemonic == 'BYTE'):
        if (operand[0] == 'C'):
            return (len(operand)-3)
        elif (operand[0] == 'X'):
            return 1
    elif (mnemonic =='WORD'):
        return 3
    else:
        error("Possibly invalid operands: "+operand+ ", for "+mnemonic)
# Used to parse the line of the text file into its parts, calc offset, etc
def line_part(line, line_num):
    global true_offset
    offset_list[line_num] = true_offset
    lmoc = line.split()
    try:
        if (line[0] == '.'):
            return 0
        if (ord(line[0]) == 9 or line[0] == ' '):
            state = 0
            mnemonic = base_mn(lmoc[0])
            traits = mnemons[mnemonic]
            if (traits._type == 'i'):
                offset = instr_len(lmoc[0])
            elif (traits._type == 'r'):
                offset = data_dec(lmoc[0], lmoc[1])
            elif (traits._type == 'a'):
                if mnemonic == "START":
                    offset = hext(lmoc[1])
                else:
                    offset = 0
            else:
                offset = 0
        else:
            state = 1
            sym_table[lmoc[0]] = true_offset
            mnemonic = base_mn(lmoc[1])
            traits = mnemons[mnemonic]
            if (traits._type == 'i'):
                offset = instr_len(lmoc[1])
            elif (traits._type == 'r'):
                offset = data_dec(lmoc[1], lmoc[2])
            elif (traits._type == 'a'):
                if mnemonic == "START":
                    offset = hext(lmoc[2])
                else:
                    offset = 0
            else:
                offset = 0
    except:
        error("Invalid syntax may be present: "+lmoc[0])
    true_offset += offset
    return
# For pass one
def pass_one(filename):
    try:
        openfile = open(filename, 'r')
    except IOError:
        print("Can't open file " + sys.argv[1])
        return 0
    
    line_num = 0
    for line in openfile:
        line_part(line, line_num)
        line_num += 1
    offset_list[line_num] = true_offset
    return 1

#ENTER PASS 2
def hext(text):
    num = 0
    mul = 16*(len(text)-1)
    for c in text:
        if ord(c) < 58:
            num += int(c)*mul
        else:
            num += (ord(c)-55)*mul
        mul = mul/16
    return num

def line_part2(line, label):
    lmoc = line.split()
    if len(lmoc)-label == 1:
        return lmoc[0+label], ""
    return lmoc[label],lmoc[label+1]

def memory_save(line, label=1):
    lmoc = line.split()
    if label == 0:
        lmoc = ['']+lmoc
    if lmoc[1][0] == 'R':
        return 1,'0'*(int(lmoc[2])*mnemons[lmoc[1]]._format)*8
    elif lmoc[1][0] == 'W':
        return 0,con2bin(int(lmoc[2]), 24)
    else:
        if lmoc[2][0] == 'C':
            opcode = ''
            for c in lmoc[2][2:len(lmoc[2])-1]:
                opcode += con2bin(ord(c), 8)
            return 0,opcode
        else:
            return 0,con2bin(hext(lmoc[2][2:4]), 8)

# This group converts numbers to their proper length bitstrings
def hexoff(num):
    return ('0'*(7-len(hex(num)))+hex(num)[2:])
def con2bin(num, ml = 4):
    return ('0'*(ml+2-len(bin(num))))+(bin(num)[2:])
def disp2bin(num):
    if num < 0:
        num = num + (1<<12)
    return ('0'*(14-len(bin(num))))+(bin(num)[2:])
def addr2bin(num):
    if num in sym_table:
        num = sym_table[num]
    else:
        num = int(num)
    return ('0'*(22-len(bin(num))))+(bin(num)[2:])

# Returns bits of regs to be used without '0b'
def reg2bits(operands, _operands):
    regs = {'A':0,'X':1,'L':2,'B':3,'S':4,'T':5,'F':6,'PC':8,'SW':9}
    if (',' in operands):
        if (',' in _operands):
            ops = operands.split(',')
            if (ops[0] in regs and ops[1] in regs):
                return (con2bin(regs[ops[0]])+(con2bin(regs[ops[1]])))
            elif (ops[0] in regs and ord(ops[1][0]) < 58):
                return (con2bin(regs[ops[0]])+(con2bin(int(ops[1])-1)))
        error()
    else:
        if (',' not in _operands):
            if (operands in regs):
                return con2bin(regs[operands])+("0000")
            elif (ord(operands[0]) < 58):
                return con2bin(int(operands))+("0000")
# Calculates the proper n and i bits
def ni_bits(opcode, operands):
    opcode = con2bin(opcode, 8)
    if operands[0] == '@':
        opcode = chg_str(opcode, len(opcode)-2, '1')
    elif operands[0] == '#':
        opcode = chg_str(opcode, len(opcode)-1, '1')
    else:
        opcode = chg_str(opcode, len(opcode)-1, '1')
        opcode = chg_str(opcode, len(opcode)-2, '1')
    return opcode
# Calculate to correct xbpe bits
def xbpe_bits(opcode, operands, e, pc):
    e = str(e - 3)
    operand_list = operands.split(',')
    operands = operand_list[0]
    b = '0'
    p = '0'
    if e == '0':
        if (operands[0] == '#' or operands[0] == '@'):
            operands = operands[1:]
        if (ord(operands[0]) > 58):
            if sym_table[operands] - pc<2048 and sym_table[operands] - pc>-2049:
                b = '0'
                p = '1'
                disp = disp2bin(sym_table[operands] - pc)
            elif ("BASE" in sym_table and \
                  sym_table[operands] - sym_table["BASE"] <= 4096):
                b = '1'
                p = '0'
                disp = disp2bin(sym_table[operands] - sym_table["BASE"])
            else:
                error("Base and PC relative addressing both impossible for "\
                      +operands)
        else:
            b = '0'
            p = '0'
            disp = disp2bin(int(operands))
    else:
        if (operands[0] == '#' or operands[0] == '@'):
            disp = addr2bin(operands[1:])
        else:
            disp = addr2bin(sym_table[operands])
        x = '0'
    if (len(operand_list) == 2):
        x = '1'
    return x+b+p+e, disp

def bitstr2file(opcode, file):
    for i in range(len(opcode)/8):
        num = int(opcode[i*8:i*8+8], 2)
        file.write(chr(num))
    return

def bitstr2hex(opcode):
    strn = ''
    for i in range(len(opcode)/8):
        num = int(opcode[i*8:i*8+8], 2)
        strn += ('0'*(4-len(hex(num)))+(hex(num)[2:]))
    return strn

def pass_two(filename):
    try:
        openfile = open(filename, 'r')
    except IOError:
        print("Can't open file " + sys.argv[1])
        return 0
    try:
        for i in sym_table:
            print str(i)+":\t"+hexoff(sym_table[i])
        newfile = open(filename[0:len(filename)-4]+(".exe"), 'w+b')
        line_num = 1
        for line in openfile:
            if line[0] == '.':
                line_num+=1
                print(line[:len(line)-1])
                continue
            opz = 1
            lnlst = line.split()
            if len(lnlst) > 1 and (lnlst[1] in mnemons or lnlst[0] in mnemons):
                label = 1
                if (ord(line[0]) == 9 or line[0] == ' '):
                    label = 0
                if mnemons[line.split()[label]]._type == 'r':
                    res,opcode = memory_save(line, label)
                    bitstr2file(opcode, newfile)
                    listing = hexoff(offset_list[line_num-1])+'\t'
                    if not bool(res):
                        println(listing, line, opcode, 1)
                    else:
                        println(listing, line, '', 1)
                    line_num+=1
                    continue
            if (ord(line[0]) == 9 or line[0] == ' '):
                mnemonic,operands = line_part2(line, 0)
            else:
                mnemonic,operands = line_part2(line, 1)
            if (mnemonic == "START"):
                opcode = '0'*hext(operands)
                if opcode == '':
                    listing = "\t"
                    println(listing, line, opcode, 1)
                    line_num+=1
                    continue
            elif (mnemonic == "END"):
                newfile.close()
                break
            elif (mnemonic == "+RSUB" or mnemonic == "RSUB"):
                opcode = "01001111"+'0'*16
                if (mnemonic[0] == '+'):
                    opcode += '0'*8
                opz = 0
            elif mnemonic == "BASE":
                if "NOBASE" in sym_table:
                    del sym_table["NOBASE"]
                println('\t', line, '', 1)
                sym_table["BASE"] = sym_table[operands]
                line_num+=1
                continue
            elif mnemonic == "NOBASE":
                if "BASE" in sym_table:
                    del sym_table["BASE"]
                println('\t', line, '', 0)
                sym_table["NOBASE"] = sym_table[operands]
                line_num+=1
                continue
            elif (mnemonic[0] == '+'):
                opcode = ni_bits(mnemons[mnemonic[1:]]._opcode, operands)
                xbpe,addr = xbpe_bits(mnemons[mnemonic[1:]]._opcode, operands,\
                                      4,offset_list[line_num])
                opcode = opcode+(xbpe+(addr))
            elif(mnemons[mnemonic]._format == 3):
                opcode = ni_bits(mnemons[mnemonic]._opcode, operands)
                xbpe, disp = xbpe_bits(mnemons[mnemonic]._opcode, operands, 3,\
                                       offset_list[line_num])
                opcode = opcode+(xbpe+(disp))
            elif(mnemons[mnemonic]._format == 2):
                opcode = con2bin(mnemons[mnemonic]._opcode, 8)
                reg_bits = reg2bits(operands, mnemons[mnemonic]._operands)
                opcode = opcode+(reg_bits)
            else:
                opcode = con2bin(mnemons[mnemonic]._opcode, 8)
                opz = 0
            bitstr2file(opcode, newfile)
            listing = hexoff(offset_list[line_num-1])+'\t'
            println(listing, line, opcode, opz)
            line_num+=1
    except:
        error("Syntax errors may be present.")
    return
# Used in the printing of each line. Makes it look acceptable.
def println(listing, line, opcode, opnum):
    lmoc = line.split()
    if ord(line[0])>32:
        label = 1
    else:
        label = 0
    lbl = label
    for i in range(opnum+lbl+1):
        if label == 1:
            listing += lmoc[i]
            label = 0
        else:
            listing += '\t'+lmoc[i]

    listing +='\t'*(-1*(opnum-1))+'\t'+bitstr2hex(opcode)
    print(listing)

def main():
    filename = sys.argv[1];
    print(filename)
    passed = pass_one(filename)
    if passed:
        passed = pass_two(filename)

if __name__ == "__main__":
    main()
