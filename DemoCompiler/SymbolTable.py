"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class Entry:
    ## should add getters
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
    # should add getters
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
    
    def isEmpty(self) -> int:
        """checks if the cur symTable is empty"""
        return self.__symTable == None or self.__symTable.getHead() == None
    
    def getNext(self) -> None:
        """retrieves the next symTable in the chain"""
        cur = self.__symTable.getNext()
        self.__symTable = cur
    
    def hasNext(self) -> bool:
        """"checks if the current table has a larger scope"""
        cur = self.__symTable.getNext()
        return cur != None

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
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
