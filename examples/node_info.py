from ipv4tree.ipv4tree import IPv4Tree


tree = IPv4Tree()
tree.insert('10.0.0.0/24', info={'country': 'RU'})
node = tree.supernet('10.0.0.34')
print(node)

print(node.info)