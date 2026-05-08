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
        # Serializes node into 512 bytes
        
        #Pad the lists with zeroes up to max sizes, ensures consistent writing of exactly 19 keys to 20 kids
        padded_keys = self.keys + [0] * (self.MAX_KEYS - len(self.keys))
        padded_values = self.values + [0] * (self.MAX_VALUES - len(self.values))
        padded_children = self.children + [0] * (self.MAX_CHILDREN - len(self.children))
        
        # Layout: [Block ID, Parent ID, Num Keys] + 19 Keys + 19 Keys + 20 Kids
        # List size will be 3 + 19 + 19 + 19 + 20 = 61
        all_integers = [self.block_id, self.parent_id, self.num_keys] + padded_keys + padded_values + padded_children
        
        # Pack integers into binary
        # 61 items * 8 bytes = 488 bytes
        packed_data = struct.pack(">61Q", *all_integers)
        
        # Remaining bytes: 24 padded with zeroes
        packed_data += b'\x00' * (self.BLOCK_SIZE - len(packed_data))
        
        return packed_data
    