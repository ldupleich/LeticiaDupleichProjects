
"""
NAND2Tetris Project 6 - Assembler
Leticia Dupleich

References:
1. Nisan, N., & Schocken, S. (2005). Assembler. In The Elements of Computing Systems: Building a Modern
Computer from First Principles (pp. 103-120). MIT Press.
"""

import os
import sys

# -----------------------------------------------------------------------
# Module 1: Parse the symbolic command into its underlying fields.
# -----------------------------------------------------------------------

def initialize (input_file):
    """
    This function goes through every command of the input file / assembler code and removes any comments and spaces.
    These stripped commands are then saved into the list clean_commands. In order for the assembler to keep track of where
    it is in the file (avoiding repition), we need to keep track of a state which can be done with classes, but I
    chose to implement a dictionary called "parser". 
    """

    clean_commands = []
    
    for line in input_file:
        line = line.partition("//")[0]
        line = line.strip()

        if line:
            clean_commands.append(line)

    # Index tracks which line we are in, current_command tracks the content of the line
    parser = {"commands": clean_commands, "index": 0, "current_command": None}
    
    return parser


def hasMoreCommands (parser):
    """
    This function simply checks if we still need to process more commands. If the function returns False,
    then all of the commands have been processed.
    """
    
    if parser["index"] < len(parser["commands"]):
        return True
    else:
        return False


def advance (parser):
    """
    This function reads the next command from the input file and makes it the current command. Since
    the dictionary "parser" has been implemented to keep track of the state of the program, every time
    this function is called, the parser knows in which line to resume. This function should only be called
    if the function hasMoreCommands() returns True.
    """

    # The statement below works in this way: If index = 0, it gets command[0], if index = 1, it gets command[1]...
    parser["current_command"] = parser["commands"][parser["index"]]
    parser["index"] += 1


def commandType(parser):
    """
    This function determines what type of command each line / command is. An A_command (or instruction)
    contains an "@" symbol before it (format: @Xxx) and denotes the case where Xxx is either a symbol
    or a decimal number. An L_command (pseudocode command) is written in parentheses (format: (Xxx)) and denotes the
    case where Xxx is a symbol. Finally, a C_command (compute instructions) has the format dest=comp;jump.
    """
    
    command = parser["current_command"]

    if command.startswith("@"):
        return "A"
    elif command.startswith("("):
        return "L"
    else:
        return "C"


def symbol(parser):
    """
    This function returns the symbol or decimal Xxx of the current command @Xxx or (Xxx). Thus, it should be called
    only when commandType() is A_command or L_command. If the command type is A then we want to return all the contents
    after the "@" so we use the splicing [1:]. If the command type is L we want to return everything within the parentheses
    so we use [1:-1] to splice.
    """
    
    command = parser["current_command"]
    command_type = commandType(parser)

    if command_type == "A":
        return command[1:]
    elif command_type == "L":
        return command[1:-1]
        
    
def dest(parser):
    """
    This function is used to extract the "dest" part of the C_command and thus should only be called when the commandType
    function returns "C". A dest part is present if there exists an "=" sign in the command and it is located before the
    "=" so it can be accessed by splitting the command at the equal sign and getting everything before it ([0]).
    """
    
    command = parser["current_command"]

    if "=" in command:
        return command.split("=")[0]
    else:
        return None


def comp(parser):
    """
    This function is used to extract the "comp" part of the C_command and thus should only be called when the commandType
    function returns "C". A comp part is always present and it exists between the "=" (if there is one) and the ";" (if there
    is one). So, to access this part, we need to determine which of the symbols is present and either get the part before ([0])
    or after it ([1]).
    """
    
    command = parser["current_command"]

    if "=" in command:
        command = command.split("=")[1]
    if ";" in command:
        command = command.split(";")[0]
    return command


def jump(parser):
    """
    This function is used to extract the "jump" part of the C_command and thus should only be called when the commandType
    function returns "C". A jump part is present if there exists an ";" in the command and it is located after the
    ";" so it can be accessed by splitting the command at the semi-colon and getting everything after it ([1]).
    """
    
    command = parser["current_command"]

    if ";" in command:
        return command.split(";")[1]
    else:
        return None

# -----------------------------------------------------------------------
# Module 2: Translates Hack assembly language mnemonics into binary codes.
# -----------------------------------------------------------------------

def dest_to_bin(mnemonics):
    """
    This function returns the binary code for the "dest" mnemonic of a C_command which corresponds to 3 bits.
    In order to do this, it uses a dictionary containing the table of translations provided in the written
    instructions for "Project 6".
    """

    d_table = {
        "null": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111"
    }

    binary = d_table[mnemonics]
    return binary


def comp_to_bin(mnemonics):
    """
    This function returns the binary code for the "comp" mnemonic of a C_command which corresponds to 7 bits.
    In order to do this, it uses a dictionary containing the table of translations provided in the written
    instructions for "Project 6". In this case, there are two cases for the first bit (a) depending on the register,
    namely A and M. For register A, the a bit is 0, for register M, the a bit is 1.
    """

    c_table = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101"
    }

    binary = c_table[mnemonics]
    return binary


def jump_to_bin(mnemonics):
    """
    This function returns the binary code for the "jump" mnemonic of a C_command which corresponds to 3 bits.
    In order to do this, it uses a dictionary containing the table of translations provided in the written
    instructions for "Project 6".
    """

    j_table = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111"
    }

    binary = j_table[mnemonics]
    return binary

# -----------------------------------------------------------------------
# Module 3: Replace all symbolic references (if any) with numeric addresses of memory locations.
# -----------------------------------------------------------------------

def constructor():
    """
    Creates a new symbol table
    """

    symbol_table = {
        "R0": "0",
        "R1": "1",
        "R2": "2",
        "R3": "3",
        "R4": "4",
        "R5": "5",
        "R6": "6",
        "R7": "7",
        "R8": "8",
        "R9": "9",
        "R10": "10",
        "R11": "11",
        "R12": "12",
        "R13": "13",
        "R14": "14",
        "R15": "15",
        "SCREEN": "16384",
        "KBD": "24576",
        "SP": "0",
        "LCL": "1",
        "ARG": "2",
        "THIS": "3",
        "THAT": "4",
        "LOOP": "4",
        "STOP": "18",
        "i": "16",
        "sum": "17"
    }

    return symbol_table

    
def addEntry(pair, table):
    """
    This function adds the pair (symbol, address) to the table.
    """

    symbol, address = pair

    table[symbol] = address

    
def contains(symbol, table):
    """
    This function returns whether the symbol is present in the table or not. So, the function returns a boolean.
    """

    if symbol in table:
        return True
    else:
        return False


def getAddress(symbol, table):
    """
    This function returns the address associated with the symbol.
    """

    address = table[symbol]

    return address

# -----------------------------------------------------------------------
# Module 4: Main Program -> Assemble the binary codes into a complete machine instruction.
# -----------------------------------------------------------------------

def main():
    """
    In the main program we call all of the above functions to be able to translate the inputted asm file into a
    binary code.
    """

    # Check if the input is via stdin, if not exit the code
    if not sys.stdin.isatty():
        assembly = sys.stdin
        output_file = sys.stdout
    else:
        sys.exit(1)

    # Initialize the parser and the symbols table
    parser = initialize(assembly)
    symbol_table = constructor()

    # --------------------------------
    # First pass: Build symbol table
    # --------------------------------
    rom_address = 0

    # Loop through all the lines of the input
    while hasMoreCommands(parser):
        advance(parser)
        command_type = commandType(parser)

        # We want to translate A and C instructions so we increment the counter
        if command_type == "A" or command_type == "C":
            rom_address += 1

        # If the command is of type L, then add it to the table
        elif command_type == "L":
            sym = symbol(parser)
            addEntry((sym, rom_address), symbol_table)

    # --------------------------------
    # Second pass: Translate to binary
    # --------------------------------

    # Restart the parser for the second looping
    assembly.seek(0)
    parser = initialize(assembly)
    next_ram_address = 16

    # Loop through all the lines of the input
    while hasMoreCommands(parser):
        advance(parser)
        command_type = commandType(parser)

        if command_type == "A":
            sym = symbol(parser)

            # If sym is a constant, then keep the number as int
            if sym.isdigit():
                bin_num = int(sym)

            # If sym is an existing symbol, get the address (binary) as an integer
            elif contains(sym, symbol_table):
                bin_num = int(getAddress(sym, symbol_table))

            # If sym is a new variable, add it to the table and increment accordingly
            else:
                addEntry((sym, next_ram_address), symbol_table)
                bin_num = next_ram_address
                next_ram_address += 1

            # Wrute the binary in the output file (starting with 0 since it is an A instruction)
            output_file.write(f"0{bin_num:015b}\n")

        elif command_type == "C":

            # Find all the parts of the binary of a C instruction
            d = dest(parser) or "null"
            c = comp(parser)
            j = jump(parser) or "null"

            # Translate them to binary
            bin_d = dest_to_bin(d)
            bin_c = comp_to_bin(c)
            bin_j = jump_to_bin(j)

            # Write them in the output file (starting with 111 since it is a C instruction)
            output_file.write(f"111{bin_c}{bin_d}{bin_j}\n")

if __name__ == "__main__":
    main()
