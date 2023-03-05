# Import dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import numpy as np
import pandas as pd
import datetime as dt


# Convert the query results from precipitation analysis to a dictionary using date as the key and prcp as the value.
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# Calculate the date one year from the last date in data set.
query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
# Perform a query to retrieve the data and precipitation scores
prcp_data = session.query(measurement.date, measurement.prcp)
prcp_data = prcp_data.filter(measurement.date >= query_date).all()
# Save the query results as a Pandas DataFrame and set the index to the date column
prcp_df = pd.DataFrame(prcp_data, columns=['Date', 'Precipitation'])
prcp_df.set_index('Date', inplace=True)
# Sort the dataframe by date
prcp_df = prcp_df.sort_values(by='Date')
# convert the dataframe to a dictionary
prcp_dict = prcp_df.to_dict()
# query for the stations
station_data = session.query(station.station, station.name)
# Save the query results as a Pandas DataFrame 
station_df = pd.DataFrame(station_data, columns=['Station', 'Name'])
station_df.set_index('Station', inplace=True)
# convert the dataframe to a dictionary
station_dict = station_df.to_dict()
# Using the most active station id
# Query the last 12 months of temperature observation data for this station
year_temp = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= query_date).all()
# Save the query results as a Pandas DataFrame
tobs_df = pd.DataFrame(year_temp, columns=['Temperature'])
# convert the dataframe to a dictionary
tobs_dict = tobs_df.to_dict()
# Query the dates and temperature observations
all_temp = session.query(measurement.date, measurement.tobs).all()
# Save the query results as a Pandas DataFrame
tobs_all_df = pd.DataFrame(all_temp, columns=['Date', 'Temperature'])
# convert the dataframe to a dictionary
tobs_all_dict = tobs_all_df.to_dict()
# close session
session.close()

# design a Flask API based on the queries that you have just developed.
# create an app
app = Flask(__name__)

# design available routes when user hits the index route
@app.route("/")
def index():
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


# design precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create a JSON of the precipitation dictionary for the last year of data
    return jsonify(prcp_dict)
# design stations route
@app.route("/api/v1.0/stations")
def stations():
    # return a json list of stations from the dataset
    return jsonify(station_dict)
# design tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # return a json list of Temperature Observations (tobs) for the previous year
    return jsonify(tobs_dict)
# design start route
@app.route("/api/v1.0/<start>")
def start(start):
    # return a json list of the minimum temperature, the average temperature, and the max temperature for a given start date
    results = {tobs_all_dict['Date'][i]: tobs_all_dict['Temperature'][i] for i in range(len(tobs_all_dict['Date'])) if tobs_all_dict['Date'][i] >= start}
    return jsonify(results)
# design start/end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # for a given start-end range, return a json list of the minimum temperature, the average temperature, and the max temperature for a given start-end range
    results2 = {tobs_all_dict['Date'][i]: tobs_all_dict['Temperature'][i] for i in range(len(tobs_all_dict['Date'])) if tobs_all_dict['Date'][i] >= start and tobs_all_dict['Date'][i] <= end}
    return jsonify(results2)

if __name__ == "__main__":
    app.run(debug=True)
    