5/7, 5:16PM
After working on the initial planning diagrams I have a working idea of the general flow/process I want to follow.  I'll likely attach the diagrams I've made if I follow the structure throughout the coding process.  Even if not they'll be a good representation of my initial thought process.

General flow:
Parse command line arg
    Check if command valid
Check cmd type
Open index file
Execute cmd
BTree Request NodeID
Check node in memory
    If Yes, move to MRU & Return node
    If not continue
    Check if 3 nodes in memory
        Yes, evict LRU node
        Check if evicted node modified?
            Yes, write evicted node to disk
            No, Read requested node from disk
        If 3 nodes not in mem
        Read requested node from disk
    Add node to memory dictionary & return
BTree processes node
Check if cmd finished
    Yes, flush buffer and exit
    No, loop back to BTree request NodeID


5/8 1:00AM
Getting started on the classes for the program, will be splitting into multiple files for organization.
Starting first with indexfilemanager which will act as the class responsible for handling raw byte manipulation and disk I/O.

Vars:
filename (string), file_pointer (File), root_id (int), next_block_id (int)

Methods:
create_new_file
open_file
read_header
write_header
read_node
write_node


1:30 AM
Continuing to write the idxfilemanager class
Got through the create and open file methods
Not too sure how to test them until everything is built.

Made some adjustments to the class structure, added a proper close method
Changed the variables root_id and next_block_id from vars to have proper getter/setter methods instead.  I'm hoping enforcing more encapsulation of these pieces will help insulate me from bugs later on but I might be wrong.
    I'm sure there'll be some typo that destroys my machine


2:46 AM
Got started on Btree node class, wanted to initialize constants and the is_leaf method.