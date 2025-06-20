traditional: traditional.c
	gcc -lm  traditional.c -o traditional

.PHONY: clean

clean:
	rm traditional
