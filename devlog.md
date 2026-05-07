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