from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import datetime, timedelta,date
import zipfile
import rasterio
from rasterio.plot import show
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from glob import glob
from tqdm import tqdm
#from haversine import haversine, Unit
#from xml.etree import ElementTree as et
import xmltodict
import json
import warnings
import shutil
warnings.filterwarnings('ignore')

##
def map_number(number):
      return str(0)+str(number) if len(str(number))==1 else str(number)

##
def download(cordinate):
    #constant
    GEOMAP = read_geojson('data/map.geojson')

    lon,lat = cordinate[0],cordinate[1]
    A,B,C,D =  [lon-0.01,lat+0.01],[lon-0.01,lat-0.01],[lon+0.01,lat-0.01],[lon+0.01,lat+0.01]
    area_of_study = [[A,B,C,D,A]]
    GEOMAP["features"][0]["geometry"]["coordinates"] = area_of_study

    N_DAYS_AGO = 7
    today = datetime.now()
    current_year_today,current_month_today,current_day_today = today.year, today.month, today.day
    n_days_ago = today - timedelta(days=N_DAYS_AGO)
    current_year_n_days_ago,current_month_n_days_ago,current_day_n_days_ago = n_days_ago.year, n_days_ago.month, n_days_ago.day
    day_format = date(current_year_today,current_month_today,current_day_today)
    n_days_ago_format = str(current_year_n_days_ago)+map_number(current_month_n_days_ago)+map_number(current_day_n_days_ago)

    # connexion to corpernicus hub
    with open('credentials.json', 'r') as openfile:
        # Reading from json file
        credentials = json.load(openfile)

    user = credentials["user"]
    pwd = credentials["pwd"]

    api = SentinelAPI(user, pwd, 'https://apihub.copernicus.eu/apihub')
    #cloudcoverpercentage=(0, 30)
    #limit = 2
    footprint = geojson_to_wkt(GEOMAP) # GEOMAP format (lon,lat)
    products = api.query(footprint,
                        date=(n_days_ago_format, day_format),
                        platformname='Sentinel-2',
                        producttype = "S2MSI2A")
    
    # download all results from the search
    api.download_all(products)

##
def unzip():
    files = glob('*.zip')
    for file in files:
         with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall()


##
def select_best_cloud_coverage_tile():
    tile_names = {}
    cld_prob = []
    folders = glob('*.SAFE')
    for fold in folders:
        metadata_path = fold+"/MTD_MSIL2A.xml"
        xml_file=open(metadata_path,"r")
        xml_string=xml_file.read()
        python_dict=xmltodict.parse(xml_string)
        cld = float(python_dict["n1:Level-2A_User_Product"]["n1:Quality_Indicators_Info"]["Cloud_Coverage_Assessment"])
        tile_names[cld] = fold
        cld_prob.append(cld)
    name = tile_names[min(cld_prob)]
    dates = name.split('_')[2][:8]
    acquisition_date = datetime.strptime(dates, "%Y%m%d")
    today = datetime.now()
    delta = (today - acquisition_date)
    days_ago = delta.days
    return name,min(cld_prob),days_ago

##
def delete_tiles():
        files = glob('*.zip')
        folders = glob('*.SAFE')
        for f in files:
            os.remove(f)
        for fold in folders:
            shutil.rmtree(fold, ignore_errors=True)




