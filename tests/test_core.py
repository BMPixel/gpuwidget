from unittest.mock import MagicMock, patch

from gpuwidget.core import live, once


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
