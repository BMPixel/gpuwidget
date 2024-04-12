import gpustat
from IPython import get_ipython
from IPython.display import clear_output, display

from .widgets import GPUStatsApp


def is_notebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True
        elif shell == "TerminalInteractiveShell":
            return False
        else:
            return False
    except NameError:
        return False


def live():
    if not is_notebook():
        print(
            "gpuwidget.live() only works in a Jupyter Notebook, return ascii version instead."
        )
        print(gpustat.new_query().print_formatted())
        return
    clear_output(wait=True)
    widget = GPUStatsApp()
    display(widget)


def once():
    if not is_notebook():
        print(
            "gpuwidget.live() only works in a Jupyter Notebook, return ascii version instead."
        )
        print(gpustat.new_query().print_formatted())
        return
    clear_output(wait=True)
    widget = GPUStatsApp()
    widget.stop_updating(widget.stop_button)
    display(widget)
