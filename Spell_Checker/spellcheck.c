// Spellcheck Lab assignment

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// maximum length for a word
#define LENGTH 45

// Defining the trie structure
typedef struct TrieNode* dict;

struct TrieNode {
  bool endNode;
  dict children[26];
};

// Create a new empty dictionary.
dict newEmptyDict(void) {
  dict d = malloc(1 * sizeof(struct TrieNode));
  d->endNode = false;
  for (int i = 0; i < 26; i++) {
    d->children[i] = NULL;
  }
  return d;
}

// Helper function (a -> 0, b -> 1, etc)
int c2n(char c) {
  c = tolower(c);
  return (c - 'a');
}

// Check if a word is in the dictionary.
bool check(char* word, dict d) {
  dict current = d;
  for (int i = 0; word[i] != '\0'; i++) {
    int n = c2n(word[i]);
    if (current->children[n] == NULL) {
      return false;
    }
    current = current->children[n];
  }
  return current->endNode;
}

// Add word to the dictionary if it is is not already known.
void addWord(char word[LENGTH + 1], dict d) {
  dict current = d;
  // Keep running while the character is not '\0'
  for (int i = 0; word[i] != '\0'; i++) {
    int n = c2n(word[i]);
    // If you do not have a node for it, create one
    if (current->children[n] == NULL) {
      current->children[n] = newEmptyDict();
    }
    current = current->children[n];
  }
  current->endNode = true;
}

// Free the memory used by the dictionary.
void freeDict(dict d) {
  for (int i = 0; i < 26; i++) {
    if (d->children[i] != NULL) {
      freeDict(d->children[i]);
    }
  }
  free(d);
}

// Remove non-alphabetic characters and convert to lower case.
void trimWord(char* word) {
  int k = 0;
  for (int i = 0; i < (int)strlen(word); i++) {
    if (isalpha(word[i])) {
      word[k] = tolower(word[i]);
      k++;
    }
  }
  word[k] = '\0';
}

// The main function
int main(void) {
  char word[LENGTH + 1] = "";

  // step 1: read in the dictionary
  dict dictionary = newEmptyDict();
  while (scanf("%45s", word) && word[0] != '%') {
    trimWord(word);
    addWord(word, dictionary);
  }

  // step 2: read in text
  int counter = 0;
  int index = 0;
  int c = EOF;

  while ((c = getchar()) && c != EOF) {
    if (isalpha(c)) {
      word[index++] = tolower(c);
    } else {
      // If the word has already started
      if (index > 0) {
        word[index] = '\0';
        // If the word is not in the dictionary
        if (!check(word, dictionary)) {
          counter++;
          printf("%s\n", word);
        }
        index = 0;
      }
    }
  }

  // step 3: print number of unknown words
  printf("%d\n", counter);

  freeDict(dictionary);
  return 0;
}
