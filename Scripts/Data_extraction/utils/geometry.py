from math import radians
import numpy as np

def rotate(pos, theta):
    theta = radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    
    return np.matmul(R, pos)
