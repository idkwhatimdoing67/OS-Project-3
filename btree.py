import struct

class BTreeNode:
    # Constants
    T = 10
    MAX_KEYS = (2 * T) - 1 # 19 keys 
    MAX_VALUES = (2 * T) - 1 # 19 values 
    MAX_CHILDREN = 2 * T # 20 children 
    BLOCK_SIZE = 512
    
    def __init__(self, block_id):
        # Initialize empty node in memory
        self.block_id = block_id
        self.parent_id = 0
        self.num_keys = 0
        
        self.keys = []
        self.values = []
        self.children = []
    
    def is_leaf(self):
        # Determines if node is a leaf
        return len(self.children) == 0 or self.children[0] == 0 # If first child pointer = 0, no kids
    
    def pack_to_bytes(self):
        