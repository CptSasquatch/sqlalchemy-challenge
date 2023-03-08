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
Base.prepare(autoload_with=engine, reflect=True)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(bind=engine)
# Find the most recent date in the data set.
last_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()
# create variable for the most recent date
last_date = dt.date.fromisoformat(last_date_row[0])
# Calculate the date one year from the last date in data set.
query_date = last_date - dt.timedelta(days=365)
# close session
session.close()

# design a Flask API based on the queries that you have just developed.
# create an app
app = Flask(__name__)

# design available routes when user hits the index route
@app.route("/")
def index():
    return(
        '''
        <h1>Welcome to the Hawaii Climate Analysis API!</h1><br/>
        
        <h2>Available Routes:</h2><br/>
        '''
        '''
        <p>/api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/yyyy-mm-dd<br/>
        /api/v1.0/yyyy-mm-dd/yyyy-mm-dd</p><br/>
        '''
    )


# design precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session (link) from Python to the DB
    session = Session(bind=engine)
    # Calculate the date one year from the last date in data set.
    last_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = dt.date.fromisoformat(last_date_row[0])
    query_date = last_date - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(measurement.date, measurement.prcp)
    prcp_data = prcp_data.filter(measurement.date >= query_date).all()
    # convert rows to dictionary
    prcp_dict = {prcp_data[i][0]: prcp_data[i][1] for i in range(len(prcp_data))}
    # close session
    session.close()
    # create a JSON of the precipitation data for the last year
    return jsonify(prcp_dict)
# design stations route
@app.route("/api/v1.0/stations")
def stations():
    # create session (link) from Python to the DB
    session = Session(bind=engine)
    # query for the stations
    station_data = session.query(station.station, station.name).all()
    # convert rows to dictionary
    station_dict = {station_data[i][0]: station_data[i][1] for i in range(len(station_data))}
    # close session
    session.close()
    # return a json list of stations from the dataset
    return jsonify(station_dict)
# design tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # create session (link) from Python to the DB
    session = Session(bind=engine)
    # query the last 12 months of temperature observation data for the most active station
    year_temp = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= query_date).all()
    # convert rows to dictionary
    tobs_dict = {year_temp[i][0]: year_temp[i][0] for i in range(len(year_temp))}
    # close session
    session.close()
    # return a json list of Temperature Observations (tobs) for the previous year
    return jsonify(tobs_dict)
# design start route
@app.route("/api/v1.0/<start>")
def start(start):
    # create session (link) from Python to the DB
    session = Session(bind=engine)
    # Query for the minimum temperature, the average temperature, and the maximum temperature for a specified start date
    temp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    # Create a dictionary from the row data and add key/value pairs
    temp_dict = {"Minimum Temperature": temp_data[0][0], "Average Temperature": temp_data[0][1], "Maximum Temperature": temp_data[0][2]}
    # close session
    session.close()
    return jsonify(temp_dict)
# design start/end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # create session (link) from Python to the DB
    session = Session(bind=engine)
    # Query for the minimum temperature, the average temperature, and the maximum temperature for a specified start and end date
    temp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    # Create a dictionary from the row data and add key/value pairs
    temp_dict = {"Minimum Temperature": temp_data[0][0], "Average Temperature": temp_data[0][1], "Maximum Temperature": temp_data[0][2]}
    # close session
    session.close()
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)
    