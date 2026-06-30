class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


# Create nodes
node1 = Node(15)
node2 = Node(3)
node3 = Node(17)
node4 = Node(90)

# Link nodes
node1.next = node2
node2.next = node3
node3.next = node4

head = node1  # Head points to the first node

# Traverse and print the linked list
current = head
while current:
    print(current.data, end=" -> ")
    current = current.next
print("None")
