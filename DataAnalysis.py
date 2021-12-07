from enum import Enum


def cut_fields(line: str):
    str_split = line.split(' ')
    return str_split[0], str_split[1], str_split[2]


class DataAnalysis:
    thrErrors = 64
    Block = Enum("Block", "none mem05 mem0A mem15 mem1A spiqf uart0 uart1 i2c spod", start=0)
    pattern = {
        Block.mem05 : 0x55555555,
        Block.mem0A : 0xAAAAAAAA,
        Block.mem15 : 0x55555555,
        Block.mem1A : 0xAAAAAAAA,
        Block.spiqf : {
            0x0 : 0,
            0x1 : 0,
            0x2 : 0
        },
        Block.uart0 : {
            0x0 : 0,
            0x1 : 0,
            0x2 : 0
        },
        Block.uart1 : {
            0x0 : 0,
            0x1 : 0,
            0x2 : 0
        },
        Block.i2c   : {
            0x0 : 0,
            0x1 : 0,
            0x2 : 0
        },
        Block.spod  : {
            0x0 : 0,
            0x1 : 0,
            0x2 : 0
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
        silence = 0xF0DA0F02

    brief = {
        Block.mem05: 0,
        Block.mem0A: 0,
        Block.mem15: 0,
        Block.mem1A: 0,
        Block.spiqf: 0,
        Block.uart0: 0,
        Block.uart1: 0,
        Block.i2c:   0,
        Block.spod:  0
    }

    StateMsg = Enum("StateMsg", "start header numb addr error hash end angle", start=0)

    block = Block.none
    numb_errors = 0
    id_error = 0
    address = 0
    hash = 0
    angle = 0

    def __init__(self):
        self.clear()

    def clear(self):
        self.block = self.Block.none
        self.numb_errors = 0
        self.id_error = 0
        self.address = 0
        self.hash = 0
        self.angle = 0

    def analysis(self, text: list):
        state = self.StateMsg.start
        nxt_state = self.StateMsg.start
        for line in text:
            date, time, code = cut_fields(line)
            code = int(code, 16)
            errors = 0
            xor = ""
            if code == self.CodeVal.startChip.value or code == self.CodeVal.sequence.value\
                    or code == self.CodeVal.silence.value:
                self.clear()
                continue
            nxt_state = self.message_process(state, code)
            if state == self.StateMsg.error:
                match self.block:
                    case self.Block.mem05:
                        errors, xor = self.mem_process(code, self.CodeVal.mem05.value)
                    case self.Block.mem0A:
                        errors, xor = self.mem_process(code, self.CodeVal.mem0A.value)
                    case self.Block.mem15:
                        errors, xor = self.mem_process(code, self.CodeVal.mem15.value)
                    case self.Block.mem1A:
                        errors, xor = self.mem_process(code, self.CodeVal.mem1A.value)
                    case self.Block.spiqf:
                        errors, xor = self.spiqf_process(code)
                    case self.Block.uart0:
                        errors, xor = self.uart_process(code)
                    case self.Block.uart1:
                        errors, xor = self.uart_process(code)
                    case self.Block.i2c:
                        errors, xor = self.i2c_process(code)
                    case self.Block.spod:
                        errors, xor = self.spod_process(code)
            state = nxt_state
            if self.block != self.Block.none:
                self.brief[self.block] += errors
        print("finish")

    def message_process(self, state: StateMsg, code: int):
        if state != self.StateMsg.hash and state != self.StateMsg.end and state != self.StateMsg.angle:
            self.hash ^= code
        match state:
            case self.StateMsg.start:
                if code != self.CodeVal.beginMsg.value:
                    raise Exception("Invalid begin" + str(code))
                self.block = self.Block.none
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
                    raise Exception("Invalid block")
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
                if code != self.hash:
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

    def mem_process(self, val, pattern):
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
            val >> 1
            pattern >> 1
        return count, xor

    def spiqf_process(self, val):
        xor = ""
        count = 0
        return count, xor

    def uart_process(self, val):
        xor = ""
        count = 0
        return count, xor

    def i2c_process(self, val):
        xor = ""
        count = 0
        return count, xor

    def spod_process(self, val):
        xor = ""
        count = 0
        return count, xor
