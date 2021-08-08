#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv) {
    char** p1_ships = malloc(5*sizeof(char*));
    char** p2_ships = malloc(5*sizeof(char*));
    for(int i = 0; i < 5; i++) {
        p1_ships[i] = malloc(sizeof(64));
        p2_ships[i] = malloc(sizeof(64));
    }
    printf("Hello and welcome to the Battle Ship game analysis program, by the sour patch kids (combined age 4)\n");
    if(argc != 2) {
        printf("Usage: ./battleship <log>\n");
        return 0;
    }
    printf("Now analysing game of battle ship...");
    FILE* log = fopen(argv[1], "r");
    if(log == NULL) {
        printf("Couldn't open game log!\n");
    }
    fgets(p1_ships[0], 64, log);
    fgets(p2_ships[1], 64, log);
    fgets(p3_ships[2], 64, log);
    fgets(p4_ships[3], 64, log);
    fgets(p5_ships[4], 64, log);
    fgets(p2_ships[0], 64, log);
    fgets(p2_ships[1], 64, log);
    fgets(p2_ships[2], 64, log);
    fgets(p2_ships[3], 64, log);
    fgets(p2_ships[4], 64, log);
    printf("Player one's aircraft carrier: ");
    printf(p1_ships[0]);
    printf("\nPlayer one's battle ship: ");
    printf(p1_ships[1]);
    printf("\nPlayer one's submarine: ");
    printf(p1_ships[2]);
    printf("\nPlayer one's destroyer: ");
    printf(p1_ships[3]);
    printf("\nPlayer one's frigate: ");
    printf(p1_ships[4]);

    printf("\nPlayer two's aircraft carrier: ");
    printf(p2_ships[0]);
    printf("\nPlayer two's battle ship: ");
    printf(p2_ships[1]);
    printf("\nPlayer two's submarine: ");
    printf(p2_ships[2]);
    printf("\nPlayer two's destroyer: ");
    printf(p2_ships[3]);
    printf("\nPlayer two's frigate: ");
    printf(p2_ships[4]);

}