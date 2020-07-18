from nmigen.asserts import Assert, Cover, Fell, Past, Rose, Stable
from nmigen.cli import main_parser, main_runner

from bin2dec import *


if __name__ == '__main__':
    parser = main_parser()
    args = parser.parse_args()

    b2d = Bin2Dec(8)

    m = Module()
    m.submodules.b2d = b2d

    m.d.comb += Cover(b2d.o_digit_rd == 1)
    m.d.comb += Cover(b2d.o_conv_rd == 1)

    # o_digit_rd is a 1-cycle strobe
    with m.If((Past(b2d.o_digit_rd, 2) == 0) & (Past(b2d.o_digit_rd, 1) == 1)):
        m.d.comb += Assert(b2d.o_digit_rd == 0)

    # i_bin_stb resets all outputs
    with m.If(Past(b2d.i_bin_stb) == 1):
        m.d.comb += Assert(b2d.o_digit == 0)
        m.d.comb += Assert(b2d.o_digit_rd == 0)
        m.d.comb += Assert(b2d.o_conv_rd == 0)

    # o_digit is stable if o_digit_rd is low
    with m.If((Past(ResetSignal()) == 0) & (Past(b2d.i_bin_stb) == 0) & (b2d.o_digit_rd == 0)):
        m.d.comb += Assert(Stable(b2d.o_digit))

    # o_digit_rd rises with o_conv_rd and falls on the next cycle
    with m.If(Rose(b2d.o_conv_rd, 2)):
        m.d.comb += Assert(Rose(b2d.o_digit_rd, 2))
        m.d.comb += Assert(Fell(b2d.o_digit_rd, 1))

    main_runner(parser, args, m, ports=b2d.ports())
