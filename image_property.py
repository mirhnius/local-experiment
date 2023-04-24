import pathlib
import numpy as np
import pandas as pd
from nilearn.image import load_img
from nilearn.image import index_img
from nilearn.image import iter_img
from nilearn.image import binarize_img
import matplotlib.pyplot as plt

#I assumed the img is 4D for now
def image_report(img):

    n_bins = 3
    data = img.get_fdata()
    type_ = type(data)
    max_each_img = np.max(np.max(np.nanmax(data, axis=0),axis=0), axis=0)
    max_ = np.nanmax(data)
    mean_each_img = np.mean(np.mean(np.nanmean(data, axis=0),axis=0), axis=0)
    mean_ = np.nanmean(data)
    min_each_img = np.min(np.min(np.nanmin(data, axis=0),axis=0), axis=0)
    min_ = np.nanmin(data)

    print(f"======== data type ======== \n {type_}") #change it. I need the image datatype also I need memmap data type
 
    names = ["Maximum", "Mean", "Minimum"]
    point_estimators = [max_, mean_, min_]
    distributions = [max_each_img, mean_each_img, min_each_img]
    for i in range(3):
        print(f"======== {names[i]} ======== \n")
        print(f"Overal {names[i]}: {point_estimators[i]:.2f}")
        plt.hist(distributions[i],n_bins)
        plt.title(f"{names[i]} Values For Along image")
        plt.show()
    



