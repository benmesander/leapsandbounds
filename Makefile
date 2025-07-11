.PHONY: clean all

all: traditional pattern generic-pattern

traditional: traditional.c
	gcc traditional.c -lm -o traditional

pattern: pattern.c
	gcc pattern.c -lm -o pattern

generic-pattern: generic-pattern.c
	gcc generic-pattern.c -lm -o generic-pattern


clean:
	rm -f traditional pattern generic-pattern
