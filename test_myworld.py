"""Test for myworld.py - verifies output has exactly one extra '!' from previous."""
import subprocess
import sys
import unittest


class TestMyWorld(unittest.TestCase):

    def test_output_has_27_exclamations(self):
        """The output should contain exactly 27 '!' characters (one more than the previous 26)."""
        result = subprocess.run(
            [sys.executable, 'myworld.py'],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        self.assertEqual(output.count('!'), 27,
                         f"Expected 27 '!', got {output.count('!')}")

    def test_output_message(self):
        """The base message should be 'Welcome to My World' followed by 27 '!'."""
        result = subprocess.run(
            [sys.executable, 'myworld.py'],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        expected = "Welcome to My World" + "!" * 27
        self.assertEqual(output, expected,
                         f"Expected '{expected}', got '{output}'")


if __name__ == '__main__':
    unittest.main()
