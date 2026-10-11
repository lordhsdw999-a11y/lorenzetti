import unittest
from GaugiKernel.Logger import Logger, LoggingLevel


class TestLogger(unittest.TestCase):
    """Unit tests for GaugiKernel Logger and LoggingLevel."""

    def test_logging_levels(self):
        self.assertTrue(hasattr(LoggingLevel, "VERBOSE"))
        self.assertTrue(hasattr(LoggingLevel, "DEBUG"))
        self.assertTrue(hasattr(LoggingLevel, "INFO"))
        self.assertTrue(hasattr(LoggingLevel, "WARNING"))
        self.assertTrue(hasattr(LoggingLevel, "ERROR"))
        self.assertTrue(hasattr(LoggingLevel, "FATAL"))

    def test_logger_instantiation(self):
        log = Logger()
        self.assertEqual(log.getLoggerName(), "Logger")
        self.assertEqual(log.getLevel(), LoggingLevel.INFO)

    def test_logger_level_change(self):
        log = Logger()
        log.level = LoggingLevel.DEBUG
        self.assertEqual(log.getLevel(), LoggingLevel.DEBUG)


if __name__ == "__main__":
    unittest.main()
