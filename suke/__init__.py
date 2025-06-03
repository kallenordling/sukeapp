from flask import Flask, request, render_template, jsonify
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geography
import numpy
import logging
import sys
user=os.environ.get("user")
password=os.environ.get("password")
host=os.environ.get("host")
database=os.environ.get("database")
DATABASE_URL =os.environ.get("DATABASE_URL")
app = Flask(__name__, template_folder='./templates')
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
	os.makedirs(UPLOAD_FOLDER)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DiveSite(Base):
	__tablename__ = "dive_sites"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	lat = Column(Integer, nullable=False)
	lon = Column(Integer, nullable=False)
	comments = Column(String)
	#geom = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

Base.metadata.create_all(bind=engine)
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stderr)])
@app.route('/')
def index():
	app.logger.debug('get dive sites')

	return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
	if 'file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	file = request.files['file']
	if file.filename == '':
		return jsonify({'error': 'No selected file'}), 400
	coordinates = request.form.get('coordinates')
	if not coordinates:
		return jsonify({'error': 'No coordinates provided'}), 400
	device = request.form.get('device')
	if not device:
		return jsonify({'error': 'No device selected'}), 400
	site = request.form.get('site')
	if not site:
		return jsonify({'error': 'No site selected'}), 400
	if file:
		filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
		file.save(filepath)
		df = pd.read_csv(filepath)
		# Add coordinates to the DataFrame
		df['coordinates'] = coordinates
		# Process based on the selected device
		if device == 'shearwater':
			filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
			file.save(filepath)
			app.logger.debug(f'File saved to {filepath}')
			df = pd.read_csv(filepath,skiprows=2,usecols=['Water Temp','Depth'])
			df.to_csv(filepath)
			# Add coordinates to the DataFrame
			#df['coordinates'] = coordinates
			#app.logger.debug(f'DataFrame: {df.head().to_dict(orient="records")}')
			return jsonify({'succcess':'file upload done'})
	return jsonify({'error': 'File not uploaded'}), 400

@app.route('/dive_sites', methods=['GET'])
def get_dive_sites():
	app.logger.error('get dive sites')
	session = SessionLocal()
	sites = session.query(DiveSite).all()
	session.close()
	return jsonify([{'id': site.id, 'name': site.name, 'lat': site.lat, 'lon': site.lon, 'comments': site.comments} for site in sites])
	#return jsonify([{'id': 1, 'name': "test"}])
	#return jsonify({'succcess':'file upload done'})

@app.route('/create_dive_site', methods=['POST'])
def create_dive_site():
	try:
		data = request.get_json()
		app.logger.debug('Received data for new dive site: %s', data)
		name = data.get('name')
		lat = data.get('lat')
		lon = data.get('lon')
		comments = data.get('comments')
        
		if not name or lat is None or lon is None:
			return jsonify({'success': False, 'error': 'Missing data for new dive site'}), 400

		session = SessionLocal()
		new_site = DiveSite(name=name, lat=lat, lon=lon, comments=comments)#, geom=f'SRID=4326;POINT({lon} {lat})')
		session.add(new_site)
		session.commit()
		session.refresh(new_site)
		session.close()
		return jsonify({'success': True, 'site': { 'name': name, 'lat': lat, 'lon': lon, 'comments': comments}})
	except Exception as e:
		app.logger.error('Error creating new dive site: %s', e)
		return jsonify({'success': False, 'error': str(e)}), 500
 

if __name__ == '__main__':
	app.run(debug=True)
