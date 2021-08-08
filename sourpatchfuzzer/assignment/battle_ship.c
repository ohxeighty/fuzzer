#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {
    char** p1_ships = malloc(5*sizeof(char*));
    char** p2_ships = malloc(5*sizeof(char*));
    for(int i = 0; i < 5; i++) {
        p1_ships[i] = malloc(sizeof(64));
        p2_ships[i] = malloc(sizeof(64));
    }
    printf("Hello and welcome to the Battle Ship game, by the sour patch kids (combined age 4)\n");

    printf("Player one please enter your aircraft carrier's location: ");
    gets(p1_ships[0]);
    printf("\nPlayer one please enter your battle ship's location: ");
    gets(p1_ships[1]);
    printf("\nPlayer one please enter your submarine's location: ");
    gets(p1_ships[2]);
    printf("\nPlayer one please enter your destroyer's location: ");
    gets(p1_ships[3]);
    printf("\nPlayer one please enter your frigate's location: ");
    gets(p1_ships[4]);
    
    printf("\n\n\nPlease turn the keyboard and screen to player two now\n\n\n");
    
    printf("\nPlayer two please enter your aircraft carrier's location: ");
    gets(p2_ships[0]);
    printf("\nPlayer two please enter your battle ship's location: ");
    gets(p2_ships[1]);
    printf("\nPlayer two please enter your submarine's location: ");
    gets(p2_ships[2]);
    printf("\nPlayer two please enter your destroyer's location: ");
    gets(p2_ships[3]);
    printf("\nPlayer two please enter your frigate's location: ");
    gets(p2_ships[4]);
    
    printf("\n\n\nPlease turn the keyboard and screen to player one now\n\n\n");

    printf("\nPlayer one's aircraft carrier: ");
    printf(p1_ships[0]);
    printf("Player one's battle ship: ");
    printf(p1_ships[1]);
    printf("Player one's submarine: ");
    printf(p1_ships[2]);
    printf("Player one's destroyer: ");
    printf(p1_ships[3]);
    printf("Player one's frigate: ");
    printf(p1_ships[4]);

    printf("\n\n\nPlease turn the keyboard and screen to player two now\n\n\n");

    printf("\nPlayer two's aircraft carrier: ");
    printf(p2_ships[0]);
    printf("Player two's battle ship: ");
    printf(p2_ships[1]);
    printf("Player two's submarine: ");
    printf(p2_ships[2]);
    printf("Player two's destroyer: ");
    printf(p2_ships[3]);
    printf("Player two's frigate: ");
    printf(p2_ships[4]);

}