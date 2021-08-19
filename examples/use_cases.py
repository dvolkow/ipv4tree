from ipv4tree.ipv4tree import IPv4Tree
from ipaddress import IPv4Address, IPv4Network

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
    print(node)


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

tree = IPv4Tree()
print('insert 1.1.1.0/24')
tree.insert('1.1.1.0/24')
for node in tree:
    if node.islast:
        print(node)
print('delete 1.1.1.2/32')
tree.delete('1.1.1.2/32')
print('delete 1.1.1.12/32')
tree.delete('1.1.1.12/32')
print('delete 1.1.1.160/31')
tree.delete('1.1.1.160/31')
for node in tree:
    if node.islast:
        print(node)

print('insert 1.1.1.2/32')
tree.insert('1.1.1.2/32')
print('insert 1.1.1.12/32')
tree.insert('1.1.1.12/32')
'''
print('insert 1.1.1.160/31')
tree.insert('1.1.1.160/31')
'''
tree.aggregate(1)
for node in tree:
    if node.islast:
        print(node)

from ipv4tree.ipv4tree import _get_binary_path_from_ipv4_addr

"""
Distance between lower and upper bound of network:
img. as bits array, greedy aggregate to networks

Example:
"""
print('Networks in range [1.1.1.1 - 1.1.1.13]')
#print(_get_binary_path_from_ipv4_addr(IPv4Address('1.1.1.1')))
#print(_get_binary_path_from_ipv4_addr(IPv4Address('1.1.1.13')))
print("".join([str(IPv4Address(int('00000001000000010000000100000001', 2))), '/32']))
print("".join([str(IPv4Address(int('00000001000000010000000100000010', 2))), '/31']))
print("".join([str(IPv4Address(int('00000001000000010000000100000100', 2))), '/30']))
print("".join([str(IPv4Address(int('00000001000000010000000100001000', 2))), '/30']))
print("".join([str(IPv4Address(int('00000001000000010000000100001100', 2))), '/32']))
print("".join([str(IPv4Address(int('00000001000000010000000100001101', 2))), '/32']))
