from torch.utils.data import Dataset, DataLoader
import glob
import os
import numpy as np
import cv2
import torch
import json
from torchvision import transforms, utils
import random

class ProcessDataset(Dataset):
    def __init__(self, root_dir, transform=None, seed=None, fraction=None, subset=None, imagecolormode='rgb'):

        self.color_dict = {'rgb': 1, 'grayscale': 0}
        assert(imagecolormode in ['rgb', 'grayscale'])        

        self.imagecolorflag = self.color_dict[imagecolormode]
        self.root_dir = root_dir
        self.transform = transform
        fn = self.root_dir+'labels.json'
        with open(fn) as f:
            self.data  = json.load(f)


        if not fraction:                    
            self.labels = list(self.data.keys())
        else:
            assert(subset in ['Train', 'Test'])
            self.fraction = fraction
            self.labels = list(self.data.keys())
            if seed:
                random.seed(seed)
                random.shuffle(self.labels)
            if subset == 'Train':
                self.labels = self.labels[:int(
                    np.ceil(len(self.labels)*(1-self.fraction)))]                
            else:
                self.labels = self.labels[int(
                    np.ceil(len(self.labels)*(1-self.fraction))):]                

    def __len__(self):
        return len(self.labels)

    def createMask(self, reg, shp):
        '''

        @param reg:
        @param shp:
        @return:
        '''
        org = np.zeros((shp),dtype=np.uint8)
        regionX = []
        regionY = []
        col = []
        for r in reg:
            regionX.append(reg[r]['x'])
            regionY.append(reg[r]['y'])
            col.append(reg[r]['color_value'])
        pts = []
        for x , y in zip(regionX, regionY):
            tmp = []
            for px, py in zip(x ,y):
                tmp.append([px,py])
            pts.append(np.array(tmp))
        for i, pt in enumerate(pts):            
            cv2.fillPoly(org,[pt],col[i])
        return org


    def __getitem__(self, idx):
        '''

        @param idx:
        @return:
        '''
        img_id = self.labels[idx]
        img_name = self.data[img_id]['filename']
        if self.imagecolorflag:
            image = cv2.imread(
                self.root_dir + img_name, self.imagecolorflag)
            shp = image.shape
            image = image.transpose(2, 0, 1)
        else:
            image = cv2.imread(self.root_dir + img_name, self.imagecolorflag)
            shp = image.shape
        #cv2.resize(image,(480,320))
        regions = self.data[img_id]['region']
        mask = self.createMask(regions,shp)
        if self.imagecolorflag:
            mask = mask.transpose(2,0,1)
        sample = {'image': image, 'mask': mask}

        if self.transform:
            sample = self.transform(sample)

        return sample

class Resize(object):
    """Resize image and/or masks."""

    def __init__(self, imageresize, maskresize):
        self.imageresize = imageresize
        self.maskresize = maskresize

        print(imageresize)
        print(maskresize)

    def __call__(self, sample):
        image, mask = sample['image'], sample['mask']
        if len(image.shape) == 3:
            image = image.transpose(1, 2, 0)
        if len(mask.shape) == 3:
            mask = mask.transpose(1, 2, 0)
        mask = cv2.resize(mask, self.maskresize, cv2.INTER_AREA)
        image = cv2.resize(image, self.imageresize, cv2.INTER_AREA)
        if len(image.shape) == 3:
            image = image.transpose(2, 0, 1)
        if len(mask.shape) == 3:
            mask = mask.transpose(2, 0, 1)

        return {'image': image,
                'mask': mask}


class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample, maskresize=None, imageresize=None):
        image, mask = sample['image'], sample['mask']
        if len(mask.shape) == 2:
            mask = mask.reshape((1,)+mask.shape)
        if len(image.shape) == 2:
            image = image.reshape((1,)+image.shape)
        return {'image': torch.from_numpy(image),
                'mask': torch.from_numpy(mask)}


class Normalize(object):
    '''Normalize image'''

    def __call__(self, sample):
        image, mask = sample['image'], sample['mask']
        return {'image': image.type(torch.FloatTensor)/255,
                'mask': mask.type(torch.FloatTensor)/255}


def get_dataloader_sep_folder(data_dir, maskFolder='Mask', batch_size=4):
    """
        Create Train and Test dataloaders from two separate Train and Test folders.
        The directory structure should be as follows.
        data_dir
        --Images
        --labels.json        
    """
    data_transforms = {
        'Train': transforms.Compose([ToTensor(), Normalize()]),
        'Test': transforms.Compose([ToTensor(), Normalize()]),
    }

    image_datasets = {x: ProcessDataset(root_dir=data_dir,
                                        transform=data_transforms[x])
                      for x in ['Train', 'Test']}
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=batch_size,
                                 shuffle=True, num_workers=0)
                   for x in ['Train', 'Test']}
    return dataloaders


def get_dataloader_single_folder(data_dir, imageFolder='Images', fraction=0.2, batch_size=4):
    """
        Create training and testing dataloaders from a single folder.
    """
    data_transforms = {
        'Train': transforms.Compose([ToTensor(), Normalize()]),
        'Test': transforms.Compose([ToTensor(), Normalize()]),
    }

    image_datasets = {x: ProcessDataset(data_dir, seed=100, fraction=fraction, subset=x, transform=data_transforms[x])
                      for x in ['Train', 'Test']}
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=batch_size,
                                 shuffle=True, num_workers=0)
                   for x in ['Train', 'Test']}
    return dataloaders
