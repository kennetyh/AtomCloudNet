import numpy as np
from Bio.PDB import PDBParser
from tqdm import tqdm, trange
import csv
import shutil

PATH = 'data/'


"""

Load Pdb and get for each atom xyz-coordinates, Atom type (CA, H, N, NZ etc.) and Residue type (ALA, PRO etc.)

"""


def load_pdb(name, path=PATH):
    p = PDBParser()
    structure = p.get_structure(name, path+name+"_pdb.txt")
    types = []
    xyz = []
    res = []
    model = structure[0]
    counter = 1
    for chain in model:
        for residue in chain:
            res.append([residue.get_resname(), "%03d" % counter])
            for atom in residue:
                xyz.append(atom.get_coord())
                types.append(atom.get_id())
            counter += 1

    return xyz, types, res


"""

Make Histogram for each amino acid.

Center: N

Radius: dist = 6

"""

def make_dist_file(name, xyz, types, res_list):
    hist_list = []
    for i in trange(0, len(xyz)):
        hist = []
        if types[i] == 'N':
            for j in range(0, len(xyz)):
                dist = np.linalg.norm(xyz[i]-xyz[j])
                if dist < 6:
                    hist.append([types[j], xyz[j].tolist()])
                else:
                    pass
        if len(hist) > 0:
            hist_list.append(hist)
    for res, hist in zip(res_list, hist_list):
        filename = PATH + name + '_' + res[1] + '_' + res[0] + '.txt'
        with open(filename, 'w', newline='') as f:
            wr = csv.writer(f)
            wr.writerows(hist)


"""

Create file txt file with filename and chemical shift:

*.xyz   H-Shift

"""

def get_shift(name, path=PATH):

    file = open(path + name + ".txt")
    stringList = file.readlines()
    file.close()

    n_shift = []
    h_shift = []
    numberN = []
    numberH = []
    number = []
    residue = []

    for line in stringList:
        tokens = line.split()
        if len(tokens) >= 27:
            if 'N    ' in line:
                n_shift.append(float(tokens[9]))
                numberN.append(float(tokens[0]))
            if 'H    ' in line:
                h_shift.append(float(tokens[9]))
                numberH.append(float(tokens[0]))
                number.append(int(tokens[17]))
                residue.append(tokens[5])

    fname = PATH + "shift/" + name + '.txt'
    with open(fname, 'w') as outfile:
        for i in range(len(numberN)):
            num = ["%.3d" % x for x in number]
            print(name + '_' + str(num[i]) + '_' + str(residue[i]) + '.xyz', n_shift[i], h_shift[i], file=outfile)
    return n_shift, h_shift, numberH, numberN


"""

Move all xyz files without NMR shift into a different folder called noshift/ . 

"""

PATH2 = "shift/"
destination = "noshift/"

def mv_Res_without_Shift(name, path=PATH2):

    file = open(path + name + ".txt")
    stringList = file.readlines()
    file.close()

    fname = []

    for line in stringList:
        tokens = line.split()
        fname.append(tokens[0])

    xyzs = glob.glob('*.xyz')

    for i in xyzs:
        if i in xyzs and i not in fname:
            shutil.move(i, destination)

