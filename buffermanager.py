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
        # Take new node created by BTree, add to buffer, marks it for saving
        
        # Enforce 3 node limit
        if len(self.nodes_in_memory) >= self.max_nodes:
            self._evict_oldest()
        
        self.nodes_in_memory[node.block_id] = node
        
        self.mark_dirty(node.block_id) # New node is inherently dirty
    
    def mark_dirty(self, block_id):
        # Marks as dirty
        if block_id in self.nodes_in_memory:
            self.dirty_blocks.add(block_id)
    
    def _evict_oldest(self):
        # Removes LRU node from mem
        # If modified, packs into bytes and saves to disk
        
        # Remove and return first item in ordereddict; last LRU item
        evicted_block_id, evicted_node = self.nodes_in_memory.popitem(last=False)
    
        # Check if evicted node was modified in mem
        if evicted_block_id in self.dirty_blocks:
            # Tell node to serialize itself back into 512 bytes
            raw_data = evicted_node.pack_to_bytes()
            
            # Write bytes to disk
            self.file_manager.write_block(evicted_block_id, raw_data)
            
            self.dirty_blocks.remove(evicted_block_id) # Remove dirty status once on disk
        
    def flush_all(self):
        # Evicts and saves all remaining nodes in memory
        while self.nodes_in_memory:
            self._evict_oldest()