# simple_methods.py
# Sara Fish
# Aug 15 2019

# Description: This file contains all simple methods used in l1_linfty.py
# None of these methods need any norm-specific functions

import math
import itertools
import time

def print_mathematica(points):
    """Prints the set of points in a Mathematica-friendly way.
    (Writing the point (1,2) as {1,2} instead.)
    Input: <points>, set or list of points
    Output: void (prints)"""
    points = list(points)
    for p in points[:-1]:
        print("{"+str(p[0]) + "," + str(p[1]) + "}",end="")
        print(",",end=" ")
    print("{"+str(points[-1][0]) + "," + str(points[-1][1]) + "}")

def is_line(p1, p2, p3):
    """Determines whether p1, p2, p3 lie on a line.
    Input: <p1>, <p2>, <p3> points
    Output: True if they lie on a line, False otherwise"""
    return (p1[0] - p2[0]) * ( p2[1] - p3[1] ) == (p1[1] - p2[1] ) * ( p2[0] - p3[0] )

def in_grid(p, grid_size):
    """Determines whether point <p> is in the grid with size <grid_size>
    Note: grid_size = 2 means a grid with 9 points: (0,0) through (2,2).
    Input: <p> point, <grid_size>
    Output: True if <p> in grid, False otherwise"""
    if not p:# if p is None
        return False
    return (0 <= p[0]) and (0 <= p[1]) and (p[0] <= grid_size) and (p[1] <= grid_size)

def increment_point( point, grid_size ):
    """Returns <point> incremented lexicographically in grid <grid_size>
    Input: <point> point
           <grid_size>
    Output: point (incremented), or None if cannot be incremented"""
    if not in_grid(point, grid_size):
        return None
    if point[1] == grid_size:
        if point[0] == grid_size:
            return None
        else:
            return ( point[0] + 1, 0)
    else:
        return ( point[0], point[1] + 1)

def forbidden_line_points(p1, p2, grid_size):
    """Returns all points that lie on the line determined by <p1>, <p2> and
    in <grid_size>.
    Input: <p1>, <p2> points
    Output: a set of points"""
    if p1 == p2: # This shouldn't happen
        raise ValueError
    mult = math.gcd( p1[0] - p2[0], p1[1] - p2[1] )
    # step is "step" of line
    step = (  int ( (p1[0] - p2[0])/mult ), int( (p1[1] - p2[1])/mult ) )
    if step[0] < 0:
        step = ( - step[0], - step[1] )
    # Find leftmost point on line
    left_pt = p1
    while in_grid( ( left_pt[0] - step[0], left_pt[1] - step[1] ) , grid_size):
        left_pt = ( left_pt[0] - step[0], left_pt[1] - step[1] )
    # Create list of points on line
    line_pts = [ left_pt ]
    while in_grid( ( line_pts[-1][0] + step[0], line_pts[-1][1] + step[1] ), grid_size ):
        line_pts.append( ( line_pts[-1][0] + step[0], line_pts[-1][1] + step[1] ) )
    return set( line_pts )

def find_grid_size(points):
    """Finds grid size containing set of points
    Input: <points>, list or set of points
    Output: grid_size (integer)"""
    grid_size = 0
    for p in points:
        grid_size = max( grid_size, p[0], p[1] )
    return grid_size 
