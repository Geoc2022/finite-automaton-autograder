import unittest
from gradescope_utils.autograder_utils.decorators import partial_credit
from gradescope_utils.autograder_utils.files import check_submitted_files


class TestFiles(unittest.TestCase):
    @partial_credit(0)
    def test_submitted_files(self, set_score=0):
        """Check submitted files"""
        missing_files = check_submitted_files(["sol1.json", "sol2a.json", "sol2b.json"])
        for path in missing_files:
            set_score(-1)
            print("Missing {0}".format(path))
        self.assertEqual(len(missing_files), 0, "Missing some required files!")
        print("All required files submitted!")
