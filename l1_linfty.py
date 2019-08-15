# l1_infty.py
# Sara Fish
# Jul 31 2019 - Aug 15 2019

# Description: This code finds crescent configurations in L1 and Linfty.
# Algorithm: backtracking.
# This code is currently not optimized, but it already quickly produces crescent
# configurations in Linfty of size n for 4 <= n <= 8 and in L1 of size n for
# 4 <= n <= 7. This is reasonable because we conjecture that they do not exist
# in Linfty for n >= 9 and in L1 for n >= 8.

# Standard libraries
#############################################
import sys
import math
import itertools
import time

# Other files used:
#############################################
# simple_methods contains helper functions which don't depend on norm
import simple_methods
# L1_methods contains l1 specific methods
import l1_methods
# Linfty_methods contains linfty specific methods
import linfty_methods

#####################################################
#####################################################
######      Splitter functions ######################
#####################################################
#####################################################

def forbidden_circle_points(norm, p1, p2, p3, grid_size):
    if norm == 1:
        return l1_methods.l1_forbidden_circle_points(p1, p2, p3, grid_size)
    elif norm == 0:
        return linfty_methods.linfty_forbidden_circle_points(p1, p2, p3, grid_size)
    else:
        return set()

def ball_points(norm, center, radius, grid_size):
    if norm == 1:
        return l1_methods.l1_ball_points(center, radius, grid_size)
    elif norm == 0:
        return linfty_methods.linfty_ball_points(center, radius, grid_size)
    else:
        return set()

def dist(norm, a, b):
    if norm == 1:
        return l1_methods.l1_dist(a,b)
    elif norm == 0:
        return linfty_methods.linfty_dist(a,b)

#####################################################
#####################################################
######      Methods depending on norm  ##############
#####################################################
#####################################################

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
        bad_line_pts = simple_methods.forbidden_line_points(p,q,grid_size)
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

# def is_general_fast(points, sto_forbidden_line_points,
#             sto_forbidden_circle_points, sto_is_line_like, printFail = False):
#     """ Determines whether a set of points is in general position.
#     WARNING: (these lists) have to be precomputed
#     WARNING: assumes points[:-1] is in general position, only checks last pt
#     Input: <points>, list of points
#            <sto_forbidden_line_points>, dict, key (a1,a2,b1,b2), value
#                                         set of points which lie on line with a,b
#            <sto_forbidden_circle_points>, dict, key (a1,a2,b1,b2,c1,c2), value
#                                         set of point on circle with a,b,c
#            <sto_is_line_like>, set, set of all (a1,a2,b1,b2,c1,c2,d1,d2) which
#                                     are line-like
#            <printFail>: print the reason it's not in general position, if it
#                         isn't. (e.g. line, circle, linelike)
#     Output: True/False (and printing if <printFail> is True)
#     """
#     # No 3 points on a line
#     for p,q,r in itertools.combinations(points, 3):
#         if r in sto_forbidden_line_points[p + q]:
#             if printFail:
#                 print("Line found: ", p, q, r)
#             return False
#     # No 4 points on circle
#     for p,q,r,s in itertools.combinations(points, 4):
#         if s in sto_forbidden_circle_points[p + q + r]:
#             if printFail:
#                 print("Circle found: ", p, q, r, s)
#             return False
#     # No 4 points in line-like
#     for p,q,r,s in itertools.combinations(points, 4):
#         if p+q+r+s in sto_is_line_like:
#             if printFail:
#                 print("Line-like found: ",p, q, r, s)
#             return False
#     return True
#     # last = points[-1]
#     # # Check no 3 points on a line.
#     # for p,q in itertools.combinations(points, 2):
#     #     bad_line_pts = sto_forbidden_line_points[p + q]
#     #     if last in bad_line_pts and last != p and last != q:
#     #         if printFail:
#     #             print("Line found: ",p,q,last)
#     #         return False
#     # # Check no 4 points on a circle.
#     # for p,q,r in itertools.combinations(points, 3):
#     #     bad_circle_pts = sto_forbidden_circle_points[p + q + r]
#     #     if last in bad_circle_pts and last != p and last != q and last != r:
#     #         if printFail:
#     #             print("Circle found: ",p,q,r,last)
#     #         return False
#     # # Check if has a line like configuration of size 4.
#     # for p,q,r in itertools.combinations(points, 3):
#     #     if p+q+r+last in sto_is_line_like:
#     #         if printFail:
#     #             print("Has line-like:",p,q,r,last)
#     #         return False
#     # Otherwise, is in general position.
#     return True


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

def is_line_like(norm, p1, p2, p3, p4):
    """ Determines whether p1, p2, p3, p4 form a line-like configuration.
    Input:  <norm>, 1 if L1, 0 if Linfty
            <p1>, <p2>, <p3>, <p4>, points
    Output: True/False, whether it is line-like
            (Actually returns line-like config if true)"""
    pts = [p1, p2, p3, p4]
    if has_crescent_dist(norm, pts):
        for perm in itertools.permutations(range(4)):
            if (dist(norm, pts[perm[0]], pts[perm[1]]) == dist(norm, pts[perm[1]], pts[perm[2]])
                and dist(norm, pts[perm[1]], pts[perm[2]]) == dist(norm, pts[perm[2]], pts[perm[3]])
                and dist(norm, pts[perm[0]], pts[perm[2]]) == dist(norm, pts[perm[1]], pts[perm[3]]) ):
                return [pts[perm[i]] for i in range(4)]


def has_line_like(norm, points):
    """ Determines whether a set of points contains a line-like config of size 4
    Input: <points>, a set of points
    Output: True / False (actually returns line-like config if true)"""
    for pts in itertools.combinations(points, 4):
        a = is_line_like(norm, pts[0], pts[1], pts[2], pts[3] )
        if a:
            return a
    return False


def find_crescent_set(norm, crescent_size, grid_size, sto_values):
    """ Finds a crescent set of size <crescent_size> in <grid_size>.
    Input: <norm>, 1 if L1, 0 if Linfty
           <crescent_size>, size of crescent set.
           <grid_size>, size of grid.
           <sto_values>, list with three items, which contain
                <sto_forbidden_line_points>, dict, key (a1,a2,b1,b2), value
                                    set of points which lie on line with a,b
                <sto_forbidden_circle_points>, dict, key (a1,a2,b1,b2,c1,c2),
                                    value set of point on circle with a,b,c
                <sto_is_line_like>, set, set of all (a1,a2,b1,b2,c1,c2,d1,d2)
                                    which are line-like
    Output: Set of points (crescent set), or None if none exists.
    """
    # sto_forbidden_line_points, sto_forbidden_circle_points, sto_is_line_like = sto_values
    count = 0
    start = time.time()
    current_set = []
    next_to_add = (0,0)
    while next_to_add:
        count += 1
        if count % 100000 == 0:
            print(time.time() - start,current_set)
        current_set.append(next_to_add)
        needs_pop = False # whether last element needs to be popped

        # #TODO
        # aa = is_general(norm, current_set,False)
        # bb = is_general_fast(current_set, sto_forbidden_line_points, sto_forbidden_circle_points, sto_is_line_like,False)
        # if aa != bb:
        #     print(current_set)
        #     print("good",aa)
        #     is_general(norm, current_set,True)
        #     print("fast",bb)
        #     is_general_fast(current_set, sto_forbidden_line_points, sto_forbidden_circle_points, sto_is_line_like,True)
        #     print()



        if not is_general(norm, current_set):
        #if not is_general_fast(current_set, sto_forbidden_line_points, sto_forbidden_circle_points, sto_is_line_like):
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
            next_next_to_add = simple_methods.increment_point(next_to_add, grid_size)
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
######      Sto init function  ######################
#####################################################
#####################################################

def init_sto(norm, grid_size, printStuff = False):
    """
    Input:  <norm> 1 if L1, 0 if Linfty
            <grid_size>
            <printStuff>, whether to print time, which step we are doing, etc
    Output: <sto_values>, which is a list of three things:
                <sto_forbidden_line_points>, dict, key (a1,a2,b1,b2), value
                                    set of points which lie on line with a,b
                <sto_forbidden_circle_points>, dict, key (a1,a2,b1,b2,c1,c2),
                                    value set of point on circle with a,b,c
                <sto_is_line_like>, set, set of all (a1,a2,b1,b2,c1,c2,d1,d2)
                                    which are line-like
    """
    start_time = time.time()
    if printStuff:
        if norm == 1:
            printable_norm = "L1"
        elif norm == 0:
            printable_norm = "Linfty"
        print("Precomputing for", grid_size, " x ", grid_size, " grid in", printable_norm, sep='')
    # Compute grid
    grid = [ (i,j) for i in range(grid_size + 1) for j in range(grid_size + 1) ]
    # Lines
    sto_forbidden_line_points = dict()
    if printStuff:
        print("Precomputing lines...")
    for a,b in itertools.combinations(grid, 2):
        sto_forbidden_line_points[a+b] = simple_methods.forbidden_line_points(a, b, grid_size)
        sto_forbidden_line_points[b+a] = sto_forbidden_line_points[a+b]
    if printStuff:
        print("DONE in",time.time() - start_time)
    start_time = time.time()
    # Circles
    sto_forbidden_circle_points = dict()
    if printStuff:
        print("Precomputing circles...")
    for a,b,c in itertools.combinations(grid, 3):
        if is_line(a,b,c):
            bad_points = set()
        else:
            bad_points = forbidden_circle_points(norm, a, b, c, grid_size)
        for p1, p2, p3 in itertools.permutations([a,b,c], 3):
            sto_forbidden_circle_points[p1+p2+p3] = bad_points
    if printStuff:
        print("DONE in", time.time() - start_time)
    start_time = time.time()
    print( sto_forbidden_circle_points[0,0,0,1,2,1] )
    # Line-like configs
    sto_is_line_like = set()
    if printStuff:
        print("Precomputing line-like configs...")
    for a,b,c,d in itertools.combinations(grid, 4):
        if is_line_like(norm,a,b,c,d):
            for p1, p2, p3, p4 in itertools.permutations([a,b,c,d], 4):
                sto_is_line_like.add(p1+p2+p3+p4)
    if printStuff:
        print("DONE in", time.time() - start_time)
    print( sto_forbidden_circle_points[0,0,0,1,2,1] )
    return [sto_forbidden_line_points, sto_forbidden_circle_points, sto_is_line_like]

#####################################################
#####################################################
######      Main  ###################################
#####################################################
#####################################################

def print_usage(args):
    print("Usage: python3 "+args[0]+" <norm>"+" <crescent_size>"+" <grid_size>")
    print("norms: l1, linfty")
    print("\t l1: L1 (taxicab metric).")
    print("\t linfty: Linfty (sup metric).")
    print("crescent_size: Size of crescent set being searched for.")
    print("grid_size: Searches grid from (0,0) to (grid_size, grid_size)")

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print_usage(sys.argv)
    elif len(sys.argv) >= 4:
        mode = sys.argv[1]
        try:
            crescent_size = int(sys.argv[2])
            grid_size = int(sys.argv[3])
        except ValueError:
            print_usage(sys.argv)
        # Detect norm.
        norm = None
        if mode == "l1":
            norm = 1
        elif mode == "linfty":
            norm = 0
        # If norm valid, run.
        if norm == None:
            print_usage(sys.argv)
        else:
            sto_values = []
            # sto_values = init_sto(norm, grid_size, True)
            # print( sto_values[1][0,0,0,1,2,1] )
            # print( sto_values[1][0,1,0,0,2,1] )
            # print( sto_values[1][0,1,2,1,0,0] )
            # print()
            # for i in sto_values[1]:
            #     a = ( i[0], i[1] )
            #     b = (i[2], i[3] )
            #     c = (i[4], i[5])
            #     if a != b and a != c and b != c and not is_line(a,b,c):
            #             if sto_values[1][i] != forbidden_circle_points(norm, a, b, c, grid_size ):
            #                 print(i)
            #                 print( sto_values[1][i] )
            #                 print(a, b, c)
            #                 print("stored", sto_values[1][i] );
            #                 print("real",forbidden_circle_points(norm, a, b, c, grid_size ))
            #                 print()
            #                 input()
            find_crescent_set( norm, crescent_size, grid_size, sto_values)
