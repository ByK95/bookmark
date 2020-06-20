import unittest
from unittest.mock import MagicMock , Mock , call
from unittest.mock import create_autospec
from bookmark import JsCmdMapper , fs , render_html_page , BookmarkApp
from interfaces import Preference

class TestJsCmdMapper(unittest.TestCase):

    def driver_mock(self, executeScript):
        mock = Mock()
        mock.execute_script = Mock(return_value = executeScript)
        return mock


    def test_unlock(self):
        msg = "On unlock JsCmdMapper should run script in browser"
        driver = self.driver_mock("script")
        mapper = JsCmdMapper(driver)
        self.assertEqual(mapper.unlock(),"script",msg)

    def test_process(self):
        msg = "On proces JsCmdMapper should run user defined function"
        mapper = JsCmdMapper(None)
        cmd = Mock()
        test = Mock()
        mapper.maps = {'cmd':cmd,'test':test}
        mapper.process(["cmd/param","test/param,param2"])

        self.assertEqual(cmd.call_count,1,msg)
        self.assertEqual(test.call_count,1,msg)

        self.assertEqual(cmd.call_args_list,[call("param")],msg)
        self.assertEqual(test.call_args_list,[call("param,param2")],msg)

    def test_process_none(self):
        msg = "On proces JsCmdMapper should run user defined function"
        mapper = JsCmdMapper(None)
        cmd = Mock()
        test = Mock()
        mapper.maps = {'cmd':cmd}
        mapper.process(["cmd/"])

        self.assertEqual(cmd.call_count,1,msg)
        self.assertEqual(cmd.call_args_list,[call()],msg)

    def test_update(self):
        driver = self.driver_mock(["hello"])
        mapper = JsCmdMapper(driver)
        mapper.process = Mock()
        mapper.unlock = Mock()
        
        mapper.update()

        self.assertEqual(mapper.process.call_count,1,"should process data")
        self.assertEqual(mapper.unlock.call_count,1,"should run unlock function")

class TestApp(unittest.TestCase):

    def test_fs(self):
        self.assertEqual(fs("real_path","file"),"real_path\\file")

    def test_render(self):
        self.assertEqual(render_html_page(),0)

    def test_inject_neg_zoom(self):
        app = BookmarkApp()
        app.driver = Mock()
        app.driver.execute_script = Mock()

        pref = Preference(name="test", style="None", zoom = -2)
        app.inject(pref)
        callstack = [
            call('document.getElementById("None").click()'),
            call('document.getElementById("zoomOut").click()'),
            call('document.getElementById("zoomOut").click()')
                        ]
        self.assertEqual(app.driver.execute_script.call_args_list, callstack)

    def test_inject_pos_zoom(self):
        app = BookmarkApp()
        app.driver = Mock()
        app.driver.execute_script = Mock()
        pref = Preference(name="test", style="None", zoom = 2)
        app.inject(pref)
        callstack = [
            call('document.getElementById("None").click()'),
            call('document.getElementById("zoomIn").click()'),
            call('document.getElementById("zoomIn").click()')
                        ]
        self.assertEqual(app.driver.execute_script.call_args_list, callstack)

    def test_landing_url(self):
        app = BookmarkApp()
        self.assertEqual(app.landing_url, "file:///D:/no-code_no-life/bookmark/index.html")



if __name__ == '__main__':
    unittest.main()