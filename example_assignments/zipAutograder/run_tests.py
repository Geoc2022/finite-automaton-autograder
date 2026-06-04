import unittest
from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner


# do not change
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("tests")
    results_file = "/autograder/results/results.json"
    with open(results_file, "w") as f:
        JSONTestRunner(visibility="visible", stream=f).run(suite)
