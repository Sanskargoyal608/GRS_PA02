#include "MT25040_Part_A_Data.h"
#include <pthread.h>
#include <sys/socket.h>
#include <sys/uio.h> 
#include <errno.h> 

#ifndef SO_ZEROCOPY
#define SO_ZEROCOPY 60
#endif

#ifndef MSG_ZEROCOPY
#define MSG_ZEROCOPY 0x4000000
#endif

int g_message_size = 1024; // Global size

void *handle_client(void *socket_desc);

int main(int argc , char *argv[]) {
    if (argc > 1) {
        g_message_size = atoi(argv[1]);
    }
    printf("Server A3 starting. Size: %d\n", g_message_size);
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

    if(listen(server_id,3) < 0) {
        perror("Listen Failed");
        exit(EXIT_FAILURE);
    }

    printf("server listening on %d\n",PORT);
    fflush(stdout);

    while((new_socket = accept(server_id, (struct sockaddr *)&address, (socklen_t*)&addrlen))) {
        new_sock = malloc(sizeof(int));
        *new_sock = new_socket;

        if(pthread_create(&t_id,NULL,handle_client,(void*)new_sock) < 0) {
            perror("could not create thread");
            return 1;
        }
        pthread_detach(t_id);
    }
    return 0;
}

void *handle_client(void *socket_desc) {
    int sock = *(int*)socket_desc;
    free(socket_desc);

    int opt = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_ZEROCOPY, &opt, sizeof(opt))) {
        // Warning only, don't exit
    }

    int message_size = g_message_size; 
    message msg;
    generate_msg(&msg, message_size);

    struct iovec iov[8];
    int field_size = message_size / 8;

    for(int i = 0; i < 8; i++) {
        iov[i].iov_base = msg.text[i];
        iov[i].iov_len = field_size;
    }

    struct msghdr msg_header = {0};
    msg_header.msg_iov = iov;
    msg_header.msg_iovlen = 8;

    for(int i = 0; i < ITERATIONS; i++) {
        ssize_t ret = sendmsg(sock, &msg_header, MSG_ZEROCOPY);
        if (ret < 0 && errno == ENOBUFS) {
            // Retry if buffer is full
            i--; 
            usleep(10);
        }
    }

    free_msg(&msg);
    close(sock);
    return NULL;
}