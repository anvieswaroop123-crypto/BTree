
from btree import BTree

tree = BTree()

# Add some keys and values
for key in [10, 20, 5, 6, 12, 30, 7, 17]:
    tree.insert(key, key * 10)

# Display the tree
print("B-tree:")
tree.display()

# Search for a key
print("Value for 12:", tree.search(12))

# Delete a key
tree.remove(12)
print("After removing 12:")
tree.display()

print("Search for 12:", tree.search(12))
