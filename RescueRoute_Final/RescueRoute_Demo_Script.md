# RescueRoute Demo Script

1. Open the RescueRoute project folder.
2. Run `python3 main.py`.
3. Say: "The application loads the donation, recipient, and volunteer CSV files and validates the data."
4. Say: "FIFO processes donations by ready time. Greedy processes the shortest shelf-life donation first."
5. Point to the result: 4 donations were processed, 3 were assigned, 1 was unmatched, and 130 items were assigned.
6. Say: "The unmatched donation has no available compatible match after capacity and pickup limits are considered."
7. Run `python3 -m unittest discover -s tests -v`.
8. Say: "All 16 automated tests pass, including validation, compatibility, scheduling, integration, and metrics tests."
