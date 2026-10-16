import csv
from datetime import datetime


def _get_reader(file, filepath, required_fields):
    """Return a CSV reader and check that required columns exist."""
    reader = csv.DictReader(file)

    if reader.fieldnames is None:
        return None

    missing_columns = [field for field in required_fields if field not in reader.fieldnames]
    if missing_columns:
        raise ValueError(f"{filepath} is missing required columns: {', '.join(missing_columns)}")

    return reader


def _check_row(row, required_fields, record_type):
    """Remove extra spaces and check that required values are present."""
    row = {key: value.strip() if value is not None else "" for key, value in row.items()}
    missing_fields = [field for field in required_fields if not row.get(field)]

    if missing_fields:
        raise ValueError(f"{record_type} is missing required fields: {', '.join(missing_fields)}")

    return row


def _valid_time(value):
    """Check that a time uses the HH:MM format."""
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False


#  Load and validate donations

def load_and_validate_donations(filepath):
    required_fields = [
        "donation_id", "donor_name", "food_type", "quantity",
        "shelf_life", "pickup_area", "ready_time"
    ]
    seen_ids = set()
    donations_dict = {}

    with open(filepath, mode="r", encoding="utf-8", newline="") as file:
        reader = _get_reader(file, filepath, required_fields)
        if reader is None:
            return donations_dict

        for row in reader:
            row = _check_row(row, required_fields, "Donation")
            d_id = row["donation_id"]

            if d_id in seen_ids:
                raise ValueError(f"Duplicate donation ID detected: {d_id}")
            seen_ids.add(d_id)

            try:
                row["quantity"] = int(row["quantity"])
                row["shelf_life"] = int(row["shelf_life"])
            except ValueError:
                raise ValueError(f"Donation {d_id} quantity and shelf_life must be integers.")

            if row["quantity"] <= 0:
                raise ValueError(f"Donation {d_id} must have a positive quantity.")
            if row["shelf_life"] < 0:
                raise ValueError(f"Donation {d_id} cannot have negative shelf life.")
            if not row["food_type"].strip():
                raise ValueError(f"Donation {d_id} must have a food type.")
            if not _valid_time(row["ready_time"]):
                raise ValueError(f"Donation {d_id} has an invalid ready_time. Use HH:MM.")

            donations_dict[d_id] = row

    return donations_dict


#  Load and validate recipients

def load_and_validate_recipients(filepath):
    required_fields = [
        "recipient_id", "org_name", "accepted_food_types",
        "capacity", "area", "closing_time"
    ]
    seen_ids = set()
    recipients_dict = {}

    with open(filepath, mode="r", encoding="utf-8", newline="") as file:
        reader = _get_reader(file, filepath, required_fields)
        if reader is None:
            return recipients_dict

        for row in reader:
            row = _check_row(row, required_fields, "Recipient")
            r_id = row["recipient_id"]

            if r_id in seen_ids:
                raise ValueError(f"Duplicate recipient ID detected: {r_id}")
            seen_ids.add(r_id)

            try:
                row["capacity"] = int(row["capacity"])
            except ValueError:
                raise ValueError(f"Recipient {r_id} capacity must be an integer.")

            if row["capacity"] < 0:
                raise ValueError(f"Recipient {r_id} cannot have negative capacity.")
            if not _valid_time(row["closing_time"]):
                raise ValueError(f"Recipient {r_id} has an invalid closing_time. Use HH:MM.")

            recipients_dict[r_id] = row

    return recipients_dict


#  Load and validate volunteers

def load_and_validate_volunteers(filepath):
    required_fields = [
        "volunteer_id", "vehicle_capacity", "area",
        "availability", "maximum_pickups"
    ]
    seen_ids = set()
    volunteers_dict = {}

    with open(filepath, mode="r", encoding="utf-8", newline="") as file:
        reader = _get_reader(file, filepath, required_fields)
        if reader is None:
            return volunteers_dict

        for row in reader:
            row = _check_row(row, required_fields, "Volunteer")
            v_id = row["volunteer_id"]

            if v_id in seen_ids:
                raise ValueError(f"Duplicate volunteer ID detected: {v_id}")
            seen_ids.add(v_id)

            try:
                row["vehicle_capacity"] = int(row["vehicle_capacity"])
                row["maximum_pickups"] = int(row["maximum_pickups"])
            except ValueError:
                raise ValueError(f"Volunteer {v_id} capacities and maximum_pickups must be integers.")

            if row["vehicle_capacity"] < 0:
                raise ValueError(f"Volunteer {v_id} cannot have negative vehicle capacity.")
            if row["maximum_pickups"] < 0:
                raise ValueError(f"Volunteer {v_id} cannot have negative maximum_pickups.")
            if row["availability"].lower() not in ("available", "busy"):
                raise ValueError(f"Volunteer {v_id} availability must be Available or Busy.")

            volunteers_dict[v_id] = row

    return volunteers_dict


# Checks compatibility

def check_compatibility(donation, recipient, volunteer):
    if donation["shelf_life"] <= 0:
        return False, "Donation has expired."

    accepted_types = {
        food_type.strip().lower()
        for food_type in recipient["accepted_food_types"].split("|")
        if food_type.strip()
    }

    if donation["food_type"].strip().lower() not in accepted_types:
        return False, "Recipient does not accept this food type."

    if recipient["capacity"] < donation["quantity"]:
        return False, "Recipient capacity is too small for this donation."

    if volunteer["vehicle_capacity"] < donation["quantity"]:
        return False, "Volunteer vehicle capacity is too small for this donation."

    if volunteer["availability"].strip().lower() != "available":
        return False, "Volunteer is currently not available."

    if volunteer["maximum_pickups"] == 0:
        return False, "Volunteer cannot take any pickups."

    if donation["ready_time"] >= recipient["closing_time"]:
        return False, "Donation is not ready before the recipient closes."

    return True, "Valid match!"


# Demonstration
if __name__ == "__main__":
    print("--- RescueRoute Data Loader & Matching Test ---")

    recipients = load_and_validate_recipients("recipients.csv")
    volunteers = load_and_validate_volunteers("volunteers.csv")
    donations = load_and_validate_donations("donations.csv")

    print(
        f"Successfully loaded {len(donations)} donations, "
        f"{len(recipients)} recipients, and {len(volunteers)} volunteers."
    )

    # Test sample match
    d = donations["D-1001"]
    r = recipients["R-2002"]
    v = volunteers["V-3001"]
    valid, msg = check_compatibility(d, r, v)
    print(f"Compatibility Check (D-1001 with R-2002 & V-3001): {valid} - {msg}")
