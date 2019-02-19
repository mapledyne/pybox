import numpy as np

# example:
# intersects_box(np.array([[20,9,44], [7,7,7], [8,8,8]]),
#                np.array([0,1,3]),
#                np.array([8,8,4]))


# based on
# http://www.gamedev.net/topic/
# 534655-aabb-triangleplane-intersection--distance-to-plane-
# is-incorrect-i-have-solved-it/
def intersects_box(triangle, box_center, box_extents):
    X, Y, Z = 0, 1, 2

    # Translate triangle as conceptually moving AABB to origin
    v0 = triangle[0] - box_center
    v1 = triangle[1] - box_center
    v2 = triangle[2] - box_center

    # Compute edge vectors for triangle
    f0 = triangle[1] - triangle[0]
    f1 = triangle[2] - triangle[1]
    f2 = triangle[0] - triangle[2]

    # Test axes a00..a22 (category 3)
    a00 = np.array([0, -f0[Z], f0[Y]])
    p0 = np.dot(v0, a00)
    p1 = np.dot(v1, a00)
    p2 = np.dot(v2, a00)
    r = box_extents[Y] * abs(f0[Z]) + box_extents[Z] * abs(f0[Y])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a01 = np.array([0, -f1[Z], f1[Y]])
    p0 = np.dot(v0, a01)
    p1 = np.dot(v1, a01)
    p2 = np.dot(v2, a01)
    r = box_extents[Y] * abs(f1[Z]) + box_extents[Z] * abs(f1[Y])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a02 = np.array([0, -f2[Z], f2[Y]])
    p0 = np.dot(v0, a02)
    p1 = np.dot(v1, a02)
    p2 = np.dot(v2, a02)
    r = box_extents[Y] * abs(f2[Z]) + box_extents[Z] * abs(f2[Y])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a10 = np.array([f0[Z], 0, -f0[X]])
    p0 = np.dot(v0, a10)
    p1 = np.dot(v1, a10)
    p2 = np.dot(v2, a10)
    r = box_extents[X] * abs(f0[Z]) + box_extents[Z] * abs(f0[X])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a11 = np.array([f1[Z], 0, -f1[X]])
    p0 = np.dot(v0, a11)
    p1 = np.dot(v1, a11)
    p2 = np.dot(v2, a11)
    r = box_extents[X] * abs(f1[Z]) + box_extents[Z] * abs(f1[X])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a11 = np.array([f2[Z], 0, -f2[X]])
    p0 = np.dot(v0, a11)
    p1 = np.dot(v1, a11)
    p2 = np.dot(v2, a11)
    r = box_extents[X] * abs(f2[Z]) + box_extents[Z] * abs(f2[X])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a20 = np.array([-f0[Y], f0[X], 0])
    p0 = np.dot(v0, a20)
    p1 = np.dot(v1, a20)
    p2 = np.dot(v2, a20)
    r = box_extents[X] * abs(f0[Y]) + box_extents[Y] * abs(f0[X])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a21 = np.array([-f1[Y], f1[X], 0])
    p0 = np.dot(v0, a21)
    p1 = np.dot(v1, a21)
    p2 = np.dot(v2, a21)
    r = box_extents[X] * abs(f1[Y]) + box_extents[Y] * abs(f1[X])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    a22 = np.array([-f2[Y], f2[X], 0])
    p0 = np.dot(v0, a22)
    p1 = np.dot(v1, a22)
    p2 = np.dot(v2, a22)
    r = box_extents[X] * abs(f2[Y]) + box_extents[Y] * abs(f2[X])
    if (max(-max(p0, p1, p2), min(p0, p1, p2))) > r:
        return False

    # three axes corresponding to the face normals of AABB b (category 1)

    # [-extents.X, extents.X] and
    # [min(v0.X,v1.X,v2.X), max(v0.X,v1.X,v2.X)] do not overlap
    if max(v0[X], v1[X], v2[X]) < -box_extents[X] \
          or min(v0[X], v1[X], v2[X]) > box_extents[X]:
        return False

    # [-extents.Y, extents.Y]
    # and [min(v0.Y,v1.Y,v2.Y), max(v0.Y,v1.Y,v2.Y)] do not overlap
    if max(v0[Y], v1[Y], v2[Y]) < -box_extents[Y] \
          or min(v0[Y], v1[Y], v2[Y]) > box_extents[Y]:
        return False

    # [-extents.Z, extents.Z]
    # and [min(v0.Z,v1.Z,v2.Z), max(v0.Z,v1.Z,v2.Z)] do not overlap
    if max(v0[Z], v1[Z], v2[Z]) < -box_extents[Z] \
          or min(v0[Z], v1[Z], v2[Z]) > box_extents[Z]:
        return False

    # separating axis corresponding to triangle face normal (category 2)
    plane_normal = np.cross(f0, f1)
    plane_distance = np.dot(plane_normal, v0)

    # Compute the projection interval radius of b onto L(t) = b.c + t * p.n
    r = box_extents[X] * abs(plane_normal[X]) + \
        box_extents[Y] * abs(plane_normal[Y]) + \
        box_extents[Z] * abs(plane_normal[Z])

    # Intersection occurs when plane distance falls within [-r,+r] interval
    if plane_distance > r:
        return False

    return True

