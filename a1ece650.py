from __future__ import print_function
from __future__ import division
import sys
import shlex
import cmd
import re
import math

# print(sys.version_info)
class ProgramLoop(cmd.Cmd):
    prompt = ''
    use_rawinput = 0

    def __init__(self):
        cmd.Cmd.__init__(self, completekey=None)
        self.graph = Graph()
    
    def parseline(self, line):
        """OVERRIDE parseline method
        Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] != ' ': i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line
    
    def do_a(self, args):
        """
        This is the help string for the add command
        """
        parsed_args = (parse(args, 'do_a'))
        if parsed_args:
            self.graph.add_street(*parsed_args)

    def do_r(self, args):
        """
        This is the help string for the remove command
        """
        parsed_args = (parse(args, 'do_r'))
        if parsed_args:
            self.graph.remove_street(*parsed_args)

    def do_c(self, args):
        """
        This is the help string for the change command
        """
        parsed_args = (parse(args, 'do_c'))
        if parsed_args:        
            self.graph.change_street(*parsed_args)

    def do_g(self, args):
        """
        This is the help string for the graph command
        """
        if not args:
            self.graph.render_graph()
            print(self.graph)
        else:
            print('Error: Invalid arguments', file=sys.stderr)

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished.""" 
        #If line empty, exit program
        if(not line or line=='EOF'):
            stop = True
        return stop
    
    def default(self, line):
        if line != 'EOF':
            print('Error: The command you entered was not found "{0}"'.format(line), file=sys.stderr)

    def emptyline(self):
        pass

class Graph(object):
    def __init__(self):
        self.history = {}
        self.vertices = {}
        self.edges = set([])
        self.intersections = set([])
    
    def __str__(self):
        string = 'V = {\n'
        for v, v_id in sorted(self.vertices.items(), key=lambda x: x[1]):
            if type(v[0]) == 'float' or type(v[1]) == 'float':
                xcoord, ycoord = round(v[0], 2), round(v[1], 2)
            else:
                xcoord, ycoord = v[0], v[1] 
            string += '  {0}: ({1},{2})\n'.format( v_id, xcoord, ycoord)
        string += '}\nE = {\n'
        if self.edges:
            for edge in self.edges:
                tmp = list(edge)
                string += '  <{0},{1}>,\n'.format(tmp[0],tmp[1])
            string = string[:-2] + '\n}'
        else:
            string += '}'

        return string

    def add_street(self, street, vertices):
        # type: (str, List[Tuple(int, int), ...]) -> Bool
        if vertices:
            if street in self.history:
                print('Error: You already have \"{0}\" in the graph'.format(street), file=sys.stderr)
            else:
                self.history[street] = vertices
                return True
        else:
            print('Error: a command has no vertices specified', file=sys.stderr)

        return False

    def change_street(self, street, vertices):
        # type: (str, List[Tuple(int, int), ...]) -> Bool
        if vertices:
            if street in self.history:
                self.history[street] = vertices
                return True
            else:
                print('Error: c specified for a street \"{0}\" that does not exist'.format(street), file=sys.stderr)
        else:
            print('Error: c command has no vertices specified', file=sys.stderr)

        return False

    def remove_street(self, street, *args):
        # type: (str, List[Tuple(int, int), ...]) -> Bool
        if street in self.history:
            del self.history[street]
            return True
        else:
            print('Error: r specified for a street \"{0}\" that does not exist'.format(street), file=sys.stderr)
        
        return False

    def render_graph(self):

        self.edges = set([])
        tmp_graph = {}
        tmp_intersections = set([])

        for street, points in self.history.iteritems():
            tmp_graph[street] = []

            # loop through edges of street
            for i in xrange(len(points)-1):
                tmp_p_to_add = [] #need this list because can have more than one intersection per segement
                
                #Loop through all other streets to find intersections
                for street_2, points_2 in self.history.iteritems():
                    if street != street_2:
                        # loop through other streets segments
                        for j in xrange(len(points_2)-1):
                            inter_p = intersect(points[i], points[i+1], points_2[j], points_2[j+1])
                            if inter_p:
                                [tmp_intersections.add(x) for x in inter_p]
                                [tmp_p_to_add.append(x) for x in inter_p if (x != points[i] and x != points[i+1])]
                        
                # add first point of segement if valid
                if (points[i] in tmp_intersections #first point is an intersection
                        or points[i+1] in tmp_intersections #next point is an intersection
                        or len(tmp_p_to_add) > 0 #there exists an intersection with the segment
                        or (tmp_graph[street] or [None])[-1] in tmp_intersections): #previous point is an intersection
                    tmp_graph[street].append(points[i])

                # insert all intersections by order of distance to segment if more than one
                if len(tmp_p_to_add) > 1:
                    tmp_p_to_add = list(set(tmp_p_to_add)) # remove duplicates
                    tmp_dist = [distance(p, points[i]) for p in tmp_p_to_add]
                    tmp_dist, tmp_p_to_add = zip(*sorted(zip(tmp_dist, tmp_p_to_add))) # sort the list by distance
                for tmp_p in tmp_p_to_add:
                    tmp_graph[street].append(tmp_p)

            #add last point if valid
            if (tmp_graph[street] or [None])[-1] in tmp_intersections:
                tmp_graph[street].append(points[-1])
        
        #remove all points from graph that are not in new graph
        to_remove = set([])
        for _, v in tmp_graph.iteritems():
            [to_remove.add(x) for x in v]
        to_remove = set(self.vertices.keys()) - tmp_intersections
        {self.vertices.pop(x) for x in to_remove}
        self.intersections = tmp_intersections

        # add remaining points that dont yet have an id
        i = 1
        for street, vertices in tmp_graph.iteritems():
            prev = None
            for index, vertex in enumerate(vertices):
                # if vertex doesnt exist, add it
                if vertex not in self.vertices:
                    #find an id that isn't used
                    while i in self.vertices.values():
                        i +=1
                    self.vertices[vertex] = i

                # create edge if valid
                v_id = self.vertices[vertex]
                if(index > 0 and (vertex in self.intersections or prev in self.intersections) ):
                    self.edges.add(frozenset([v_id, self.vertices.get(prev)]))
                prev = vertex

        return
    
def parse(args, func):
    """return a list [street, [list of points]]
        returns False if Error
    """
    if not args:
        print('Error: invalid input', file=sys.stderr)
        return False
    try:
        tmp = shlex.split(args)
    except:
        print('Error: Invalid input', file=sys.stderr)
        return False

    street = tmp[0].lower()
    if re.search(r'[^A-Za-z0-9 ]', street):
        print('Error: Invalid character used in street name', file=sys.stderr)
        return False

    if len(tmp) > 1:
        if func == 'do_r':
            print('Error: r command has too many arguments', file=sys.stderr)
            return False
        vertices = ''.join(tmp[1:])
        if re.search(r'[^0-9,\(\)\- ]', vertices):
            print('Error: Invalid character used in vertices', file=sys.stderr)
            return False
        
        #Check all vertices have open and closing parentheses
        open_paren_count = vertices.count('(')
        close_paren_count = vertices.count(')')
        if open_paren_count != close_paren_count:
            print('Error: Vertices entered are missing a parenthesis', file=sys.stderr)
            return False

        # match everything between '(' and ')'
        regex = r'\((.*?)\)+?'
        vertices = re.findall(regex, vertices)
        parsed_vertices = []
        
        # Cast all inputs to tuples of type int
        try:        
            for vertex in vertices:
                coords = vertex.split(',')
                if len(coords) != 2:
                    raise Exception
                parsed_vertices.append(tuple([int(x) for x in coords]))  
        except:
            print('Error: Vertices entered could not be parsed', file=sys.stderr)
            return False
        
        if (len(parsed_vertices) == 0 or
            len(parsed_vertices) != open_paren_count):
            
            print('Error: No valid vertices were entered', file=sys.stderr)
            return False

        return [street, parsed_vertices]
    
    else:
        return [street, None]
 
    return False

def distance(p1, p2):
    p1x, p1y = p1
    p2x, p2y = p2

    dist = math.sqrt((p1x-p2x)**2 + (p1y-p2y)**2)
    return dist

def intersect(p_1, p_2, p_3, p_4):
    # type: (Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]) -> list[Tuple[float, float] ...]

    x1, y1 = p_1[0], p_1[1]
    x2, y2 = p_2[0], p_2[1]
    x3, y3 = p_3[0], p_3[1]
    x4, y4 = p_4[0], p_4[1]

    seg1_xmin = min(x1,x2)
    seg1_xmax = max(x1,x2)
    seg2_xmin = min(x3,x4)
    seg2_xmax = max(x3,x4)
    seg1_ymin = min(y1,y2)
    seg1_ymax = max(y1,y2)
    seg2_ymin = min(y3,y4)
    seg2_ymax = max(y3,y4)
    x_interval = (max(seg1_xmin, seg2_xmin), min(seg1_xmax, seg2_xmax))
    y_interval = (max(seg1_ymin, seg2_ymin), min(seg1_ymax, seg2_ymax))

    # check for vertical overlapping lines
    if x1 == x2 == x3 == x4:
        pnts = [p_1,p_2,p_3,p_4]
        intersections = []
        for pnt in pnts:
            if y_interval[0] <= pnt[1] <= y_interval[1]:
                intersections.append(pnt)
        return intersections

    # check equations of lines
    elif x1 != x2 and x3 != x4:
        m1 = (y2-y1)/(x2-x1)
        b1 = y1-m1*x1
        m2 = (y4-y3)/(x4-x3)
        b2 = y3-m2*x3   
        # check if line equations are equal
        if m1 == m2 and b1 == b2:
            pnts = [p_1,p_2,p_3,p_4]
            intersections = []
            for pnt in pnts:
                if (x_interval[0] <= pnt[0] <= x_interval[1] and
                    y_interval[0] <= pnt[1] <= y_interval[1]):
                    intersections.append(pnt)
            return intersections

    xnum = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4))
    xden = ((x1-x2)*(y3-y4) - (y1-y2)*(x3-x4))

    ynum = (x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)
    yden = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    try:
        xcoor =  xnum / xden    
        ycoor = ynum / yden
    except ZeroDivisionError:
        return []

    if (xcoor < x_interval[0] or xcoor > x_interval[1] or
        ycoor < y_interval[0] or ycoor > y_interval[1]):
        return []

    return [(round(xcoor,2), round(ycoor,2))]

def main(args):
    program = ProgramLoop()
    program.cmdloop()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

'''
test inputs:
a "Weber Street" (2,-1) (2,2) (5,5) (5,6) (3,8)
a "King Street S" (4,2) (4,8)
a "Davenport Road" (1,4) (5,8)
g
c "Weber Street" (2,1) (2,2)
g
r "King Street S"
g
'''