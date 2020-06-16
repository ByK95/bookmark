import unittest
from unittest.mock import MagicMock , Mock , call
from unittest.mock import create_autospec
from interfaces import *

class TestBook(unittest.TestCase):

    def test_init(self):
        a = Book(name="hello",path="friend")
        self.assertEqual(a.name , "hello")
        self.assertEqual(a.path , "friend")