from typing import BinaryIO

from nbt.classes.base import NBTBase, NBTPrimitiveFloat, NBTPrimitiveInt


class NBTTagEnd(NBTBase):

    def write(self, data_stream: BinaryIO) -> None:
        pass

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        return cls()

    @classmethod
    def id(cls) -> int:
        return 0

    def copy(self) -> 'NBTBase':
        return NBTTagEnd()

    def __str__(self) -> str:
        return "END"


class NBTTagByte(NBTPrimitiveInt):

    @classmethod
    def format(cls) -> str:
        return 'b'

    @classmethod
    def id(cls) -> int:
        return 1

    def __str__(self) -> str:
        return str(int(self)) + "b"


class NBTTagShort(NBTPrimitiveInt):

    @classmethod
    def format(cls) -> str:
        return 'h'

    @classmethod
    def id(cls) -> int:
        return 2

    def __str__(self) -> str:
        return str(int(self)) + "s"


class NBTTagInt(NBTPrimitiveInt):

    @classmethod
    def format(cls) -> str:
        return 'i'

    @classmethod
    def id(cls) -> int:
        return 3

    def __str__(self) -> str:
        return str(int(self))


class NBTTagLong(NBTPrimitiveInt):

    @classmethod
    def format(cls) -> str:
        return 'q'

    @classmethod
    def id(cls) -> int:
        return 4

    def __str__(self) -> str:
        return str(int(self)) + "L"


class NBTTagFloat(NBTPrimitiveFloat):

    @classmethod
    def format(cls) -> str:
        return 'f'

    @classmethod
    def id(cls) -> int:
        return 5

    def __str__(self) -> str:
        return str(float(self)) + "f"


class NBTTagDouble(NBTPrimitiveFloat):

    @classmethod
    def format(cls) -> str:
        return 'd'

    @classmethod
    def id(cls) -> int:
        return 6

    def __str__(self) -> str:
        return str(float(self)) + "d"
