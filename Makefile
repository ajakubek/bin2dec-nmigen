MODULE_SOURCES := bin2dec.py

all: formal simulate
	@echo 'Build complete!'

formal: $(MODULE_SOURCES) formal.py
	mkdir -p build
	python formal.py generate -t il >build/formal.il
	sby -f bin2dec.sby

icebreaker: $(MODULE_SOURCES) icebreaker.py
	python icebreaker.py

simulate: $(MODULE_SOURCES) simulate.py
	python simulate.py

$(TEST_EXECUTABLE): $(SOURCES) $(TEST_SOURCES)
	iverilog -s $(TEST_TOP_MODULE) -o $(TEST_EXECUTABLE) $(SOURCES) $(TEST_SOURCES)

clean:
	rm -rf __pycache__ build bin2dec_bmc bin2dec_cover
	rm -f *.gtkw *.vcd

.PHONY: all clean formal icebreaker simulate
