import gradio as gr
from api import *
from processing import *
import pandas as pd
from indices import indices
import xgboost as xgb
import pickle

def predict(lat, lon):
    cord = [lon,lat]
    download(cord)
    unzip()
    name,cld_prob,days_ago = select_best_cloud_coverage_tile()
    
    bandes_path_10,bandes_path_20,bandes_path_60,tile_path,path_cld_20,path_cld_60 =paths(name)
    # create image dataset
    images_10 = extract_sub_image(bandes_path_10,tile_path,cord)

    # bandes with 20m resolution
    #path_cld_20
    images_20 = extract_sub_image(bandes_path_20,tile_path,cord,20,1)

    # bandes with 60m resolution
    #path_cld_60
    images_60 = extract_sub_image(bandes_path_60,tile_path,cord,60)
    #
    feature = images_10.tolist()+images_20.tolist()+images_60.tolist()
    bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B11', 'B12','B01','B09']
    X = pd.DataFrame([feature],columns = bands)
    # vegetation index calculation
    X = indices(X)
    # load the model from disk
    filename = "data/finalized_model.sav"
    loaded_model = pickle.load(open(filename, 'rb'))
    # make prediction
    biomass = loaded_model.predict(X)[0]
    carbon = 0.55*biomass

    # NDVI
    ndvi_index = ndvi(cord,name)

    # deleted download files
    delete_tiles()

    return str(cld_prob)+ " % cloud coverage", str(days_ago)+" days ago",str(biomass)+" Mg/ha", str(carbon)+" MgC/ha","NDVI: "+ str(ndvi_index)

# Create title, description and article strings
title = "🌴BEEPAS : Biomass estimation to Evaluate the Environmental Performance of Agroforestry System🌴"
description = "This application estimates the biomass of certain areas using AI and satellite images (S2)."
article = "Created by data354."

# Create examples list from "examples/" directory
#example_list = [["examples/" + example] for example in os.listdir("examples")]
example_list = [[5.379913, -4.050445],[6.54644,-7.86156],[5.346938, -4.027849]]

outputs = [
    gr.Textbox(label="Cloud coverage"),
    gr.Textbox(label="Number of days since sensing"),
    gr.Textbox(label="Above ground biomass density(AGBD) Mg/ha"),
    gr.Textbox(label="Carbon stock density MgC/ha "),
    gr.Textbox(label="Mean NDVI"),]


demo = gr.Interface(
    fn=predict,
    inputs=["number", "number"],
    outputs=outputs, #[ "text", "text","text","text","text"],
    examples=example_list,
    title=title,
    description=description,
    article=article,
    )

demo.launch(share=True)