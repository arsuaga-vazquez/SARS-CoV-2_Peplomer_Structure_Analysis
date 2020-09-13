"""
A collection of functions to use in analyzing the SARS-CoV2 spike protein

Throughout this file, groups of points will be stored mostly as matrices with
each row representing a point, and each column representing a dimension (x, y, or z)
"""
import math
import numpy as np
from typing import *

def backbone(protein_name: str, chain: chr):
    # Uses a PDB file to get the coordinates of atoms in the backbone of a protein chain
    with open(f'{protein_name.lower()}.pdb') as pdb_file:
        pdb_data = pdb_file.read()
    atoms = []
    for line in pdb_data.split('\n'):
        if line[0:4] == 'ATOM' and line[21] == chain and line[13:16].rstrip(' ') == 'CA':
            residue_num = int(line[24:26])
            x = float(line[31:38].rstrip(' '))
            y = float(line[39:46].rstrip(' '))
            z = float(line[47:54].rstrip(' '))
            atoms.append([x, y, z])
    return np.matrix(atoms)

def dump_beads(*components, file_name='/home/computer/knotplot/beads.txt') -> None:
    # Given a list of atom coordinates, creates a file for knotplot to open
    # Find centroid of all chains, in order to center it
    centroid = np.array([[0., 0., 0.]])
    total_atoms = 0
    for component in components:
        for atom in component:
            centroid += atom[0]
            total_atoms += 1
    centroid /= total_atoms
    for component in components:
        for atom in component:
            atom -= centroid
    knotplot_data = ''
    components = [component.tolist() for component in components]
    for component_num in range(len(components)):
        knotplot_data += f'Component {component_num + 1} of {len(components)}:\n'
        component = components[component_num]
        for atom in component:
            knotplot_data += ' '.join([str(coord) for coord in atom]) + '\n'
    with open(file_name, 'w+') as knotplot_file:
        knotplot_file.write(knotplot_data)

def rmsd(chain1, chain2):
    # TODO: create functions for just getting the centroid or rotation matrix
    n = len(chain1)
    if n != len(chain2): raise Error
    chain1 = np.matrix(chain1)
    chain2 = np.matrix(chain2)
    # Center each group of points by subtracting their respective centroids
    chain1 = chain1 - np.ones((n, n)) * chain1 / n
    chain2 = chain2 - np.ones((n, n)) * chain2 / n
    # Use Kabsch algorithm to line up chain1 and chain2 in order to minimize RMSD
    # The Kabsch algo finds the rotation matrix that best maps chain1 onto chain2
    # https://en.wikipedia.org/wiki/Kabsch_algorithm
    covariance_matrix = chain1.T * chain2
    U, S, VT = np.linalg.svd(covariance_matrix)
    d = np.linalg.det(U * VT)
    rotation_matrix = U * np.diag([1,1,d]) * VT
    chain1 *= rotation_matrix
    total_square_diff = sum([row * row.T for row in chain1 - chain2])[0, 0]
    return math.sqrt(total_square_diff / n)

def angle(points):
    # Parameter: list of 3 points, which are each lists of 3 coords
    # returns the angle that they form (in radians)
    points = [np.array(point) for point in points]
    v1 = points[0] - points[1]
    v2 = points[2] - points[1]
    return math.acos(v1.dot(v2.T) / np.linalg.norm(v1) / np.linalg.norm(v2))
