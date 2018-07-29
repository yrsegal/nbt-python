from abc import abstractmethod as abstract, ABCMeta as AbstractClass

from typing import BinaryIO, Union, Optional, Type

import struct


class NBTBase(metaclass=AbstractClass):

    @staticmethod
    def _quote_escape(unescaped: str) -> str:
        out = '"'
        for char in unescaped:
            if char == '\\' or char == '"':
                out += '\\'
            out += char
        return out + '"'

    @staticmethod
    def _get_class(tag_id: int) -> Optional[Type['NBTBase']]:
        all_subclasses = NBTBase.__subclasses__()

        while all_subclasses:
            sub = all_subclasses.pop()
            if sub.id() == tag_id:
                return sub
            all_subclasses.extend(sub.__subclasses__())

    @staticmethod
    def read_new_tag(stream: BinaryIO) -> Optional['NBTBase']:
        tag_type: int = NBTBase._read(stream, 'B')
        if tag_type == 0:
            return NBTBase.read_in(0, stream, 0)
        NBTBase._read_utf8(stream)
        return NBTBase.read_in(tag_type, stream, 0)

    @staticmethod
    def read_in(tag_id: int, stream: BinaryIO, depth: int) -> Optional['NBTBase']:
        sub_class = NBTBase._get_class(tag_id)
        if sub_class is not None:
            return sub_class.read(stream, depth)

    @staticmethod
    def _write(data_stream: BinaryIO, fmt: str, *args: Union[int, float]):
        data_stream.write(struct.pack("!" + fmt, *args))

    @staticmethod
    def _read(data_stream: BinaryIO, fmt: str) -> Union[int, float]:
        return struct.unpack("!" + fmt, data_stream.read(struct.calcsize(fmt)))[0]

    @staticmethod
    def _write_utf8(data_stream: BinaryIO, value: str):
        utf_len: int = 0

        for i in value:
            char = ord(i)
            if 0x0001 <= char <= 0x007F:
                utf_len += 1
            elif char > 0x07FF:
                utf_len += 3
            else:
                utf_len += 2

        if utf_len > 65535:
            raise RuntimeError("Encoded string too long: " + utf_len + " bytes")

        NBTBase._write(data_stream, 'H', utf_len)

        for i in value:
            char = ord(i)
            if not 0x0001 <= char <= 0x007F:
                break
            NBTBase._write(data_stream, 'c', char)

        for i in value:
            char = ord(i)
            if 0x0001 <= char <= 0x007F:
                NBTBase._write(data_stream, 'c', char)
            elif char > 0x07FF:
                NBTBase._write(data_stream, 'ccc',
                               (0xE0 | ((char >> 12) & 0x0F)),
                               (0x80 | ((char >> 6) & 0x3F)),
                               (0x80 | (char & 0x3F)))
            else:
                NBTBase._write(data_stream, 'cc',
                               (0xC0 | ((char >> 6) & 0x1F)),
                               (0x80 | (char & 0x3F)))

    @staticmethod
    def _read_utf8(data_stream: BinaryIO) -> str:
        utf_len: int = NBTBase._read(data_stream, "H")
        byte_data: bytes = data_stream.read(utf_len)
        out: str = ""

        pos: int = 0

        while pos < utf_len:
            char = byte_data[pos]
            if char > 0xFF:
                break
            pos += 1
            out += chr(char)

        while pos < utf_len:
            char = byte_data[pos]
            pointer = char >> 4
            if 0x0000 <= pointer <= 0x0111:
                pos += 1
                out += chr(char)
            elif 0x1100 <= pointer <= 0x1101:
                pos += 2
                if pos > utf_len:
                    raise RuntimeError("Malformed input: partial character at end")
                char_part = byte_data[pos - 1]
                if (char_part & 0xC0) != 0x80:
                    raise RuntimeError("Malformed input around byte " + str(pos))
                out += chr(((char & 0x1F) << 6) | (char_part & 0x3F))
            elif pointer == 0x1110:
                pos += 3
                if pos > utf_len:
                    raise RuntimeError("Malformed input: partial character at end")
                char_part = byte_data[pos - 2]
                char_extra = byte_data[pos - 1]
                if (char_part & 0xC0) != 0x80 or (char_extra & 0xC0) != 0x80:
                    raise RuntimeError("Malformed input around byte " + str(pos - 1))

                out += chr(((char & 0x0F) << 12) | ((char_part & 0x3F) << 6) | (char_extra & 0x3F))

        return out

    def write_out(self, data_stream: BinaryIO):
        self._write(data_stream, 'B', self.id())
        if self.id() != 0:
            self._write_utf8(data_stream, "")
            self.write(data_stream)

    @abstract
    def write(self, data_stream: BinaryIO) -> None:
        pass

    @classmethod
    @abstract
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        pass

    @classmethod
    @abstract
    def id(cls) -> int:
        pass

    @abstract
    def copy(self) -> 'NBTBase':
        pass

    @abstract
    def __str__(self) -> str:
        pass


class NBTPrimitiveInt(NBTBase, int, metaclass=AbstractClass):

    @classmethod
    @abstract
    def format(cls) -> str:
        pass

    def write(self, data_stream: BinaryIO) -> None:
        self._write(data_stream, self.format(), self)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        return cls(cls._read(data_stream, cls.format()))

    def copy(self) -> 'NBTBase':
        return type(self)(self)


class NBTPrimitiveFloat(NBTBase, float, metaclass=AbstractClass):

    @classmethod
    @abstract
    def format(cls) -> str:
        pass

    def write(self, data_stream: BinaryIO) -> None:
        self._write(data_stream, self.format(), self)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        return cls(cls._read(data_stream, cls.format()))

    def copy(self) -> 'NBTBase':
        return type(self)(self)


NBTPrimitive = Union[NBTPrimitiveInt, NBTPrimitiveFloat]
