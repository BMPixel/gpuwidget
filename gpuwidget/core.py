import gpustat
from IPython import get_ipython
from IPython.display import clear_output, display

from .widgets import GPUStatsApp


def is_notebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":  # jupyter notebook
            return True
        elif shell == "TerminalInteractiveShell":  # iPython
            return False
        elif shell == "Shell":  # Google Colab
            return True
        else:
            return False
    except NameError:
        return False


def live(stop_immediately=False):
    try:
        if not is_notebook():
            print(
                "gpuwidget.live() only works in a Jupyter Notebook, return ascii version instead."
            )
            print(gpustat.new_query().print_formatted())
            return
        clear_output(wait=True)
        widget = GPUStatsApp()
        if stop_immediately:
            widget.stop_updating(widget.stop_button)
        display(widget)
    except OSError as e:
        print(e)
        print("It's likely your runtime does not contains GPU instance.")


def once():
    live(stop_immediately=True)
