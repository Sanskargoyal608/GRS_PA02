# Makefile for GRS PA02
# Author: MT25040

CC = gcc
CFLAGS = -pthread -Wall

# Targets
all: server_a1 server_a2 server_a3 client_a1

# Part A1: Baseline Server (Note: Capital 'S' in filename)
server_a1: MT25040_Part_A1_Server.c MT25040_Part_A_Data.h
	$(CC) $(CFLAGS) MT25040_Part_A1_Server.c -o server_a1

# Part A2: One-Copy Server (Note: Lowercase 's' in filename)
server_a2: MT25040_Part_A2_Server.c MT25040_Part_A_Data.h
	$(CC) $(CFLAGS) MT25040_Part_A2_Server.c -o server_a2

# Part A3: Zero-Copy Server (Note: Lowercase 's' in filename)
server_a3: MT25040_Part_A3_Server.c MT25040_Part_A_Data.h
	$(CC) $(CFLAGS) MT25040_Part_A3_Server.c -o server_a3

# Client (Note: Lowercase 'c' in filename)
client_a1: MT25040_Part_A1_Client.c MT25040_Part_A_Data.h
	$(CC) $(CFLAGS) MT25040_Part_A1_Client.c -o client_a1

# Clean up binaries and results
clean:
	rm -f server_a1 server_a2 server_a3 client_a1 results/*.csv