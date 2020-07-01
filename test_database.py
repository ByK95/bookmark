import os
import unittest
from unittest.mock import MagicMock , Mock , call
from unittest.mock import create_autospec
from db import db, datab, db_decorator, save_data, insert_book_db, load_books, load_prefs, insert_pref_db, mark_finished, insert_pin, load_pins
from interfaces import Book, Preference
datab = Mock()

class TestDB(unittest.TestCase):
    def init_test_db(self):
        if hasattr(self,"testDb"):
            return self.testDb
        testDb = db
        testDb.db_name = "test.db"
        setattr(self,"testDb",testDb())
        return self.testDb

    def test_db_creation(self):
        # cleanup before running tests
        self.clean_up("test.db")

        tdb = self.init_test_db()
        self.assertEqual(os.path.exists(tdb.db_name),True,"Should create database if the isnt any")

    def test_decorator(self):
        datab = Mock()
        datab.connect = Mock(return_value = Mock(return_value="hello friend"))
        @db_decorator(datab)
        def test(conn,text):
            return conn(text)
        
        self.assertEqual(test("") ,"hello friend" ,"Should execute code on mock" ) 

    def test_insert_book(self):
        a = Book(name = 'test', path = 'test', page = 0)
        insert_book_db([a])
        books = load_books()
        self.assertEqual(books[0].name, a.name, "Should be returned from database")
        self.assertEqual(books[0].path, a.path, "Should be returned from database")
        self.assertEqual(int(books[0].page), a.page, "Should be returned from database")
        

    def test_insert_books(self):
        a = Book(name = 'books1', path = 'test', page = 0)
        b = Book(name = 'books2', path = 'test', page = 0)
        insert_book_db([a,b])
        books = load_books()
        self.assertEqual( len(books) ,3,"Should be returned from database")

    def test_pref_rw(self):
        a = Preference(name="tpref", style="None", zoom = -2)
        insert_pref_db(a)
        prefs = load_prefs()
        self.assertEqual(a in prefs ,True, "Should be in returned list")

    def test_mark_finished(self):
        book = load_books()[0]
        mark_finished(book.name)
        books = load_books()
        self.assertEqual(book in books, False, "Should not be in list")

    def test_z_insert_pin(self):
        bookname = 'books1'
        page = 44
        text = 'hello world example'
        insert_pin(bookname, page, text)
    
    def test_zz_pins(self):
        bookname = 'books1'
        pins = load_pins(bookname)
        self.assertEqual(len(pins) > 0, True, "Should be more than 0")

    def clean_up(self, filename):
        if os.path.exists(filename):
            os.remove(filename)


if __name__ == "__main__":
    unittest.main()