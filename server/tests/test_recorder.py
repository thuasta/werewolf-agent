"""Tests for Recorder class."""

from recorder.recorder import Recorder


class TestRecorder:
    """Test cases for Recorder class."""

    def test_initialization(self):
        """Test Recorder can be instantiated."""
        recorder = Recorder()
        assert isinstance(recorder, Recorder)
