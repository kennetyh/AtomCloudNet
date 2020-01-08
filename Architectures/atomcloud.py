from Architectures.cloud_utils import *


def create_emb_layer(num_embeddings, embedding_dim):
    return nn.Embedding(num_embeddings, embedding_dim)


class AtomEmbedding(nn.Module):
    def __init__(self, num_embeddings=16, embedding_dim=64, transform=True, transformed_emb_dim=None, device='cpu'):
        super(AtomEmbedding, self).__init__()
        """
        Embedding of atoms. Consider Z as a class. Embedding size.
        :param num_embeddings: number of atoms in the input
        :param embedding_dim: number of features generated by the embedding layer
        :param transform: whether to apply a linear layer on the embedding
        :param transformed_emb_dim: number of features generated by the forward layer
        """
        self.device = device
        if transformed_emb_dim is None:
            transformed_emb_dim = embedding_dim
        self.transform = transform
        self.emb_layer = nn.Embedding(num_embeddings, embedding_dim)
        self.transformed_emb = nn.Linear(embedding_dim, transformed_emb_dim)

    def forward(self, Z):
        emb = self.emb_layer(Z)
        transformed_emb = self.transformed_emb(emb)
        if not self.transform:
            return emb
        else:
            return transformed_emb


class AtomResiduals(nn.Module):
    def __init__(self, in_channel, res_blocks, activation='tanh', device='cpu'):
        r"""
        Calculate Atom Residuals. Output is twice the size of the input
        :param in_channel: number of features of the atom
        :param res_blocks: number of residual blocks
        """
        super(AtomResiduals, self).__init__()
        self.device = device
        self.feature_size = in_channel
        self.activation = activation
        self.unnormalized = True
        self.atom_res_blocks = nn.ModuleList()
        self.atom_norm_blocks = nn.ModuleList()
        for _ in range(res_blocks):
            self.atom_res_blocks.append(nn.Linear(in_channel, in_channel))
            self.atom_norm_blocks.append(nn.BatchNorm1d(in_channel))

    def forward(self, features, geometry=None):
        batch_size = features.shape[0]
        features_ = features.permute(1, 0, 2)
        transformed_ = features_
        for atom in range(features.shape[1]):
            input_ = transformed_[atom].clone()
            # print("Input shape of a batch of atoms", input_.shape)
            for i, res in enumerate(self.atom_res_blocks):
                res_features = res(input_)
                if batch_size == 1 or self.unnormalized:
                    if self.activation is 'relu':
                        input_ = F.relu(res_features)
                    elif self.activation is 'tanh':
                        input_ = torch.tanh(res_features)
                else:
                    bn = self.atom_norm_blocks[i]
                    if self.activation is 'relu':
                        input_ = F.relu(bn(res_features))
                    elif self.activation is 'tanh':
                        input_ = torch.tanh(bn(res_features))
            transformed_[atom] = input_

        new_features = torch.cat([features_, transformed_], axis=2).permute(1, 0, 2)
        return new_features


# Atomclouds should be universal
class AtomcloudVectorization(nn.Module):
    def __init__(self, natoms, nfeats, layers, retain_features, mode, activation='tanh', device='cpu'):
        r"""
        Atomcloud is the module transforming an atomcloud into a vector - this vector represents the new features of
        the Atomcloud's centroid/center atom. This module takes fixed number of atoms and features input.
        :param natoms: number of atoms to be selected in the cloud
        :param nfeats: number of features per atom
        :param layers: list of <convolution filter size>'s
        """
        super(AtomcloudVectorization, self).__init__()
        self.device = device
        self.natoms = natoms
        self.nfeats = nfeats
        self.mode = mode
        self.activation = activation
        self.retain_features = retain_features
        self.apply_vec_transform = False
        if self.nfeats == 1:
            self.apply_vec_transform = False
        self.spatial_abstraction = nn.Linear(nfeats + 3, nfeats).float()

        self.conv_features = False  # true if convolution filter dimension should be over features instead of atoms
        self.cloud_convs = nn.ModuleList()
        self.cloud_norms = nn.ModuleList()

        if self.conv_features:
            last_channel = nfeats
        else:
            last_channel = natoms
        for out_channel in layers:
            self.cloud_convs.append(nn.Conv1d(last_channel, out_channel, 1)).to(self.device)
            self.cloud_norms.append(nn.BatchNorm1d(out_channel)).to(self.device)
            last_channel = out_channel

    def forward(self, xyz, features, centroid, cloud):
        _, natoms, ncoords = xyz.size()
        _, _, nfeatures = features.size()
        batch_size, cloud_size = cloud.size()
        xyz = xyz.float().to(self.device)
        features = features.float().to(self.device)

        masked_xyz = torch.zeros((batch_size, cloud_size, ncoords)).float().to(self.device)
        masked_features = torch.zeros((batch_size, cloud_size, nfeatures)).float().to(self.device)

        for b, mask in enumerate(cloud):
            masked_xyz[b] = xyz[b, mask]
            masked_features[b] = features[b, mask]

        if self.apply_vec_transform:
            masked_features = torch.cat([masked_xyz, masked_features], axis=2)
            masked_features = self.spatial_abstraction(masked_features)
        new_features = masked_features.to(self.device)

        # Todo: Run convolution over cloud representation - This could/should be kernelized -> eg. Gaussian
        for i, conv in enumerate(self.cloud_convs):
            conv_features = conv(new_features)
            if batch_size == 1:
                if self.activation is 'relu':
                    new_features = F.relu(conv_features)
                elif self.activation is 'tanh':
                    new_features = torch.tanh(conv_features)
            else:
                bn = self.cloud_norms[i]
                if self.activation is 'relu':
                    new_features = F.relu(bn(conv_features))
                elif self.activation is 'tanh':
                    new_features = torch.tanh(bn(conv_features))
        new_features = torch.max(new_features, 2)[0]
        return new_features


class Atomcloud(nn.Module):
    def __init__(self, natoms, nfeats, radius=None, layers=[32, 64, 128], include_self=True, retain_features=True,
                 mode='potential', device='cpu'):
        super(Atomcloud, self).__init__()
        self.device = device
        self.natoms = natoms
        self.nfeats = nfeats
        self.include_self = include_self
        self.retain_features = retain_features
        self.out_features = layers[-1]
        self.radius = radius
        self.mode = mode
        self.Z = None
        self.cloud = AtomcloudVectorization(natoms=natoms, nfeats=nfeats, layers=layers,
                                            retain_features=retain_features, mode=mode, device=self.device)

    def forward(self, xyz, features, Z=None):
        xyz = xyz.permute(0, 2, 1)
        xyz_ = xyz
        if features.shape[1] != xyz.shape[1]:
            features = features.permute(0, 2, 1).to(self.device)
        batch_size, natoms, nfeatures = features.size()
        new_features = torch.zeros((batch_size, natoms, self.out_features)).to(self.device)
        Z = Z.view(-1, Z.shape[1], 1)
        # clouds is a list of masks for all atoms
        clouds, dists = cloud_sampling(xyz, Z=Z.float(), natoms=self.natoms, radius=self.radius, mode=self.mode,
                                       include_self=self.include_self)
        for c, cloud in enumerate(clouds):
            centroid = (xyz[:, c].float(), features[:, c].float())
            # Shift coordinates of xyz to center cloud
            for b in range(batch_size):
                xyz_[b] = xyz[b] - centroid[0][b]
            new_features[:, c] = self.cloud(xyz_, features, centroid, cloud).to(self.device)

        if self.retain_features:
            return torch.cat([features, new_features], axis=2)
        else:
            return new_features
