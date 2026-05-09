This code is split into multiple files

main.py: Main driver, only file needed to be called when running


How to run:
Type out: python3 main.py cmd <index_file>

Below is a format to help with the commands available
  create <index_file>
  insert <index_file> <key> <value>
  search <index_file> <key>
  load <index_file> <csv_file>
  print <index_file>
  extract <index_file> <csv_file>

Example: python3 main.py extract index.idx output.csv


Class Files:
btree.py
buffermanager.py
indexfilemanager.py

Info files:
devlog.md: Houses the development log and notes on conceptual process
README.txt: Quick explanation file/how to run code

Diagrams:
OS Project3 Flow.drawio.png
OS Project3 UML.drawio.png

These were both made in the original design process, 
while not 1:1 accurate with my final implementation they exist to help inform my conceptual process


Index File:
test.idx: added in from the assignment for testing

