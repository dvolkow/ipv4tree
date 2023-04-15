from ipaddress import IPv4Network, IPv4Address
from ipv4tree.ipv4tree import IPv4Tree
from ipv4tree.utils import ipv4_space_split
from multiprocessing import Process, Manager
from typing import Iterable, Dict


def _insert_task(dct: Dict, data: Iterable, network: IPv4Network, thread_id: int):
    """
    Example of insert task, data contains ipv4 address items.
    """
    tree = IPv4Tree()
    for item in data:
        if IPv4Network(item).network_address in network:
            tree.insert(item)

    dct[thread_id] = tree


def insert(data: Iterable, log_threads_num: int) -> IPv4Tree:
    """
    Insert data to IPv4Tree in 2**(log_threads_num) threads.
    Return IPv4Tree. Use this example for multiprocessing inserts.

    Items in data must correct converted as IPv4Address(item).
    """
    nets = ipv4_space_split(log_threads_num)
    threads_num = 2 ** log_threads_num

    tree = IPv4Tree()
    manager = Manager()
    proxy_dict = manager.dict()
    processes = []

    for i in range(threads_num):
        proc = Process(target=_insert_task,
                       args=(proxy_dict, data, nets[i], i,))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    # merge roots:
    for i in range(threads_num):
        root = proxy_dict[i][nets[i]]
        if root is not None:
            tree.insert_node(root)

    return tree
