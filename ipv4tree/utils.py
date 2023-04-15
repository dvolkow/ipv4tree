from itertools import product
from typing import Union, List
from ipaddress import IPv4Address, IPv4Network


def _get_binary_path_from_ipv4_addr(ipv4: Union[IPv4Address, IPv4Network]):
    if isinstance(ipv4, IPv4Network):
        return "{0:032b}".format(int(ipv4.network_address))
    if isinstance(ipv4, IPv4Address):
        return "{0:032b}".format(int(ipv4))
    raise TypeError("bad type {}".format(type(ipv4)))


def _get_ipv4_from_binary_string(s: str) -> IPv4Address:
    """
    Revert _get_binary_path_from_ipv4_addr function result.
    """
    return IPv4Address(int(s, 2))


def ipv4_space_split(log_parts_num: int) -> List[IPv4Network]:
    """
    Split IPv4 addresses space for 2 ** log_parts_num equal parts.
    Return list with subnets prefixes.
    """
    nets = []
    for _ in product(['0', '1'], repeat=log_parts_num):
        _string = "".join(_)
        _b32ip = f'0{_string}{"0" * (32 - log_parts_num)}'
        nets.append(IPv4Network(f'{_get_ipv4_from_binary_string(_b32ip)}/{log_parts_num}'))

    return nets
