from nmigen import *
from nmigen.build import *
from nmigen_boards.icebreaker import ICEBreakerPlatform

from bin2dec import *


bin_conv_resources = [
    Resource("bin_conv_ports", 0,
             Subsignal("bin_value", Pins("4 2 47 45 3 48 46 44", dir="i")),
             Subsignal("bin_stb", Pins("43", dir="i")),
             Subsignal("dec_digit", Pins("38 34 31 42", dir="o")),
             Subsignal("digit_rd", Pins("36", dir="o")),
             Subsignal("conv_rd", Pins("32", dir="o")),
             Attrs(IO_STANDARD="SB_LVCMOS33"))
]


class Top(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform):
        bin_conv_ports = platform.request("bin_conv_ports")

        b2d = Bin2Dec(8)

        m = Module()

        m.submodules.bin2dec = b2d
        m.d.comb += [
            b2d.i_bin.eq(bin_conv_ports.bin_value),
            b2d.i_bin_stb.eq(bin_conv_ports.bin_stb),
            bin_conv_ports.dec_digit.eq(b2d.o_digit),
            bin_conv_ports.digit_rd.eq(b2d.o_digit_rd),
            bin_conv_ports.conv_rd.eq(b2d.o_conv_rd),
        ]

        return m


if __name__ == '__main__':
    platform = ICEBreakerPlatform()
    platform.add_resources(bin_conv_resources)
    platform.build(Top(), do_program=True)
