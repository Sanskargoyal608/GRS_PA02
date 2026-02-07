#ifndef DATA_FILE_H
#define DATA_FILE_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
// Reduced to 10000 for faster testing 
#define ITERATIONS 1000 

typedef struct {
    char *text[8];
} message ;

void free_msg(message *msg) {
    for (int i = 0; i < 8; i++) {
        if (msg->text[i]) free(msg->text[i]);
    }
}

void generate_msg(message *msg ,int size) {
    int field_size = size / 8;
    for (int i = 0; i < 8; i++) {
        msg->text[i] = (char *)malloc(field_size); 
        memset(msg->text[i], 'A', field_size);
    }
}
#endif