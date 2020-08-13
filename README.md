# DOTA-2-Project

## Goal
The primary focus of this project is to explore the data from the [Dota 2 API](https://www.opendota.com/) and work on machine learning techniques with said data. Because of the large variety and amount of data available through the API, my first task will be to look at an explore the picks and bans of a single professional team and see what information can be gained.

## Data Extraction and Procesing
Thanks to [This Article](https://medium.com/@waprin/python-and-dota2-analyzing-team-liquids-io-success-and-failure-7d44cc5979b2) for instuctions and code for extracting data from the api. To start the project I need to learn how to access the api and get the data to start analysing it. So I started by dirrectly downloading the jsons for the hero id pairs and the matches recently played by liquid. Once this step was done I then used request package to get the match data from the api. At the start of this project Team Liquid (the profesional team I was looking at) had 1608 recorded matches and each match had almost too much information to for me at this time so I decided to only look at 100 matches and save the picks and bans to a local csv file.

## EDA
Because I was looking at the picks and bans in the 100 most recent Team Liquid matches...