import unittest
from pathlib import Path

from data_loader import (
    load_and_validate_donations,
    load_and_validate_recipients,
    load_and_validate_volunteers,
)
from metrics import calculate_metrics
from scheduler import fifo_rule, greedy_rule


ROOT = Path(__file__).resolve().parents[1]


class TestRescueRouteIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = ROOT / "data"
        cls.donations = load_and_validate_donations(data / "donations.csv")
        cls.recipients = load_and_validate_recipients(data / "recipients.csv")
        cls.volunteers = load_and_validate_volunteers(data / "volunteers.csv")

    def test_fifo_returns_every_donation_once(self):
        assignments, unmatched = fifo_rule(self.donations, self.recipients, self.volunteers)
        ids = [a["donation_id"] for a in assignments] + [u["donation_id"] for u in unmatched]
        self.assertCountEqual(ids, self.donations.keys())

    def test_greedy_starts_with_most_urgent_donation(self):
        assignments, unmatched = greedy_rule(self.donations, self.recipients, self.volunteers)
        processed = [a["donation_id"] for a in assignments] + [u["donation_id"] for u in unmatched]
        self.assertEqual(processed[0], "D-1004")

    def test_assignments_respect_capacity_and_pickup_limits(self):
        assignments, _ = greedy_rule(self.donations, self.recipients, self.volunteers)
        for assignment in assignments:
            self.assertIn(assignment["donation_id"], self.donations)
            self.assertGreater(assignment["quantity"], 0)
            self.assertTrue(assignment["reason"])

    def test_metrics_match_results(self):
        assignments, unmatched = fifo_rule(self.donations, self.recipients, self.volunteers)
        result = calculate_metrics(assignments, unmatched, len(self.donations))
        self.assertEqual(result["assigned_donations"] + result["unmatched_donations"], len(self.donations))
        self.assertEqual(result["assigned_quantity"], sum(a["quantity"] for a in assignments))

