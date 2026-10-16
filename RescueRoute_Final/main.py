from pathlib import Path

from data_loader import (
    load_and_validate_donations,
    load_and_validate_recipients,
    load_and_validate_volunteers,
)
from metrics import calculate_metrics, print_metrics
from scheduler import fifo_rule, greedy_rule


DATA = Path(__file__).parent / "data"


def main():
    donations = load_and_validate_donations(DATA / "donations.csv")
    recipients = load_and_validate_recipients(DATA / "recipients.csv")
    volunteers = load_and_validate_volunteers(DATA / "volunteers.csv")

    fifo_assignments, fifo_unmatched = fifo_rule(donations, recipients, volunteers)
    greedy_assignments, greedy_unmatched = greedy_rule(donations, recipients, volunteers)

    print("RescueRoute scheduling comparison")
    print_metrics("FIFO", calculate_metrics(fifo_assignments, fifo_unmatched, len(donations)))
    print_metrics("Greedy", calculate_metrics(greedy_assignments, greedy_unmatched, len(donations)))

    print("\nGreedy assignments:")
    for assignment in greedy_assignments:
        print(f"  {assignment['donation_id']} -> {assignment['recipient_id']} "
              f"with {assignment['volunteer_id']} ({assignment['reason']})")
    if greedy_unmatched:
        print("\nUnmatched:")
        for item in greedy_unmatched:
            print(f"  {item['donation_id']}: {item['reason']}")


if __name__ == "__main__":
    main()
