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


1:00 PM
Wrote in pack_to_bytes, the full class plan I have for BTree Node will be:
init
is_leaf
pack_to_bytes
unpack_from_bytes

This way the node can ideally just exist to work with the disk by packing/unpacking and we can focus on core functionality in BTree class proper.

2:00 PM
Begin writing the buffermanager class
The goal will be to create methods to work on the lower level than the btree.  I'm thinking of it on a conceptual level where we have:

BTree
BTreeNode
BufferManager

Where the BTree will be manipulating the Node class which will be directly interacting with the buffer

Methods:
init
getnode
register_new_node
mark_dirty
evict_oldest
flush_all

This should ideally capture all buffer functionality we'll need.

3:03 PM
Finished writing in the logic for the buffermanager class, should have everything needed for proper BTree class now.

BTree class:
Init
get_root
search
search_node (Act as node helper for the search wrapper method)
insert
split_child
insert_non_full
print_tree
extract_to_csv
load_from_csv
in_order_traverse

This will be the largest class and ideally handle the complete functionality that the Btree will need.


3:40 PM
Wrote in the Search logic for the BTree
So far the init, get_root, search, and search_node methods are done.

I'm deciding to split the class conceptually into multiple sections;
I'm targeting these sections:
Search
Insertion
Utility

This will help me stay organized at least in my head when writing them.

I've written the first piece of the insertion logic, my goal is to define the regular insertion and just put the calls to the other "edge" cases into that logic so I can better visualize how it comes together before writing the logic for those methods specifically. 

4:30 PM
I've written the rest of the insertion logic, will begin on the utility logic next.  Hopefully it'll come together but the challenge is that I can't really test much until the program is all fully built.  At least if I can I'm not sure how.

4:50 PM
Alright now the entirety of the btree code is written, all that's needed now will be main.py and putting it all together.  This is where I'll get to dive into more testing and hopefully find it running perfectly.

5:36 PM
I've written in the main driver, the code was written as an elif structure to then fill in logic for each command.  While a separate method was used for error outputting.

I'm going to begin testing and go through the debugging process.



5:40 PM
Initial testing seemed to go well.  I tried a few insertion commands and got a goo search and print output:
PS C:\Users\colin\OneDrive\Documents\GitHub\OS-Project-3> python3 main.py search myindex.idx 10
FoundL Key=10, Value=500
PS C:\Users\colin\OneDrive\Documents\GitHub\OS-Project-3> python3 main.py print myindex.idx
10 500
20 600

