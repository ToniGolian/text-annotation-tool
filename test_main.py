import unittest
import tests.pdf_extraction_tests  # Import the entire test module


def load_tests():
    """
    Dynamically loads all test classes from the specified test modules.
    Modify this method to include or exclude specific test modules.
    """
    # Load all test classes from `pdf_extraction_tests`
    return unittest.defaultTestLoader.loadTestsFromModule(tests.pdf_extraction_tests)


def run_tests():
    """
    Runs all tests loaded by load_tests().
    """
    suite = unittest.TestSuite()
    suite.addTests(load_tests())
    unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
    # Load and run tests
    run_tests()
