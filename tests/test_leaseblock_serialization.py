from django.test import TestCase
from scenarios.models import LeaseBlock, LeaseBlockSelection

class TestScenario(TestCase):
    fixtures = ['leaseblock_selections']

    def test_nonulls(self):
        good = LeaseBlockSelection.objects.get(id=2)
        sa = good.serialize_attributes()
        self.assertEqual(sa['report_values']['distance-to-substation']['min'],
                         63.0)

    def test_nulls(self):
        bad = LeaseBlockSelection.objects.get(id=1)
        # in pre-refactored code, this would raise a TypeError
        sa = bad.serialize_attributes()
        self.assertEqual(sa['report_values']['distance-to-substation']['min'],
                         "Unknown")
