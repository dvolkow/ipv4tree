# ipv4tree

Prefix (radix-like) tree (trie) for IPv4 addresses manipulations. Allow aggregate prefixes, fast LogN search entries, store additional info in nodes.

![Trie](https://i.ibb.co/6ZCZV1L/2023-04-14-22-00-34.png)

## Setup

With pip:
```buildoutcfg
pip3 install ipv4tree
```

```
python3 setup.py build
python3 setup.py install
```

## Usage:


```python
from ipv4tree.ipv4tree import IPv4Tree

tree = IPv4Tree()
tree.insert('1.1.1.1')
tree.insert('1.1.1.2')
tree.insert('1.1.1.3')
tree.insert('1.1.1.4')
tree.insert('1.1.1.5')
tree.insert('1.1.1.6')
# Show nodes:
print('Common everybody:')
for node in tree:
    if node.islast:
        print(str(node))


# Aggregate to network with rate 1.0:
tree.aggregate(1.0)
print('Only full networks:')
for node in tree:
    if node.islast:
        print(str(node))

# Aggregate to network with rate 0.7:
print('Networks with >0.7 fullness rate:')
tree.aggregate(0.7)
for node in tree:
    if node.islast:
        print(str(node), 'fullness rate', node.fullness())
```

Output:

```
Common everybody:
1.1.1.1/32
1.1.1.2/32
1.1.1.3/32
1.1.1.4/32
1.1.1.5/32
1.1.1.6/32
Only full networks:
1.1.1.1/32
1.1.1.2/31
1.1.1.4/31
1.1.1.6/32
Networks with >0.7 fullness rate:
1.1.1.0/29 fullness rate 0.75
```

# Get supernet for custom IPv4 address:

```python
tree = IPv4Tree()
tree.insert('10.0.0.0/24')

supernet_node = tree.supernet('10.0.0.12')
print(supernet_node)

supernet_node = tree.supernet('10.1.0.12')
print(supernet_node)
```

Output:

```
10.0.0.0/24
None
```

# Custom node info:

```python
tree = IPv4Tree()

tree.insert('10.0.0.0/24', info={'country': 'RU'})
node = tree.supernet('10.0.0.34')

print(node)
print(node.info)
```

Output:

```
10.0.0.0/24
{'country': 'RU'}
```


# CIDR tree:

```python
from ipv4tree.ipv4tree import IPv4Tree, CIDRTree


tree = IPv4Tree()
tree.insert('93.170.0.0/15', info={'asn': 44546})
tree.insert('93.171.161.0/24', info={'asn': 50685})
node = tree.supernet('93.171.161.164')

print('IPv4Tree supernet for 93.171.161.164:')
print(node, node.info['asn'])


tree = CIDRTree()
tree.insert('93.170.0.0/15', info={'asn': 44546})
tree.insert('93.171.161.0/24', info={'asn': 50685})
node = tree.supernet('93.171.161.164')

print('CIDRTree supernet for 93.171.161.164:')
print(node, node.info['asn'])
```

```
IPv4Tree supernet for 93.171.161.164:
93.170.0.0/15 44546
CIDRTree supernet for 93.171.161.164:
93.171.161.0/24 50685
```

So you get supernet with largest prefixlen.


# Utils:


1. IPv4 space split by 2^N parts.
Code:
```python
from ipv4tree.utils import ipv4_space_split

print(ipv4_space_split(1))
print(ipv4_space_split(2))
print(ipv4_space_split(3))
```

Output:
```commandline
[IPv4Network('0.0.0.0/1'), IPv4Network('128.0.0.0/1')]
[IPv4Network('0.0.0.0/2'), IPv4Network('64.0.0.0/2'), IPv4Network('128.0.0.0/2'), IPv4Network('192.0.0.0/2')]
[IPv4Network('0.0.0.0/3'), IPv4Network('32.0.0.0/3'), IPv4Network('64.0.0.0/3'), IPv4Network('96.0.0.0/3'), IPv4Network('128.0.0.0/3'), IPv4Network('160.0.0.0/3'), IPv4Network('192.0.0.0/3'), IPv4Network('224.0.0.0/3')]
```

2. IPv4 address to binary string as bits conversions:
```python
from ipaddress import IPv4Address
from ipv4tree.utils import _get_binary_path_from_ipv4_addr, _get_ipv4_from_binary_string

ip = IPv4Address('42.42.42.42')
print(ip)
ip_str = _get_binary_path_from_ipv4_addr(ip)
print(ip_str)
rev_ip = _get_ipv4_from_binary_string(ip_str)
print(rev_ip)
```

Output:
```commandline
42.42.42.42
00101010001010100010101000101010
42.42.42.42
```

# Tries arithmetic

You can use operator `+` for merge two tree:
```python
from ipv4tree.ipv4tree import IPv4Tree

a, b = IPv4Tree(), IPv4Tree()
a.insert('42.42.42.0/24')
b.insert('224.0.0.0/8')

def print_nodes(a: IPv4Tree):
    for node in a:
        if node.islast:
            print(node)

print_nodes(a)
print_nodes(b)

a += b # equal a = a + b
print_nodes(a)
```

# Multiprocessing:

1. Insert in trie with multiprocess mode (see `ipv4tree/multiprocessing.py`).

If you have too much IPv4 prefixes for insert to tree, it may be make with multiprocessing. 

First, get splitted ipv4 space. You must use 2^N processes. For example, `N = 4`.
```python
from ipv4tree.utils import ipv4_space_split

N = 4
nets = ipv4_space_split(N)
threads_num = 2 ** N
print(len(nets), threads_num)
```

Second, your insert task may be similar as this example:
```python
from ipv4tree.ipv4tree import IPv4Tree
from ipaddress import IPv4Address, IPv4Network

def _insert_task(dct, data, network: IPv4Network, thread_id: int):
    tree = IPv4Tree()
    for item in data:
        if IPv4Address(item) in network:
            tree.insert(item)

    dct[thread_id] = tree
```

`dct` is `manager.dict()` object for store your tree.

For example, listing for mutliprocess inserts:

```python
from multiprocessing import Manager, Process

manager = Manager()
tree_dict = manager.dict()
processes = []

for i in range(threads_num):
    proc = Process(target=_insert_task,
                   args=(tree_dict, data, nets[i], i,))
    processes.append(proc)
    proc.start()

for proc in processes:
    proc.join()
```

Merge tries to one tree from result values:
```python
tree = IPv4Tree()

for i in range(threads_num):
    root = tree_dict[i][nets[i]] # take direct root node from new tree by thread i
    if root is not None:
        tree.insert_node(root)
```