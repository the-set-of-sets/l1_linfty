# linfty_methods.py
# Sara Fish
# Aug 15 2019

# Description: This file contains all methods used for Linfty.
# It is imported into l1_linfty.

import math
import itertools
import time

import simple_methods

def linfty_dist(p1, p2):
    '''Computes linfty distance between p1 and p2.
    Input: p1, p2 points
    Output: distance'''
    return max( abs(p1[0] - p2[0]), abs(p1[1] - p2[1] ) )

def linfty_reflect_pt(p):
    """Returns reflected point <p>, about the line y = x
    Input: <p> point
    Output: reflected point (about y = x)"""
    return ( p[1], p[0] )


def linfty_reorder_points(p1, p2, p3):
    """Returns the points p1, p2, p3, reordered and reflected.
    If there is shared coord pair: Set q1, q2 to be equal in the y coord, and
    q1[0] < q2[0].
    Input: <p1>, <p2>, <p3> points
    Output: [q1, q2, q3, isReflected] where
            q1, q2, q3 is p1, p2, p3 reordered
            isReflected is True / False, whether p1, p2, p3 were reflected """
    if p1 == p2 or p2 == p3 or p1 == p3:
        raise ValueError
    for p,q,r in [(p1,p2,p3), (p1,p3,p2), (p2,p3,p1) ]:
        if p[1] == q[1]:
            if p[0] < q[0]:
                return [p, q, r, False]
            else:
                return [q, p, r, False]
        if p[0] == q[0]:
            q1 = linfty_reflect_pt(p)
            q2 = linfty_reflect_pt(q)
            q3 = linfty_reflect_pt(r)
            if q1[0] < q2[0]:
                return [q1, q2, q3, True]
            else:
                return [q2, q1, q3, True]
    # Otherwise, they do not share any coordinate. Order such that max distance is
    # determined by q1 q2 and in the y coord.
    square_diameter = 0
    for p, q, r in [(p1,p2,p3), (p1,p3,p2), (p2,p3,p1) ]:
        if abs( p[1] - q[1] ) > square_diameter:
            isReflected = False
            square_diameter = abs( p[1] - q[1] )
            if q[1] > p[1]:
                q1, q2, q3 = p, q, r
            else:
                q1, q2, q3 = q, p, r
        if abs( p[0] - q[0] ) > square_diameter:
            isReflected = True
            square_diameter = abs( p[0] - q[0] )
            if q[0] > p[0]:
                q1, q2, q3 = linfty_reflect_pt(p), linfty_reflect_pt(q), linfty_reflect_pt(r)
            else:
                q1, q2, q3 = linfty_reflect_pt(q), linfty_reflect_pt(p), linfty_reflect_pt(r)
    # Now q1, q2, q3 is the arrangement of p,q,r (possibly reflected) such that
    # max distance is determined by q1 q2 and mesaured in y coord. Also q2 is above q1.
    return [q1, q2, q3, isReflected]

def linfty_find_bad_circles(p1, p2, p3, grid_size):
    """Returns all bad circles that lie on a circle wih <p1>, <p2>, <p3>
    Input: <p1>, <p2>, <p3> points, <grid_size>
    Output: a list of things of the form [ (center), diameter]
            and also <isReflected>, whether we computed this reflected."""
    if p1 == p2 or p2 == p3 or p1 == p3:
        raise ValueError
    # First reorder.
    q1, q2, q3, isReflected = linfty_reorder_points(p1, p2, p3)
    bad_circles = []
    if q1[1] != q2[1]:
        # Since we reordered, they do not share any coordinate.
        square_diameter = q2[1] - q1[1]
        if q3[0] < q1[0]:
            bottom_left = ( q3[0], q1[1] )
            bad_circles.append( [bottom_left, square_diameter] )
        elif q3[0] == q1[0] or q3[0] == q2[0]:
            raise ValueError # this shouldn't happen
        elif q3[0] > q1[0] and q3[0] < q2[0]:
            # No circle. bad_circles stays empty
            pass
        elif q3[0] > q2[0]:
            bottom_left = ( q3[0] - square_diameter , q2[1] - square_diameter)
            bad_circles.append ( [bottom_left, square_diameter] )
    else:
        # q1[1] = q2[1], q1[0] < q2[0]
        if q3[1] == q1[1]:
            raise ValueError
            # this shouldn't happen
        if q1[0] < q3[0] and q3[0] < q2[0]:
            if q2[0] - q1[0] > abs( q1[1] - q3[1] ):
                #Fixed diameter, one circle.
                square_diameter = q2[0] - q1[0]
                if q3[1] < q1[1]:
                    bottom_left = ( q1[0], q3[1])
                else:
                    top_left = (q1[0], q3[1])
                    bottom_left = ( top_left[0], top_left[1] - square_diameter)
                bad_circles.append( [ bottom_left, square_diameter] )
            else:
                #Fixed diameter, many circles (can be "shifted")
                square_diameter = abs( q1[1] - q3[1] )
                left_x = [i for i in range(q2[0] - square_diameter, q1[0] + 1)]
                if q3[1] < q1[1]:
                    bottom_y = q3[1]
                else:
                    bottom_y = q1[1]
                bad_circles.extend( [[(i, bottom_y), square_diameter] for i in left_x ] )
        else:# q1[0] >= q3[0] or q2[0] <= q3[0], q3 on "outside" of segment
            # Points define a "corner", can make lots of circles.
            if q3[0] <= q1[0] and q3[1] > q1[1]:
                min_square_diameter = max( q2[0] - q3[0], q3[1] - q1[1])
                bottom_left = (q3[0], q1[1])
                bad_circles = [ [bottom_left, d]
                                for d in range(min_square_diameter, grid_size + 1) ]
            elif q3[0] <= q1[0] and q3[1] < q1[1]:
                min_square_diameter = max( q2[0] - q3[0], q1[1] - q3[1])
                top_left = (q3[0], q1[1])
                bad_circles = [ [(top_left[0], top_left[1] - d), d]
                                for d in range(min_square_diameter, grid_size + 1) ]
            elif q3[0] >= q2[0] and q3[1] > q1[1]:
                min_square_diameter = max( q3[0] - q1[0], q3[1] - q1[1])
                bottom_right = (q3[0], q1[1])
                bad_circles = [ [(bottom_right[0] - d, bottom_right[1]), d]
                                for d in range(min_square_diameter, grid_size + 1)]
            elif q3[0] >= q2[0] and q3[1] < q1[1]:
                min_square_diameter = max( q3[0] - q1[0], q1[1] - q3[1])
                top_right = (q3[0], q1[1])
                bad_circles = [ [(top_right[0] - d, top_right[1] - d), d]
                                for d in range(min_square_diameter, grid_size + 1)]
            # Points define a corner, but abs( q3[1] - q1[1] ) > q2[0] - q1[0]
            # so we can also slide
            if abs(q1[1] - q3[1]) > max( abs(q1[0] - q3[0]), abs(q2[0] - q3[0])):
                square_diameter = abs(q1[1] - q3[1])
                if q3[0] <= q1[0]:
                    left_x = [i for i in range(q3[0], q2[0] - square_diameter + 1) ]
                    if q3[1] >= q1[1]:
                        bottom_y = q1[1]
                    else:
                        bottom_y = q3[1]
                    bad_circles.extend( [ [(i, bottom_y), square_diameter] for i in left_x])
                else:
                    left_x = [i for i in range(q3[0] - square_diameter, q1[0] + 1)]
                    if q3[1] >= q1[1]:
                        bottom_y = q1[1]
                    else:
                        bottom_y = q3[1]
                    bad_circles.extend( [ [(i,bottom_y), square_diameter] for i in left_x ] )
    return [bad_circles, isReflected]

def linfty_forbidden_circle_points(p1, p2, p3, grid_size):
    """Returns all points which lie on bad_circles in a grid <grid_size>
    Input: p1, p2, p3 points
           grid_size
    Output: Set of points (which are verified to lie in grid)
    """
    bad_circles, isReflected = linfty_find_bad_circles(p1, p2, p3, grid_size)
    forbidden_pts = set()
    for circle in bad_circles:
        # Undo reflection.
        if isReflected:
            bottom_left = ( circle[0][1], circle[0][0] )
        else:
            bottom_left = circle[0]
        # Compute circles.
        diam = circle[1]
        bottom_right = (bottom_left[0] + diam, bottom_left[1])
        top_left = (bottom_left[0], bottom_left[1] + diam)
        top_right = (bottom_left[0] + diam, bottom_left[1] + diam)
        p1,p2,p3,p4 = bottom_left, bottom_right, top_right, top_left
        for i in range(diam):
            for p in [p1,p2,p3,p4]:
                if simple_methods.in_grid(p, grid_size):
                    forbidden_pts.add(p)
            # Increment p1,p2,p3,p4
            p1 = (p1[0] + 1, p1[1])
            p2 = (p2[0], p2[1] + 1)
            p3 = (p3[0] - 1, p3[1])
            p4 = (p4[0], p4[1] - 1)
    return forbidden_pts

def linfty_ball_points(center, radius, grid_size):
    """Returns set of points lying on the ball with <center>, <radius> on
        <grid_size>
    Input: center, point with integer coordinates
           radius, integer
           grid_size
    Output: set of points """
    ball_pts = set()
    bottom_left = ( center[0] - radius, center[1] - radius )
    bottom_right = ( center[0] + radius, center[1] - radius )
    top_right = ( center[0] + radius, center[1] + radius )
    top_left = ( center[0] - radius, center[1] + radius )
    p1,p2,p3,p4 = bottom_left, bottom_right, top_right, top_left
    for i in range(2*radius):
        for p in [p1,p2,p3,p4]:
            if simple_methods.in_grid(p, grid_size):
                ball_pts.add(p)
        # Increment p1, p2, p3, p4
        p1 = (p1[0] + 1, p1[1])
        p2 = (p2[0], p2[1] + 1)
        p3 = (p3[0] - 1, p3[1])
        p4 = (p4[0], p4[1] - 1)
    return ball_pts
