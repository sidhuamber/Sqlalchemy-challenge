#Importing dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func

from flask import Flask, jsonify

#Database setup
engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect an axisting data base into a new model
Base=automap_base()

#Reflect the table
Base.prepare(engine,reflect=True)

#Save references to the table measurement
Measurement = Base.classes.measurement

# Save references to each table - Station table
Station = Base.classes.station

#Flask Setup

app = Flask(__name__)

#Flask routes

@app.route("/")
def welcome():
    return(
        f"WELCOME TO THE CLIMATE APP HOMEPAGE<br/>"
        f"Available Routes:<br/>"
        f"----------------------------------------------<br/>"
        f"API to return the dates and precipitation values<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"----------------------------------------------<br/>"
        f"API for the list of stations in the data<br/>"
        f"/api/v1.0/stations<br/>"
        f"----------------------------------------------<br/>"
        f"API for the dates with the following temperature observations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"----------------------------------------------<br/>"
        f"API for the min temperature,average temperature and max temperature for a start date<br/>"
        f"/api/v1.0/start_date<br/>"
        f"----------------------------------------------<br/>"
        f"API for the min temperature,average temperature and max temperature for a start date and end date<br/>"
        f"/api/v1.0/start_date/end_date"
        )

#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link from python to DB)
    session=Session(engine)

    # Return a list of date and precipitation from Measurement table
    results=session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    # Create a dictionary from the raw data and append to a list of all measurements
    all_measurement=[]
    for date,prcp in results:
        measurement_dict={}
        measurement_dict["date"]=date
        measurement_dict["prcp"]=prcp
        all_measurement.append(measurement_dict)

    return jsonify(all_measurement)

#Stations route

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link from python to DB)
    session=Session(engine)

    # Return a JSON list of stations from the dataset.

    results = session.query(Station.station,Station.name).all()
    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# TOBS Route

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link from python to DB)
    session=Session(engine)

    # Return a JSON list of temperature observations (TOBS) for the previous year.

    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date >'2016-08-23').\
        filter(Measurement.station =="USC00519281").\
        order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the raw data and append to a list of all tobs

    all_tobs=[]
    for date,tobs in results:
        tobs_dict={}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

# Start Route 

@app.route("/api/v1.0/<start_date>")
def value(start_date):

    # Create our session (link from python to DB)
    session=Session(engine)

    # Return a JSON list When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    value = session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).group_by(Measurement.date).all()

    session.close()

    return jsonify(value)

# Start and end Route 

@app.route("/api/v1.0/<start_date>/<end_date>")
def svalue(start_date,end_date):

    # Create our session (link from python to DB)
    session=Session(engine)

    # Return a JSON list When given the start and end date, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    svalue = session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date).group_by(Measurement.date).all()

    session.close()

    return jsonify(svalue)


if __name__ == '__main__':
    app.run(debug=True)
