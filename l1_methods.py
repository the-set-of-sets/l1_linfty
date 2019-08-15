# l1_methods.py
# Sara Fish
# Aug 15 2019

# Description: This file contains all methods used for L1.
# It is imported into l1_linfty.

import math
import itertools
import time

import simple_methods

def l1_dist(p1, p2):
    """Computes L1 distance between <p1> and <p2>.
    Input: <p1>, <p2> points
    Output: integer distance"""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1] )

def l1_is_slope_plus1(p1, p2):
    """Determines whether <p1> and <p2> lie on a line of slope +1.
    Input: <p1>, <p2> points
    Output: True / False """
    return p2[1] - p1[1] == p2[0] - p1[0]

def l1_is_slope_minus1(p1, p2):
    """Determines whether <p1> and <p2> lie on a line of slope -1.
    Input: <p1>, <p2> points
    Output: True / False"""
    return p2[1] - p1[1] == p1[0] - p2[0]

def l1_double_point(p):
    """Returns <p> with doubled coordinates.
    Example: (1,1) becomes (2,2). This is used for technical reasons so we don't
    have to deal with half-integer coordinates.
    Input: <p> point
    Output: <p> point (doubled)"""
    return (p[0] * 2, p[1] * 2)

def l1_is_double_point(p):
    """Returns whether <p> is a doubled point.
    Input: <p> point
    Output: True / False (True if is point with doubled coords)"""
    return p[0] % 2 == 0 and p[1] % 2 == 0

def l1_halve_point(p):
    """Returns <p> with halved coordinates. If <p> is not a double point, None.
    Input: <p> point
    Output: point (if <p> double), None (otherwise)"""
    if l1_is_double_point(p):
        return ( p[0] //2, p[1] // 2)
    else:
        return None

def l1_find_bad_double_circles(p1, p2, grid_size):
    """Returns a list of pairs [center, radius]. These are circles that
    contain p1, p2, with centers in grid_size. <center>, <radius> are integers.
    Input: <p1>, <p2> (points, only works as intended with DOUBLE points,
                       otherwise it misses circles.)
           <grid_size>
    Output: List of [center, radius], where center,radius are integers. """
    if p1[0] > p2[0]:
        p1, p2 = p2, p1
    # Can assume p1[0] <= p2[0]
    bad_circles = []
    if abs( p1[0] - p2[0] ) == abs( p1[1] - p2[1] ):
        return []# this shouldn't happen
    elif abs( p1[1] - p2[1] ) > abs( p1[0] - p2[0] ):
        if p1[1] > p2[1]:
            left_center = (p1[0], (p1[1] + p2[1] + p1[0] - p2[0])//2 )
            right_center = (p2[0], (p1[1] + p2[1] - p1[0] + p2[0])//2 )
        else:# p2[1] >= p1[1]
            left_center = (p1[0], (p1[1] + p2[1] - p1[0] + p2[0])//2 )
            right_center = (p2[0], (p1[1] + p2[1] + p1[0] - p2[0])//2 )
        # Without loss of generality, can assume centers are in grid.
        # Without loss of generality, can assume centers are lattice pts.
        # (Second assumption only works if points are double coords.)
        while left_center[0] >= 0:
            bad_circles.append( [left_center, l1_dist(left_center, p1)] )
            left_center = (left_center[0] - 1, left_center[1])
        while right_center[0] <= grid_size:
            bad_circles.append( [right_center, l1_dist(right_center, p1)])
            right_center = (right_center[0] + 1, right_center[1])
    elif abs( p1[1] - p2[1] ) < abs( p1[0] - p2[0] ):
        if p1[1] > p2[1]:
            down_center   = ( (p1[0] + p2[0] - p1[1] + p2[1] )//2, p2[1])
            up_center  = ( (p1[0] + p2[0] + p1[1] - p2[1] )//2, p1[1])
        else:
            down_center = ( (p1[0] + p2[0] - p1[1] + p2[1] )//2, p1[1])
            up_center = ( (p1[0] + p2[0] + p1[1] - p2[1] )//2, p2[1])
        while up_center[1] <= grid_size:
            bad_circles.append( [up_center, l1_dist(up_center, p1)])
            up_center = (up_center[0], up_center[1] + 1)
        while down_center[1] >= 0:
            bad_circles.append( [ down_center, l1_dist(down_center, p1)])
            down_center = ( down_center[0], down_center[1] - 1)
    return bad_circles

def l1_forbidden_circle_points(p1, p2, p3, grid_size):
    """Returns all points which lie on bad circles in a grid <grid_size>
    Input: <p1>, <p2>, <p3> points
           <grid_size>
    Output: Set of points (which are verified to lie in grid)
    """
    plus_slope12 = l1_is_slope_plus1(p1, p2)
    plus_slope13 = l1_is_slope_plus1(p1, p3)
    plus_slope23 = l1_is_slope_plus1(p2, p3)
    minus_slope12 = l1_is_slope_minus1(p1, p2)
    minus_slope13 = l1_is_slope_minus1(p1, p3)
    minus_slope23 = l1_is_slope_minus1(p2, p3)
    # If not all 3 lie on a line, then there exist two points which are neither
    # on +1 slope nor -1 slope. Reorder them to q1, q2, q3 so that q1, q2 are
    # neither on +1 nor -1 slope.
    if not plus_slope12 and not minus_slope12:
        q1, q2, q3 = p1, p2, p3
    elif not plus_slope13 and not minus_slope13:
        q1, q2, q3 = p1, p3, p2
    elif not plus_slope23 and not minus_slope23:
        q1, q2, q3 = p2, p3, p1
    else:
        # This only happens if they lie on a line, which shouldn't happen.
        return set()
    # Compute two arcs up/right down/left determined by q1, q2. These arcs
    # contain all of the points in circles made by q1, q2.
    d1, d2, d3 = l1_double_point(q1), l1_double_point(q2), l1_double_point(q3)
    bad_circles = l1_find_bad_double_circles(d1, d2, grid_size*2)
    # If p3 in each circle, then forbid those points.
    forbidden_points = set()
    for circle in bad_circles:
        if l1_dist(d3, circle[0]) == circle[1]:
            doubled_circle_points = l1_ball_points(circle[0], circle[1], grid_size*2 )
            for p in doubled_circle_points:
                if l1_is_double_point(p):
                    forbidden_points.add(l1_halve_point(p))
    return forbidden_points

def l1_ball_points(center, radius, grid_size):
    """Returns set of points lying on the ball with <center>, <radius> on
    <grid_size>
    Input: <center> point, integer coordinates
           <radius>, integer
           <grid_size>
    Output: set of points """
    ball_pts = set()
    bottom = ( center[0] , center[1] - radius )
    right = ( center[0] + radius, center[1]  )
    top = ( center[0] , center[1] + radius )
    left = ( center[0] - radius, center[1]  )
    p1,p2,p3,p4 = bottom, right, top, left
    for i in range(radius):
        for p in [p1,p2,p3,p4]:
            if simple_methods.in_grid(p, grid_size):
                ball_pts.add(p)
        # Increment p1, p2, p3, p4
        p1 = (p1[0] + 1, p1[1] + 1)
        p2 = (p2[0] - 1, p2[1] + 1)
        p3 = (p3[0] - 1, p3[1] - 1)
        p4 = (p4[0] + 1, p4[1] - 1)
    return ball_pts
