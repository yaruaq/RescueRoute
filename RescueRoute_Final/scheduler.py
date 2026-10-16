"""FIFO and Greedy scheduling rules for RescueRoute."""

from copy import deepcopy

from data_loader import check_compatibility


def _records(records):
    """Accept either a dictionary returned by data_loader or a list."""
    return list(records.values()) if isinstance(records, dict) else list(records)


def _try_assign(donation, recipients, volunteers):
    """Return an assignment and update remaining capacity/pickup counts."""
    for recipient in recipients:
        for volunteer in volunteers:
            valid, reason = check_compatibility(donation, recipient, volunteer)
            if not valid:
                continue

            recipient["capacity"] -= donation["quantity"]
            volunteer["maximum_pickups"] -= 1
            return {
                "donation_id": donation["donation_id"],
                "recipient_id": recipient["recipient_id"],
                "volunteer_id": volunteer["volunteer_id"],
                "food_type": donation["food_type"],
                "quantity": donation["quantity"],
                "shelf_life": donation["shelf_life"],
                "reason": "Compatible recipient and available volunteer found.",
            }
    return None


def _schedule(donations, recipients, volunteers, sort_key):
    recipients = deepcopy(_records(recipients))
    volunteers = deepcopy(_records(volunteers))
    ordered = sorted(_records(donations), key=sort_key)
    assignments, unmatched = [], []

    for donation in ordered:
        assignment = _try_assign(donation, recipients, volunteers)
        if assignment:
            assignments.append(assignment)
        else:
            unmatched.append({
                "donation_id": donation["donation_id"],
                "reason": "No compatible recipient and volunteer were available.",
            })
    return assignments, unmatched


def fifo_rule(donations, recipients, volunteers):
    """Process donations in ready/arrival time order."""
    return _schedule(
        donations, recipients, volunteers,
        lambda d: (d["ready_time"], d["donation_id"]),
    )


def greedy_rule(donations, recipients, volunteers):
    """Process the most urgent donations first (lowest shelf life)."""
    return _schedule(
        donations, recipients, volunteers,
        lambda d: (d["shelf_life"], d["ready_time"], d["donation_id"]),
    )
