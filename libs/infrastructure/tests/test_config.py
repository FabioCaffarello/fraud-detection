import unittest

from infra.config import Settings


class TestSettings(unittest.TestCase):
    def test_default_settings(self):
        settings = Settings()
        self.assertEqual(settings.log_level, "INFO")
        self.assertFalse(settings.verbose)
        self.assertFalse(settings.debug)
        self.assertEqual(settings.kafka_bootstrap_servers, "localhost:9092")
        self.assertIsNone(settings.kafka_username)
        self.assertIsNone(settings.kafka_password)

    def test_valid_log_level_case_insensitive(self):
        settings = Settings(log_level="debug")
        self.assertEqual(settings.log_level, "DEBUG")

        settings = Settings(log_level="Warning")
        self.assertEqual(settings.log_level, "WARNING")

        settings = Settings(log_level="error")
        self.assertEqual(settings.log_level, "ERROR")

        settings = Settings(log_level="CRITICAL")
        self.assertEqual(settings.log_level, "CRITICAL")

    def test_invalid_log_level(self):
        with self.assertRaises(ValueError) as context:
            Settings(log_level="invalid")
        self.assertIn("Invalid log level", str(context.exception))


if __name__ == "__main__":
    unittest.main()
