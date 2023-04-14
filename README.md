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

# Multiprocessing:

1. Insert in trie with multiprocess mode.

If you have too much IPv4 prefixes for insert to tree, it may be make with multiprocessing. 

First, get splitted ipv4 space. You must use 2^N processes. For example, `N = 4`.
```python
from ipv4tree.utils import ipv4_space_split

N = 4
nets = ipv4_space_split(N)
threads_num = 2 ** N
print(len(nets), threads_num)
```

Second, prepare your trie for multiprocess inserts. Use `fake_insert` method for roots creating:
```python
from ipv4tree.ipv4tree import IPv4Tree

tree = IPv4Tree()
for net in nets:
    tree.fake_insert(net)
```