import os

class IndexFileManager:
    MAGIC_NUMBER = b"4348PRJ3"
    BLOCK_SIZE = 512
    
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.root_id = 0
        self.next_block_id = 1
        
    def create_new_file(self):
        # Create new index file and write header block
        if os.path.exists(self.filename):
            raise FileExistsError(f"Error: File '{self.filename}' already exists.")
    
        #Open in write binary mode to initialize
        with open(self.filename, 'wb') as f:
            # Write the magic number
            f.write(self.MAGIC_NUMBER)
            
            #Write 8 byte root ID
            f.write((0).to_bytes(8, 'big', signed=False)) # 0 initially with tree empty
            
            # Write 8 byte next block ID
            f.write((1).to_bytes(8, 'big', signed=False)) # 1 initially with block 0 as header
            
            # Write remaining 488 blocks as 0 for now
            f.write(b'\x00' * (self.BLOCK_SIZE - 24))
        
        # Re-open file in read/write binary mode
        self.file = open(self.filename, 'r+b')
        self.root_id = 0
        self.next_block_id = 1
        
    def open_file(self):
        # Open existing file, verify magic number, read header
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Error: File '{self.filename}' does not exist.")
        
        self.file = open(self.filename, 'r+b')
        
        # Read first 8 bytes/verify magic number
        magic = self.file.read(8)
        if magic != self.MAGIC_NUMBER:
            self.file.close()  # Close file if we don't see a valid idx match
            raise ValueError("Error: File is not a valid index file (magic number mismatch).")
        
        # Read root id and next block id
        self.root_id = int.from_bytes(self.file.read(8), 'big', signed=False)
        self.next_block_id = int.from_bytes(self.file.read(8), 'big', signed=False)
        