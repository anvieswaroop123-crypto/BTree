
# Maximum number of keys in each node
MAX_KEYS = 3


class Node:
    def __init__(self, leaf=True):
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf


class BTree:
    def __init__(self):
        self.root = Node()

    # Find a key and return its position
    def find_key(self, node, key):
        i = 0

        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        return i

    # Search for a key in the tree
    def search(self, key, node=None):
        if node is None:
            node = self.root

        i = self.find_key(node, key)

        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]

        if node.leaf:
            return None

        return self.search(key, node.children[i])

    # Split a full child into two nodes
    def split_child(self, parent, i):
        child = parent.children[i]
        right = Node(child.leaf)

        # Move the middle key up to the parent
        middle_key = child.keys[1]
        middle_value = child.values[1]

        right.keys = child.keys[2:]
        right.values = child.values[2:]

        child.keys = child.keys[:1]
        child.values = child.values[:1]

        # Move the children too, if needed
        if not child.leaf:
            right.children = child.children[2:]
            child.children = child.children[:2]

        parent.keys.insert(i, middle_key)
        parent.values.insert(i, middle_value)
        parent.children.insert(i + 1, right)

    # Insert into a node that has space
    def insert_non_full(self, node, key, value):
        i = len(node.keys) - 1

        if node.leaf:
            # Put the key in sorted order
            node.keys.append(key)
            node.values.append(value)

            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1

            node.keys[i + 1] = key
            node.values[i + 1] = value

        else:
            # Find the child where the key belongs
            while i >= 0 and key < node.keys[i]:
                i -= 1

            i += 1

            # Split the child if it is full
            if len(node.children[i].keys) == MAX_KEYS:
                self.split_child(node, i)

                if key > node.keys[i]:
                    i += 1

            self.insert_non_full(node.children[i], key, value)

    # Add a key and value to the tree
    def insert(self, key, value):
        # Update the value if the key already exists
        if self.search(key) is not None:
            self.update_value(self.root, key, value)
            return

        # Split the root if it is full
        if len(self.root.keys) == MAX_KEYS:
            new_root = Node(False)
            new_root.children.append(self.root)
            self.root = new_root
            self.split_child(new_root, 0)

        self.insert_non_full(self.root, key, value)

    # Change the value for an existing key
    def update_value(self, node, key, value):
        i = self.find_key(node, key)

        if i < len(node.keys) and node.keys[i] == key:
            node.values[i] = value
            return

        if not node.leaf:
            self.update_value(node.children[i], key, value)

    # Borrow a key from the left sibling
    def borrow_left(self, parent, i):
        node = parent.children[i]
        left = parent.children[i - 1]

        node.keys.insert(0, parent.keys[i - 1])
        node.values.insert(0, parent.values[i - 1])

        if not node.leaf:
            node.children.insert(0, left.children.pop())

        parent.keys[i - 1] = left.keys.pop()
        parent.values[i - 1] = left.values.pop()

    # Borrow a key from the right sibling
    def borrow_right(self, parent, i):
        node = parent.children[i]
        right = parent.children[i + 1]

        node.keys.append(parent.keys[i])
        node.values.append(parent.values[i])

        if not node.leaf:
            node.children.append(right.children.pop(0))

        parent.keys[i] = right.keys.pop(0)
        parent.values[i] = right.values.pop(0)

    # Merge two children together
    def merge(self, parent, i):
        left = parent.children[i]
        right = parent.children[i + 1]

        left.keys.append(parent.keys.pop(i))
        left.values.append(parent.values.pop(i))

        left.keys.extend(right.keys)
        left.values.extend(right.values)
        left.children.extend(right.children)

        parent.children.pop(i + 1)

    # Make sure a child has enough keys before deleting
    def fill_child(self, parent, i):
        if i > 0 and len(parent.children[i - 1].keys) >= 2:
            self.borrow_left(parent, i)

        elif (i < len(parent.children) - 1
              and len(parent.children[i + 1].keys) >= 2):
            self.borrow_right(parent, i)

        else:
            if i < len(parent.children) - 1:
                self.merge(parent, i)
            else:
                self.merge(parent, i - 1)

    # Find the biggest key in a subtree
    def predecessor(self, node):
        while not node.leaf:
            node = node.children[-1]

        return node.keys[-1], node.values[-1]

    # Find the smallest key in a subtree
    def successor(self, node):
        while not node.leaf:
            node = node.children[0]

        return node.keys[0], node.values[0]

    # Delete a key from a leaf
    def remove_from_leaf(self, node, i):
        node.keys.pop(i)
        node.values.pop(i)

    # Delete a key from a node with children
    def remove_from_internal(self, node, i):
        key = node.keys[i]

        if len(node.children[i].keys) >= 2:
            new_key, new_value = self.predecessor(node.children[i])
            node.keys[i] = new_key
            node.values[i] = new_value
            self.remove_key(node.children[i], new_key)

        elif len(node.children[i + 1].keys) >= 2:
            new_key, new_value = self.successor(node.children[i + 1])
            node.keys[i] = new_key
            node.values[i] = new_value
            self.remove_key(node.children[i + 1], new_key)

        else:
            self.merge(node, i)
            self.remove_key(node.children[i], key)

    # Remove a key from the tree
    def remove_key(self, node, key):
        i = self.find_key(node, key)

        if i < len(node.keys) and node.keys[i] == key:
            if node.leaf:
                self.remove_from_leaf(node, i)
            else:
                self.remove_from_internal(node, i)

        else:
            if node.leaf:
                return

            last_child = (i == len(node.keys))

            if len(node.children[i].keys) < 2:
                self.fill_child(node, i)

            if last_child and i > len(node.keys):
                self.remove_key(node.children[i - 1], key)
            else:
                self.remove_key(node.children[i], key)

    # Delete a key and fix the root if needed
    def remove(self, key):
        if self.search(key) is None:
            return

        self.remove_key(self.root, key)

        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    # Display the tree
    def display(self, node=None, level=0):
        if node is None:
            node = self.root

        print("  " * level + str(node.keys))

        for child in node.children:
            self.display(child, level + 1)
