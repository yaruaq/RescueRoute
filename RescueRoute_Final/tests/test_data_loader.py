import os
import tempfile
import unittest

from data_loader import (
    load_and_validate_donations,
    load_and_validate_recipients,
    load_and_validate_volunteers,
    check_compatibility,
)


class TestRescueRouteDataAndMatching(unittest.TestCase):

    def setUp(self):
        self.donation = {
            "donation_id": "D-1001",
            "donor_name": "Trader Joes",
            "food_type": "produce",
            "quantity": 50,
            "shelf_life": 90,
            "pickup_area": "North",
            "ready_time": "10:00",
        }
        self.recipient = {
            "recipient_id": "R-2002",
            "org_name": "Hope Pantry",
            "accepted_food_types": "produce | packaged goods",
            "capacity": 150,
            "area": "South",
            "closing_time": "16:00",
        }
        self.volunteer = {
            "volunteer_id": "V-3001",
            "vehicle_capacity": 60,
            "area": "North",
            "availability": "Available",
            "maximum_pickups": 3,
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def write_temp_file(self, filename, content):
        path = os.path.join(self.temp_dir.name, filename)
        with open(path, "w", encoding="utf-8", newline="") as file:
            file.write(content)
        return path

    def test_normal_matching(self):
        valid, msg = check_compatibility(self.donation, self.recipient, self.volunteer)
        self.assertTrue(valid)
        self.assertEqual(msg, "Valid match!")

    def test_incompatible_food_type(self):
        bad_recipient = self.recipient.copy()
        bad_recipient["accepted_food_types"] = "baked goods | prepared meals"
        valid, msg = check_compatibility(self.donation, bad_recipient, self.volunteer)
        self.assertFalse(valid)
        self.assertIn("food type", msg.lower())

    def test_insufficient_recipient_capacity(self):
        small_recipient = self.recipient.copy()
        small_recipient["capacity"] = 20
        valid, msg = check_compatibility(self.donation, small_recipient, self.volunteer)
        self.assertFalse(valid)
        self.assertIn("recipient capacity", msg.lower())

    def test_insufficient_volunteer_capacity(self):
        small_volunteer = self.volunteer.copy()
        small_volunteer["vehicle_capacity"] = 30
        valid, msg = check_compatibility(self.donation, self.recipient, small_volunteer)
        self.assertFalse(valid)
        self.assertIn("vehicle capacity", msg.lower())

    def test_volunteer_not_available(self):
        busy_volunteer = self.volunteer.copy()
        busy_volunteer["availability"] = "Busy"
        valid, msg = check_compatibility(self.donation, self.recipient, busy_volunteer)
        self.assertFalse(valid)
        self.assertIn("not available", msg.lower())

    def test_expired_donation(self):
        expired_donation = self.donation.copy()
        expired_donation["shelf_life"] = 0
        valid, msg = check_compatibility(expired_donation, self.recipient, self.volunteer)
        self.assertFalse(valid)
        self.assertIn("expired", msg.lower())

    def test_ready_time_after_closing_time(self):
        late_donation = self.donation.copy()
        late_donation["ready_time"] = "17:00"
        valid, msg = check_compatibility(late_donation, self.recipient, self.volunteer)
        self.assertFalse(valid)
        self.assertIn("closes", msg.lower())

    def test_duplicate_donation_id(self):
        content = (
            "donation_id,donor_name,food_type,quantity,shelf_life,pickup_area,ready_time\n"
            "D-1001,Store A,produce,10,60,North,10:00\n"
            "D-1001,Store B,produce,20,60,South,10:30\n"
        )
        path = self.write_temp_file("duplicate_donations.csv", content)
        with self.assertRaisesRegex(ValueError, "Duplicate donation ID"):
            load_and_validate_donations(path)

    def test_nonpositive_donation_quantity(self):
        content = (
            "donation_id,donor_name,food_type,quantity,shelf_life,pickup_area,ready_time\n"
            "D-1001,Store A,produce,0,60,North,10:00\n"
        )
        path = self.write_temp_file("bad_quantity.csv", content)
        with self.assertRaisesRegex(ValueError, "positive quantity"):
            load_and_validate_donations(path)

    def test_invalid_time_value(self):
        content = (
            "donation_id,donor_name,food_type,quantity,shelf_life,pickup_area,ready_time\n"
            "D-1001,Store A,produce,10,60,North,25:90\n"
        )
        path = self.write_temp_file("bad_time.csv", content)
        with self.assertRaisesRegex(ValueError, "invalid ready_time"):
            load_and_validate_donations(path)

    def test_empty_input_files(self):
        empty_donations = self.write_temp_file("empty_donations.csv", "")
        empty_recipients = self.write_temp_file("empty_recipients.csv", "")
        empty_volunteers = self.write_temp_file("empty_volunteers.csv", "")

        self.assertEqual(load_and_validate_donations(empty_donations), {})
        self.assertEqual(load_and_validate_recipients(empty_recipients), {})
        self.assertEqual(load_and_validate_volunteers(empty_volunteers), {})

    def test_two_donations_competing_for_recipient_capacity(self):
        first_donation = self.donation.copy()
        first_donation["quantity"] = 100
        second_donation = self.donation.copy()
        second_donation["quantity"] = 80
        recipient = self.recipient.copy()
        recipient["capacity"] = 150
        volunteer = self.volunteer.copy()
        volunteer["vehicle_capacity"] = 120

        first_valid, _ = check_compatibility(first_donation, recipient, volunteer)
        self.assertTrue(first_valid)

        recipient["capacity"] -= first_donation["quantity"]
        second_valid, msg = check_compatibility(second_donation, recipient, volunteer)
        self.assertFalse(second_valid)
        self.assertIn("recipient capacity", msg.lower())


if __name__ == "__main__":
    unittest.main()
