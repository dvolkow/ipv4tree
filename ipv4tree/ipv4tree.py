from collections.abc import Collection, Iterable


class IPv4TreeNode(Iterable):
    def __init__(self, key, prefixlen, size=1, parent=None, islast=False):
        if parent is not None:
            parent.new_child(key, self)
        self._parent = parent
        self._children = [None, None]
        self._prefixlen = prefixlen
        self._prefix = "".join([parent.prefix(), str(key)]) if parent is not None else str(key)
        self._size = size
        self._islast = islast

    def parent(self):
        return self._parent

    def prefix(self):
        return self._prefix

    def prefixlen(self):
        return self._prefixlen

    def child(self, key):
        return self._children[int(key)]

    def children(self):
        return self._children

    def new_child(self, key, node):
        self._children[int(key)] = node

    def update(self, prefixlen, size=1):
        self._size += size
        if prefixlen > self._prefixlen:
            self._islast = True

    def fullness(self):
        if self._prefixlen == 32:
            return 1
        if self._prefixlen == 31:
            return self._size / 2
        return self._size / (2 ** (32 - self._prefixlen))

    def __repr__(self):
        return str(self)

    def aggregate(self, fullness):
        if self.fullness() >= fullness:
            self._islast = True

    def __iter__(self):
        yield self
        if not self._islast:
            for child in self._children:
                if child is not None:
                    yield from iter(child)

    def __int__(self):
        from copy import deepcopy
        s = deepcopy(self._prefix)
        for _ in range(32 - self._prefixlen):
            s = "".join([s, "0"])
        return int(s, 2)

    def __str__(self):
        from ipaddress import IPv4Address
        if self._prefixlen > 0:
            return "/".join([str(IPv4Address(int(self))),
                            str(self._prefixlen)])
        return "root"

    def _is_root(self):
        return "root" == str(self)

    def network_address(self):
        from ipaddress import IPv4Address
        return IPv4Address(str(self).split('/')[0])

    def size(self):
        return self._size

    def islast(self):
        return self._islast


class IPv4Tree(Collection):
    def __init__(self):
        self._root = IPv4TreeNode(key=0,
                                  prefixlen=0,
                                  size=0)
        self._nodes = 1
        self._nodes_map = {}

    def _insert_node(self, prev, key, size=1, **kwargs):
        node = IPv4TreeNode(key=key,
                            prefixlen=prev.prefixlen() + 1,
                            size=size,
                            parent=prev)
        self._nodes += 1
        return node

    def delete(self, ip):
        from ipaddress import IPv4Network

        net = IPv4Network(ip)
        intree = net in self
        if not intree:
            return

        node = self[ip]
        size = node.size()
        node = self._root
        for n in _get_binary_path_from_ipv4_addr(net):
            node.update(-1, -size)
            prev = node
            node = prev.child(n)

            if node.prefixlen() == net.prefixlen:
                break

        prev.new_child(n, None)
        self._nodes_map.pop(net, None)

    def intree(self, ip):
        from ipaddress import IPv4Network
        ip = IPv4Network(ip)
        intree = ip in self
        if intree:
            return True
        node = self._root
        for n in _get_binary_path_from_ipv4_addr(ip):
            prev = node
            node = prev.child(n)
            if node is None:
                return False
            if node.islast() or node.prefixlen() == ip.prefixlen:
                break
        return True

    def insert(self, ip, **kwargs):
        from ipaddress import IPv4Network

        ip = IPv4Network(ip)
        intree = ip in self
        if intree:
            return

        size = ip.num_addresses
        node = self._root
        self._root.update(-1, size)
        was_insert = False
        for n in _get_binary_path_from_ipv4_addr(ip):
            prev = node
            node = prev.child(n)
            if node is None:
                node = self._insert_node(prev, n, size, **kwargs)
                was_insert = True
            else:
                node.update(node.prefixlen(), size)

            if node.islast():
                # try insert for subnetwork of exist in tree
                break

            if node.prefixlen() == ip.prefixlen:
                # try insert for supernetwork?
                break

        node._islast = True
        if not was_insert:
            if node.prefixlen() != ip.prefixlen:
                # is supernet
                excess = size
            else:
                excess = node.size() - size
            while node is not None:
                node.update(-1, -excess)
                node = node.parent()
        else:
            # new node in last level
            self._nodes_map[ip] = node

    def __contains__(self, ipv4):
        from ipaddress import IPv4Network
        return IPv4Network(ipv4) in self._nodes_map.keys()

    def __iter__(self):
        return iter(self._root)

    def __len__(self):
        return self._root.size()

    def __getitem__(self, ipv4):
        from ipaddress import IPv4Network
        net = IPv4Network(ipv4)
        node = self._root
        for n in _get_binary_path_from_ipv4_addr(net):
            node = node.child(n)
            if node is None or node.prefixlen() == net.prefixlen:
                break
        return node

    def aggregate(self, fullness):
        for node in self:
            node.aggregate(fullness)

    def last_assignment(self, prefixlen=32, islast=False):
        """
        Default values undo 'aggregate' method
        """
        for node in self:
            if node.prefixlen() < prefixlen:
                node._islast = islast

    def __repr__(self):
        prefixlens = {}
        last_nodes = 0
        for node in self:
            prefixlen = str(node.prefixlen())
            if prefixlen not in prefixlens.keys():
                prefixlens[prefixlen] = 1
            else:
                prefixlens[prefixlen] += 1
            if node._islast:
                last_nodes += 1
        return str(prefixlens) + "\nTotal nodes: {}\nSize: {}"\
            "\nLast nodes: {}".format(self._nodes,
                                      self._root.size(),
                                      last_nodes)


def _get_binary_path_from_ipv4_addr(ipv4):
    from ipaddress import IPv4Address, IPv4Network
    if isinstance(ipv4, IPv4Network):
        return "{0:032b}".format(int(ipv4.network_address))
    if isinstance(ipv4, IPv4Address):
        return "{0:032b}".format(int(ipv4))
    raise TypeError("bad type {}".format(type(ipv4)))
