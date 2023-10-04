# BIOMASS

**Biomass**, is an application based on satellite imagery (sentinel-2) and machine learning to estimate the above ground biomass density (AGBD) in Mg/ha and the carbon stock density MgC/ha of a 302 m^2 surface based on its centroid (lon,lat) provided as input.

## Prerequisites

- [x] Make sure all the library in requirements are install.

## Installation

To install Biomass app, follow these steps:

1. Clone the repository to your local machine, then open the project folder.

2. Copernicus API Using

Before, to use the app, you must have an account on copernicus hub [here] (https://scihub.copernicus.eu/dhus/#/home).

 Once you have your credentials on copernicus hub, you can use it to replace user and pwd, in the programme:

3. Start the application

You can  use the following command to start the app:
`python3 app.py`

4. Use the application

Once the server is up and running, you can access by going to `http://127.0.0.1:7860/` in your web browser.

This is the running applications interface 
![running application interface]("data/start.png")
![interface after AGBD estimation]("data/estimation.png")

That's it! You should now be able to use Biomass application. If you have any questions or problems, please don't hesitate to contact us at "issouf.toure@data354.co"





