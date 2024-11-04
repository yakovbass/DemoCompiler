"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

NOTES = "//#*"
class JackTokenizer:

    keyword_list = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null",
                        "this", "let", "do", "if", "else", "while", "return"]
    symbol_list = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~", "^", "#"]
    geresh = '"'

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.total_count = 0
        self.cur_count = -1
        self.cur_token:str = None
        self.all_words = list()
        text = input_stream.read()
        text = self.remove_block_comments(text)
        lines = text.splitlines()
        self.input_lines = list()
        self.words = []


        for i in range (0, len(lines)): # striping each line from useless spaces
            lines[i] = lines[i].strip()
        
        for i in range (0, len(lines)): #saving only the lines with commands!
            if len(lines[i]) > 0 and lines[i][0] not in NOTES:
                self.input_lines.append(lines[i])

        self.remove_line_comments()
        
        for i in range (len(self.input_lines)):
            line = []
            cur_words = self.split_keep_delimiters(self.input_lines[i])
            for word in cur_words:
                self.all_words.append(word)
            line.append(cur_words)
            self.words.append(line)

        self.total_count = len(self.all_words)

    def split_keep_delimiters(self, cur_string: str):
        # Regular expression to match quoted substrings
        quoted_pattern = r'"(.*?)"'
        # Regular expression to match delimiters
        delimiter_pattern = r'([' + ''.join(re.escape(delimiter) for delimiter in self.symbol_list) + '])'

        # Split the string on quoted substrings
        parts = re.split(quoted_pattern, cur_string)

        new_parts = list()
        inside_quote = False

        for part in parts:
            if inside_quote:
                # This part is inside quotes, add it as a single item
                new_parts.append('"' + part + '"')
            else:
                # Split non-quoted part by delimiters
                sub_parts = re.split(delimiter_pattern, part)
                for sub_part in sub_parts:
                    sub_part = sub_part.strip()
                    if sub_part:
                        if sub_part[0] == self.geresh:
                            new_parts.append(sub_part)
                        else:
                            new_parts.extend(sub_part.split())
            # Toggle the inside_quote flag
            inside_quote = not inside_quote

        return new_parts
    
    def remove_line_comments(self):
        in_string = False
        new_lines = []

        for line in self.input_lines:
            new_line = ""
            i = 0
            while i < len(line):
                if line[i] == '"' or line[i] == "'":
                    if not in_string:
                        in_string = line[i]
                    elif in_string == line[i]:
                        in_string = False
                    new_line += line[i]
                elif line[i:i+2] == '//' and not in_string:
                    break
                else:
                    new_line += line[i]
                i += 1
            new_lines.append(new_line.strip())

        self.input_lines = new_lines

    def remove_block_comments(self, text: str) -> str:
        """Remove all block comments (/* ... */) from the text."""
        pattern = r'/\*.*?\*/'
        return re.sub(pattern, '', text, flags=re.DOTALL)


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.cur_count < self.total_count

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.cur_count += 1
        if self.cur_count == 0:
            self.cur_token = self.all_words[self.cur_count]
        
        elif self.has_more_tokens():
            self.cur_token = self.all_words[self.cur_count]
        
    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in self.keyword_list:
            return "KEYWORD"
        elif self.cur_token in self.symbol_list:
            return "SYMBOL"
        elif self.cur_token[0] == self.geresh:
            return "STRING_CONST"
        elif self.cur_token.isdigit() and 0 <= int(self.cur_token) <= 32767:
            return "INT_CONST"
        elif self.check_identifier():
            return "IDENTIFIER"
        else:
            ""

    def which_token(self) -> str:
        token_type = self.token_type()
        if token_type == "KEYWORD":
            return self.keyword().lower()
        elif token_type == "SYMBOL":
            return self.symbol()
        elif token_type == "IDENTIFIER":
            return self.identifier()
        elif token_type == "INT_CONST":
            return self.int_val()
        elif token_type == "STRING_CONST":
            return self.string_val()

    def check_identifier(self) -> bool:
        """
        """
        numbers_l = "1234567890"
        if self.cur_token[0] in numbers_l:
            return False
        for letter in self.cur_token:
            if not ('a' <= letter <= 'z') and not ('A' <= letter <= 'Z') and not (letter == "_") and letter not in numbers_l:
                return False
        return True

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "KEYWORD":
            if self.cur_token in self.keyword_list:
                return self.cur_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.token_type() == "SYMBOL":
            if self.cur_token in self.symbol_list:
                return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        if self.token_type() == "IDENTIFIER":
            return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        if self.token_type() == "INT_CONST":
            return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        if self.token_type() == "STRING_CONST":
            return self.cur_token.strip('"\n')

    def get_token(self) -> str:
        """gets the current token"""
        return self.cur_token

    def get_arit(self, arit: str) -> str:
        op_dict1 = {'+': 'add', '-': 'sub','*': 'call Math.multiply 2', '/': 'call Math.divide 2', '&': 'and', '|': 'or','<': 'lt','>': 'gt','=': 'eq'}
        if arit in op_dict1:
            return op_dict1[arit]
    
    def get_arit_unary(self, arit: str) -> str:
        op_dict2 = {'~': "not", '-': "neg"}
        if arit in op_dict2:
            return op_dict2[arit]