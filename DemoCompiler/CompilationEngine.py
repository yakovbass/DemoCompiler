"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import copy
from JackTokenizer import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

op_list = {'+','-','*','/','&','|','<','>',"="}
op_list_ext:dict = {'<': "&lt;", '>': "&gt;", '&': "&amp;"}
keyword_const = {"true", "false", "null", "this"}

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.input_stream: JackTokenizer = input_stream
        self.output_stream = VMWriter(output_stream)
        self.class_name: str = None
        self.symTable: SymbolTable = None
        self.label_counter_if = -1
        self.label_counter_while = -1
    
    def get_if_label(self, mes_in, mes_out):
        self.label_counter_if += 1
        return f'{mes_in}.{self.label_counter_if}', f'{mes_out}.{self.label_counter_if}'
    
    def get_while_label(self, mes_in, mes_out):
        self.label_counter_while += 1
        return f'{mes_in}.{self.label_counter_while}', f'{mes_out}.{self.label_counter_while}'

    def compile_class(self) -> None:
        """Compiles a complete class."""
        if self.input_stream.has_more_tokens():

            self.input_stream.advance()
            # class keyword
            self.input_stream.advance()

            #write className
            self.class_name = self.input_stream.which_token()
            self.input_stream.advance()

            #write {
            self.input_stream.advance()

            #create symbolTable
            self.symTable = SymbolTable()

            # check for class variables
            while self.input_stream.which_token() == "static" or self.input_stream.which_token() == "field":
                self.compile_class_var_dec()
            
            #check for class methods
            while self.input_stream.which_token() == "constructor" or\
                self.input_stream.which_token() == "method" or\
                self.input_stream.which_token() == "function":
                self.compile_subroutine()
            
            #skipping }

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        #retrieving static/field
        kind = self.input_stream.which_token()
        self.input_stream.advance()

        #retrieving type
        type = self.input_stream.which_token()
        self.input_stream.advance()

        #retriving name
        name = self.input_stream.which_token()
        self.input_stream.advance()

        # add class vars to symTable
        self.symTable.define(name, type, kind)

        while self.input_stream.which_token() == ",":
            # skip ,
            self.input_stream.advance()
            #retriving name
            name = self.input_stream.which_token()
            self.input_stream.advance()
            self.symTable.define(name, type, kind)

        #skipping ;
        self.input_stream.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """

        #writing type of function/method/constructor
        typeFunc = self.input_stream.which_token()
        self.input_stream.advance()

        # type of function subroutine
        typeReturn = self.input_stream.which_token()
        self.input_stream.advance()

        # name of subroutine
        name = self.input_stream.which_token()
        self.input_stream.advance()

        # writing (
        # self.print_symbol()
        self.input_stream.advance()

        #create subroutine's symbolTable
        self.symTable.start_subroutine()

        if typeFunc == "method":
            self.symTable.define("this", self.class_name, "arg")
        
        #parameter list
        self.compile_parameter_list()

        # writing )
        # self.print_symbol()
        self.input_stream.advance()

        #subroutine body
        # writing {
        self.input_stream.advance()
    
        #writing var declerations
        while self.input_stream.which_token() == "var":
            self.compile_var_dec()

        if not self.symTable.isEmpty():
            num_args = self.symTable.var_count("var")
        else:
            num_args = 0

        if typeFunc == "constructor":
            self.output_stream.write_function(f"{self.class_name}.{name}", 0)

            # search x withing current scope
            cur_sym_table = copy.deepcopy(self.symTable)
            index = cur_sym_table.var_count("field")
            while index <= 0:
            # #if not found, go deeper
                cur_sym_table.getNext()
                index = cur_sym_table.var_count("field")
            self.output_stream.write_push("const", index)
            self.output_stream.write_call("Memory.alloc", 1)
            self.output_stream.write_pop("pointer", 0)
        elif typeFunc == "method":
            self.output_stream.write_function(f"{self.class_name}.{name}", num_args)
            self.output_stream.write_push("arg", 0)
            self.output_stream.write_pop("pointer", 0)
        else:
            self.output_stream.write_function(f"{self.class_name}.{name}", num_args)
        
    
        self.compile_statements(typeReturn)
        
        self.input_stream.advance() 

        #reset symTable
        self.symTable.getNext()      

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if self.input_stream.which_token() != ")":
            kind = "arg"
            type = self.input_stream.which_token()
            self.input_stream.advance()

            # varname
            name = self.input_stream.which_token()

            self.symTable.define(name, type, kind)

            self.input_stream.advance()

            while self.input_stream.which_token() == ",":
                #skipping ,
                self.input_stream.advance()
                type = self.input_stream.which_token()
                self.input_stream.advance()
                name = self.input_stream.which_token()
                self.symTable.define(name, type, kind)
                self.input_stream.advance()
        
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        #writing var
        # self.print_keyword()
        kind = "var"
        self.input_stream.advance()

        #writing type
        type = self.input_stream.which_token()
        self.input_stream.advance()

        #varName
        name = self.input_stream.which_token()

        self.symTable.define(name, type, kind)

        self.input_stream.advance()

        #maybe more varNames
        while self.input_stream.which_token() == ",":
            self.input_stream.advance()
            #writing varName
            name = self.input_stream.which_token()
            self.symTable.define(name, type, kind)
            self.input_stream.advance()
        
        #skipping ;
        self.input_stream.advance()
        
    def compile_statements(self, name: str = None) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.input_stream.which_token() != "}":
            self.compile_statement(name)
    
    def compile_statement(self, name: str = None):
        if self.input_stream.which_token() == "if":
            self.compile_if()
        if self.input_stream.which_token() == "let":
            self.compile_let()
        if self.input_stream.which_token() == "while":
            self.compile_while()
        if self.input_stream.which_token() == "do":
            self.compile_do()
        if self.input_stream.which_token() == "return":
            if name == "void":
                self.output_stream.write_push("const", 0)
            self.compile_return()
        
    def compile_do(self) -> None:
        """Compiles a do statement."""
        #skipping do
        self.input_stream.advance()
        #printing subroutine call
        className = self.input_stream.which_token()
        self.input_stream.advance()
        self.compile_subroutineCall(className)
        self.input_stream.advance()
        self.output_stream.write_pop("temp", 0)
        #printing ;

        self.input_stream.advance()
    
    def compile_subroutineCall(self, className):
        """compiles when we want to call to a function"""
        if self.input_stream.which_token() == ".":
            #writing .
            self.input_stream.advance()
            #writing subroutine name
            # self.print_identifier()
            subName = self.input_stream.which_token()
            self.input_stream.advance()
        
            #printing (
            self.input_stream.advance()
            
            cur_sym_table = copy.deepcopy(self.symTable)
            inSym = cur_sym_table.isNameInSym(className)
            while not inSym and cur_sym_table.hasNext():
                cur_sym_table.getNext()
                inSym = cur_sym_table.isNameInSym(className)
            #inner method inside the class
            if className == self.class_name and className != "Main" and subName != "new":
                countArgs = self.compile_expression_list()
                self.output_stream.write_call(f"{self.class_name}.{subName}", countArgs + 1)
            elif inSym:
                segment = cur_sym_table.kind_of(className)
                index = cur_sym_table.index_of(className)
                self.output_stream.write_push(segment, index)
                ##pushing the arguments in the expression list
                countArgs = self.compile_expression_list()
                ##call
                type_arg = cur_sym_table.type_of(className)
                self.output_stream.write_call(f"{type_arg}.{subName}", countArgs + 1)
            else:
                countArgs = self.compile_expression_list()
                self.output_stream.write_call(f"{className}.{subName}", countArgs)

        else:
            #printing (
            self.input_stream.advance()
            self.output_stream.write_push("pointer", 0)
            countArgs = self.compile_expression_list()
            self.output_stream.write_call(f"{self.class_name}.{className}", countArgs + 1)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # skipping let keyword
        self.input_stream.advance()

        #skipping var name
        varName = self.input_stream.which_token()
        segment = self.symTable.kind_of(varName)
        index = self.symTable.index_of(varName)
        self.input_stream.advance()
        # self.output_stream.write_push(segment, index)
        if self.input_stream.which_token() == "[":
            self.output_stream.write_push(segment, index)
            self.input_stream.advance()
            self.compile_expression()
            self.input_stream.advance()
            self.input_stream.advance()
            self.output_stream.write_arithmetic("add")
            self.compile_expression()
            self.output_stream.write_pop("temp", 0)
            self.output_stream.write_pop("pointer", 1)
            self.output_stream.write_push("temp", 0)
            self.output_stream.write_pop("that", 0)
        else:
        #printing =
            self.input_stream.advance()

            self.compile_expression()

            # search x withing current scope
            cur_sym_table = copy.deepcopy(self.symTable)
            segment = cur_sym_table.kind_of(varName)
            while segment == None:
                #if not found, go deeper
                cur_sym_table.getNext()
                segment = cur_sym_table.kind_of(varName)
            index = cur_sym_table.index_of(varName)

            self.output_stream.write_pop(segment, index)

        self.input_stream.advance()

    def compile_while(self) -> None:
        """Compiles a while statement."""
        in_while, out_while = self.get_while_label("IN_WHILE", "OUT_WHILE")

        # printing while
        self.input_stream.advance()

        # printing (
        self.input_stream.advance()

        self.output_stream.write_label(in_while)

        self.compile_expression()

        # printing )
        self.input_stream.advance()

        self.output_stream.write_arithmetic("not")

        #printing {
        self.input_stream.advance()

        self.output_stream.write_if(out_while)

        self.compile_statements()

        self.output_stream.write_goto(in_while)

        #printing }

        self.output_stream.write_label(out_while)

        self.input_stream.advance()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # printing return 
        self.input_stream.advance()
    
        #maybe printing expression
        if self.input_stream.which_token() != ";":
            self.compile_expression()
        
        #printing ;
        self.output_stream.write_return()

        self.input_stream.advance()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        if_out, else_in = self.get_if_label("IF_OUT", "ELSE_IN")
        
        #printing if
        self.input_stream.advance()

        # printing (
        self.input_stream.advance()

        self.compile_expression()

        self.output_stream.write_arithmetic("not")

        # printing )
        self.input_stream.advance()

        self.output_stream.write_if(else_in)

        # printing {
        self.input_stream.advance()
        self.compile_statements()
        self.output_stream.write_goto(if_out)

        # printing }
        self.input_stream.advance()

        self.output_stream.write_label(else_in)
        if self.input_stream.which_token() == "else":
            # self.print_keyword()
            
            self.input_stream.advance()
            # printing {
            self.input_stream.advance()

            self.compile_statements()

            # printing }
            self.input_stream.advance()
        self.output_stream.write_label(if_out)
        
    def compile_expression(self) -> None:
        """Compiles an expression."""

        self.compile_term()
        op = self.input_stream.which_token()
        while op in op_list:
            self.input_stream.advance()
            self.compile_term()
            self.output_stream.write_arithmetic(self.input_stream.get_arit(op))
            op = self.input_stream.which_token()
            

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self.input_stream.token_type() == "INT_CONST":
            self.output_stream.write_push("const", self.input_stream.which_token())
            self.input_stream.advance()
        elif self.input_stream.token_type() == "STRING_CONST":
            token = self.input_stream.which_token()
            lenS = len(token)
            self.output_stream.write_push("const", lenS)
            self.output_stream.write_call("String.new", 1)
            for i in range (lenS):
                self.output_stream.write_push("const", ord(token[i]))
                self.output_stream.write_call("String.appendChar", 2)
            self.input_stream.advance()
        elif self.input_stream.which_token() in keyword_const:
            token = self.input_stream.which_token()
            if token == "true":
                self.output_stream.write_push("const", 0)
                self.output_stream.write_arithmetic("not")
            elif token == "this":
                self.output_stream.write_push("pointer", 0)
            else:
                self.output_stream.write_push("const", 0)
            self.input_stream.advance()
        elif self.input_stream.token_type() == "IDENTIFIER":
            token = self.input_stream.which_token()
            segment = self.symTable.kind_of(token)
            
            if segment != None:
                index = self.symTable.index_of(token)
            else:
                # search x withing current scope
                cur_sym_table = copy.deepcopy(self.symTable)
                segment = cur_sym_table.kind_of(token)
                while segment == None:
                # #if not found, go deeper
                    cur_sym_table.getNext()
                    segment = cur_sym_table.kind_of(token)
                index = cur_sym_table.index_of(token)

            self.input_stream.advance()
            
            # maybe printing [
            if self.input_stream.which_token() == "[":
                self.input_stream.advance()
                self.compile_expression()
                self.output_stream.write_push(segment, index)
                self.output_stream.write_arithmetic("add")
                self.output_stream.write_pop("pointer", 1)
                self.output_stream.write_push("that", 0)
                # printing ]
                self.input_stream.advance()
            elif self.input_stream.which_token() == ".":
                self.compile_subroutineCall(token)
                self.input_stream.advance()
            elif self.input_stream.which_token() == "(":
                self.input_stream.advance()
                count_args = self.compile_expression_list()
                self.output_stream.write_push("arg", 0)
                self.output_stream.write_call(token, count_args + 1)
                self.input_stream.advance()
            else:
                self.output_stream.write_push(segment, index)
                

        elif self.input_stream.which_token() == "(":
            self.input_stream.advance()
            self.compile_expression()
            
            #printing )
            self.input_stream.advance()

        elif self.input_stream.which_token() == "-" or self.input_stream.which_token() == "~":
            op = self.input_stream.which_token()
            self.input_stream.advance()
            self.compile_term()
            self.output_stream.write_arithmetic(self.input_stream.get_arit_unary(op))

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        countArgs = 0 
        if self.input_stream.which_token() != ")":
            self.compile_expression()
            countArgs += 1
            #maybe ,
            while self.input_stream.which_token() == ",":
                self.input_stream.advance()
                countArgs += 1
                self.compile_expression()
        
        if self.input_stream.which_token() == "(":
            self.compile_expression()
            countArgs += 1
            while self.input_stream.which_token() == ",":
                self.input_stream.advance()
                countArgs += 1
                self.compile_expression()

        return countArgs

        
