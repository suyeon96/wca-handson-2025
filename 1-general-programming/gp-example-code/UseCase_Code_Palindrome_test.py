# Assisted by watsonx Code Assistant 
# watsonx Code Assistant did not check whether this code suggestion might be similar to third party code.
import unittest
from UseCase_Code_Palindrome import isPalindrome

class TestPalindrome(unittest.TestCase):
    def test_palindrome(self):
        self.assertTrue(isPalindrome("racecar"))
        self.assertTrue(isPalindrome("level"))
        self.assertFalse(isPalindrome("hello"))
        self.assertTrue(isPalindrome("a"))
        self.assertTrue(isPalindrome("abba"))
        self.assertFalse(isPalindrome("abca"))

if __name__ == '__main__':
    unittest.main()
