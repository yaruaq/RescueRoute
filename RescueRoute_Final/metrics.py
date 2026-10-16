


def calculate_metrics(assignments, unmatched, total_donations):
    assigned_quantity = sum(item["quantity"] for item in assignments)
    urgent_assignments = sum(item["shelf_life"] <= 60 for item in assignments)
    return {
        "total_donations": total_donations,
        "assigned_donations": len(assignments),
        "unmatched_donations": len(unmatched),
        "assigned_quantity": assigned_quantity,
        "urgent_donations_saved": urgent_assignments,
        "assignment_rate": round(len(assignments) / total_donations * 100, 1)
        if total_donations else 0.0,
    }


def print_metrics(name, metrics):
    print(f"\n{name}")
    for label, value in metrics.items():
        print(f"  {label.replace('_', ' ').title()}: {value}")
