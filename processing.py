
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from glob import glob
import os
import utm
from tqdm import tqdm
#from xml.etree import ElementTree as et
import xmltodict

##
def cloud_masking(image,cld):
        cloud_mask = cld > 30
        band_mean = image.mean()
        image[cloud_mask] = band_mean
        return image

##
def load_file(fp):
    """Takes a PosixPath object or string filepath
    and returns np array"""

    return np.array(Image.open(fp.__str__()))

def paths (name): 

    fold_band_10 = glob(name+"/GRANULE/*/IMG_DATA/R10m")[0]
    fold_band_20 = glob(name+"/GRANULE/*/IMG_DATA/R20m")[0]
    fold_band_60 = glob(name+"/GRANULE/*/IMG_DATA/R60m")[0]
    path = name+"/GRANULE/*/IMG_DATA/R10m"+"/*.jp2"
    x = glob(path)
    lists = x[0].split("/")[-1].split("_")
    fixe = lists[0]+'_'+lists[1]

    band_10 = ['B02', 'B03', 'B04','B08']
    band_20 = ['B05', 'B06', 'B07','B8A','B11', 'B12']
    band_60 = ['B01','B09']
    images_name_10m = [fixe+"_"+band+"_10m.jp2" for band in band_10 ]
    images_name_20m = [fixe+"_"+band+"_20m.jp2" for band in band_20 ]
    images_name_60m = [fixe+"_"+band+"_60m.jp2" for band in band_60 ]
    #
    bandes_path_10 = [os.path.join(fold_band_10,img) for img in images_name_10m]
    bandes_path_20 = [os.path.join(fold_band_20,img) for img in images_name_20m]
    bandes_path_60 = [os.path.join(fold_band_60,img) for img in images_name_60m]
    #
    tile_path = name+"/INSPIRE.xml"
    path_cld_20 = glob(name+"/GRANULE/*/QI_DATA/MSK_CLDPRB_20m.jp2")[0]
    path_cld_60 = glob(name+"/GRANULE/*/QI_DATA/MSK_CLDPRB_60m.jp2")[0]

    return bandes_path_10,bandes_path_20,bandes_path_60,tile_path,path_cld_20,path_cld_60

##
def coords_to_pixels(ref, utm, m=10):
    """ Convert UTM coordinates to pixel coordinates"""

    x = int((utm[0] - ref[0])/m)
    y = int((ref[1] - utm[1])/m)

    return x, y

##
def extract_sub_image(bandes_path,tile_path,area,resolution=10, d= 3, cld_path = None):
    
  xml_file=open(tile_path,"r")
  xml_string=xml_file.read()
  python_dict=xmltodict.parse(xml_string)
  tile_coordonnates = python_dict["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:abstract"]["gco:CharacterString"].split()

  # S2 tile coordonnates
  lat,lon = float(tile_coordonnates[0]),float(tile_coordonnates[1])
  tile_coordonnate = [lat,lon]

  refx, refy, _, _ = utm.from_latlon(tile_coordonnate[0], tile_coordonnate[1])
  ax,ay,_,_ = utm.from_latlon(area[1],area[0]) # lat,lon
  
  ref = [refx, refy]
  utm_cord = [ax,ay]
  x,y = coords_to_pixels(ref,utm_cord,resolution)
  
  images = []
  # sub_image_extraction
  for band_path in tqdm(bandes_path, total=len(bandes_path)):
    image = load_file(band_path).astype(np.float32)
    if resolution==60:
        sub_image = image[y,x]
        images.append(sub_image)
   
    else:
        sub_image = image[y-d:y+d,x-d:x+d]
        images.append(sub_image)

  images = np.array(images)
        

 # verify if the study are is cloudy
  if cld_path is not None:
    cld_mask = load_file(cld_path).astype(np.float32)
    cld = cld_mask[y-d:y+d,x-d:x+d]
    # cloud removing
    images = cloud_masking(images,cld)

  if resolution==60:
      return images
  else:
      return images.mean((1,2))