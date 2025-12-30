**Jack Compiler**

This project implements a compiler for the Jack programming language, translating Jack source files into VM code, according to the Nand2Tetris specification.

The compiler is written in Python and was developed as part of an academic assignment on compiler construction.

Files
JackCompiler.py        – main entry point
JackTokenizer.py      – tokenizes Jack source code
CompilationEngine.py  – parses the Jack grammar and generates VM code
SymbolTable.py        – manages symbol scopes and indices
VMWriter.py           – writes VM commands

**Description**

The compilation process consists of the following stages:

Tokenization
The source file is read and broken into tokens (keywords, symbols, identifiers, constants).

Parsing and code generation
A recursive-descent parser processes the tokens according to the Jack grammar and generates VM code directly.

Symbol management
Identifiers are stored in a symbol table with support for class and subroutine scopes.

VM output
The generated VM commands are written to a .vm output file.

**Supported Features**

Class and subroutine declarations

Static, field, argument, and local variables

Control flow statements (if, else, while)

Expressions and operators

Array access and subroutine calls

Integer, string, and keyword constants

**Usage**

Run the compiler on a Jack file or a directory containing Jack files:

python JackCompiler.py <path>


A .vm file will be created for each .jack file.

**Notes**

The compiler follows the official Jack grammar.

Parsing and code generation are done in a single pass.

Symbol tables are reset per subroutine to ensure correct scoping.
