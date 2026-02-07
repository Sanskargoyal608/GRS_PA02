#include "MT25040_Part_A_Data.h"
#include <pthread.h>

// Global to store the size passed from the script
int g_message_size = 1024; 

void *handle_client(void *socket_desc);

int main(int argc , char *argv[]) {
    // 1. READ SIZE FROM SCRIPT (Crucial Fix)
    if (argc > 1) {
        g_message_size = atoi(argv[1]);
    }
    printf("Server A1 starting. Size: %d\n", g_message_size);
    fflush(stdout);

    int server_id, new_socket, *new_sock;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    pthread_t t_id;
    
    if((server_id = socket(AF_INET,SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    if(setsockopt(server_id,SOL_SOCKET,SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; 
    address.sin_port = htons(PORT); 

    if(bind(server_id,(struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind Failed");
        exit(EXIT_FAILURE);
    }

    if(listen(server_id,32) < 0) {
        perror("Listen Failed");
        exit(EXIT_FAILURE);
    }

    printf("server listening on %d\n",PORT);
    fflush(stdout);

    // 2. FIXED COMPILER WARNING (Added extra parentheses)
    while((new_socket = accept(server_id, (struct sockaddr *)&address, (socklen_t*)&addrlen))) {
        // printf("connection accepted\n"); // Commented out to reduce spam in CSV mode
        // fflush(stdout);

        new_sock = malloc(sizeof(int));
        *new_sock = new_socket;

        if(pthread_create(&t_id,NULL,handle_client,(void*)new_sock) < 0) {
            perror("could not create thread");
            return 1;
        }

        pthread_detach(t_id);
    }

    if (new_socket < 0) {
        perror("accept failed");
        return 1;
    }
    return 0;
}

void *handle_client(void *socket_desc) {
    int sock = *(int*)socket_desc;
    free(socket_desc);

    // 3. USE GLOBAL SIZE
    int message_size = g_message_size;

    message msg;
    generate_msg(&msg, message_size);

    char *flat_buffer = (char*)malloc(message_size); 
    int byte_p_f = message_size/8;
    int offset = 0;

    for(int i = 0; i < 8 ; i++) {
        memcpy(flat_buffer+offset,msg.text[i],byte_p_f);
        offset += byte_p_f;
    }

    for(int i = 0; i < ITERATIONS; i++) {
        send(sock,flat_buffer, message_size,0);
    }

    free(flat_buffer);
    free_msg(&msg);
    close(sock);
    return NULL; 
}