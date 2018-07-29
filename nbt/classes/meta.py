from typing import BinaryIO, Dict, List

from nbt.classes.base import NBTBase

import re


class NBTTagList(NBTBase, List[NBTBase]):

    def write(self, data_stream: BinaryIO) -> None:
        size: int = len(self)
        if size == 0:
            self._write(data_stream, 'B', 0)
        else:
            self._write(data_stream, 'B', self[0].id())

        self._write(data_stream, 'i', size)

        for tag in self:
            tag.write(data_stream)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        if depth > 512:
            raise RuntimeError("Tried to read NBT tag with too high complexity, depth > 512")

        tag_type: int = cls._read(data_stream, 'B')
        size: int = cls._read(data_stream, 'i')
        if tag_type == 0 and size > 0:
            raise RuntimeError("Missing type on ListTag")

        tag_list = NBTTagList()

        for i in range(size):
            tag_list.append(NBTBase.read_in(tag_type, data_stream, depth + 1))

        return tag_list

    @classmethod
    def id(cls) -> int:
        return 9

    def copy(self) -> 'NBTBase':
        return NBTTagList([tag.copy() for tag in self])

    def __str__(self) -> str:
        return "[" + ",".join(map(str, self)) + "]"


class NBTTagCompound(NBTBase, Dict[str, NBTBase]):

    def write(self, data_stream: BinaryIO) -> None:
        for key in self.keys():
            tag = self[key]
            self._write(data_stream, 'B', tag.id())
            self._write_utf8(data_stream, key)
            tag.write(data_stream)
        self._write(data_stream, 'B', 0)

    @classmethod
    def read(cls, data_stream: BinaryIO, depth: int) -> 'NBTBase':
        if depth > 512:
            raise RuntimeError("Tried to read NBT tag with too high complexity, depth > 512")

        compound = NBTTagCompound()

        tag_type: int = -1
        while tag_type != 0:
            tag_type = cls._read(data_stream, 'B')
            if tag_type == 0:
                break
            key: str = cls._read_utf8(data_stream)
            compound[key] = cls.read_in(tag_type, data_stream, depth + 1)

        return compound

    @classmethod
    def id(cls) -> int:
        return 10

    def copy(self) -> 'NBTBase':
        return NBTTagCompound({key: tag.copy() for (key, tag) in self})

    _simple_pattern = re.compile("[A-Za-z0-9._+-]+")

    def __str__(self) -> str:
        out = "{"
        for key in self:
            if len(out) != 1:
                out += ","

            if NBTTagCompound._simple_pattern.fullmatch(key):
                out += key
            else:
                out += self._quote_escape(key)

            out += ":" + str(self[key])

        return out + "}"
