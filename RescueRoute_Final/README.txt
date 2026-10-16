RescueRoute

RescueRoute is a food donation scheduling project. It matches food donations with organizations that can accept the food and volunteers who can deliver it.

The project uses three CSV files. donations.csv has the food donations. recipients.csv has the organizations that need food. volunteers.csv has the volunteers and their vehicle capacity.

Before making a match, the program checks if the food type is accepted, if the recipient has enough capacity, and if the volunteer is available and has enough vehicle capacity. It also checks the pickup limit and closing time.

There are two scheduling methods. FIFO handles the donation that is ready first. Greedy handles the donation with the shortest shelf life first. This helps give priority to food that may expire sooner.

How to run the project:

1. Open Terminal in this folder.
2. Run this command:

python3 main.py

The program will show the FIFO and Greedy results. It will show the assignments, donations that could not be matched, and the final metrics.

To run the tests, use this command:

python3 -m unittest discover -s tests -v

Project files:

data folder: the CSV files.
data_loader.py: reads and checks the data.
scheduler.py: FIFO and Greedy scheduling.
metrics.py: calculates the final results.
main.py: runs the project.
tests folder: automated tests for the program.
