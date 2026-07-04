import unittest

from ttr.backends.mymemory import MAX_QUERY_BYTES, MyMemoryBackend
from ttr.errors import BackendError


class MyMemoryTests(unittest.TestCase):
    def test_long_input_errors_before_request(self):
        text = "a" * (MAX_QUERY_BYTES + 1)

        with self.assertRaisesRegex(BackendError, "text too large"):
            MyMemoryBackend().translate(text, "en", "zh")


if __name__ == "__main__":
    unittest.main()

