#pragma once

#include <iostream>
#include <vector>

class Graph {
private:
    int vertices;
    std::vector< std::vector<int> > graph;
    std::vector<int> pred;
    std::vector<int> dist;

    bool breadth_first_search(int src, int dest);
    bool check_valid_input(std::vector< std::pair<int,int> > edges);

public:
    Graph( int v = 0 );

    /// Accessors
    void print_shortest_path(int src, int dest);
    int get_vertices() const;
    
    /// Mutators
    void add_edge(int src, int dest);
    void add_edges(std::vector< std::pair<int,int> > edges);

};