"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

"""Symbol table implementation for the Jack compiler.

The Jack language has two nested scopes:
- Class scope: `static` and `field` identifiers.
- Subroutine scope: `arg` and `var` identifiers.

This implementation models scopes as a linked list of `SymbolNode`s.
`start_subroutine()` pushes a new scope node whose `next` points to the
previous scope. `getNext()` pops the current scope.

Note: Some methods return 0 when the table is empty (instead of None) to
match behavior expected by the surrounding project code.
"""

import typing

class Entry:
    """A single symbol table entry.

    Stores the identifier's name, type, kind and running index.
    """
    def __init__(self, name, type, kind, num):
        self.__name: str = name
        self.__type: str = type
        self.__kind: str = kind
        self.__num: int = num
    def getName(self)->str:
        return self.__name
    def getType(self)->str:
        return self.__type
    def getKind(self)->str:
        return self.__kind
    def getNum(self)->int:
        return self.__num


class SymbolNode:
    """A scope node in the symbol table chain.

    Each node holds a list of `Entry` objects for one scope. The `next`
    pointer refers to the enclosing (outer) scope.
    """
    def __init__(self, head: list[Entry] = None, next: typing.Any = None):
            self.head = head if head is not None else []
            self.next = next
    def addEntry(self, entry: Entry):
        self.head.append(entry)
    def getHead(self):
        return self.head
    def getNext(self):
        return self.next

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.__symTable = SymbolNode()

    def isEmpty(self) -> bool:
        """Return True if the current scope has no entries."""
        return self.__symTable == None or self.__symTable.getHead() == None

    def getNext(self) -> None:
        """Pop the current scope and move to the enclosing scope."""
        cur = self.__symTable.getNext()
        self.__symTable = cur

    def hasNext(self) -> bool:
        """Return True if there is an enclosing scope."""
        cur = self.__symTable.getNext()
        return cur != None

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's
        symbol table).
        """
        # Push a new (empty) scope for the subroutine.
        self.__symTable = SymbolNode(None, self.__symTable)

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns
        it a running index. "STATIC" and "FIELD" identifiers have a class scope,
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # The running index is the number of already-defined identifiers of this kind
        # in the *current* scope.
        self.__symTable.addEntry(Entry(name, type, kind, self.var_count(kind)))

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        count = -1
        scope_list = self.__symTable.getHead()
        if self.isEmpty():
            return count + 1
        count += 1
        for i in range (len(scope_list)):
            cur_kind = scope_list[i].getKind()
            if cur_kind == kind:
                count += 1
        return count


    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if self.isEmpty():
            return 0
        scope_list = self.__symTable.getHead()
        for i in range (len(scope_list)):
            cur_name = scope_list[i].getName()
            if cur_name == name:
                return scope_list[i].getKind()
        return None

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if self.isEmpty():
            return 0
        scope_list = self.__symTable.getHead()
        for i in range(len(scope_list)):
            cur_name = scope_list[i].getName()
            if cur_name == name:
                return scope_list[i].getType()
        return None

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if self.isEmpty():
            return 0
        scope_list = self.__symTable.getHead()
        for i in range(len(scope_list)):
            cur_name = scope_list[i].getName()
            if cur_name == name:
                return scope_list[i].getNum()
        return None

    def isNameInSym(self, name: str) -> bool:
        if self.isEmpty():
            return 0
        scope_list = self.__symTable.getHead()
        for i in range(len(scope_list)):
            cur_name = scope_list[i].getName()
            if cur_name == name:
                return True
        return False
