from ipv4tree.ipv4tree import IPv4Tree


tree = IPv4Tree()
tree.insert('10.0.0.0/24')
print(tree)

print(tree.intree('10.0.0.12'))
print(tree.intree('10.1.0.12'))

supernet_node = tree.supernet('10.0.0.12')
print(supernet_node)

supernet_node = tree.supernet('10.1.0.12')
print(supernet_node)
