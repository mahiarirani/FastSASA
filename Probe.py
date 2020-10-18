import numpy as np
import csv
import unknown_radii


class Probe:
    def __init__(self, atoms, points, radius, coords=None, tree=None):
        self.points = points
        self.radius = radius
        self.coords = coords
        self.tree = tree
        self.atoms = atoms
        self.atom_radii = self.load_atom_radii()
        self.attach_probe()

    @staticmethod
    def load_atom_radii(file='vdw_radii.csv'):
        print('----------\nLoading Atom Radii')
        atom_radii_dict = {}
        with open(file, 'r') as data:
            for line in csv.reader(data):
                if line[0] == 'RESIDUE':
                    residue = line[2]
                    atom_radii_dict[residue] = {}
                elif line[0] == 'ATOM':
                    atom = line[1]
                    atom_radii_dict[residue][atom] = {}
                    atom_radii_dict[residue][atom]['radii'] = float(line[2])
                    atom_radii_dict[residue][atom]['polar'] = bool(line[3])
        print('Atom Radii Loaded Successfully\n----------')
        return atom_radii_dict

    def get_coordinates(self):
        coords = []
        for item in self.atoms:
            for probe in item.probe:
                coords.append(probe)
        return coords

    @staticmethod
    def create_probe(n):
        indices = np.arange(0, n, dtype=float) + 0.5

        phi = np.arccos(1 - 2 * indices / n)
        theta = np.pi * (1 + 5 ** 0.5) * indices

        points = np.dstack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)])
        return points[0]

    def attach_probe(self):
        probe = self.create_probe(self.points)
        print('----------\nBegin Probe Attachment')
        for index, atom in enumerate(self.atoms):
            res = atom.get_parent().get_resname()
            try:
                atom.radius = self.atom_radii[res][atom.name]['radii']
                atom.polar = self.atom_radii[res][atom.name]['polar']
            except KeyError:
                atom = unknown_radii.get_data(atom)
            atom.probe = probe * (self.radius + atom.radius) + atom.get_coord()
            print('Creating Atom #%s [%s] Probe' % (index + 1, atom.element), end='\r')
        print('Probe Attached Successfully\n----------')