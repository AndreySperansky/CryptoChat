import unittest


class MyClass(object):
    def __init__(self, foo):
        if foo != 0:
            raise ValueError("foo is not equal to 1!")


class MyClass2(object):
    def __init__(self):
        pass


class TestFoo(unittest.TestCase):
    def testInsufficientArgs(self):
        foo = 1
        self.assertRaises(ValueError, MyClass, foo)

    def testArgs(self):
        self.assertRaises(TypeError, MyClass2, ("fsa", "fds"))


if __name__ == '__main__':
    unittest.main()