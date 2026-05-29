"""Test for myworld.py - verifies output has exactly one extra '!' from original (now 26)."""
import subprocess
import sys
import unittest


class TestMyWorld(unittest.TestCase):

    def test_output_has_26_exclamations(self):
        """The output should contain exactly 26 '!' characters (one more than the original 25)."""
        result = subprocess.run(
            [sys.executable, 'myworld.py'],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        self.assertEqual(output.count('!'), 26,
                         f"Expected 26 '!', got {output.count('!')}")

    def test_output_message(self):
        """The base message should be 'Welcome to My World' followed by 26 '!'."""
        result = subprocess.run(
            [sys.executable, 'myworld.py'],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        expected = "Welcome to My World" + "!" * 26
        self.assertEqual(output, expected,
                         f"Expected '{expected}', got '{output}'")


if __name__ == '__main__':
    unittest.main()
