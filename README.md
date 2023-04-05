# ipv4tree

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


