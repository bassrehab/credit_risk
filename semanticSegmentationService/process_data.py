from torch.utils.data import Dataset, DataLoader
import glob
import os
import numpy as np
import cv2
import torch
import json
from torchvision import transforms, utils
import random

class SegDataset(Dataset):
    """Segmentation Dataset"""
    def __init__(self, root_dir, transform=None, seed=None, fraction=None, subset=None, imagecolormode='rgb'):
        """
        Args:
            Create Train and Test dataloaders from two separate Train and Test folders.
            The directory structure should be as follows.
            data_dir
            --Images
            --labels.json        
    
            imageFolder (string) = 'Images' : Name of the folder which contains the Images.
            maskFolder (string)  = 'Masks : Name of the folder which contains the Masks.
            transform (callable, optional): Optional transform to be applied on a sample.
            seed: Specify a seed for the train and test split
            fraction: A float value from 0 to 1 which specifies the validation split fraction
            subset: 'Train' or 'Test' to select the appropriate set.
            imagecolormode: 'rgb' or 'grayscale'
            maskcolormode: 'rgb' or 'grayscale'
        """
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
                #np.random.seed(seed)
                #indices = np.arange(len(self.labels))
                #np.random.shuffle(indices)
                random.seed(seed)
                random.shuffle(self.labels)
                #self.labels = self.labels[indices]                
            if subset == 'Train':
                self.labels = self.labels[:int(
                    np.ceil(len(self.labels)*(1-self.fraction)))]                
            else:
                self.labels = self.labels[int(
                    np.ceil(len(self.labels)*(1-self.fraction))):]                

    def __len__(self):
        return len(self.labels)
    def createMask(self, reg, shp):
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
        #cv2.imshow("out",org)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        return org


    def __getitem__(self, idx):
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

# Define few transformations for the Segmentation Dataloader


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

    image_datasets = {x: SegDataset(root_dir=data_dir,
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

    image_datasets = {x: SegDataset(data_dir, seed=100, fraction=fraction, subset=x, transform=data_transforms[x])
                      for x in ['Train', 'Test']}
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=batch_size,
                                 shuffle=True, num_workers=0)
                   for x in ['Train', 'Test']}
    return dataloaders
