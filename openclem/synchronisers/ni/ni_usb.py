import time

import nidaqmx
from nidaqmx.constants import LineGrouping

from openclem.structures import SynchroniserMessage, SynchroniserSettings
from openclem.synchronisation import Synchroniser

LINES = {
    0: "Dev1/port0/line0",
    1: "Dev1/port0/line1",
    2: "Dev1/port0/line2",
    3: "Dev1/port0/line3",
    4: "Dev1/port0/line4",
    5: "Dev1/port0/line5",
    6: "Dev1/port0/line6",
    7: "Dev1/port0/line7",
    10: "Dev1/port1/line0",
    11: "Dev1/port1/line1",
    12: "Dev1/port1/line2",
    13: "Dev1/port1/line3",
    14: "Dev1/port1/line4",
    15: "Dev1/port1/line5",
    16: "Dev1/port1/line6",
    17: "Dev1/port1/line7",
    20: "Dev1/port2/line0",
    21: "Dev1/port2/line1",
    22: "Dev1/port2/line2",
    23: "Dev1/port2/line3",
    24: "Dev1/port2/line4",
    25: "Dev1/port2/line5",
    26: "Dev1/port2/line6",
    27: "Dev1/port2/line7",
}


class NI_USB(Synchroniser):
    def __init__(self, synchroniser_settings: SynchroniserSettings):
        self.settings = synchroniser_settings
        self.task = None
        self.pins = {}
        self.values = []
        self.lines = []

    def connect(self):
        # TODO: check if should just be pass
        self.task = nidaqmx.Task()

    def disconnect(self):
        if self.task is not None:
            self.task.close()

    def send_command(self, command):
        self.task.write(command, auto_start=True)

    def synch_image(self, message: SynchroniserMessage):
        self.lines = []
        self.delays = []
        self.pins = message.pins
        self.mode = message.mode
        self.exposures = message.exposures
        for pin in self.pins.keys():
            self.lines.append(LINES[self.pins[pin]])

        for exposure in self.exposures:
            self.delays.append(exposure)

        if self.mode == 'single':
            for i in range(len(self.lines)):
                self.single_line_pulse(self.lines[i], self.delays[i])
            
    def add_line(self, line):
        self.lines.append(line)

    def get_lines(self):
        return self.lines

    def get_values(self):
        return self.values

    def single_line_pulse(self, line, duration):
        task = nidaqmx.Task()
        task.do_channels.add_do_chan(
            LINES[line], line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
        )
        task.write(True)
        time.sleep(duration / 1e6)  # us to s
        task.write(False)
        task.close()

    def multi_line_pulse(self, lines, duration):
        task = nidaqmx.Task()
        for line in lines:
            task.do_channels.add_do_chan(
                LINES[line], line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
            )
        task.write(True)
        time.sleep(duration / 1e6)
        task.write(False)
        task.close()

    def single_line_onoff(onoff, pin):
        task = nidaqmx.Task()
        task.do_channels.add_do_chan(
            LINES[pin], line_grouping=LineGrouping.CHAN_FOR_ALL_LINES
        )
        task.write(onoff)
        task.close()
