#import dependcies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, desc
from datetime import datetime 
import datetime as dt


from flask import Flask, jsonify


# setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#set up flask
app = Flask(__name__)



# routes
@app.route('/')
def home():
    return ("Welcome to the Hawaii Climate Home Page<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start_date<br/>" 
            f"/api/v1.0/start_date/end_date"
           )

@app.route('/api/v1.0/precipitation')
def precipitation():
    
    #query prcp from last 12 months of last data point
    last_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date_formatted = datetime.strptime(last_date.date, '%Y-%m-%d')
    year_ago = last_date_formatted - dt.timedelta(days=365)
    year_ago_str = datetime.strftime(year_ago, '%Y-%m-%d')
    
    # Perform a query to retrieve the data and precipitation scores
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago_str).all()
    
    prcp_list = []
    for result in prcp_results:
        prcp_dict = {}
        prcp_dict[result[0]] = result[1]
        prcp_list.append(prcp_dict)
        
    return jsonify(prcp_list)

@app.route('/api/v1.0/stations')
def stations():
    stations = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(desc(func.count(Measurement.station))).all()


    return jsonify(stations)


@app.route('/api/v1.0/tobs')
def tobs():
    
    #query prcp from last 12 months of last data point
    last_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
    last_date_formatted = datetime.strptime(last_date.date, '%Y-%m-%d')
    year_ago = last_date_formatted - dt.timedelta(days=365)
    year_ago_str = datetime.strftime(year_ago, '%Y-%m-%d')
    
    temp_obs = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago_str).all()
    
    return jsonify(temp_obs)

@app.route('/api/v1.0/<start>')
def start_temp(start):
    
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    return jsonify(temps)

@app.route('/api/v1.0/<start>/<end>')
def start_end_temp(start, end):
    
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug = False)