from enum import Enum
import logging
import sys
import os
import json
import datetime
import time


def cut_fields(line: str):
    str_split = line.split(' ')
    match str_split:
        case date, time, code, *_:
            return date, time, code
        case _:
            return "none", "none", "none"


def mem_process(val: int, pattern: int):
    xor = ""
    count = 0
    for i in range(32):
        if val & 1 == pattern & 1:
            xor += '.'
        elif val & 1 == 0 and pattern & 1 == 1:
            xor += '-'
            count += 1
        elif val & 1 == 1 and pattern & 1 == 0:
            xor += '+'
            count += 1
        else:
            xor += 'X'
        val = val >> 1
        pattern = pattern >> 1
    return count, xor[::-1]


def spiqf_process(val):
    xor = ""
    count = 0
    return count, xor


def uart_process(val):
    xor = ""
    count = 0
    return count, xor


def i2c_process(val):
    xor = ""
    count = 0
    return count, xor


def spod_process(val):
    xor = ""
    count = 0
    return count, xor


class DataAnalysis:
    thrErrors = 64
    MUX = 8
    Block = Enum("Block", "none mem05 mem0A mem15 mem1A spiqf uart0 uart1 i2c spod", start=0)
    pattern = {
        Block.mem05: 0x55555555,
        Block.mem0A: 0xAAAAAAAA,
        Block.mem15: 0x55555555,
        Block.mem1A: 0xAAAAAAAA,
        Block.spiqf: {
            0x0: 0,
            0x1: 0,
            0x2: 0
        },
        Block.uart0: {
            0x0: 0,
            0x1: 0,
            0x2: 0
        },
        Block.uart1: {
            0x0: 0,
            0x1: 0,
            0x2: 0
        },
        Block.i2c: {
            0x0: 0,
            0x1: 0,
            0x2: 0
        },
        Block.spod: {
            0x0: 0,
            0x1: 0,
            0x2: 0
        }
    }

    class CodeVal(Enum):
        startChip = 0xF0DAA000
        beginMsg = 0xF0DA0000
        mem05 = 0xF0DA0010
        mem0A = 0xF0DA0011
        mem15 = 0xF0DA0012
        mem1A = 0xF0DA0013
        spiqf = 0xF0DA0020
        uart0 = 0xF0DA0030
        uart1 = 0xF0DA0040
        i2c = 0xF0DA0050
        spod = 0xF0DA0060
        endMsg = 0xF0DA0EFF
        sequence = 0xF0DA0F00
        hashErr = 0xF0DA0F01
        silence = 0xF0DA0F02

    brief = {
        Block.mem05:        0,
        Block.mem0A:        0,
        Block.mem15:        0,
        Block.mem1A:        0,
        Block.spiqf:        0,
        Block.uart0:        0,
        Block.uart1:        0,
        Block.i2c:          0,
        Block.spod:         0,
        "hashErr":          0,
        "processedLines":   0,
        "skippedLines":     0
    }
    local_brief = {
        Block.mem05: 0,
        Block.mem0A: 0,
        Block.mem15: 0,
        Block.mem1A: 0,
        Block.spiqf: 0,
        Block.uart0: 0,
        Block.uart1: 0,
        Block.i2c: 0,
        Block.spod: 0
    }
    datetime_format = "%d.%m.%Y %H:%M:%S"

    StateMsg = Enum("StateMsg", "start header numb addr error hash end angle", start=0)

    block = Block.none
    numb_errors = 0
    id_error = 0
    address = 0
    hash = 0
    angle = 0

    cur_filename = ""
    mem_packets = []
    local_mem_packet = {}
    mem_coords = []

    def __init__(self):
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        self.clear()

    def clear(self):
        self.cur_filename = ""
        self.mem_packets = []
        self.local_mem_packet = {}
        self.mem_coords = []
        self.pkt_clear()
        self.local_brief_clear()
        self.brief_clear()

    def pkt_clear(self):
        self.block = self.Block.none
        self.numb_errors = 0
        self.id_error = 0
        self.address = 0
        self.hash = 0
        self.angle = 0

    def local_brief_clear(self):
        for key in self.brief.keys():
            self.local_brief[key] = 0

    def brief_clear(self):
        for key in self.brief.keys():
            self.brief[key] = 0

    def file_analysis(self, filename: str, num_str: int):
        self.clear()
        self.cur_filename = filename
        self.pkt_clear()
        self.brief_clear()
        with open(filename, 'r') as f:
            text = f.readlines()
        self.analysis(text)

    def analysis(self, text: list):
        state = self.StateMsg.start
        for line in text:
            self.brief['processedLines'] += 1
            date_str, time_str, code_str = cut_fields(line)
            if code_str == "none":
                self.brief['skippedLines'] += 1
                continue
            code = int(code_str, 16)
            errors = 0
            xor = ""
            if code == self.CodeVal.startChip.value or code == self.CodeVal.sequence.value\
                    or code == self.CodeVal.silence.value:
                self.pkt_clear()
                continue
            if state == self.StateMsg.start:
                self.pkt_clear()
                self.local_brief_clear()
            nxt_state = self.message_process(state, code)
            pattern = ""
            if state == self.StateMsg.error:
                match self.block:
                    case self.Block.mem05:
                        pattern = f"{self.pattern[self.Block.mem05]:08X}"
                        errors, xor = mem_process(code, self.pattern[self.Block.mem05])
                    case self.Block.mem0A:
                        pattern = f"{self.pattern[self.Block.mem0A]:08X}"
                        errors, xor = mem_process(code, self.pattern[self.Block.mem0A])
                    case self.Block.mem15:
                        pattern = f"{self.pattern[self.Block.mem15]:08X}"
                        errors, xor = mem_process(code, self.pattern[self.Block.mem15])
                    case self.Block.mem1A:
                        pattern = f"{self.pattern[self.Block.mem1A]:08X}"
                        errors, xor = mem_process(code, self.pattern[self.Block.mem1A])
                    case self.Block.spiqf:
                        errors, xor = spiqf_process(code)
                    case self.Block.uart0:
                        errors, xor = uart_process(code)
                    case self.Block.uart1:
                        errors, xor = uart_process(code)
                    case self.Block.i2c:
                        errors, xor = i2c_process(code)
                    case self.Block.spod:
                        errors, xor = spod_process(code)

                self.local_brief[self.block] += errors
                if self.block == self.Block.mem05 or self.block == self.Block.mem0A or \
                        self.block == self.Block.mem15 or self.block == self.Block.mem1A:
                    ftm = time.strptime(date_str + " " + time_str, self.datetime_format)
                    dt = datetime.datetime(ftm.tm_year, ftm.tm_mon, ftm.tm_mday, ftm.tm_hour, ftm.tm_min, ftm.tm_sec)
                    if len(self.local_mem_packet) > 0:
                        ftm = time.strptime(self.local_mem_packet['time'], self.datetime_format)
                        dt_packet = datetime.datetime(ftm.tm_year, ftm.tm_mon, ftm.tm_mday,
                                                      ftm.tm_hour, ftm.tm_min, ftm.tm_sec)
                        if (dt - dt_packet).seconds >= 2:
                            self.mem_packets.append(self.local_mem_packet)
                            self.local_mem_packet = {}
                    del ftm

                    if len(self.local_mem_packet) == 0:
                        self.local_mem_packet['time'] = dt.strftime(self.datetime_format)
                        self.local_mem_packet['data'] = []
                    self.local_mem_packet['data'] += [{
                        'adr': f"{self.address:08X}",
                        'pat': pattern,
                        'val': f"{code:08X}",
                        'bin': xor,
                        'angle': "none"
                    }]

            if state == self.StateMsg.angle and len(self.local_mem_packet) > 0 and \
                    self.local_mem_packet['data'][-1]['angle'] == "none":
                for pack in self.local_mem_packet['data'][::-1]:
                    if pack['angle'] != "none":
                        break
                    pack['angle'] = self.angle

            if state == self.StateMsg.angle:
                for key in self.local_brief.keys():
                    self.brief[key] += self.local_brief[key]
                self.local_brief_clear()
            state = nxt_state
        self.analysis_coords()
        for key, value in self.brief.items():
            print(f"  {key:14s}: {value}")

    def analysis_coords(self):
        for timeframe in self.mem_packets:
            data = timeframe['data']
            pack_coords = []
            for pack in data:
                for num_bit, bit_simb in enumerate(pack['bin'][::-1]):
                    if bit_simb == '+' or bit_simb == '-':
                        num_word = int(pack['adr'], 16) // 4;
                        num_word_in_line = num_word % self.MUX
                        y = num_word // self.MUX
                        x = num_bit * self.MUX + num_word_in_line
                        pack_coords += [[x, y]]
            self.mem_coords += [{'angle': data[0]['angle'], 'coords': pack_coords}]

    def message_process(self, state: StateMsg, code: int):
        match code:
            case self.CodeVal.hashErr.value:
                self.brief['hashErr'] += 1
                return self.StateMsg.start
            case self.CodeVal.startChip.value:
                self.brief['startChip'] += 1
                return self.StateMsg.start
            case self.CodeVal.silence.value:
                self.brief['silence'] += 1
                return self.StateMsg.start

        if state != self.StateMsg.hash and state != self.StateMsg.end and state != self.StateMsg.angle:
            self.hash ^= code
        match state:
            case self.StateMsg.start:
                if code != self.CodeVal.beginMsg.value:
                    self.brief['skippedLines'] += 1
                    # logging.debug("Invalid begin " + str(code) + ", line " + str(self.brief["processedLines"]))
                    return self.StateMsg.start
                return self.StateMsg.header
            case self.StateMsg.header:
                if code == self.CodeVal.mem05.value:
                    self.block = self.Block.mem05
                elif code == self.CodeVal.mem0A.value:
                    self.block = self.Block.mem0A
                elif code == self.CodeVal.mem15.value:
                    self.block = self.Block.mem15
                elif code == self.CodeVal.mem1A.value:
                    self.block = self.Block.mem1A
                elif code == self.CodeVal.spiqf.value:
                    self.block = self.Block.spiqf
                elif code == self.CodeVal.uart0.value:
                    self.block = self.Block.uart0
                elif code == self.CodeVal.uart1.value:
                    self.block = self.Block.uart1
                elif code == self.CodeVal.i2c.value:
                    self.block = self.Block.i2c
                elif code == self.CodeVal.spod.value:
                    self.block = self.Block.spod
                else:
                    self.brief['skippedLines'] += 1
                    # logging.debug("Invalid Block " + str(code) + ", line " + str(self.brief["processedLines"]))
                    return self.StateMsg.start
                return self.StateMsg.numb
            case self.StateMsg.numb:
                self.numb_errors = code
                self.id_error = 0
                return self.StateMsg.addr if self.numb_errors > 0 else self.StateMsg.hash
            case self.StateMsg.addr:
                self.address = code
                return self.StateMsg.error
            case self.StateMsg.error:
                self.id_error += 1
                local_numb = self.numb_errors if self.numb_errors <= self.thrErrors else self.thrErrors
                return self.StateMsg.addr if self.id_error < local_numb else self.StateMsg.hash
            case self.StateMsg.hash:
                self.block = self.Block.none
                if code != self.hash:
                    logging.debug("Invalid hash " + str(code) + " " + str(self.hash) +
                                  ", line " + str(self.brief['processedLines']))
                    raise Exception("Invalid hash")
                self.hash = 0
                return self.StateMsg.end
            case self.StateMsg.end:
                if code != self.CodeVal.endMsg.value:
                    raise Exception("Invalid end")
                return self.StateMsg.angle
            case self.StateMsg.angle:
                if code > 360:
                    raise Exception("Invalid angle")
                self.angle = code
                return self.StateMsg.start

    def write_brief(self, filename: str):
        work_dir = os.path.split(filename)[0]
        if not os.path.isdir(work_dir):
            os.makedirs(work_dir)
        text = [self.cur_filename + "\n"]
        for key, value in self.brief.items():
            text += f"  {key:14s} {value}\n"
        text += "\n"
        with open(filename, 'a') as f:
            f.writelines(text)

    def write_packets(self, filename: str):
        work_dir = os.path.split(filename)[0]
        if not os.path.isdir(work_dir):
            os.makedirs(work_dir)
        with open(filename, 'w') as f:
            f.write(self.cur_filename + "\n")
            json.dump(self.mem_packets, f, indent=4)

    def write_coords(self, filename: str):
        work_dir = os.path.split(filename)[0]
        if not os.path.isdir(work_dir):
            os.makedirs(work_dir)
        with open(filename, 'w') as f:
            f.write(self.cur_filename + "\n")
            json.dump(self.mem_coords, f, indent=4)

    def write_coords_wolfram(self, filename: str):
        work_dir = os.path.split(filename)[0]
        if not os.path.isdir(work_dir):
            os.makedirs(work_dir)
        with open(filename, 'w') as f:
            for pack in self.mem_coords:
                line = "{{"
                for coords in pack['coords'][:-1]:
                    line += f"{{{coords[0]},{coords[1]}}},"
                line += f"{{{pack['coords'][-1][0]},{pack['coords'][-1][1]}}}"
                line += "}"
                line += f",{pack['angle']}}}"
                f.write(line + "\n")
