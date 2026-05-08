import struct
import csv
import os

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
    
    def unpack_from_bytes(self, raw_data):
        # Deserializes 512 byte block into lists 
        if len(raw_data) != self.BLOCK_SIZE:
            raise ValueError(f"Expected {self.BLOCK_SIZE} bytes, got {len(raw_data)}")
        
        #Unpack first 488 bytes
        unpacked_data = struct.unpack(">61Q", raw_data[:488]) # Last 24 are useless as established in packing method
        
        # Restore header vars
        self.block_id = unpacked_data[0]
        self.parent_id = unpacked_data[1]
        self.num_keys = unpacked_data[2]
        
        # Restore lists by slicing
        # Remember to only slice the valid list and leave the padded one alone
        
        # Keys start at index 3
        self.keys = list(unpacked_data[3:3+self.num_keys])
        
        # Values start at 22
        self.values = list(unpacked_data[22:22+self.num_keys])
        
        # Children start at 41
        num_children = self.num_keys + 1 if self.num_keys > 0 else 0
        self.children = list(unpacked_data[41:41+num_children])
        

class BTree:
    def __init__(self, buffer_manager):
        # Initialize tree
        # Uses buffer_manager to enforce 3 node limit
        
        self.buffer = buffer_manager
        self.file_manager = self.buffer.file_manager
        
        # Min degree = 10, max 19 keys per node
        self.t = 10
        self.max_keys = (2*self.t) -1
        
        # If file is brand new, root ID = 0
        # Create initial empty root node
        if self.file_manager.root_id == 0:
            new_root_id = self.file_manager.get_new_block_id()
            new_root = BTreeNode(new_root_id)
            
            # Register with mem manager and set as official root
            self.buffer.register_new_node(new_root)
            self.file_manager.set_root_id(new_root_id)
            
    def _get_root(self):
        # Fetch current root node via buffermanager
        return self.buffer.get_node(self.file_manager.root_id)
    
    " Below will cover the search logic "
    
    def search(self, key):
        # Search BTree for specific key, returns (key,value) tuple
        return self._search_node(self._get_root(), key)
    
    def _search_node(self,node,key):
        # Search helper, acts as core functionality
        i = 0
        
        # Find first key >= to target
        while i < node.num_keys and key > node.keys[i]:
            i += 1
        
        # Check if the exact key was found
        if i < node.num_keys and key == node.keys[i]:
            return (node.keys[i], node.values[i])
        
        # If not found and node is leaf, then the key must not exist
        if node.is_leaf():
            return None
        
    
    " Insertion logic below "
    
    def insert(self, key, value):
        # Insert new key/value pair into BTree
        
        root = self._get_root()
        
        # If root is full, must split
        if root.num_keys == self.max_keys:
            # Create new empty node to become new root
            new_root_id = self.file_manager.get_new_block_id()
            new_root = BTreeNode(new_root_id)
            
            #Make old root a child of new root
            new_root.children.append(root.block_id)
            self.buffer.register_new_node(new_root)
            
            #Update file manager's global root pointer
            self.file_manager.set_root_id(new_root_id)
            
            # Split old root
            self._split_child(new_root, 0, root)
            
            # Insert new key into new tree
            self._insert_non_full(new_root, key, value)
        else:
            # Root isn't full, start normal insertion
            self._insert_non_full(root, key, value)
        
    def _split_child(self, parent, index, full_child):
        # Split full node into two nodes (19 keys to 9 each)
        # Middle key (The 10th) becomes parent node
        
        # Crate new sibling node
        new_sibling_id = self.file_manager.get_new_block_id()
        new_sibling = BTreeNode(new_sibling_id)
        new_sibling.parent_id = parent.block_id
        
        # New sibling gets upper 9 keys/values
        new_sibling.keys = full_child.keys[self.t:]
        new_sibling.values = full_child.values[self.t:]
        new_sibling.num_keys = self.t - 1
        
        # If the full child is not leaf, sibling also takes upper 10
        if not full_child.is_leaf():
            new_sibling.children = full_child.children[self.t:]
            full_child.children = full_child.children[:self.t]
        
        # Full child keeps lower 9 keys
        # 10th key is median to be pushed up
        median_key = full_child.keys[self.t - 1]
        median_val = full_child.values[self.t - 1]
        
        full_child.keys = full_child.keys[:self.t - 1]
        full_child.values = full_child.values[:self.t - 1]
        full_child.num_keys = self.t - 1
        
        # Push median key/value up to parent
        parent.keys.insert(index, median_key)
        parent.values.insert(index, median_val)
        parent.num_keys += 1
        
        # Add new sibling's ID to parent's children array
        parent.children.insert(index + 1, new_sibling_id)
        
        # Register new sibling and mark all 3 nodes as dirty
        # Marked as dirty so they save
        self.buffer.register_new_node(new_sibling)
        self.buffer.mark_dirty(parent.block_id)
        self.buffer.mark_dirty(full_child.block_id)
        
    def _insert_non_full(self, node, key, value):
        # Descend through tree, preemptively splitting if finding a full node
        # Allows us not to need backward traversal
        
        i = node.num_keys - 1
        
        if node.is_leaf():
            # Base Case: If a leaf node, Insert
            
            # Pad lists first with 0s
            node.keys.append(0)
            node.values.append(0)
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i+1] = node.keys[i]
                node.values[i+1] = node.values[i]
                i -= 1
            
            node.keys[i+1] = key
            node.values[i+1] = value
            node.num_keys += 1
            
            # Pop the trailing zeros
            node.keys = node.keys[:node.num_keys]
            node.values = node.values[:node.num_keys]
            
            self.buffer.mark_dirty(node.block_id)
            
        else:
            # Recursive case: Find which child pointer to descend into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            child_id = node.children[i]
            child = self.buffer.get_node(child_id)
            
            # Preemptive split
            # If child is full split before entering (This sounds crazy out of context)
            if child.num_keys == self.max_keys:
                self._split_child(node, i, child)
            
                # Once split, move median key up
                # Check where key should go: left or right
                if key > node.keys[i]:
                    i += 1
                    child_id = node.children[i]
                    child = self.buffer.get_node(child_id)
            
            # Descended into non-full kid
            self._insert_non_full(child, key, value)
            
   
    " Utility Logic Below "
    
    def print_tree(self):
        # Print all keys/values in order
        self._in_order_traverse(self.file_manager.root_id, lambda k, v: print(f"{k} {v}"))
    
    def extract_to_csv(self, filename):
        # Extract tree to csv file
        if os.path.exists(filename):
            raise FileExistsError(f"Error: Output file '{filename}' already exists.")
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            self._in_order_traverse(self.file_manager.root_id, lambda k, v: writer.writerow([k, v]))
    
    def load_from_csv(self, filename):
        # Read a csv and insert each key/value pair
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Error: Input file '{filename}' does not exist.")

        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    key, val = int(row[0].strip()), int(row[1].strip())
                    self.insert(key, val)
    
    def _in_order_traverse(self, node_id, callback):
        # Traverses tree in order, calling callback on each pair
        # Uses buffermanager to handle paging nodes I/O memory
        
        if node_id == 0:
            return
        
        node = self.buffer.get_node(node_id)
        
        for i in range(node.num_keys):
            if not node.is_leaf():
                self._in_order_traverse(node.children[i], callback)
            
            # Re-fetch node after recursive return
            # Traversing deep into children has potential to evict parent
            node = self.buffer.get_node(node_id) 
            callback(node.keys[i], node.values[i])
        
        if not node.is_leaf():
            self._in_order_traverse(node.children[node.num_keys], callback)
