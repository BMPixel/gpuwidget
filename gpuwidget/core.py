from IPython.display import display

from .widgets import GPUStatsApp


def live():
    widget = GPUStatsApp()
    display(widget)


def once():
    widget = GPUStatsApp()
    widget.stop_updating(widget.stop_button)
    display(widget)
