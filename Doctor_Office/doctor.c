#include <stdio.h>
#include <stdlib.h>

#include "libs/LibQueue.h"

int main(void) {
  // Write a program to manage the waiting room of a doctor using a queue.
  // The program should behave as shown below.
  /*
    Currently there are 0 patients in the queue.
    What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: N
    Please enter the patient ID: 101
    Currently there is 1 patient in the queue.
    What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: N
    Please enter the patient ID: 202
    Currently there are 2 patients in the queue.
    What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: N
    Please enter the patient ID: 303
    Currently there are 3 patients in the queue.
    What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: N
    Sorry, the queue is full!
    Currently there are 3 patients in the queue.
    What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: T
    Now treating patient 101.
    Currently there are 2 patients in the queue.
    What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: Q
  */

  Queue q = newQueue();
  int count = 0;
  char command;
  while (1) {
    printf("Currently there are %d patients in the queue.\n", count);
    printf("What do you want to do? [N]ew patient, [T]reat patient, [Q]uit: ");
    scanf("%c", &command);
    if (command == 'N') {
      int id;

      if (count < 3) {
        printf("Please enter the patient ID: ");
        scanf("%d", &id);
        enqueue(id, q);
        count++;
      }

      else {
        printf("Sorry, the queue is full!\n");
      }
    }
    if (command == 'T') {
      if (count == 0) {
        printf("There is nobody to treat!\n");
      } else {
        printf("Now treating patient %d.\n", dequeue(q));
        count--;
      }
    }

    if (command == 'Q') {
      freeQueue(q);
      exit(0);
    }
    getchar();  // keep this to read/skip the newline input
  }
}
