import unittest
from GaugiKernel.Configurable import Configurable


class MockSingleArg:
    def __init__(self, name):
        self.name = name
        self._properties = []

    def getProperties(self):
        return self._properties

    def hasProperty(self, name):
        return name in self._properties


class MockDefaultConstructor:
    def __init__(self):
        self.name = "default"
        self._properties = []

    def getProperties(self):
        return self._properties

    def hasProperty(self, name):
        return name in self._properties


class MockMultiArgs:
    def __init__(self, name, arg1, arg2):
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2
        self._properties = ["OutputFile"]
        self.OutputFile = "output.root"

    def getProperties(self):
        return self._properties

    def hasProperty(self, name):
        return name in self._properties

    def setProperty(self, name, value):
        setattr(self, name, value)


class TestConfigurable(unittest.TestCase):
    """Unit tests for GaugiKernel Configurable with single, zero, and multi-argument constructors."""

    def test_single_arg_constructor(self):
        c = Configurable(MockSingleArg, "test_single")
        self.assertEqual(c.c_ptr().name, "test_single")

    def test_default_constructor(self):
        c = Configurable(MockDefaultConstructor, "test_default")
        self.assertEqual(c.c_ptr().name, "default")

    def test_multi_args_constructor(self):
        c = Configurable(MockMultiArgs, "test_multi", 123, "custom_str", OutputFile="custom.root")
        self.assertEqual(c.c_ptr().name, "test_multi")
        self.assertEqual(c.c_ptr().arg1, 123)
        self.assertEqual(c.c_ptr().arg2, "custom_str")
        self.assertEqual(c.c_ptr().OutputFile, "custom.root")

    def test_multi_args_with_configurable_arg(self):
        # Nested configurable passed as positional argument
        inner = Configurable(MockSingleArg, "inner")
        c = Configurable(MockMultiArgs, "outer", inner, 456)
        # Should unwrap inner.c_ptr()
        self.assertEqual(c.c_ptr().arg1, inner.c_ptr())
        self.assertEqual(c.c_ptr().arg2, 456)


if __name__ == "__main__":
    unittest.main()
