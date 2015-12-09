CC=g++
CFLAGS=-std=c++11 -I
LIBS=-lsndfile -lfftw3 -lSDL2

processmake: ProcessingTools.cpp Processor.cpp
	$(CC) processmake ProcessingTools.cpp Processor.cpp -o processor.o
