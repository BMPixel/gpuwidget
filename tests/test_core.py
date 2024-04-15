from unittest.mock import MagicMock, patch

from gpuwidget.core import is_notebook, live, once


def test_is_notebook():
    with patch("core.get_ipython") as mock_get_ipython:
        # Test case when shell is ZMQInteractiveShell
        mock_get_ipython.return_value.__class__.__name__ = "ZMQInteractiveShell"
        assert is_notebook()

        # Test case when shell is TerminalInteractiveShell
        mock_get_ipython.return_value.__class__.__name__ = "TerminalInteractiveShell"
        assert not is_notebook()

        # Test case when shell is Shell
        mock_get_ipython.return_value.__class__.__name__ = "Shell"
        assert is_notebook()

        # Test case when shell is not any of the above
        mock_get_ipython.return_value.__class__.__name__ = "OtherShell"
        assert not is_notebook()


@patch("gpuwidget.core.is_notebook")
@patch("gpuwidget.core.GPUStatsApp")
def test_live(mock_GPUStatsApp, mock_is_notebook):
    mock_is_notebook.return_value = True
    mock_GPUStatsApp.return_value = MagicMock()
    live()
    mock_GPUStatsApp.assert_called_once()


@patch("gpuwidget.core.live")
def test_once(mock_live):
    once()
    mock_live.assert_called_once_with(stop_immediately=True)
