from collections import OrderedDict
from btree import BTreeNode

class BufferManager:
    def __init__(self, file_manager, max_nodes=3):
        # Initialize buffer
        # file_manager will be Index File Manager instance for I/O
        # Max nodes will be the hard limit outlined in assignment
        
        self.file_manager = file_manager
        self.max_nodes = max_nodes
        
        # Ordered dict will be the LRU cache
        self.nodes_in_memory = OrderedDict()
        
        # Set will track block IDs that have been modified
        self.dirty_blocks = set()
        
    def get_node(self, block_id):
        # Fetch node, if in mem it returns
        # If not in mem, it evicts old node and loads to disk
        
        # Cache hit, if in mem
        if block_id in self.nodes_in_memory:
            # Move accessed node to end of OrderedDict (LRU cache)
            self.nodes_in_memory.move_to_end(block_id)
            return self.nodes_in_memory[block_id]
        
        #Cache miss, if not in mem
        # Check if at 3 limit
        if len(self.nodes_in_memory) >= self.max_nodes:
            self._evict_oldest()
        
        raw_data = self.file_manager.read_block(block_id) # Ask file manager for 512 block
        
        # Create new btree node, tell it to go through raw bytes from file manager
        node = BTreeNode(block_id)
        node.unpack_from_bytes(raw_data)
        
        # Store new node in memory dict
        self.nodes_in_memory[block_id] = node
        
        return node
    
    def register_new_node(self, node):
        
    
    def mark_dirty(self, block_id):
    
    def _evict_oldest(self):
    
    def flush_all(self):