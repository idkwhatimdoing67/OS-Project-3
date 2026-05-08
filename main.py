import sys
import os

# Custom classes
from indexfilemanager import IndexFileManager
from buffermanager import BufferManager
from btree import BTree

def print_usage_and_exit():
    # Print valid commands and exit program
    # Useful for debugging as we need to track what the program is doing
    print("Invalid command or arguments. Valid commands are:")
    print("  create <index_file>")
    print("  insert <index_file> <key> <value>")
    print("  search <index_file> <key>")
    print("  load <index_file> <csv_file>")
    print("  print <index_file>")
    print("  extract <index_file> <csv_file>")
    sys.exit(1)


def main():
    # Need 3 argv
    if len(sys.argv) < 3:
        print_usage_and_exit()
    
    # All cmds should be lowercase
    command = sys.argv[1].lower()
    index_file = sys.argv[2]
    
    #Instantiate disk manager
    file_manager = IndexFileManager(index_file)
    
    # Create CMD
    if command == "create":
        # First arg after create is index file name
        try:
            # If file already exists, fail with error msg
            file_manager.create_new_file()
            print(f"Success: Index file '{index_file}' created.")
        except Exception as e:
            print(e)
            sys.exist(1)
        finally:
            file_manager.close()
        return
    
    # All other cmds, these actually require opening of file
    try:
        # If file doesn't exist or invalid then exit
        file_manager.open_file()
    except Exception as e:
        print(e)
        sys.exit(1)
    
    #Initialize memory and logic
    buffer_manager = BufferManager(file_manager, max_nodes=3)
    btree = BTree(buffer_manager)
    
    try:
        if command == "insert":
            if len(sys.argv) != 5:
                print_usage_and_exit
            
            try:
                key = int(sys.argv[3])
                value = int(sys.argv[4])
                if key < 0 or value < 0:
                    raise ValueError("Keys and values must be positive integers")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            
            btree.insert(key,value)
            print(f"Inserted key {key} with value {value}.")
        
        elif command == "search":
            if len(sys.argv) != 4:
                print_usage_and_exit()
            try:
                key = int(sys.argv[3])
            except ValueError:
                print("Error: Key must be an integer.")
                sys.exit(1)
            
            # Search index for key
            result = btree.search(key)
            if result:
                # If found, print key/value pair
                print(f"FoundL Key={result[0]}, Value={result[1]}")
            else:
                # Else, print error msg
                print(f"Error: Key {key} not found in the index.")
            
        elif command == "load":
            if len(sys.argv) != 4:
                print_usage_and_exit()
            csv_file = sys.argv[3]
            try:
                btree.load_from_csv(csv_file)
                print(f"Successfully loaded data from {csv_file}.")
            except Exception as e:
                print(e)
                sys.exit(1)
                
        elif command == "print":
            if len(sys.argv) != 3:
                print_usage_and_exit()
            # Print every key/value pair
            btree.print_tree()
            
        elif command == "extract":
            if len(sys.argv) != 4:
                print_usage_and_exit()
            csv_file = sys.argv[3]
            try:
                # Save all key/value pair in index to file
                btree.extract_to_csv(csv_file)
                print(f"Successfully extracted data to {csv_file}.")
            except Exception as e:
                print(e)
                sys.exit(1)
        
        else:
            print_usage_and_exit()
        
    finally:
        # No matter success or crash we push any nodes left in memory to disk and release file lock
        buffer_manager.flush_all()
        file_manager.close()
    

if __name__ == "__main__":
    main()