.PHONY: clean all

all: traditional pattern

traditional: traditional.c
	gcc  traditional.c -lm -o traditional

pattern: pattern.c
	gcc  pattern.c -lm -o pattern

clean:
	rm -f traditional pattern
