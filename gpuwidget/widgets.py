import threading
import time
from typing import List

import gpustat
import ipywidgets as widgets
from gpustat.core import GPUStat, GPUStatCollection
from ipywidgets import HTML, Button, HBox, IntProgress, VBox


class TextWidgetStyle(HTML):
    def __init__(
        self,
        text: str,
        color: str = None,
        bold: bool = False,
        italic: bool = False,
        right_align: bool = False,
        mono_font: bool = True,
        layout: dict = None,
    ):
        super().__init__()
        self.update_text(text, color, bold, italic, right_align, mono_font)
        self.layout = layout or {}

    def update_text(
        self,
        text: str,
        color: str = None,
        bold: bool = False,
        italic: bool = False,
        right_align: bool = False,
        mono_font: bool = True,
    ):
        style_components = []
        if bold:
            text = "<b>" + text + "</b>"
        if italic:
            text = "<i>" + text + "</i>"
        if right_align:
            style_components.append("text-align: right;")
        if color:
            style_components.append(f"color: {color};")
        if mono_font:
            style_components.append("font-family: monospace;")

        style_attribute = " ".join(style_components)
        self.value = f'<div style="{style_attribute}">{text}</div>'


class GPUStatWidget(HBox):
    def __init__(self, stat: GPUStat):
        super().__init__()
        processes_str = self.processes_to_str(stat.processes)
        self.id_widget = TextWidgetStyle(
            f"[{stat.index}]",
            color="green",
            bold=True,
            layout={"width": "auto", "padding": "0px 10px 0px 0px"},
        )
        self.name_widget = TextWidgetStyle(
            stat.name, color="blue", layout={"width": "100px"}
        )
        self.power_widget = TextWidgetStyle(
            f"{stat.power_draw}W", color="red", layout={"width": "40px"}
        )
        self.util_text_widget = TextWidgetStyle(
            f"{stat.utilization} %", right_align=True, layout={"width": "50px"}
        )
        self.util_widget = self.create_progress_bar(stat.utilization)
        self.mem_text_widget = TextWidgetStyle(
            f"{stat.memory_used} / {stat.memory_total} MB",
            right_align=True,
            layout={"width": "150px"},
        )
        self.mem_widget = self.create_progress_bar(
            int(stat.memory_used / stat.memory_total * 100)
        )
        self.process_widget = TextWidgetStyle(
            processes_str,
            color="gray",
            layout={
                "width": "20%",
                "margin": "0px 10px 0px 0px",
                "overflow": "hidden",
                "text-overflow": "ellipsis",
                "white-space": "nowrap",
            },
        )
        self.children = [
            self.id_widget,
            self.name_widget,
            self.power_widget,
            self.util_text_widget,
            self.util_widget,
            self.mem_text_widget,
            self.mem_widget,
            self.process_widget,
        ]

    def create_progress_bar(self, value):
        return IntProgress(
            value=value,
            min=0,
            max=100,
            description="",
            bar_style=self.color_by_value(value),
            orientation="horizontal",
            layout={"flex": "1"},
        )

    @staticmethod
    def color_by_value(value: int) -> str:
        if value < 50:
            return "info"
        if value < 80:
            return "warning"
        return "danger"

    @staticmethod
    def processes_to_str(processes: List[dict]) -> str:
        if len(processes) == 0:
            return "No process"

        def process_summary(process: dict) -> str:
            cmd_abbr = process["full_command"][0].split("/")[-1]
            for subcmd in process["full_command"][1:]:
                if subcmd.endswith(".py"):
                    cmd_abbr = subcmd.split("/")[-1]
                    break
            return f"{process['username']}:{cmd_abbr}({process['pid']})"

        return ", ".join([process_summary(process) for process in processes])

    def update_with_gpu(self, stat: GPUStat):
        self.id_widget.update_text(f"[{stat.index}]", color="green", bold=True)
        self.name_widget.update_text(stat.name, color="blue")
        self.power_widget.update_text(f"{stat.power_draw}W", color="red")
        self.util_text_widget.update_text(f"{stat.utilization} %", right_align=True)
        self.util_widget.value = stat.utilization
        self.util_widget.bar_style = self.color_by_value(stat.utilization)
        memory_util = int(stat.memory_used / stat.memory_total * 100)
        self.mem_text_widget.update_text(
            f"{stat.memory_used} / {stat.memory_total} MB", right_align=True
        )
        self.mem_widget.value = memory_util
        self.mem_widget.bar_style = self.color_by_value(memory_util)
        processes_str = self.processes_to_str(stat.processes)
        self.process_widget.update_text(processes_str, color="gray")


class HeaderWidget(HBox):
    def __init__(self, stats: GPUStatCollection):
        super().__init__()
        self.icon_widget = TextWidgetStyle(
            "(⚡)",
            color="green",
            bold=True,
            layout={"width": "auto", "padding": "0px 10px 0px 0px"},
        )
        self.hostname_widget = TextWidgetStyle(
            stats.hostname,
            bold=True,
            color="green",
            layout={"width": "auto", "padding": "0px 10px 0px 0px"},
        )
        self.driver_widget = TextWidgetStyle(
            f"Driver: {stats.driver_version}", color="blue", layout={"flex": "1"}
        )
        self.time_widget = TextWidgetStyle(
            stats.query_time.strftime("%Y-%m-%d %H:%M:%S"),
            color="gray",
            right_align=True,
        )
        self.stop_button = Button(
            description="Stop Tracking",
            layout={"width": "auto", "margin": "0px 15px 0px 0px"},
        )
        self.children = [
            self.icon_widget,
            self.hostname_widget,
            self.driver_widget,
            self.time_widget,
            self.stop_button,
        ]
        self.layout = widgets.Layout(width="100%", overflow_x="hidden")

    def update_with_gpustat(self, stats: GPUStatCollection):
        self.time_widget.update_text(
            stats.query_time.strftime("%Y-%m-%d %H:%M:%S"),
            color="gray",
            right_align=True,
        )


class GPUStatsWidget(VBox):
    def __init__(self, stats: List[GPUStat]):
        super().__init__()
        self.gpu_widgets = [GPUStatWidget(stat) for stat in stats]
        self.children = self.gpu_widgets

    def update_with_gpus(self, stats: List[GPUStat]):
        for widget, stat in zip(self.gpu_widgets, stats):
            widget.update_with_gpu(stat)


class GPUStatsApp(VBox):
    def __init__(self):
        super().__init__()
        stats = gpustat.new_query()
        self.header = HeaderWidget(stats)
        self.gpu_stats = GPUStatsWidget(stats.gpus)
        self.children = [self.header, self.gpu_stats]
        self.stop_button = (
            self.header.stop_button
        )  # Expose stop button for external use
        self.stop_button.on_click(self.stop_updating)

        self.update_thread = None
        self.stop_event = threading.Event()

        self.live()

    def update_with_gpustat(self, stats: GPUStatCollection):
        self.header.update_with_gpustat(stats)
        self.gpu_stats.update_with_gpus(stats.gpus)

    @property
    def stop_tracking_button(self):
        return self.header.stop_button

    def _update_widget_continuously(self, interval=0.2):
        try:
            while not self.stop_event.is_set():
                stats = gpustat.new_query()
                self.update_with_gpustat(stats)
                time.sleep(interval)
        except Exception as e:
            print("Error updating widget:", e)

    def stop_updating(self, b):
        self.stop_event.set()
        b.description = "Stopped"
        b.disabled = True

    def live(self):
        """Launch thread to update widget"""
        self.stop_event.clear()
        self.update_thread = threading.Thread(target=self._update_widget_continuously)
        self.update_thread.start()

    def __del__(self):
        print("Deleting GPUStatsApp")
        if self.update_thread is not None:
            self.stop_event.set()
            self.update_thread.join()
        return super().__del__()
