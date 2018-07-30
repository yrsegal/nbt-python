from gzip import GzipFile

from nbt.classes import *
from nbt.json import NBTReader

__all__ = [
    'NBTBase',
    'NBTPrimitive',
    'NBTTagByte',
    'NBTTagShort',
    'NBTTagInt',
    'NBTTagLong',
    'NBTTagFloat',
    'NBTTagDouble',
    'NBTTagByteArray',
    'NBTTagString',
    'NBTTagList',
    'NBTTagCompound',
    'NBTTagIntArray',
    'NBTTagLongArray',
    'NBTReader',
    'read',
    'read_zipped',
    'write',
    'write_zipped'
]


def read(location: str) -> NBTBase:
    with open(location, 'rb') as stream:
        return NBTBase.read_new_tag(stream)


def read_zipped(location: str) -> NBTBase:
    with GzipFile(location, 'rb') as stream:
        return NBTBase.read_new_tag(stream)


def write(nbt: NBTBase, location: str):
    with open(location, 'wb') as stream:
        nbt.write_out(stream)


def write_zipped(nbt: NBTBase, location: str):
    with GzipFile(location, 'wb') as stream:
        nbt.write_out(stream)

