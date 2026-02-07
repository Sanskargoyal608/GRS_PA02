#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <arpa/inet.h>

// Define the argument structure for threads
typedef struct {
    char *server_ip;
    int port;
    int message_size;
} threadArgs;

void* client_thread(void* args);

int main(int argc, char *argv[]) {
    if(argc != 5) {
        printf("Usage: %s <IP> <PORT> <THREADS> <MSG_SIZE>\n", argv[0]);
        return 1;
    }

    char *server_ip = argv[1];
    int port = atoi(argv[2]);
    int thread_cnt = atoi(argv[3]);
    int msg_size = atoi(argv[4]);

    pthread_t *threads = malloc(sizeof(pthread_t) * thread_cnt);
    threadArgs t_args;

    t_args.server_ip = server_ip;
    t_args.port = port;
    t_args.message_size = msg_size;

    // Create threads
    for(int i = 0; i < thread_cnt; i++) {
        if(pthread_create(&threads[i], NULL, client_thread, (void*)&t_args) != 0) {
            perror("Thread creation failed");
            return 1;
        }
    }

    // Join threads and sum up total bytes received
    long long total_bytes_all_threads = 0;
    void *retval;

    for(int i = 0; i < thread_cnt; i++) {
        pthread_join(threads[i], &retval);
        if (retval != NULL) {
            total_bytes_all_threads += *(long long*)retval;
            free(retval); // Free the memory allocated in the thread
        }
    }

    // Print the exact string the script looks for
    printf("TOTAL_BYTES:%lld\n", total_bytes_all_threads);

    free(threads);
    return 0;
}

void *client_thread(void *args) {   
    int client_id; 
    threadArgs *t_args = (threadArgs *)args;
    struct sockaddr_in serv_addr;
    
    // Allocate buffer once
    char *buffer = malloc(t_args->message_size);
    
    // Allocate memory for the result (bytes received)
    long long *bytes_received = malloc(sizeof(long long));
    *bytes_received = 0;

    // Creating socket
    if ((client_id = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Socket creation failed");
        free(buffer);
        free(bytes_received);
        return NULL;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(t_args->port);

    if (inet_pton(AF_INET, t_args->server_ip, &serv_addr.sin_addr) <= 0) {
        printf("\nInvalid address / Address not supported \n");
        close(client_id);
        free(buffer);
        free(bytes_received);
        return NULL;
    }

    // Connect to server
    if (connect(client_id, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        close(client_id);
        free(buffer);
        free(bytes_received); 
        return NULL;
    }

    // Receive data until server closes connection (time-based)
    ssize_t read_size;
    while((read_size = recv(client_id, buffer, t_args->message_size, 0)) > 0){
        *bytes_received += read_size;
    }

    close(client_id);
    free(buffer);
    return (void*)bytes_received;
}