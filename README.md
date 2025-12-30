Jack Compiler
Overview

This project implements a Jack-to-VM compiler as part of the Nand2Tetris course.
The compiler translates programs written in the Jack programming language into VM code, following the official Jack grammar and VM specification.

The project is written in Python and follows a modular design, where each compilation stage is handled by a dedicated component.

Project Structure
.
├── JackCompiler.py
├── JackTokenizer.py
├── CompilationEngine.py
├── SymbolTable.py
├── VMWriter.py
└── README.md

Main Components

JackCompiler
Entry point of the compiler. Handles input .jack files or directories and orchestrates the compilation process.

JackTokenizer
Reads a Jack source file and breaks it into a stream of tokens according to the Jack language specification.
Handles keywords, symbols, identifiers, integer constants, and string constants.

CompilationEngine
Implements a recursive-descent parser for the Jack grammar.
Translates parsed constructs directly into VM commands using the VMWriter.

SymbolTable
Manages symbol scopes (class scope and subroutine scope).
Tracks variable names, types, kinds (static, field, arg, var), and running indices.

VMWriter
Provides an abstraction for writing VM commands.
Encapsulates VM instructions such as push/pop, arithmetic commands, labels, function calls, and returns.

Supported Jack Features

Class declarations

Field and static variables

Subroutines (constructors, functions, methods)

Local variables and arguments

Control flow (if, if-else, while)

Expressions and operators

Array access

Subroutine calls

String and integer constants

Keyword constants (true, false, null, this)

How It Works

Tokenization
The input .jack file is tokenized using JackTokenizer.

Parsing & Code Generation
CompilationEngine parses the token stream using recursive descent and generates VM code on the fly.

Symbol Management
SymbolTable keeps track of identifiers and their scope throughout compilation.

VM Output
VMWriter outputs valid .vm files that can be executed on the Nand2Tetris Virtual Machine.

Usage

To compile a Jack file or a directory containing Jack files:

python JackCompiler.py <input_path>


Where <input_path> can be:

A single .jack file

A directory containing one or more .jack files

The compiler generates a corresponding .vm file for each .jack file.

Design Notes

The compiler follows a single-pass compilation strategy.

Parsing and code generation are tightly integrated.

Symbol tables are reset per subroutine to correctly manage scope.

The implementation adheres closely to the official Jack grammar.
