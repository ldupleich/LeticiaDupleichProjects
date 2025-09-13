"""
ABSTRACT SYNTAX

Ide := String
Num := Integer
Bl := True | False

Exp := Int(Num) | Plus(Exp, Exp) | Mult(Exp, Exp) | Minus(Exp) |
       Bool(Bl) | And(Exp, Exp) | Or(Exp, Exp) | Not(Exp) | Equal(Exp, Exp) |
       If (Exp, Exp, Exp) | Deref (Ide) | Val(Ide)
       
Com := Assign(Ide, Exp) | While(Exp, Com) | CIf (Exp, Com, Com)
       | Procedure(Ide, Listof Ide, Listof Com) | Call(Ide, Listof Exp)
       | NewPointer(Ide, Exp) | DestroyPointer(Ide)
       | UpdatePointerV al(Ide, Exp) | Block(Listof Decl, Listof Com)
       | Show(Exp)
       
Decl := Decl(Ide, Exp)
"""

from dataclasses import dataclass

# --------------------------------------------
# SYNTACIC DOMAINS
# --------------------------------------------

Ide = str

@dataclass
class Int:
    value: int

@dataclass
class Plus:
    e1: "Exp"
    e2: "Exp"

@dataclass
class Mult:
    e1: "Exp"
    e2: "Exp"

@dataclass
class Minus:
    e: "Exp"

@dataclass
class Bool:
    value: bool

@dataclass
class And:
    e1: "Exp"
    e2: "Exp"

@dataclass
class Or:
    e1: "Exp"
    e2: "Exp"

@dataclass
class Not:
    e: "Exp"

@dataclass
class Equal:
    e1: "Exp"
    e2: "Exp"

@dataclass
class If:
    c: "Exp"
    e1: "Exp"
    e2: "Exp"

@dataclass
class Deref:
    i: Ide

@dataclass
class Val:
    i: Ide

Exp = Int | Plus | Mult | Minus | Bool | And | Or | Not | Equal | If | Deref | Val

@dataclass
class Assign:
    i: Ide
    v: Exp

@dataclass
class While:
    c: Exp
    b: "Com"

@dataclass
class CIf:
    c: Exp
    b1: "Com"
    b2: "Com"

@dataclass
class Procedure:
    name: Ide
    parameters: list[Ide]
    body: list["Com"]

@dataclass
class Call:
    name: Ide
    parameters: list["Exp"]

@dataclass
class NewPointer:
    i: Ide
    c: "Exp"

@dataclass
class DestroyPointer:
    i: Ide

@dataclass
class UpdatePointerVal:
    i: Ide
    c: Exp

@dataclass
class Block:
    dl: list["Decl"]
    cl: list["Com"]

@dataclass
class Show:
    e: Exp

Com = Assign | While | CIf | Procedure | Call | NewPointer | DestroyPointer | UpdatePointerVal | Block | Show

@dataclass
class Decl:
    i: Ide
    e: Exp

# --------------------------------------------
# SEMANTIC DOMAINS
# --------------------------------------------

# Expressible values
@dataclass
class EInt:
    v: int

@dataclass
class EBool:
    v: bool

Eval = EInt | EBool

# Denotable values
@dataclass
class DInt:
    v: int

@dataclass
class DBool:
    v: bool

@dataclass
class DLoc:
    loc: int
    frame: int

@dataclass
class DProc:
    parameters: list[Ide]
    body: list[Com]
    frame: int

Dval = DInt | DBool | DLoc | DProc

# Storable values
@dataclass
class SInt:
    v: int

@dataclass
class SBool:
    v: bool

@dataclass
class SPointer:
    v: int

Sval = SInt | SBool | SPointer

# Heapable values
@dataclass
class HInt:
    v: int

@dataclass
class HBool:
    v: bool

Hval = HInt | HBool

# --------------------------------------------
# CONVERSION FUNCTIONS (only ones used)
# --------------------------------------------

def eval_to_sval(v: Eval) -> Sval:
    """
    Converts expressible values into storable values.
    """
    match v:
        case EInt(i):
            return SInt(i)
        case EBool(b):
            return SBool(b)
        case _:
            raise Exception("Trying to convert a non-storable type")

def eval_to_hval(v: Eval) -> Hval:
    """
    Converts expressible values into heapable values.
    """
    match v:
        case EInt(i):
            return HInt(i)
        case EBool(b):
            return HBool(b)
        case _:
            raise Exception("Trying to convert a non-heapable type")

def sval_to_eval(v: Sval) -> Eval:
    """
    Converts storable values into expressible values.
    """
    match v:
        case SInt(i):
            return EInt(i)
        case SBool(b):
            return EBool(b)

def sval_to_hval(v: Sval) -> Hval:
    """
    Converts storable values into heapable values.
    """
    match v:
        case SInt(i):
            return HInt(i)
        case SBool(b):
            return HBool(b)
        case _:
            raise Exception("Trying to convert a non-heapable type")
        
def hval_to_eval(v: Hval) -> Eval:
    """
    Converts heapable values into expressible values.
    """
    match v:
        case HInt(i):
            return EInt(i)
        case HBool(b):
            return EBool(b)
        
def hval_to_sval(v: Hval) -> Sval:
    """
    Converts heapable values into storable values.
    """
    match v:
        case HInt(i):
            return SInt(i)
        case HBool(b):
            return SBool(b)

# --------------------------------------------
# STRUCTURES: ENVIRONMENT, STORE AND FRAMES
# --------------------------------------------

# Defining the enviornment as a stack
@dataclass
class Bind:
    identifier: Ide
    value: Dval

class Env:
    """
    The Env class functions to bound identifiers to their corresponding values.
    It offers methods for searching for identifier bindings and adding new bindings.
    """
    
    def __init__(self):
        self.s: list[Bind] = []

    def applyEnv(self, ide: Ide) -> Dval | None:
        """
        Looks for a name "ide" in the enviornment
        """
        i = len(self.s) - 1
        while(i > -1 and self.s[i].identifier != ide):
            i -= 1
        if i > -1:
            return self.s[i].value
        else:
            return None

    def bind(self, ide: Ide, value: Dval):
        """
        Adds a new pair (Identifier, Denotable value) to the enviornment
        """
        self.s.append(Bind(ide, value))

# Definfing the store as a stack
class Store:
    """
    The Store class functions as (stacked) memory for variables in a block-structured
    language. It holds a list of values (Sval) and provides methods to allocate,
    update, and access stored values.
    """
    
    def __init__(self):
        """
        Initializes an empty store
        """
        self.s: list[Sval] = []
        
    def apply(self, l: int) -> Sval:
        """
        Looks for a value at the location "loc" in the store
        """
        if len(self.s) <= l:
            raise Exception("Trying to access wrong location")
        else:
            return self.s[l]
        
    def alloc(self, v: Sval) -> int:
        """
        Adds a new value "v" to the store and returns its location
        """
        self.s.append(v)
        return len(self.s) - 1
    
    def update(self, l: int, v: Sval):
        """
        Accesses location "loc" in the store and changes its value to "v"
        """
        if len(self.s) <= l:
            raise Exception("Trying to access wrong location")
        else:
            self.s[l] = v

# Defining (a stack of) frames
@dataclass
class Frame:
    env: Env
    sto: Store
    slink: int

class FrameStack:
    """
    The FrameStack class represents the stack of frames (environments and stores) used in 
    a block-structured language with static scoping.
    """
    
    def __init__(self):
        """
        Initializes an empty frame
        """
        self.s: list[Frame] = []

    def push_frame(self, f: Frame):
        """
        Adds a frame to the frame stack
        """
        self.s.append(f)

    def top_frame(self) -> Frame:
        """
        Retruns the index of the top frame
        """
        return self.s[len(self.s) - 1]

    def frame_at(self, n: int) -> Frame:
        """
        Returns the frame at location "n"
        """
        return self.s[n]

    def pop_frame(self) -> None:
        """
        Removes a frame from the frame stack
        """
        self.s.pop()

    def current_frame_index(self) -> int:
        """
        Returns the index of the current frame
        """
        return len(self.s) - 1

    def search_name(self, i: Ide) -> Dval:
        """
        Returns the frame where an identifier "i" (name) is located
        """
        current = self.current_frame_index()
        found = False
        v = None
        while current > -1 and not found:
            v = self.s[current].env.applyEnv(i)
            found = v is not None
            current = self.s[current].slink
        if found:
            return v
        raise Exception("Name Not Found")

# --------------------------------------------
# NEW STRUCTURE: HEAP
# --------------------------------------------

# Defining the heap as a list
class Heap:
    """
    The Heap class represents a fixed-size heap structure for user-managed memory
    storage. This heap manages memory cells where users can store heapable values 
    (integers and booleans) in a controlled manner. The heap maintains a list 
    of free cells, enabling efficient allocation and deallocation of memory. 
    """
    
    def __init__(self, size=100):
        """
        Initializes the heap to have a fixed-size of 100 (free and empty) cells
        """
        self.size = size
        self.cells = [None] * size
        self.free_cells = list(range(size))

    def alloc(self, v: Hval) -> int:
        """
        If there are free cells in the heap, places "v" in the next free cell and returns that location
        """
        if not self.free_cells:
            raise Exception("Heap is full. Heap overflow")
        loc = self.free_cells.pop()
        self.cells[loc] = v
        return loc

    def free(self, loc: int):
        """
        Frees the space at location "loc" of the heap
        """
        if loc >= self.size or self.cells[loc] is None:
            raise Exception("Heap location is invalid")
        self.cells[loc] = None
        self.free_cells.append(loc)

    def apply(self, loc: int) -> Hval:
        """
        Returns the value stored at location "loc" of the heap
        """
        if loc >= self.size or self.cells[loc] is None:
            raise Exception("Heap location is invalid")
        return self.cells[loc]

    def update(self, loc: int, v: Hval):
        """
        Accesses location "loc" in the heap and changes its value to "v"
        """
        if loc >= self.size or self.cells[loc] is None:
            raise Exception("Heap location is invalid")
        self.cells[loc] = v

# --------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------

def typeCheck(typ: type[Eval], val: Eval) -> bool:
    return type(val) == typ

def applyBinOperator(tpy: type[Eval], op, v1: Eval, v2: Eval) -> Eval:
    """
    Evaluates binary operators (operators with two inputs)
    These operators include: Plus, Mult, And, Or
    """
    if (typeCheck(tpy, v1) and typeCheck(tpy, v2)):
        match (v1, v2):
            case (EInt(i1), EInt(i2)):
                return EInt(op(i1, i2))
            case (EBool(b1), EBool(b2)):
                return EBool(op(b1, b2))
    raise Exception("Wrong Types in Binary Operation")

def applyUnaryOperator(tpy: type[Eval], op, v1: Eval) -> Eval:
    """
    Evaluates unary operators (operators with one input)
    These operators include: Minus, not
    """
    if typeCheck(tpy, v1):
        match v1:
            case EInt(i1):
                return EInt(op(i1))
            case EBool(b1):
                return EBool(op(b1))
    else:
        raise Exception("Wrong Types in Unary Operation")

# --------------------------------------------
# SEMANTICS OF EXPRESSIONS
# --------------------------------------------

def sem(ex: Exp, frame_stack: FrameStack, heap: Heap) -> Eval:
    """
    This is the semantics of expressions. It will use recursion to evaluate the inner-expressions
    within any expressions.
    """
    match ex:
        case Int(n):
            return EInt(n)

        case Plus(e1, e2):
            v1 = sem(e1, frame_stack, heap)
            v2 = sem(e2, frame_stack, heap)
            return applyBinOperator(EInt, lambda x, y: x + y, v1, v2)

        case Mult(e1, e2):
            v1 = sem(e1, frame_stack, heap)
            v2 = sem(e2, frame_stack, heap)
            return applyBinOperator(EInt, lambda x, y: x * y, v1, v2)

        case Minus(e):
            v1 = sem(e, frame_stack, heap)
            return applyUnaryOperator(EInt, lambda x: -x, v1)

        case Bool(b):
            return EBool(b)

        case And(e1, e2):
            v1 = sem(e1, frame_stack, heap)
            v2 = sem(e2, frame_stack, heap)
            return applyBinOperator(EBool, lambda x, y: x and y, v1, v2)

        case Or(e1, e2):
            v1 = sem(e1, frame_stack, heap)
            v2 = sem(e2, frame_stack, heap)
            return applyBinOperator(EBool, lambda x, y: x or y, v1, v2)

        case Not(e):
            v1 = sem(e, frame_stack, heap)
            return applyUnaryOperator(EBool, lambda x: not x, v1)

        case Equal(e1, e2):
            v1 = sem(e1, frame_stack, heap)
            v2 = sem(e2, frame_stack, heap)
            if v1 == v2:
                return EBool(True)
            else:
                return EBool(False)

        case If(c, e1, e2):
            vc = sem(c, frame_stack, heap)
            if not typeCheck(EBool, vc):
                raise Exception("Non Boolean Condition in Conditional")
            if vc == EBool(True):
                return sem(e1, frame_stack, heap)
            else:
                return sem(e2, frame_stack, heap)


    # NEW SEMANTICS FOR EXPRESSIONS:
        
        case Deref(i):

            # Look up the identifier in the frame stack to get its dloc
            dloc: Dval = frame_stack.search_name(i)

            match dloc:
                case DLoc(location, frame_index):
                    store_val = frame_stack.frame_at(frame_index).sto.apply(location)
                    match store_val:

                        # If "i" is the name of a variable containing a pointer, return the value in the cell
                        # pointed by the pointer (convert from heapable to expressible value)
                        case SPointer(location):
                            hval = heap.apply(location)
                            expressible_value = hval_to_eval (hval)
                            return expressible_value

                        # Raise exception if no pointer is found
                        case _:
                            raise Exception ("Variable does not contain a pointer")

                case _:
                    raise Exception ("Identifier is not bound to a variable")


        case Val(i):
            
            # Look up the identifier in the frame stack to get its dloc
            dloc: Dval = frame_stack.search_name(i)
            
            match dloc:
                case DLoc (location, frame_index):
                    store_val = frame_stack.frame_at(frame_index).sto.apply(location)
                    match store_val:
                        
                        # If "i" is the name of a variable containing a pointer return the address of the cell
                        # pointed by the pointer (cannot return the pointer because they are not expressible)
                        case SPointer (heap_location):
                            raise Exception ("Variable contains a pointer, pointers are not expressible")

                        # If the variable does not contain a pointer, return the value
                        case _:
                            expressible_value = sval_to_eval(store_val)
                            return expressible_value

                # If the dloc is not a variable, then raise exception
                case _:
                    raise Exception ("Identifier is not bound to a variable")
                    
        case _:
            raise Exception("Unknown Expression")

# --------------------------------------------
# SEMANTICS OF COMMANDS
# --------------------------------------------
        
def semcom(c: Com, frame_stack: FrameStack, heap: Heap):
    """
    This is the semantics of commands. It will use recursion to evaluate the inner-commands
    within any command.
    """
    match c:

    # NEW SEMANTICS FOR COMMANDS (ASSIGN)

        case Assign(i, exp):

            # Look up the identifier in the frame stack to get its dloc
            dloc: Dval = frame_stack.search_name(i)
            
            match dloc:
                case DLoc(location, frame_index):
                    sto1 = frame_stack.frame_at(frame_index).sto
        
                    match exp:

                        # The assignment could be from another variable x
                        case Val(x):
                            dloc = frame_stack.search_name(x)
                            match dloc:

                                # If x already points to a location, retrieve the value and assign to i
                                case DLoc(location2, frame_index2):
                                    sto2 = frame_stack.frame_at(frame_index2).sto
                                    v = sto2.apply(location2)
                                    sto1.update(location, v)
                                case _:
                                    raise Exception("Variable does not contain a pointer")
                                
                        # This is the case where "exp" is a more complex expression, not a simple variable
                        case _:
                            v = sem(exp, frame_stack, heap)
                            sto1.update(location, eval_to_sval(v))          
                case _:
                    raise Exception("Identifier is not bound to a variable")
        
        case While(e, b):
            if sem(e, frame_stack, heap) == EBool(True):
                semcom(b, frame_stack, heap)
                semcom(c, frame_stack, heap)
                
        case CIf(e, b1, b2):
            if sem(e, frame_stack, heap) == EBool(True):
                semcom(b1, frame_stack, heap)
            else:
                semcom(b2, frame_stack, heap)

    # NEW SEMANTICS FOR COMMANDS (PROCEDURES)
    
        case Procedure(name, formal_par, body):
            env = frame_stack.top_frame().env
            dproc = DProc(formal_par, body, frame_stack.current_frame_index())
            env.bind(name, dproc)
            
        case Call(i, actual_par):

            # Look up the identifier in the frame stack to get its dloc
            dproc: Dval = frame_stack.search_name(i)

            match dproc:

                # If we are dealing with a procedure, we continue
                case DProc(formal_par, body, frame_n):
                    new_store: Store = Store()
                    new_env: Env = Env()

                    vl: list[Sval] = []

                    # Iterate through the actual parameters since pointers have to be handled differently
                    for exp in actual_par:

                        # Using eager evaluation here as the values of the actual parameters are immediately evaluated
                        match exp:

                            # Case where Val(x) exists meaning the actual parameter is a variable
                            case Val(x):
                                match x:

                                    # If x is a pointer, just append the address its pointing to
                                    case SPointer(address):
                                        vl.append(SPointer(address))

                                    # If x is not a pointer, evaluate its value and then append that
                                    case Ide(varname):
                                        dloc = frame_stack.search_name(varname)
                                        match dloc:
                                            case DLoc(location, frame_index):
                                                sto = frame_stack.frame_at(frame_index).sto
                                                val_at_loc = sto.apply(location)
                                                vl.append(val_at_loc)
                                            case _:
                                                raise Exception ("Variable was not properly declared or accessible")
                                            
                                    # Raise an exception if x is not a pointer or a value
                                    case _:
                                        raise Exception ("Expected a variable")

                            # Case without Val(x), we simply evaluate with "sem"
                            case _:
                                v = sem (exp, frame_stack, heap)
                                vl.append(eval_to_sval(v))

                    # Binding (assign) the actual parameters to the formal parameters (pass by value)
                    bind_list: zip[tuple[Ide, Sval]] = zip(formal_par, vl)
                    for (i, v) in bind_list:
                        l = new_store.alloc(v)
                        dloc = DLoc(l, frame_stack.current_frame_index() + 1)
                        new_env.bind(i, dloc)
                        
                    frame_stack.push_frame(Frame(new_env, new_store, frame_n))
                    semcomlist(body, frame_stack, heap)
                    frame_stack.pop_frame()

                # If we are not dealing with a procedure we raise an exception
                case _:
                    raise Exception("Attempting to call a non-callable value")


    # NEW SEMANTICS FOR COMMANDS (POINTERS)
    
        case NewPointer(i, exp):
            
            # Evaluate the expression that will be stored where the pointer is
            # pointing, and convert to heapable value
            evaluation = sem(exp, frame_stack, heap)
            hval = eval_to_hval(evaluation)
            
            # Create a new variable whose content is going to be the pointer which
            # points to the evaluation of exp
            heap_location = heap.alloc(hval)
            pointer = SPointer(heap_location)
            
            # Store the new pointer in the store (of the current frame) and bind
            # it to the identifier (name)
            current_frame = frame_stack.top_frame()
            store_location = current_frame.sto.alloc(pointer)
            current_frame.env.bind(i, DLoc(store_location, frame_stack.current_frame_index()))

        case DestroyPointer(i):
            
            # Look up the identifier in the frame stack to get its dloc
            dloc: Dval = frame_stack.search_name(i)

            match dloc:

                # In the case where dloc conatins a variable, we can proceed to look if it contains a pointer
                case DLoc(location, frame_index):
                    
                    # ⁠Access the store cell at the location given by DLoc to get the pointer
                    target_frame = frame_stack.frame_at(frame_index)
                    store = target_frame.sto
                    pointer_val = store.apply(location)

                    match pointer_val:

                        # If "i" is the name of a variable containing a pointer, free the memory
                        # associated to the pointer
                        case SPointer(heap_location):
                            heap.free(heap_location)

                        # Raise exception if the variable does not contain a pointer
                        case _:
                            raise Exception ("Variable does not contain a pointer")
                case _:
                    raise Exception ("Identifier is not bound to a variable")

        case UpdatePointerVal(i, exp):
            
            # Look up the identifier in the frame stack to get its dloc
            dloc: Dval = frame_stack.search_name(i)

            match dloc:

                # In the case where dloc conatins a variable, we can proceed to look if it contains a pointer
                case DLoc(location, frame_index):
                    
                    # Access the store at the frame where DLoc lives
                    target_frame = frame_stack.frame_at(frame_index)
                    store = target_frame.sto
                    pointer_val = store.apply(location)
                    
                    match pointer_val:

                        # If "i" is the name of a variable containing a pointer, update the cell pointed
                        # by the pointer with the evaluated value of "exp" (convert from expressible to
                        # heapable to be able to store in heap)
                        case SPointer(heap_location):
                            location = heap_location
                            evaluation = sem(exp, frame_stack, heap)
                            hval = eval_to_hval(evaluation)
                            heap.update(location, hval)

                        # If variable i does not contain a pointer, raise an exception
                        case _:
                            raise Exception ("Variable does not contain a pointer")

                # If dloc is not a variable, we raise an exception
                case _:
                    raise Exception ("Identifier is not bound to a variable")

        case Block(dl, cl):
            semblock(c, frame_stack, heap)
                    
        case Show(exp):
            # Prints expressible values. Can be used to print values of variables that are not pointers
            
            evaluation = sem(exp, frame_stack, heap)
            
            match evaluation:
                case EInt(n):
                    print(n)
                case EBool(b):
                    print(b)
                case _:
                    raise Exception("Not a printable value")

        case _:
            raise Exception ("Unknown command")

# --------------------------------------------
# OTHER SEMANTICS
# --------------------------------------------

def semblock(block: Block, frame_stack: FrameStack, heap: Heap):
    """
    Semantics of blocks. Uses semantics of declarations and of list of commands
    to fully evaluate blocks
    """
    match block:
        case Block(dl, cl):
            f = Frame(Env(), Store(), frame_stack.current_frame_index())
            frame_stack.push_frame(f)
            semdecl(dl, frame_stack, heap)
            semcomlist(cl, frame_stack, heap)
            frame_stack.pop_frame()
        case _:
            raise Exception("Block Expected")

def semdecl(dl: list[Decl], frame_stack: FrameStack, heap: Heap):
    """
    Semantics of declarations. Used to evaluate variable declarations in the
    current frame by binding a variable name to the value computed from a
    given expression
    """
    top: Frame = frame_stack.top_frame()
    env: Env = top.env
    sto: Store = top.sto

    for d in dl:
        match d:
            case Decl(i, e):
                v = sem(e, frame_stack, heap)
                l = sto.alloc(eval_to_sval(v))
                env.bind(i, DLoc(l, frame_stack.current_frame_index()))
            case _:
                raise Exception("Invalid Declaration")

def semcomlist(cl: list[Com], frame_stack: FrameStack, heap: Heap):
    """
    Executes the semantics of a list of commands (iteratively calls cemcom)
    """
    for c in cl:
        semcom(c, frame_stack, heap)

def interpret(c: Com):
    """
    Interprets the command "c", creates a new frame and heap
    """
    frame_stack = FrameStack()
    heap = Heap()
    semcom(c, frame_stack, heap)

# --------------------------------------------
# TESTING
# --------------------------------------------

# TEST 1 (example given in assignment) --> Should print 1 2 3 4 5 6 7 8 9 10 10
##command1 = Block(
##    [Decl("y", Int(2))],
##    [
##        NewPointer("x", Int(10)),
##        NewPointer("w", Int(0)),
##        Procedure("p", ["z"],
##            [
##                While(Not(Equal(Deref("z"), Deref("x"))),
##                    Block(
##                        [Decl("y", Int(1))],
##                        [
##                            UpdatePointerVal("z", Plus(Deref("z"), Val("y"))),
##                            Show(Deref("z"))
##                        ]
##                    )
##                )
##            ]
##        ),
##        Call("p", [Val("w")]),
##        Show(Deref("w"))
##    ]
##)
##print("Command 1 result: ")
##interpret(command1)

# TEST 2 (simple pointer operation) --> Should print 10 15
##command2 = Block(
##    [Decl("a", Int(5))],
##    [
##        NewPointer("p", Int(10)),
##        Show(Deref("p")),
##        UpdatePointerVal("p", Plus(Deref("p"), Val("a"))),
##        Show(Deref("p")),
##        DestroyPointer("p")
##    ]
##)
##print("Command 2 result: ")
##interpret(command2)

# TEST 3 (no pointers) --> 42 True
##command3 = Block(
##    [Decl("x", Int(42)), Decl("flag", Bool(True))], 
##    [
##        Show(Val("x")),
##        Show(Val("flag"))
##    ]
##)
##print("Command 3 result: ")
##interpret(command3)
  
