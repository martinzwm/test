// compile: g++ -o a2ece650 ../a2ece650.cpp ../graph.cpp -std=c++11
#include <iostream>
#include <limits>
#include <regex>
#include "a2-ece650.hpp"
#include "graph.hpp"

std::vector< std::pair<int,int> > parse(std::string s) {
    std::pair<int, int> edge;
    std::vector< std::pair<int,int> > result;
    
    // using regex
    try {
        std::regex re("-?[0-9]+"); //match consectuive numbers
        std::sregex_iterator next(s.begin(), s.end(), re);
        std::sregex_iterator end;
        while (next != end) {
            std::smatch match1;
            std::smatch match2;
            
            match1 = *next;
            next++;
            // iterate to next match
            if (next != end) {
                match2 = *next;
                edge.first = std::stoi(match1.str());
                edge.second = std::stoi(match2.str());
                result.push_back(edge);
                next++;
            }
        } 
    } 
    catch (std::regex_error& e) {
        result.clear();
    }

    return result;
}

int main() {
    char cmd;
    int vertices;
    int start_vertex;
    int end_vertex;
    std::string edges_input;
    Graph* g = new Graph(0);

    while(std::cin >> cmd){    
        
        switch(cmd) {
            
            case 'V': case 'v':
                std::cin >> vertices;      
                // Create a new graph
                if (vertices >= 0) {
                    delete g;
                    g = new Graph(vertices);
                } else {
                    std::cerr << "Error: Incorrect value for vertices entered" << std::endl;
                }
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

                break;
            
            case 'E': case 'e':
                std::cin >> edges_input;
                g->add_edges( parse(edges_input) );
                
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

                break;

            case 'S': case 's':
                std::cin >> start_vertex >> end_vertex;
                g->print_shortest_path(start_vertex, end_vertex);
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

                break;

            default:
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                std::cerr << "Error: command not recognized" << std::endl;
        }
    }
    delete g;
    return 0;
}