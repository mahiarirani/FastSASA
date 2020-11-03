import tkinter as tk
from tkinter import filedialog
import os
import csv
import unknown_radii
from Bio.PDB import *
from Timer import Timer


class PDB:
    timer = Timer()

    def __init__(self, address=None, atom_radii_file=None):
        self.timer.start()
        self.structure = self.load(address)
        self.remove_water_residues()
        self.atoms = self.get_atoms()
        self.timer.stop()

        self.timer.start()
        self.atom_radii = self.load_atom_radii(atom_radii_file)
        self.attach_atom_radii()
        self.timer.stop()

    @staticmethod
    def load(file=None):
        print('----------\nLoading PDB File', end='\r')
        if file is None:
            root = tk.Tk()
            root.withdraw()
            file = filedialog.askopenfilename()

        path, file = os.path.split(file)
        file_name, file_extension = os.path.splitext(file)

        parser = PDBParser()
        parser.QUIET = True
        structure = parser.get_structure(file_name, path + '/' + file)
        print('PDB File Loaded Successfully')
        return structure

    @staticmethod
    def load_atom_radii(file=None):
        print('----------\nLoading Atom Radii', end='\r')
        if file is None:
            file = 'vdw_radii.csv'
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
                    atom_radii_dict[residue][atom]['polar'] = bool(int(line[3]))
        print('Atom Radii Loaded Successfully')
        return atom_radii_dict

    def attach_atom_radii(self):
        for atom in self.atoms:
            res = atom.get_parent().get_resname()
            try:
                atom.radius = self.atom_radii[res][atom.name]['radii']
                atom.polar = self.atom_radii[res][atom.name]['polar']
            except KeyError:
                atom.radius, atom.polar = unknown_radii.get_data(atom.element, atom.name)
        return self.atoms

    def get_atoms(self, item=None):
        if item is None:
            item = self.structure
        return Selection.unfold_entities(item, "A")

    @staticmethod
    def get_coordinates(a):
        return [a.get_coord()[0], a.get_coord()[1], a.get_coord()[2]]

    def get_item(self, model, chain=None, residue=None):
        try:
            if chain is None:
                item = self.structure[model]
            elif residue is None:
                item = self.structure[model][chain]
            else:
                item = self.structure[model][chain][(' ', residue, ' ')]
        except KeyError:
            item = None
        return item

    def remove_water_residues(self):
        water_residues = []
        residues = [r for r in self.structure.get_residues()]
        for residue in residues:
            if residue.get_id()[0] == 'W':
                water_residues.append(residue)
        [water_residue.get_parent().detach_child(water_residue.id) for water_residue in water_residues]
