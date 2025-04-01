import re
import requests
import urllib.parse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from math import radians, cos, sin, sqrt, atan2

# Mapbox API For Routing
MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoiam9zaHVhdG11IiwiYSI6ImNtODIxZWx3ejBwamMyaXBpZDVkZ3Y5YXMifQ.n0rtPaR1apUFhruHZA9ggA"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ems.db'
db = SQLAlchemy(app)


class DispatchMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    incident_location = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(50), default='Normal')
    ambulance_id = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=func.now())


class Ambulance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    current_location = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=func.now())


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    available_beds = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=func.now())


class ems_app:
    def __init__(self):
        pass

    def get_coordinates(self, address):
        encoded_address = urllib.parse.quote(address)
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}.json?access_token={MAPBOX_ACCESS_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            features = data.get('features', [])
            if features:
                coordinates = features[0]['geometry']['coordinates']
                return (coordinates[1], coordinates[0])
        return None

    def get_directions(self, origin_coordinates, destination_coordinates, mode='driving'):
        origin_coordinates_str = f"{origin_coordinates[1]},{origin_coordinates[0]}"
        destination_coordinates_str = f"{destination_coordinates[1]},{destination_coordinates[0]}"
        url = (f"https://api.mapbox.com/directions/v5/mapbox/{mode}/{origin_coordinates_str};"
               f"{destination_coordinates_str}?geometries=geojson&steps=true&access_token={MAPBOX_ACCESS_TOKEN}&overview=full")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            routes = data.get('routes', [])
            if routes:
                route = routes[0]
                leg = route.get('legs', [])[0]
                steps = []
                for step in leg.get('steps', []):
                    instruction = step.get('maneuver', {}).get('instruction', '')
                    instruction = re.sub('<.*?>', '', instruction)
                    steps.append(instruction)
                route_info = {
                    'distance': {
                        'text': f"{route.get('distance', 0)/1000:.2f} km",
                        'value': route.get('distance', 0)
                    },
                    'duration': {
                        'text': f"{int(route.get('duration', 0)//60)} min {int(route.get('duration', 0)%60)} sec",
                        'value': route.get('duration', 0)
                    },
                    'steps': steps
                }
                return route_info
        return None

    def get_best_hospital(self, incident_coordinates, hospitals):
        best_hospital = None
        best_duration = None
        for hospital in hospitals:
            if hospital.available_beds <= 0:
                continue
            hospital_coordinates = self.get_coordinates(hospital.address)
            route_info = self.get_directions(incident_coordinates, hospital_coordinates, mode='driving')
            if route_info and 'duration' in route_info:
                duration = route_info['duration']['value']
                if best_duration is None or duration < best_duration:
                    best_duration = duration
                    best_hospital = hospital
        return best_hospital, best_duration

    def calculate_distance(self, coord1, coord2):
        R = 6371  # Radius of Earth in kilometers
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def startEMS(self):
        # Initialize the database and add sample data
        db.create_all()
        # Add Sample Hospitals
        if not Hospital.query.first():
            mountSinai = Hospital(
                name="Mount Sinai Hospital",
                address="600 University Ave, Toronto",
                available_beds=100
            )
            sunnybrook = Hospital(
                name="Sunnybrook Health Sciences Centre",
                address="2075 Bayview Ave, Toronto",
                available_beds=0
            )
            torontoGeneral = Hospital(
                name="Toronto General Hospital",
                address="200 Elizabeth St, Toronto",
                available_beds=5
            )
            stMichaels = Hospital(
                name="St. Michael's Hospital",
                address="30 Bond St, Toronto",
                available_beds=5
            )
            humberRiver = Hospital(
                name="Humber River Hospital",
                address="1235 Wilson Ave, North York",
                available_beds=5
            )
            northYorkGeneral = Hospital(
                name="North York General Hospital",
                address="4001 Leslie St, North York",
                available_beds=5
            )
            sickKids = Hospital(
                name="The Hospital for Sick Children",
                address="555 University Ave, Toronto",
                available_beds=5
            )
            db.session.add_all([mountSinai, sunnybrook, torontoGeneral,
                                stMichaels, humberRiver, northYorkGeneral, sickKids])
            db.session.commit()
        # Add Sample Ambulances
        if not Ambulance.query.first():
            ambulance1 = Ambulance(
                identifier="Ambulance 1",
                status=True,
                current_location="58 Richmond St E, Toronto"
            )
            ambulance2 = Ambulance(
                identifier="Ambulance 2",
                status=True,
                current_location="135 Davenport Rd, Toronto"
            )
            ambulance3 = Ambulance(
                identifier="Ambulance 3",
                status=False,
                current_location="135 Davenport Rd, Toronto"
            )
            ambulance4 = Ambulance(
                identifier="Ambulance 4",
                status=True,
                current_location="12 Canterbury Pl, North York"
            )
            ambulance5 = Ambulance(
                identifier="Ambulance 5",
                status=True,
                current_location="3300 Bayview Ave, North York"
            )
            db.session.add_all(
                [ambulance1, ambulance2, ambulance3, ambulance4, ambulance5])
            db.session.commit()

    def create_dispatch(self):
        try:
            data = request.get_json()
            message = data.get('message')
            incident_location = data.get('incident_location')
            severity = data.get('severity', 'Normal')

            if not all([message, incident_location]):
                return jsonify({'error': 'Missing Required Fields'}), 400

            # Get incident coordinates
            incident_coordinates = self.get_coordinates(incident_location)
            if not incident_coordinates:
                return jsonify({'error': 'Unable to Retrieve Incident Location Coordinates'}), 400

            # Find all available ambulances
            available_ambulances = Ambulance.query.filter_by(status=True).all()
            if not available_ambulances:
                return jsonify({'error': 'No Available Ambulances'}), 400

            # Find the closest ambulance
            closest_ambulance = None
            shortest_distance = float('inf')
            for ambulance in available_ambulances:
                ambulance_coordinates = self.get_coordinates(ambulance.current_location)
                if ambulance_coordinates:
                    distance = self.calculate_distance(incident_coordinates, ambulance_coordinates)
                    print(f"Ambulance {ambulance.identifier} Distance: {distance}")
                    if distance < shortest_distance:
                        shortest_distance = distance
                        closest_ambulance = ambulance

            if not closest_ambulance:
                return jsonify({'error': 'No Ambulances with Valid Locations'}), 400

            # Update ambulance status and location
            closest_ambulance.status = False
            closest_ambulance.current_location = incident_location
            db.session.commit()

            # Create dispatch message
            dispatch_message = DispatchMessage(
                message=message,
                incident_location=incident_location,
                severity=severity,
                ambulance_id=closest_ambulance.identifier
            )
            db.session.add(dispatch_message)
            db.session.commit()

            return jsonify({
                'message': 'Dispatch Message Created Successfully',
                'ambulance': closest_ambulance.identifier
            }), 201

        except Exception as e:
            print(f"Error in create_dispatch: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500

    def get_dispatches(self):
        dispatchMessages = DispatchMessage.query.order_by(DispatchMessage.timestamp.desc()).all()
        allDispatches = []
        for dispatchMessage in dispatchMessages:
            allDispatches.append({
                'id': dispatchMessage.id,
                'message': dispatchMessage.message,
                'incident_location': dispatchMessage.incident_location,
                'severity': dispatchMessage.severity,
                'timestamp': dispatchMessage.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'ambulance': dispatchMessage.ambulance_id
            })
        return jsonify(allDispatches), 200

    def get_ambulances(self):
        ambulances = Ambulance.query.all()
        allAmbulances = []
        for ambulance in ambulances:
            allAmbulances.append({
                'id': ambulance.id,
                'identifier': ambulance.identifier,
                'status': ambulance.status,
                'current_location': ambulance.current_location,
                'last_updated': ambulance.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify(allAmbulances), 200

    def get_route(self):
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        mode = data.get('mode', 'driving')
        origin_coordinates = self.get_coordinates(origin)
        destination_coordinates = self.get_coordinates(destination)
        if not origin_coordinates or not destination_coordinates:
            return jsonify({'error': 'Unable to Retrieve Coordinates'}), 400
        route_info = self.get_directions(origin_coordinates, destination_coordinates, mode)
        if route_info:
            route_info['origin'] = origin
            route_info['destination'] = destination
            return jsonify(route_info), 200
        return jsonify({'error': 'No route found'}), 400

    def suggest_hospital(self):
        data = request.get_json()
        incident_location = data.get('incident_location')
        incident_coordinates = self.get_coordinates(incident_location)
        if not incident_coordinates:
            return jsonify({'error': 'Unable to Retrieve Incident Location'}), 400
        hospitals = Hospital.query.all()
        best_hospital, best_duration = self.get_best_hospital(incident_coordinates, hospitals)
        if best_hospital is None:
            return jsonify({'error': 'No hospital available'}), 400
        minutes = int(best_duration // 60)
        seconds = int(best_duration % 60)
        return jsonify({
            'hospital_id': best_hospital.id,
            'name': best_hospital.name,
            'address': best_hospital.address,
            'available_beds': best_hospital.available_beds,
            'estimated_travel_time': f"{minutes} min {seconds} sec"
        }), 200

    def debug_ambulances(self):
        ambulances = Ambulance.query.all()
        return jsonify([{
            'id': amb.id,
            'identifier': amb.identifier,
            'status': amb.status,
            'current_location': amb.current_location
        } for amb in ambulances])


# Create an instance of our EMS app logic
ems = ems_app()

# Define the Flask endpoints as standalone functions
@app.route('/')
def home():
    return "EMS Dispatcher Server is Running..."


@app.route('/dispatch', methods=['POST'])
def create_dispatch():
    return ems.create_dispatch()


@app.route('/dispatches', methods=['GET'])
def get_dispatches():
    return ems.get_dispatches()


@app.route('/ambulances', methods=['GET'])
def get_ambulances():
    return ems.get_ambulances()


@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    hospitals = Hospital.query.all()
    allHospitals = []
    for hospital in hospitals:
        allHospitals.append({
            'id': hospital.id,
            'name': hospital.name,
            'address': hospital.address,
            'available_beds': hospital.available_beds,
            'last_updated': hospital.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(allHospitals), 200


@app.route('/route', methods=['POST'])
def get_route():
    return ems.get_route()


@app.route('/suggest_hospital', methods=['POST'])
def suggest_hospital():
    return ems.suggest_hospital()


@app.route('/debug/ambulances', methods=['GET'])
def debug_ambulances():
    return ems.debug_ambulances()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    shutdown_func()
    return 'Server shutting down...'


if __name__ == '__main__':
    # Ensure the app context is active for initializing the database and sample data
    with app.app_context():
        ems.startEMS()
    app.run(debug=True, use_reloader=False)
