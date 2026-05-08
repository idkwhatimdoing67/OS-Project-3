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
    
    def update_header(self):
        # Write current root id and next block id to block 0
        if not self.file:
            raise IOError("File is not open.")
        
        # Seek to byte 8
        # This will skip 8 bytes, we need to skip the Magic Number
        self.file.seek(8) 
        self.file.write(self.root_id.to_bytes(8, 'big', signed=False))
        self.file.write(self.next_block_id.to_bytes(8, 'big', signed=False))
        
    def get_new_block_id(self):
        # Return next available block id, will also increment counter
        new_id = self.next_block_id
        self.next_block_id += 1
        self.update_header() # Commits increment to disk
        return new_id
    
    def set_root_id(self, new_root_id):
        # Updates root id in memory; saves it to header block
        self.root_id = new_root_id
        self.update_header()
    
    def read_block(self, block_id):
        # Read and return raw 512 byte block from disk
        if not self.file:
            raise IOError("File isn't open")
        
        self.file.seek(block_id * self.BLOCK_SIZE)
        data = self.file.read(self.BLOCK_SIZE)
        
        if len(data) != self.BLOCK_SIZE:
            data = data.ljust(self.BLOCK_SIZE, b'\x00')
            # Check in case file end is reached prematurely
        
        return data
    
    def write_block(self, block_id, data):
        # Write 512 bytes to block id input
        if not self.file:
            raise IOError("File is not open.")
        if len(data) != self.BLOCK_SIZE:
            raise ValueError(f"Error: Data block must be exactly {self.BLOCK_SIZE} bytes.")
        
        self.file.seek(block_id * self.BLOCK_SIZE)
        self.file.write(data)
        
    def close(self):
        # Closes file pointer
        if self.file:
            self.update_header()
            self.file.close()
            self.file = None