from nmigen import *
from nmigen.back import verilog
from nmigen.back.pysim import Simulator

from bin2dec import *


if __name__ == '__main__':
    b2d = Bin2Dec(8)

    sim = Simulator(b2d)

    def process():
        for num in range(256):
            yield b2d.i_bin.eq(num)
            yield b2d.i_bin_stb.eq(1)
            yield
            yield b2d.i_bin.eq(0)
            yield b2d.i_bin_stb.eq(0)
            yield

            digits = []

            while (yield b2d.o_conv_rd) == 0 or (yield b2d.o_digit_rd) == 1:
                if (yield b2d.o_digit_rd) == 1:
                    digits.append((yield b2d.o_digit))
                yield

            converted_num = ''.join([str(d) for d in reversed(digits)])
            if converted_num != str(num):
                print("Conversion failed! Expected {}, got {}".format(num, converted_num))

    sim.add_sync_process(process)
    sim.add_clock(1e-6)

    with sim.write_vcd("simulation.vcd", "simulation.gtkw", traces=b2d.ports()):
        sim.run()
