# l1_infty.py
# Sara Fish
# Jul 31 2019

# Description: This code finds crescent configurations in L1 and Linfty.
# Algorithm: backtracking.
# This code is currently not optimized, but it already quickly produces crescent
# configurations in Linfty of size n for 4 <= n <= 8 and in L1 of size n for
# 4 <= n <= 7. This is reasonable because we conjecture that they do not exist
# in Linfty for n >= 9 and in L1 for n >= 8.

import sys
import math
import itertools
import time

#####################################################
#####################################################
######      Methods used in both L1 and Linfty ######
#####################################################
#####################################################

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
    return abs(p1[0] - p2[0]) * abs( p2[1] - p3[1] ) == abs(p1[1] - p2[1] ) * abs( p2[0] - p3[0] )

def in_grid(p, grid_size):
    """Determines whether point <p> is in the grid with size <grid_size>
    Note: grid_size = 2 means a grid with 9 points: (0,0) through (2,2).
    Input: <p> point, <grid_size>
    Output: True if <p> in grid, False otherwise"""
    if not p:# if p is None
        return False
    return (0 <= p[0]) and (0 <= p[1]) and (p[0] <= grid_size) and (p[1] <= grid_size)

def distance_set(norm, points):
    """Computes the distance set of a set of points <points>.
    Input: <norm>, 1 if L1, 0 if Linfty
           <points>, a set or list of points
    Output: returns a dict with pairs {distance: number of occurances}."""
    distances = dict()
    for a,b in itertools.combinations(points, 2):
        d = dist(norm, a,b)
        if d in distances.keys():
            distances[d] += 1
        else:
            distances[d] = 1
    return distances

def has_crescent_dist(norm, points):
    """Determines whether a set of points <points> has a 'crescent' distance
    set. This means that for 1 <= i <= len(points) - 1, the ith distance occurs
    i - 1 times.
    Input: <norm>, 1 if L1, 0 if Linfty
           <points>, a list of points
    Output: True if crescent distance set, False otherwise"""
    n = len(points)
    distances = distance_set(norm, points)
    return set(distances.values()) == set(range(1,n))

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

def forbidden_linelike_points(norm, p1, p2, p3, grid_size):
    """Returns set of points p in the grid <grid_size> which are forbidden
    because p, p1, p2, p3 (in any order) form a line-like configuration.
    Input: <norm>, 1 if L1, 0 if Linfty
           <p1>, <p2>, <p3> points
           <grid_size>
    Output: set of points """
    # Reorder p1, p2, p3 into q1, q2, q3 so that dist(q1, q2) = dist(q2, q3).
    if dist(norm, p1, p2) == dist(norm, p2, p3):
        q1, q2, q3 = p1, p2, p3
    elif dist(norm, p1, p2) == dist(norm, p1, p3):
        q1, q2, q3 = p2, p1, p3
    elif dist(norm, p1, p3) == dist(norm, p2, p3):
        q1, q2, q3 = p1, p3, p2
    else:
        return set()# p1, p2, p3 are not line-like, because they have no
                    # repeated distance
    # Otherwise, q1, q2, q3 are line-like and dist(q1, q2) = dist(q2, q3).
    forbidden_pts = set()
    for p,q,r in [(q1,q2,q3), (q3,q2,q1)]:
        # We are trying to add a fourth point s to make p q r s line-like.
        first_order = ball_points(norm, r, dist(p, q), grid_size)
        second_order = ball_points(norm, q, dist(p,r), grid_size)
        both = first_order.intersection(second_order)
        forbidden_pts = forbidden_pts.union(both)
    return forbidden_pts


def is_general(norm, points, printFail = False):
    """ Determines whether a set of points is in general position.
    (This means: no lines, balls, or line-like configs of size 4.)
    Input: <norm>: 1 for L1, 0 for Linfty
           <points>: a set of points
           <printFail>: print the reason it's not in general position if false
                        (default False)
    Output: True / False (whether in general position)"""
    # Find grid size.
    grid_size = 0
    for p in points:
        grid_size = max( grid_size, p[0], p[1] )
    # Check no 3 points on a line.
    for p,q in itertools.combinations(points, 2):
        bad_line_pts = forbidden_line_points(p,q,grid_size)
        if len( bad_line_pts.intersection(points) ) >= 3:
            if printFail:
                print("Line found: ",p,q,bad_line_pts.intersection(points))
            return False
    # Check no 4 points on a circle.
    for p,q,r in itertools.combinations(points, 3):
        bad_circle_pts = forbidden_circle_points(norm,  p,q,r, grid_size)
        if len( bad_circle_pts.intersection(points) ) >= 4:
            if printFail:
                print("Circle found: ",p,q,r,bad_circle_pts.intersection(points))
            return False
    # Check if has a line like configuration of size 4.
    a = has_line_like(norm, points)
    if a:
        if printFail:
            print("Has line-like.",a)
        return False
    # Otherwise, is in general position.
    return True


def is_crescent(norm, points, printFail = False):
    """ Determines whether a set of points is crescent.
    Crescent means: in general position, and has "crescent" distance set.
    Input: <norm>, 1 if L1, 0 if Linfty
           <points>, set of points
    Output: True / False """
    if not is_general(norm, points, printFail):
        return False
    if not has_crescent_dist(norm, points):
        if printFail:
            print("No crescent dist: ",distance_set(norm, points))
        return False
    return True



def has_line_like(norm, points):
    """ Determines whether a set of points contains a line-like config of size 4
    Input: <points>, a set of points
    Output: True / False """
    for pts in itertools.combinations(points, 4):
        if has_crescent_dist(norm, pts):
            for perm in itertools.permutations(range(4)):
                if (dist(norm, pts[perm[0]], pts[perm[1]]) == dist(norm, pts[perm[1]], pts[perm[2]])
                    and dist(norm, pts[perm[1]], pts[perm[2]]) == dist(norm, pts[perm[2]], pts[perm[3]])
                    and dist(norm, pts[perm[0]], pts[perm[2]]) == dist(norm, pts[perm[1]], pts[perm[3]]) ):
                    return [pts[perm[i]] for i in range(4)]
    return False


def find_crescent_set(norm, crescent_size, grid_size ):
    """ Finds a crescent set of size <crescent_size> in <grid_size>.
    Input: <norm>, 1 if L1, 0 if Linfty
           <crescent_size>, size of crescent set.
           <grid_size>, size of grid.
    Output: Set of points (crescent set), or None if none exists.
    """
    count = 0
    start = time.time()
    current_set = []
    next_to_add = (0,0)
    while next_to_add:
        count += 1
        if count % 10000 == 0:
            print(time.time() - start,current_set)
        current_set.append(next_to_add)
        # print(current_set)
        needs_pop = False # whether last element needs to be popped
        if not is_general(norm, current_set):
            needs_pop = True
        elif len( distance_set(norm, current_set) ) >= crescent_size:
            needs_pop = True
        elif len(current_set) >= crescent_size and has_crescent_dist(norm, current_set):
            print("Crescent found!", current_set)
            return current_set
        elif len(current_set) >= crescent_size:
            needs_pop = True
        if needs_pop:
            current_set.pop()# the popped element is next_to_add
        # Add next.
        have_added = False
        while not have_added and next_to_add:
            next_next_to_add = increment_point(next_to_add, grid_size)
            if next_next_to_add:
                next_to_add = next_next_to_add
                have_added = True
            elif current_set:
                next_to_add = current_set.pop()
            else:# current_set is empty, and next_to_add = (8,8)
                next_to_add = None# no crescent config, exist next
    print("No crescent set, try a bigger grid_size.")
    return None


#####################################################
#####################################################
######      Methods used in L1  #####################
#####################################################
#####################################################


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
            bad_circles.append( [left_center, dist(1, left_center, p1)] )
            left_center = (left_center[0] - 1, left_center[1])
        while right_center[0] <= grid_size:
            bad_circles.append( [right_center, dist(1, right_center, p1)])
            right_center = (right_center[0] + 1, right_center[1])
    elif abs( p1[1] - p2[1] ) < abs( p1[0] - p2[0] ):
        if p1[1] > p2[1]:
            down_center   = ( (p1[0] + p2[0] - p1[1] + p2[1] )//2, p2[1])
            up_center  = ( (p1[0] + p2[0] + p1[1] - p2[1] )//2, p1[1])
        else:
            down_center = ( (p1[0] + p2[0] - p1[1] + p2[1] )//2, p1[1])
            up_center = ( (p1[0] + p2[0] + p1[1] - p2[1] )//2, p2[1])
        while up_center[1] <= grid_size:
            bad_circles.append( [up_center, dist(1, up_center, p1)])
            up_center = (up_center[0], up_center[1] + 1)
        while down_center[1] >= 0:
            bad_circles.append( [ down_center, dist(1, down_center, p1)])
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
        doubled_circle_points = ball_points(1, circle[0], circle[1], grid_size*2 )
        if d3 in doubled_circle_points:
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
            if in_grid(p, grid_size):
                ball_pts.add(p)
        # Increment p1, p2, p3, p4
        p1 = (p1[0] + 1, p1[1] + 1)
        p2 = (p2[0] - 1, p2[1] + 1)
        p3 = (p3[0] - 1, p3[1] - 1)
        p4 = (p4[0] + 1, p4[1] - 1)
    return ball_pts

#####################################################
#####################################################
######      Methods used in Linfty  #################
#####################################################
#####################################################

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
                if in_grid(p, grid_size):
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
            if in_grid(p, grid_size):
                ball_pts.add(p)
        # Increment p1, p2, p3, p4
        p1 = (p1[0] + 1, p1[1])
        p2 = (p2[0], p2[1] + 1)
        p3 = (p3[0] - 1, p3[1])
        p4 = (p4[0], p4[1] - 1)
    return ball_pts

#####################################################
#####################################################
######      Splitter functions ######################
#####################################################
#####################################################

def forbidden_circle_points(norm, p1, p2, p3, grid_size):
    if norm == 1:
        return l1_forbidden_circle_points(p1, p2, p3, grid_size)
    elif norm == 0:
        return linfty_forbidden_circle_points(p1, p2, p3, grid_size)
    else:
        return set()

def ball_points(norm, center, radius, grid_size):
    if norm == 1:
        return l1_ball_points(center, radius, grid_size)
    elif norm == 0:
        return linfty_ball_points(center, radius, grid_size)
    else:
        return set()

def dist(norm, a, b):
    if norm == 1:
        return l1_dist(a,b)
    elif norm == 0:
        return linfty_dist(a,b)

#####################################################
#####################################################
######      Main  ###################################
#####################################################
#####################################################

if __name__ == "__main__":
    print_usage = False
    if len(sys.argv) <= 3:
        print_usage = True
    elif len(sys.argv) >= 4:
        mode = sys.argv[1]
        try:
            crescent_size = int(sys.argv[2])
            grid_size = int(sys.argv[3])
        except ValueError:
            print_usage = True
        if mode == "l1":
            find_crescent_set( 1, crescent_size, grid_size)
        elif mode == "linfty":
            find_crescent_set( 0, crescent_size, grid_size )
        else:
            print_usage = True
    if print_usage:
        print("Usage: python3 "+sys.argv[0]+" <norm>"+" <crescent_size>"+" <grid_size>")
        print("norms: l1, linfty")
        print("\t l1: L1 (taxicab metric).")
        print("\t linfty: Linfty (sup metric).")
        print("crescent_size: Size of crescent set being searched for.")
        print("grid_size: Searches grid from (0,0) to (grid_size, grid_size)")
