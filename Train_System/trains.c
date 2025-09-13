// Trains lab assignment

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NUM_STATIONS 12
#define INFINITY 9999

// An array with all of the station names
const char* stations[] = {
    "Amsterdam", "Den Haag", "Den Helder", "Utrecht",
    "Eindhoven", "Maastricht", "Nijmegen", "Enschede",
    "Zwolle", "Groningen", "Leeuwarden", "Meppel"};

// Function that maps each station to an index to avoid using strcmp too much
int mapStationIndex(const char* name) {
  for (int i = 0; i < NUM_STATIONS; i++) {
    if (strcmp(stations[i], name) == 0) {
      return i;
    }
  }
  return -1;
}

// IMPLEMENTING A GRAPH

// Creating the structure for nodes of the adjacency list of the graph below
typedef struct stationNode {
  int index;
  int weight;
  struct stationNode* next;
} stationNode;

// Creating a graph using adjacency list
typedef struct Graph {
  // Number of stations (nodes) in the graph
  int N;
  // Array of adjacency list for each of the stations
  stationNode** neighbours;
} Graph;

// Initializing the graph by setting to NULL
void init_graph(Graph* g) {
  g->neighbours = malloc(g->N * sizeof(stationNode*));
  for (int i = 0; i < g->N; i++) {
    g->neighbours[i] = NULL;
  }
}

// Function to add an edge to the graph
void add_edge(Graph* g, const char* u, const char* v, int weight) {
  // Map each station to its index (once again avoiding repetitive code)
  int to = mapStationIndex(u);
  int from = mapStationIndex(v);

  // If either of the cities does not exist do nothing
  if (to == -1 || from == -1) {
    return;
  }

  // Add the edge from city u to city v
  stationNode* newNode = (stationNode*)malloc(sizeof(stationNode));
  newNode->index = from;
  newNode->weight = weight;
  newNode->next = g->neighbours[to];
  g->neighbours[to] = newNode;

  // Since the assignment assumes that the forward and reverse distance is the same
  // we use the same ideas as above for the reverse weight
  newNode = (stationNode*)malloc(sizeof(stationNode));
  newNode->index = to;
  newNode->weight = weight;
  newNode->next = g->neighbours[from];
  g->neighbours[from] = newNode;
}

// Function to remove an edge from the graph
void remove_edge(Graph* g, const char* u, const char* v) {
  // Map the city to the index
  int to = mapStationIndex(u);
  int from = mapStationIndex(v);

  // If either of the cities does not exist do nothing
  if (to == -1 || from == -1) {
    return;
  }

  // Remove the edge from u to v
  stationNode** current = &g->neighbours[to];
  while (*current != NULL) {
    // When we find the edge from city u to v...
    if ((*current)->index == from) {
      stationNode* temp = *current;
      // Remove the edge and free memory
      *current = (*current)->next;
      free(temp);
      break;
    }
    current = &(*current)->next;
  }

  // Once again, same idea for reverse edge
  current = &g->neighbours[from];
  while (*current != NULL) {
    if ((*current)->index == to) {
      stationNode* temp = *current;
      *current = (*current)->next;
      free(temp);
      break;
    }
    current = &(*current)->next;
  }
}

// Freeing the memory needed for the graph
void freeGraph(Graph* g) {
  for (int i = 0; i < g->N; i++) {
    stationNode* node = g->neighbours[i];
    while (node != NULL) {
      stationNode* temp = node;
      node = node->next;
      free(temp);
    }
  }
  free(g->neighbours);
}

// IMPLEMENTING A PRIORITY QUEUE AND HEAP

// Creating a node for the heap containing the station and distance/weight
typedef struct {
  int station;
  // The distance here refers to the distance from the STARTING NODE
  int distance;
} HeapNode;

// Using the above definition to define a heap
typedef struct {
  HeapNode* array;
  int front;
  int size;
} Heap;

// MinHeap since Dijkstra's algorithm finds the minimal distance
Heap* createMinHeap(int size) {
  Heap* heap = (Heap*)malloc(sizeof(Heap));
  // We know the size that we want the heap
  heap->array = (HeapNode*)malloc(size * sizeof(HeapNode));
  heap->front = 0;
  heap->size = size;
  return heap;
}

// Swap function from heap.c exercise
void swap(HeapNode* x, HeapNode* y) {
  HeapNode temp = *x;
  *x = *y;
  *y = temp;
}

// Upheap function from heap.c exercise
// Only change is that since our root now has index 0 we need a strictly bigger index
void upheap(Heap* hp, int index) {
  if (index > 0) {
    int parent = (index - 1) / 2;
    if (hp->array[parent].distance > hp->array[index].distance) {
      swap(&(hp->array[parent]), &(hp->array[index]));
      upheap(hp, parent);
    }
  }
}

// Downheap function from heap.c exercise
void downheap(Heap* hp, int index) {
  int best = index;
  int leftChild = 2 * index + 1;
  int rightChild = 2 * index + 2;

  // Requires ".distance" since now we have weights on the edges
  if (leftChild < hp->front && hp->array[leftChild].distance < hp->array[best].distance) {
    best = leftChild;
  }

  if (rightChild < hp->front && hp->array[rightChild].distance < hp->array[best].distance) {
    best = rightChild;
  }

  if (best != index) {
    swap(&hp->array[index], &hp->array[best]);
    downheap(hp, best);
  }
}

// Similar implementation to that of removeMax in the exercise heap.c
// Function that removes the min node
HeapNode removeMin(Heap* hp) {
  if (hp->front <= 0) {
    HeapNode empty = {-1, INFINITY};
    return empty;
  }

  HeapNode root = hp->array[0];
  hp->array[0] = hp->array[hp->front - 1];
  hp->front--;
  downheap(hp, 0);
  return root;
}

// Useful function for Dijkstra's algorithm
// Updates the distances of each edge depending on what is minimal
void decreaseDistance(Heap* hp, int station, int distance) {
  for (int i = 0; i < hp->front; i++) {
    if (hp->array[i].station == station) {
      hp->array[i].distance = distance;
      // Makes sure to restore the heap property
      upheap(hp, i);
      return;
    }
  }
}

// Similar implementation to that of enqueue in the exercise heap.c
// Function responsible for adding elements to a heap
void enqueue(Heap* hp, int station, int distance) {
  if (hp->front == hp->size)
    return;

  (hp->front)++;
  hp->array[hp->front - 1].station = station;
  hp->array[hp->front - 1].distance = distance;
  upheap(hp, hp->front - 1);
}

// Dijkstra's algorithm function

void Dijkstra(Graph* g, int start, int end) {
  // Storing the minimal distances per edge
  int dist[NUM_STATIONS];
  int prev[NUM_STATIONS];
  // Marks all nodes as not visited (false)
  bool visited[NUM_STATIONS] = {false};

  Heap* hp = createMinHeap(NUM_STATIONS);

  // Initilize the distances to infinity
  for (int i = 0; i < NUM_STATIONS; i++) {
    dist[i] = INFINITY;
    prev[i] = -1;
    enqueue(hp, i, INFINITY);
  }

  // The distance at the starting node is 0
  dist[start] = 0;
  // Update the distance to the starting node
  decreaseDistance(hp, start, 0);

  // Loop that goes through all the nodes and edges and minimizes distances
  while (hp->front > 0) {
    HeapNode minNode = removeMin(hp);
    int u = minNode.station;

    if (visited[u])
      continue;

    visited[u] = true;

    // Traverse the adjacency list of station u (all the neighbours)
    stationNode* node = g->neighbours[u];

    while (node != NULL) {
      int v = node->index;
      int weight = node->weight;

      // Check if there exists a shorter path and update the heap with the new distance
      if (dist[u] + weight < dist[v]) {
        // Update distance/weight and path
        dist[v] = dist[u] + weight;
        prev[v] = u;
        decreaseDistance(hp, v, dist[v]);
      }
      // Continue with the rest of the nodes
      node = node->next;
    }
  }

  // If we cannot reach the node, print UNREACHABLE
  if (dist[end] == INFINITY) {
    printf("UNREACHABLE\n");
  } else {
    // If we can reach the node, create the path
    int path[NUM_STATIONS];
    int path_len = 0;

    // Add the node to the path
    for (int i = end; i != -1; i = prev[i]) {
      path[path_len++] = i;
    }

    // Prints in reverse (so from start to end of the path)
    for (int i = path_len - 1; i >= 0; i--) {
      printf("%s\n", stations[path[i]]);
    }
    printf("%d\n", dist[end]);
  }

  // Prevent memory leaks by freeing memory
  free(hp->array);
  free(hp);
}

int main(void) {
  Graph g;
  g.N = NUM_STATIONS;
  init_graph(&g);

  // Adding the edges to the graph corresponding to the city nodes
  add_edge(&g, "Amsterdam", "Den Haag", 46);
  add_edge(&g, "Amsterdam", "Den Helder", 77);
  add_edge(&g, "Amsterdam", "Utrecht", 26);
  add_edge(&g, "Den Haag", "Eindhoven", 89);
  add_edge(&g, "Eindhoven", "Maastricht", 63);
  add_edge(&g, "Eindhoven", "Nijmegen", 55);
  add_edge(&g, "Eindhoven", "Utrecht", 47);
  add_edge(&g, "Enschede", "Zwolle", 50);
  add_edge(&g, "Groningen", "Leeuwarden", 34);
  add_edge(&g, "Groningen", "Meppel", 49);
  add_edge(&g, "Leeuwarden", "Meppel", 40);
  add_edge(&g, "Maastricht", "Nijmegen", 111);
  add_edge(&g, "Meppel", "Zwolle", 15);
  add_edge(&g, "Nijmegen", "Zwolle", 77);
  add_edge(&g, "Utrecht", "Zwolle", 51);

  // The number of disruptions
  int n;
  scanf("%d", &n);

  // Remove edges depending on disruption number
  for (int i = 0; i < n; i++) {
    // These store the names of the stations
    char from[100], to[100];
    // New implementation of scanf that takes into account spaces (like in "Den Haag")
    scanf(" %[^\n]", from);
    scanf(" %[^\n]", to);
    remove_edge(&g, from, to);
  }

  // These store the names of the stations
  char from[100], to[100];

  // Loop that runs while there are two stations as inputs
  while (scanf(" %[^\n] %[^\n]", from, to) == 2) {
    // Mapping station to index
    int start = mapStationIndex(from);
    int end = mapStationIndex(to);

    // Find the shortest distance by running the algorithm
    if (start != -1 && end != -1) {
      Dijkstra(&g, start, end);
    } else {
      printf("UNREACHABLE\n");
    }
  }

  // Free graph memory to prevent memory leaks
  freeGraph(&g);

  return 0;
}
