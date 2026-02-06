#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <arpa/inet.h>

typedef struct {
    char *server_ip;
    int port;
    int message_size;
} threadArgs;

void* client_thread(void*args);

int main(int argc, char *argv[]) {
    if(argc != 5) {
        printf("something is missing in command line argument");
        return 1;
    }

    char *server_ip = argv[1];
    int  port = atoi(argv[2]);
    int thread_cnt = atoi(argv[3]);
    int msg_size = atoi(argv[4]);

    pthread_t threads[thread_cnt];
    threadArgs t_args;

    t_args.server_ip = server_ip;
    t_args.port = port;
    t_args.message_size = msg_size;

    for(int i = 0; i < thread_cnt; i++) {
        if(pthread_create(&threads[i],NULL,client_thread,(void*)&t_args) != 0) {
            perror("thread not created");
            return 1;
        }
    }

    for(int i = 0; i < thread_cnt; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("All clients finished");
    return 0;

}

void *client_thread(void *args) {   

    int client_id; 
    threadArgs *t_args = (threadArgs *)args;
    struct sockaddr_in serv_addr;
    char *buffer = malloc(t_args-> message_size);

    // Creating socket file descriptor
    if ((client_id = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket failed");
        free(buffer);
        return NULL;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(t_args -> port);

    if (inet_pton(AF_INET, t_args -> server_ip, &serv_addr.sin_addr) <= 0) {
        printf("\nInvalid address/ Address not supported \n");
        close(client_id);
        free(buffer);
        return NULL;
    }

    if ((connect(client_id, (struct sockaddr*)&serv_addr,sizeof(serv_addr)))< 0) {
        printf("\nConnection Failed \n");
        close(client_id);
        free(buffer);
        return NULL;
    }

    // The recv() function returns the number of bytes read.

    while(recv(client_id,buffer,t_args->message_size,0) > 0){
        

    }

    close(client_id);
    free(buffer);
    return NULL;


}