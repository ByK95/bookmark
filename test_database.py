import unittest
from unittest.mock import MagicMock , Mock , call
from unittest.mock import create_autospec
from db import db, db_decorator
import os

datab = Mock()

class TestDB(unittest.TestCase):

    def test_db_creation(self):
        testDb = db
        testDb.db_name = "test.db"
        tdb = testDb()
        
        self.assertEqual(os.path.exists(tdb.db_name),True,"Should create database if the isnt any")
        self.clean_up(tdb.db_name)

    def test_decorator(self):
        datab = Mock()
        datab.connect = Mock(return_value = Mock(return_value="hello friend"))
        @db_decorator(datab)
        def test(conn,text):
            return conn(text)
        
        self.assertEqual(test("") ,"hello friend" ,"Should execute code on mock" ) 


    def clean_up(self, filename):
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == "__main__":
    unittest.main()