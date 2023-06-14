
target/bmh: src/bmh/main.c
	mkdir -p target
	gcc -o target/bmh src/bmh/main.c

bench: target/bmh
	@./bench.py

clean:
	rm -r target

