"""
Tree delete subnets testing samples.
"""
from ipv4tree.ipv4tree import IPv4Tree


tree = IPv4Tree()
tree.insert('1.0.0.0/24')
tree.insert('1.0.1.0/24')
tree.insert('1.0.2.0/24')
print(tree)
print(tree.sizeof('1.0.0.0/20'))

tree.delete('1.0.0.0/20')  # more than exist prefixes
print(tree)
print(tree.sizeof('1.0.0.0/22'))

for node in tree:
    if node.islast:
        print(node, node.sizeof(), node.size)


tree = IPv4Tree()
tree.insert('1.0.0.0/24')
tree.insert('1.0.1.0/24')
tree.insert('1.0.2.0/24')
tree.delete('1.0.0.25/32')  # less than exist prefixes
print(tree)
print(tree.sizeof('1.0.0.0/22'))

for node in tree:
    if node.islast:
        print(node, node.sizeof(), node.size)
