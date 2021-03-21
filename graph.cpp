/*
The code used for breadth first search and shortest path
is a modified version retrieved from:
https://www.geeksforgeeks.org/shortest-path-unweighted-graph/
*/

#include <iostream>
#include <vector>
#include <list>
#include <climits>
#include "graph.hpp"

// Constructor
Graph::Graph( int v ):
    vertices(v), graph(v), pred(v), dist(v) {/*empty constructor*/}

// Private
bool Graph::breadth_first_search(int src, int dest) {
    std::list<int> queue;
    bool visited[vertices];

    if (vertices < 1) {
        return false;
    }
    if (src >= vertices || dest >= vertices) {
        return false;
    }
    
    // initialization: visted to false dist to inf and no predecessors
    for (int i = 0; i < vertices; i++) {
        visited[i] = false;
        dist[i] = INT_MAX;
        pred[i] = -1;
    }

    // source is first to be visited and 
    // distance from source to itself should be 0 
    visited[src] = true;
    dist[src] = 0;
    queue.push_back(src);

    // iterate through graph breadth first and halt when destination is found
    while (!queue.empty()) {
        int n = queue.front();
        queue.pop_front();
        for (int i =0; i < graph[n].size(); i++) {
            if (visited[graph[n][i]] == false) 
            {
                visited[graph[n][i]] = true;
                dist[graph[n][i]] = dist[n] + 1;
                pred[graph[n][i]] = n;
                queue.push_back(graph[n][i]);

                if (graph[n][i] == dest) {
                    return true;
                }
            }
        }
    }
    return false;
}

bool Graph::check_valid_input(std::vector< std::pair<int,int> > edges) {
    for ( auto& e : edges) {
        if (vertices <= e.first || vertices <= e.second || e.first < 0 || e.second < 0) {
            std::cerr << "Error: Attempted to add edge to vertex that does not exist"
                      << std::endl;
            return false;
        }
        // if (e.first == e.second) {
        //     std::cerr << "Error:  Cannot add edge from vertex to iteself"
        //               << std::endl;
        //     return false;
        // }    
    }
    return true;
}

// Mutators
void Graph::add_edge(int src, int dest) {
    graph[src].push_back(dest); 
    graph[dest].push_back(src); 

    return;
}

void Graph::add_edges(std::vector< std::pair<int,int> > edges) {
    if ( check_valid_input(edges) ) {
        for ( auto& e : edges) {
                // std::cout << vertices << " " << e.first << " " << e.second << std::endl;
                add_edge(e.first, e.second);
            }
        }
    return;
}

// Accessors
int Graph::get_vertices() const {
    return vertices;
}

void Graph::print_shortest_path(int src, int dest) {
    if(src >= vertices || dest >= vertices) {
        std::cerr << "Error: invalid vertex specified" << std::endl;
        return;
    }
    
    std::vector<int> shortest_path;
    int current = dest;


    if (breadth_first_search(src, dest) == false) {
        std::cerr << "Error: There is no path between Source " << src 
                  << " and Destination: " << dest << std::endl;
        
        return;
    }

    shortest_path.push_back(current);
    while (pred[current] != -1) {
        shortest_path.push_back(pred[current]);
        current = pred[current];
    }

    for (int i = shortest_path.size() -1; i >=0; i--) {
        std::cout << shortest_path[i];
        if (i > 0) std::cout << "-";
    }
    std::cout << std::endl;

    return;
}