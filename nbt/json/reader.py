import re
from typing import NoReturn, Type, Iterable, List, Optional

from nbt.classes import *

DOUBLE_PATTERN_NO_SUFFIX = re.compile("[-+]?(?:[0-9]+[.]|[0-9]*[.][0-9]+)(?:e[-+]?[0-9]+)?", re.RegexFlag.IGNORECASE)
DOUBLE_PATTERN = re.compile("[-+]?(?:[0-9]+[.]?|[0-9]*[.][0-9]+)(?:e[-+]?[0-9]+)?d", re.RegexFlag.IGNORECASE)
FLOAT_PATTERN = re.compile("[-+]?(?:[0-9]+[.]?|[0-9]*[.][0-9]+)(?:e[-+]?[0-9]+)?f", re.RegexFlag.IGNORECASE)
BYTE_PATTERN = re.compile("[-+]?(?:0|[1-9][0-9]*)b", re.RegexFlag.IGNORECASE)
LONG_PATTERN = re.compile("[-+]?(?:0|[1-9][0-9]*)l", re.RegexFlag.IGNORECASE)
SHORT_PATTERN = re.compile("[-+]?(?:0|[1-9][0-9]*)s", re.RegexFlag.IGNORECASE)
INT_PATTERN = re.compile("[-+]?(?:0|[1-9][0-9]*)", re.RegexFlag.IGNORECASE)


class NBTReader:

    def __init__(self, data: str):
        self.data: str = data
        self.cursor: int = 0

    def _throw(self, message: str) -> NoReturn:
        raise RuntimeError(message + " at: " + self._slice_data())

    def _slice_data(self) -> str:
        start = max(self.cursor - 35, 0)
        end = min(self.cursor, len(self.data))
        return ("..." if end > 35 else "") + self.data[start:end] + "<--[HERE]"

    def _can_read(self, i: int = 0) -> bool:
        return self.cursor + i < len(self.data)

    def _peek(self, i: int = 0) -> str:
        return self.data[self.cursor + i]

    def _pop(self) -> str:
        out = self._peek()
        self.cursor += 1
        return out

    def _skip_whitespace(self) -> None:
        while self._peek().isspace():
            self.cursor += 1

    def _has_separator(self) -> bool:
        self._skip_whitespace()
        if self._can_read() and self._peek() == ',':
            self.cursor += 1
            self._skip_whitespace()
            return True
        return False

    def _expect(self, expected: str) -> None:
        assert len(expected) == 1

        self._skip_whitespace()
        can_read = self._can_read()
        if can_read and self._peek() == expected:
            self.cursor += len(expected)
        else:
            self._throw("Expected '" + expected + "' but got '" + (self._peek() if can_read else "<EOF>") + "'")

    def _read_value(self) -> NBTBase:
        self._skip_whitespace()
        if not self._can_read():
            self._throw("Expected value")
        else:
            char = self._peek()
            if char == '{':
                return self.read_compound()
            elif char == '[':
                return self._read_list()
            else:
                return self._read_typed_value()

    def _read_typed_value(self) -> NBTBase:
        self._skip_whitespace()
        if self._peek() == '"':
            return NBTTagString(self._read_quoted_string())
        else:
            data = self._read_string()
            if not data:
                self._throw("Expected value")
            else:
                return self._type(data)

    @staticmethod
    def _type(data) -> NBTBase:
        if FLOAT_PATTERN.fullmatch(data):
            return NBTTagFloat(float(data[:-1]))
        elif BYTE_PATTERN.fullmatch(data):
            return NBTTagByte(int(data[:-1]))
        elif LONG_PATTERN.fullmatch(data):
            return NBTTagLong(int(data[:-1]))
        elif SHORT_PATTERN.fullmatch(data):
            return NBTTagShort(int(data[:-1]))
        elif INT_PATTERN.fullmatch(data):
            return NBTTagInt(int(data))
        elif DOUBLE_PATTERN.fullmatch(data):
            return NBTTagDouble(float(data[:-1]))
        elif DOUBLE_PATTERN_NO_SUFFIX.fullmatch(data):
            return NBTTagDouble(float(data))
        elif data == "true":
            return NBTTagByte(1)
        elif data == "false":
            return NBTTagByte(0)
        else:
            return NBTTagString(data)

    def _read_key(self) -> str:
        self._skip_whitespace()
        if not self._can_read():
            self._throw("Expected key")
        elif self._peek() == '"':
            return self._read_quoted_string()
        else:
            return self._read_string()

    def _read_string(self) -> str:
        start = self.cursor
        while self._simple_key(self._peek()):
            self.cursor += 1
        return self.data[start:self.cursor]

    def _read_quoted_string(self) -> str:
        out = ""
        self.cursor += 1
        escape = False
        while self._can_read():
            char = self._pop()
            if escape:
                if char != '\\' and char != '"':
                    self._throw("Invalid escape of '" + char + "'")
                escape = False
            else:
                if char == '\\':
                    escape = True
                    continue
                elif char == '"':
                    return out
            out += char
        self._throw("Missing termination quote")

    @staticmethod
    def _simple_key(char: str) -> bool:
        assert len(char) == 1

        return NBTTagCompound.KEY_PATTERN.fullmatch(char)

    def _read_list(self) -> NBTBase:
        if self._can_read(2) and self._peek(1) != '"' and self._peek(2) == ';':
            return self._read_array()
        else:
            return self._read_list_tag()

    def _read_list_tag(self) -> NBTTagList:
        self._expect('[')
        self._skip_whitespace()
        if not self._can_read():
            self._throw("Expected value")
        else:
            tags = NBTTagList()
            tag_type: Optional[Type[NBTBase]] = None
            while self._peek() != ']':
                nbt = self._read_value()
                if tag_type is None:
                    tag_type = type(nbt)
                elif tag_type != type(nbt):
                    self._throw("Unable to insert " + type(nbt).__name__ + " into ListTag of type " + tag_type.__name__)
                tags.append(nbt)
                if not self._has_separator():
                    break
                elif not self._can_read():
                    self._throw("Expected value")
            self._expect(']')
            return tags

    def _read_array(self) -> NBTBase:
        self._expect('[')
        char = self._pop()
        self.cursor += 1
        self._skip_whitespace()
        if not self._can_read():
            self._throw("Expected value")
        elif char == 'B':
            return NBTTagByteArray(self._read_array_numbers(NBTTagByte, NBTTagByteArray))
        elif char == 'L':
            return NBTTagLongArray(self._read_array_numbers(NBTTagLong, NBTTagLongArray))
        elif char == 'I':
            return NBTTagIntArray(self._read_array_numbers(NBTTagInt, NBTTagIntArray))
        else:
            self._throw("Invalid array type '" + char + "' found")

    def _read_array_numbers(self, tag: Type[NBTPrimitive], array: Type[NBTBase]) -> Iterable[int]:
        out: List[int] = []
        while True:
            if self._peek() != ']':
                value = self._read_value()
                if not isinstance(value, tag):
                    self._throw("Unable to insert " + tag.__name__ + " into " + array.__name__)
                out.append(int(value))

                if self._has_separator():
                    if not self._can_read():
                        self._throw("Expected value")
                    continue
            self._expect(']')
            return out

    def read_compound(self) -> NBTTagCompound:
        self._expect('{')
        compound = NBTTagCompound()
        self._skip_whitespace()
        while self._can_read() and self._peek() != '}':
            key = self._read_key()
            if not key:
                self._throw("Expected non-empty key")
            self._expect(':')
            compound[key] = self._read_value()
            if not self._has_separator():
                break
            elif not self._can_read():
                self._throw("Expected key")
        self._expect('}')
        return compound

    @staticmethod
    def read(data: str) -> NBTTagCompound:
        return NBTReader(data).read_compound()





