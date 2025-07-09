traditional: traditional.c
	gcc  traditional.c -lm -o traditional

.PHONY: clean

clean:
	rm traditional
