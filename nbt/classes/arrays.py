from typing import BinaryIO, List

from nbt.classes.base import NBTBase


class NBTTagByteArray(NBTBase, bytearray):

    def write(self, data_stream: BinaryIO) -> None:
        self._write(data_stream, 'i', len(self))
        data_stream.write(self)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        size: int = cls._read(data_stream, 'i')
        return NBTTagByteArray(data_stream.read(size))

    @classmethod
    def id(cls) -> int:
        return 7

    def copy(self) -> 'NBTBase':
        return NBTTagByteArray(self)

    def __str__(self) -> str:
        out = "[B;"
        for byte in self:
            if len(out) != 3:
                out += ","
            out += str(byte) + "B"
        return out + "]"


class NBTTagString(NBTBase, str):

    def write(self, data_stream: BinaryIO) -> None:
        self._write_utf8(data_stream, self)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        return NBTTagString(cls._read_utf8(data_stream))

    @classmethod
    def id(cls) -> int:
        return 8

    def copy(self) -> 'NBTBase':
        return NBTTagString(self)

    def __str__(self) -> str:
        return self._quote_escape(self)


class NBTTagIntArray(NBTBase, List[int]):

    def write(self, data_stream: BinaryIO) -> None:
        self._write(data_stream, 'i', len(self))
        for i in self:
            self._write(data_stream, 'i', i)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        size: int = cls._read(data_stream, 'i')
        return NBTTagIntArray([cls._read(data_stream, 'i') for _ in range(size)])

    @classmethod
    def id(cls) -> int:
        return 11

    def copy(self) -> 'NBTBase':
        return NBTTagIntArray(self[:])

    def __str__(self) -> str:
        out = "[I;"
        for byte in self:
            if len(out) != 3:
                out += ","
            out += str(byte) + "I"
        return out + "]"


class NBTTagLongArray(NBTBase, List[int]):

    def write(self, data_stream: BinaryIO) -> None:
        self._write(data_stream, 'i', len(self))
        for i in self:
            self._write(data_stream, 'l', i)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        size: int = cls._read(data_stream, 'i')
        return NBTTagLongArray([cls._read(data_stream, 'l') for _ in range(size)])

    @classmethod
    def id(cls) -> int:
        return 12

    def copy(self) -> 'NBTBase':
        return NBTTagLongArray(self[:])

    def __str__(self) -> str:
        out = "[L;"
        for byte in self:
            if len(out) != 3:
                out += ","
            out += str(byte) + "L"
        return out + "]"
