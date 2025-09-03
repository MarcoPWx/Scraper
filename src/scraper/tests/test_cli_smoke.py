import unittest

class TestCLISmoke(unittest.TestCase):
    def test_cli_build_parser(self):
        from scraper.cli import build_parser
        parser = build_parser()
        self.assertIsNotNone(parser)

    def test_cli_help_contains_commands(self):
        from scraper.cli import build_parser
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("harvest", help_text)
        self.assertIn("export", help_text)

if __name__ == "__main__":
    unittest.main()

