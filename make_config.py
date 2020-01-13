from configparser import ConfigParser
import argparse
import os

# self.['SETTING']['layers'] = ast.literal_eval(config.get("section", "option"))


class Config:
    def __init__(self, setting):
        if setting == 0:
            print("CoulombNet configuration generator... ")
            path = "config/config"
            config_file = path+".ini"
            self.parser = ConfigParser()
            self.parser.read(config_file)
            self.idx = 0
            self.parser['SETTING']['model'] = 'NN'

            lr = [0.1, 0.005, 0.0001]
            momentum = [0, 0.1, 0.5]
            dropout = [0, 0.1, 0.2, 0.3]
            patience = [10, 25, 50]
            pfactor = [0.5]
            epochs = [50, 200, 500]
            batchsize = [8, 64, 256]
            architectures = [[1024, 1024, 512],
                            [50, 50, 50, 50, 50, 50],
                            [1024, 512, 128, 32],
                            [512, 256, 64, 64, 32, 32]]

            for l in lr:
                for m in momentum:
                    for d in dropout:
                        for p in patience:
                            for pf in pfactor:
                                for e in epochs:
                                    for b in batchsize:
                                        for a in architectures:
                                            self.idx += 1
                                            new_config = path+'_'+str(setting+self.idx).zfill(5)+'.ini'
                                            self.parser['SETTING']['lr'] = str(l)
                                            self.parser['SETTING']['momentum'] = str(m)
                                            self.parser['SETTING']['dropout'] = str(d)
                                            self.parser['SETTING']['patience'] = str(p)
                                            self.parser['SETTING']['pfactor'] = str(pf)
                                            self.parser['SETTING']['layers'] = str(a)
                                            self.parser['SETTING']['epochs'] = str(e)
                                            self.parser['SETTING']['batchsize'] = str(b)
                                            if os.path.isfile(new_config):
                                                os.remove(new_config)
                                            with open(new_config, "w") as f:
                                                self.parser.write(f)

        if setting == 1:
            print("AtomCloudNet configuration generator.... WRUMM WRUMM")
            path = "config_ACN/config"
            config_file = path + ".ini"
            self.parser = ConfigParser()
            self.parser.read(config_file)
            self.idx = 900
            self.parser['SETTING']['model'] = 'ACN'

            lr = [0.0005]
            epochs = [100]
            batchsize = [16]
            neighborradius = [4]
            nclouds = [1]
            clouddim = [4]
            cloudord = [3, 5]
            resblocks = [2, 4]
            nffl = [2]
            ffl1size = [256, 1024]
            emb_dim = [16]

            # Todo: optimize: nffl=1, ffl1size=128, emb_dim=32
            for l in lr:
                for e in epochs:
                    for b in batchsize:
                        for n in neighborradius:
                            for nc in nclouds:
                                for cd in clouddim:
                                    for co in cloudord:
                                        for rb in resblocks:
                                            for nf in nffl:
                                                for ff in ffl1size:
                                                    for ed in emb_dim:
                                                        self.idx += 1
                                                        new_config = path + '_' + str(self.idx).zfill(5) + '.ini'
                                                        self.parser['SETTING']['lr'] = str(l)
                                                        self.parser['SETTING']['neighborradius'] = str(n)
                                                        self.parser['SETTING']['nclouds'] = str(nc)
                                                        self.parser['SETTING']['clouddim'] = str(cd)
                                                        self.parser['SETTING']['resblocks'] = str(rb)
                                                        self.parser['SETTING']['nffl'] = str(nf)
                                                        self.parser['SETTING']['ffl1size'] = str(ff)
                                                        self.parser['SETTING']['emb_dim'] = str(ed)
                                                        self.parser['SETTING']['epochs'] = str(e)
                                                        self.parser['SETTING']['batchsize'] = str(b)
                                                        self.parser['SETTING']['cloudord'] = str(co)
                                                        if os.path.isfile(new_config):
                                                            os.remove(new_config)
                                                        with open(new_config, "w") as f:
                                                            self.parser.write(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Specify setting (generates all corresponding .ini files).')
    parser.add_argument('--setting', type=int, default=1, help='Please specify setting:\n'
                                                               '   0 : Testing purposes\n')
    args = parser.parse_args()
    Config(setting=args.setting)







"""def two_body(self, xyz, Z, norm=False):
    dists = squareform(pdist(xyz, 'euclidean', p=2, w=None, V=None, VI=None))
    dists = dists ** 6
    zz = np.outer(Z, Z)
    out = np.asarray([dists[i, j] / zz[i, j] if zz[i, j] != 0 else 0
                      for i, j in itertools.product(range(30), range(30))])
    mask = np.where(out == 0)
    out[mask] = 1
    # Todo: Normalization
    for i in range(out.shape[0]):
        if norm:
            sigma = 5
            mu = 50
            out[i] = 1 / (sigma * np.sqrt(mu * 2)) * np.e ** -(out[i] ** 2)
    final = 1 / out
    final[mask] = 0
    final = final.reshape((30, 30))
    return final.sum(1)


def three_body(self, xyz, Z):
    dists = squareform(pdist(xyz, 'euclidean', p=3, w=None, V=None, VI=None))
    dists = dists ** 3
    zz = np.outer(Z, Z, Z)
    out = np.asarray([dists[i, j] / zz[i, j] if zz[i, j] != 0 else 0
                      for i, j in itertools.product(range(30), range(30))])
    mask = np.where(out == 0)
    out[mask] = 1
    final = 1 / out
    final[mask] = 0
    final = final.reshape((30, 30, 30))
    pass


path = 'data/QM9Train'

data = qm9_loader(limit = 10000, path = path + '/*.xyz')
#print(data.data['0']['two'])
for i in range(1000):
    print(data.data[str(i)]['two'])"""


