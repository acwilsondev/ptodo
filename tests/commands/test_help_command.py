from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture

from ptodo.app import main


class TestHelpCommand:
    """Tests for the help command functionality of ptodo."""

    @patch("sys.argv")
    def test_help_command(
        self, mock_argv: MagicMock, capsys: CaptureFixture[str]
    ) -> None:
        """Test the help command."""
        mock_argv.__getitem__.side_effect = lambda idx: ["ptodo", "--help"][idx]

        # The main function would typically exit when showing help
        # We catch the SystemExit to continue the test
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()

        # Check for common help text indicators
        assert "usage" in captured.out.lower()
        assert "commands" in captured.out.lower() or "options" in captured.out.lower()

