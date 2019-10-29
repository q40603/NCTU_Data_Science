import numpy as np
import pandas as pd
import cv2
from math import sqrt, ceil
import matplotlib.pyplot as plt
#from scipy.ndimage import gaussian_filter1d
#from scipy import signal
#from scipy.ndimage.filters import convolve
import os
subsample = [0.25,0.5,1.0,2.0,4.0,8.0]
array_of_origin_img = []
array_of_img = [] # Store all the image data
gauss_pyr = {}
DOG_pyr = {}
filter_size = {}
filter_sigma = {}
absolute_sigma = {}
loc = {}

# Read directory function
def read_directory(directory_name):
    filenumber = len([name for name in os.listdir(directory_name) if os.path.isfile(os.path.join(directory_name, name))])
    for i in range(1,filenumber+1):
        img = cv2.imread(directory_name + "/" + str(i)+".jpg")
        array_of_img.append(img)
        array_of_origin_img.append(img)

def init_dict():
    octaves = 4
    for i in range(octaves+1):
        gauss_pyr[i] = {}
        DOG_pyr[i] = {}
        filter_size[i] = {}
        filter_sigma[i] = {}
        absolute_sigma[i] = {}
        loc[i] = {}
        
def clear_all():
    gauss_pyr.clear()
    DOG_pyr.clear()
    filter_size.clear()
    filter_sigma.clear()
    loc.clear()
            
def gaussian_blur(img, sigma):
    size = 2*round(3.5*sigma)+1
    return cv2.GaussianBlur(img,(size,size),sigma)   

def length(sigma):
    return 2*round(3.5*sigma)+1

def pre_process_img(image):
    signal = image
    signal = cv2.cvtColor(signal, cv2.COLOR_BGR2GRAY)
    signal = cv2.normalize(signal, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    signal = gaussian_blur(signal,0.5)
    #signal = cv2.resize(signal,None,fx=2,fy=2)
    
    return signal


def generate_octave(image):
    octaves = 4
    intervals = 2
    
    s = 2
    k = 2 ** (1.0 / s)
    init_sigma = 1.6
    
    image = gaussian_blur(image,init_sigma)
    
    absolute_sigma[1][1] = init_sigma * subsample[1] 
    gauss_pyr[1][1] = np.array(image)
    
    
    for octave in range(1,octaves+1):
        sigma = init_sigma
        DOG_pyr[octave] = np.zeros((intervals+3,np.size(gauss_pyr[octave][1],0),np.size(gauss_pyr[octave][1],1)))
        filter_size[octave][1] = length(sigma)
        filter_sigma[octave][1] = sigma        
        for interval in range(2,intervals+4):
            
            sigma_f = sqrt(2**(1/intervals) -1)*sigma
            sigma = (2**(1/intervals))*sigma
            gauss_pyr[octave][interval] = gaussian_blur(gauss_pyr[octave][interval-1],sigma_f)
            DOG_pyr[octave][interval-1] = gauss_pyr[octave][interval] - gauss_pyr[octave][interval-1]

            absolute_sigma[octave][interval] = sigma*subsample[octave]

            filter_size[octave][interval] = length(sigma)
            filter_sigma[octave][interval] = sigma

        if octave < octaves:
            gauss_pyr[octave+1][1] = cv2.resize(gauss_pyr[octave][intervals+1],None,fx=0.5,fy=0.5,interpolation=cv2.INTER_NEAREST)


def find_key_points():
    octaves = 4
    intervals = 2
    contrast_threshold = 0.02
    curvature_threshold = 10.0
    curvature_threshold = ((curvature_threshold + 1)**2)/curvature_threshold
    
    xx = np.array([1,-2,1])
    yy = xx.T
    xy = np.array([[1,0,-1],[0,0,0],[-1,0,1]])/4
    
    raw_keypoints = []
    contrast_keypoints = []
    curve_keypoints = []
    
    for octave in range(1,octaves+1):
        for interval in range(2,intervals+2):
            keypoint_count = 0;
            contrast_mask = np.absolute(DOG_pyr[octave][interval]) >= contrast_threshold
            loc[octave][interval] = np.zeros(np.shape(DOG_pyr[octave][interval])) 
            edge = ceil(filter_size[octave][interval]/2)
            #print("===========================================")
            #print(edge)
            for x in range((edge),(np.size(DOG_pyr[octave][interval],0)-edge)):         
                for y in range((edge),(np.size(DOG_pyr[octave][interval],1)-edge)):
                    if(contrast_mask[x][y] == 1):
                        #print(interval,x,y)
                        #print(np.shape(DOG_pyr[octave][(interval-1):(interval+1)]))
                        #print(DOG_pyr[octave][(interval-1):(interval+1)][x-1:x+1])
                        tmp = DOG_pyr[octave][(interval-1):(interval+1),(x-1):(x+2),(y-1):(y+2)]
                        #print(tmp)
                        pt_val = tmp[1,1,1]
                        if( (pt_val == tmp.min()) | (pt_val == tmp.max()) ):
                            #print("pt_val == tmp.min | pt_val == tmp.max ",end="")
                            if abs(DOG_pyr[octave][interval,x,y]) >= contrast_threshold:
                                #pass
                                #print(">= contrast_threshold ",end="")
                                Dxx = np.sum(DOG_pyr[octave][interval,x-1:x+2,y] * xx)
                                Dyy = np.sum(DOG_pyr[octave][interval,x,y-1:y+2] * yy)
                                Dxy = np.sum(np.sum(DOG_pyr[octave][interval,x-1:x+2,y-1:y+2] * xy,axis=1))                              

                                Tr_H = Dxx + Dyy;
                                Det_H = Dxx*Dyy - Dxy**2;

                                curvature_ratio = (Tr_H**2)/Det_H;
                                
                                if ((Det_H >= 0) & (curvature_ratio < curvature_threshold)):
                                    #print("< curvature_threshold")
                                    loc[octave][interval][x,y] = 1;
                                    keypoint_count += 1; 
        print(keypoint_count)
    
                        #print(pt_val)
                        
    
    
def SIFT(inputname):
    
    read_directory(inputname)
    
    
    for i in range(len(array_of_img)):
        image = array_of_img[i]
        image = pre_process_img(image)
        init_dict()
        generate_octave(image)
        find_key_points()
        clear_all()
        print("===================")
    
    
    
    print(len(array_of_img))
#     for i in range(len(array_of_img)):
#         imageout = cv2.resize(array_of_img[i],None,fx=0.5,fy=0.5)
    #use: len(array_of_img) for looping the image, array_of_img[0],
    #array_of_img[1],array_of_img[2],...for processing each image
    #Start SIFT here
    
    #print(array_of_img)
    #End of SIFT here and use imageoutput for your output
    imageoutput = array_of_img[0]
    array_of_img.clear()
    array_of_origin_img.clear()
    return imageoutput


f = open('testfile.txt', 'r')
dirname = str(f.readline()).strip()
while(dirname):   
    print(dirname)
    imageout=SIFT(dirname)
    plt.figure()
    plt.imshow(imageout)
    cv2.imwrite(dirname+'.jpg', imageout)
    dirname = str(f.readline()).strip()