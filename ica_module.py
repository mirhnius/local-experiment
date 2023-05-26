import copy
import pathlib
import numpy as np
from nilearn.image import binarize_img, new_img_like, iter_img, threshold_img
from nilearn.decomposition import CanICA
from nilearn.plotting import plot_prob_atlas, plot_stat_map, show

NonePath = type('NonePath', (), {'resolve': lambda: None})

ICS_PATH = pathlib.Path('/data/origami/niusha/code/local-experiment/io/ICAs')
io_path = ICS_PATH.parent
n_components = 30

def ICA_decomposition(filenames, group, i, path=ICS_PATH, n=n_components):
    """
    This function receives nifiti images and calculates 30 independent components

    inputs: 
        filenames: list of input filenames or a 4D image containing all inputs concatenated.
        group: a group of subjects (PD/Healthy/Pooled). It is used for naming IC files.
        path: parent directory for storing ICs.
        i: iteration number is used for naming IC files.
        n: number of ICs.

    outputs: 
        ICA_s: A 4D image that contains 30 ICs.
    """
    fast_ica = CanICA(n_components=n,
        memory="nilearn_cache", memory_level=2,
        mask_strategy='whole-brain-template',
        do_cca=False,
        random_state=0,
        standardize=True, 
        standardize_confounds=True,
        )
    fast_ica.fit(filenames)

    ICA_s = fast_ica.components_img_
    ICA_s.to_filename(path / (f'ICAs_{group}_{i}.nii.gz'))
    return ICA_s

def threshold_masking(data, mask, threshold="99.6%", two_sided=False):
    
    mask_thr = threshold_img(img=mask, threshold=threshold, two_sided=two_sided)
    mask_d = mask_thr.get_fdata()
    masked_data = data * np.reshape(mask_d, newshape=list(mask_d.shape)+[1])
    
    return masked_data, mask_thr

def mean_calc(extracted_from_mask, masked_data, i):
    
    n_subjects = extracted_from_mask.shape[1]
    for j in range(n_subjects):
            subject = masked_data[...,j]
            index = np.nonzero(subject)
            extracted_from_mask[i,j] = np.nanmean(subject[index])
    
    return extracted_from_mask

def weighted_sum_masking(data, mask):
    
    mask_d = copy.deepcopy(mask.get_fdata())
    mask_d[mask_d < 0] = 0
    masked_data = data * np.reshape(mask_d, newshape=list(mask_d.shape)+[1])
    filtered_mask = new_img_like(ref_niimg=mask, data=mask_d)
    
    return masked_data, filtered_mask

def whighted_sum_calc(extracted_from_mask, masked_data, mask_d, i):

    extracted_from_mask[i,:] = np.sum(masked_data, axis=(0,1,2)) / np.sum(mask_d)
    
    return extracted_from_mask

def Means_after_masking(ICAs, DBM_maps, path=NonePath, group="", func=threshold_masking):
    """
    This function first extracts a mask from each IC and then applies it to each subject.
    After extracting regions of interest, the function calculates the mean value of these regions
    for each subject.
      
    inputs:
        ICAs: IC components
        DBM_maps: input images; a 4 D image
        path: Directory to save masks ans masked data.
 
    outputs:
        means_after_mask: an array contains the mean value of each input DBM after applying IC masks.
    """
    mask_dir = path / "masks"
    masked_data_dir = path / "masked_data"

    if path.resolve()is not None:
      mask_dir.mkdir(parents=True, exist_ok=True)  
      masked_data_dir.mkdir(parents=True, exist_ok=True)
      
    n = ICAs.shape[3]
    n_subjects = data.shape[3]
    extracted_from_mask = np.zeros((n,n_subjects), dtype='<f8') #, dtype='<f4'
    data = DBM_maps.get_fdata()
    for i, cur_ic in enumerate(iter_img(ICAs)):
        masked_data, mask = func(data, cur_ic)
        
        if str(func) == "threshold_masking":
            whighted_sum_calc(extracted_from_mask, masked_data, mask.get_fdata(), i)
        elif  str(func) == "weighted_sum_masking": 
            extracted_from_mask = whighted_sum_calc(extracted_from_mask, masked_data, mask.get_fdata(), i)
        
        if path.resolve() is not None:
            # new_img_like(DBM_maps, masked_data).to_filename(masked_data_dir / f"masked_{group}_IC_{i}.nii.gz")
            np.savetxt(masked_data_dir / f"masked_{group}_IC_{str(func)}_{i}.txt", extracted_from_mask)
            mask.to_filename(mask_dir / f"IC_{group}_{i}.nii.gz")

    return extracted_from_mask
