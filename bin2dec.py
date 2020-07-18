from nmigen import *
from nmigen.cli import main
from nmigen.hdl.ast import Statement

from typing import *


class Counter(object):
    def __init__(self, num_steps):
        self.num_steps = num_steps
        self._value = Signal(range(num_steps + 1))

    def is_triggered(self) -> Signal:
        return self._value == 0

    def decrement(self) -> Statement:
        return self._value.eq(Mux(self._value != 0, self._value - 1, self.num_steps))

    def reset(self) -> Statement:
        return self._value.eq(self.num_steps)


class Bin2Dec(Elaboratable):
    def __init__(self, width: int):
        self.width = width

        self.i_bin = Signal(width)
        self.i_bin_stb = Signal()
        self.o_digit = Signal(range(10))
        self.o_digit_rd = Signal()
        self.o_conv_rd = Signal()

    def elaborate(self, platform):
        bin = Signal.like(self.i_bin)
        dividend = Signal.like(self.i_bin)
        carry = Signal()
        shift_counter = Counter(self.width)

        rot_bin = Signal.like(bin)
        rot_dividend = Signal(self.width + 1)
        diff = Signal.like(rot_dividend)
        quotient = Signal()
        remainder = Signal(self.width)

        m = Module()

        m.d.comb += [
            rot_bin.eq(Cat(carry, bin[:-1])),
            rot_dividend.eq(Cat(bin[-1], dividend[:-1], 1)),
            diff.eq(rot_dividend - 10),
            quotient.eq(diff[-1]),
            remainder.eq(diff[:-1]),
        ]

        with m.If(self.i_bin_stb == 1):
            # set initial state when strobed
            m.d.sync += [
                self.o_digit.eq(0),
                self.o_digit_rd.eq(0),
                self.o_conv_rd.eq(0),
                bin.eq(self.i_bin),
                dividend.eq(0),
                carry.eq(0),
                shift_counter.reset(),
            ]

        with m.Else():
            with m.If((rot_bin != 0) | ~shift_counter.is_triggered()):
                m.d.sync += bin.eq(rot_bin)
                m.d.sync += carry.eq(quotient)
                m.d.sync += shift_counter.decrement()

                with m.If(~shift_counter.is_triggered()):
                    m.d.sync += dividend.eq(Mux(quotient == 1, remainder, rot_dividend))
                    m.d.sync += self.o_digit_rd.eq(0)
                with m.Else():
                    # digit complete
                    m.d.sync += dividend.eq(0)
                    m.d.sync += self.o_digit.eq(dividend)
                    m.d.sync += self.o_digit_rd.eq(1)

            with m.Else():
                # conversion complete
                m.d.sync += self.o_digit.eq(dividend)
                m.d.sync += self.o_digit_rd.eq(~self.o_conv_rd) # 1-cycle digit strobe
                m.d.sync += self.o_conv_rd.eq(1)

        return m

    def ports(self) -> List[Signal]:
        return [self.i_bin, self.i_bin_stb, self.o_digit, self.o_digit_rd, self.o_conv_rd]


if __name__ == '__main__':
    bin2dec = Bin2Dec(8)
    main(bin2dec, ports=[bin2dec.ports()])
