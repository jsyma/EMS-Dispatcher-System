import requests
import urllib.parse

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

class EMS_Server():
    def __init__(self):
        self.emsApp = Flask(__name__)
        self.emsApp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ems.db'
        self.emsApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.database = SQLAlchemy(self.emsApp)

        self.map = Map(self)

class MessageHandler():
    def __init__(self): #@TODO
        pass

class Dispatcher():
    def __init__(self, server:EMS_Server): #@TODO
        self.server = server
        pass

    def kill_server(self):
        '''
        Kills the primary server when called 
        '''
        foo = request.environ.get('werkzeug.server.shutdown')
        if foo is None:
            raise RuntimeError("Shutdown failure")
        foo()

        @self.server.route('/shutdown', methods=['POST'])
        def shutdown():
            self.shutdown_server()
            return 'Server shutting down...'

from abc import ABC, abstractmethod 
class EMSObject(ABC):
    '''
    An abstract class for objects of interest within the EMS program 
    '''
    def __init__(self):
        pass

    @abstractmethod
    def update(): #@TODO
        pass

class Hospital(EMSObject):
    def __init__(self): 
        super().__init__()
        #@TODO
    
    def update(): #TODO
        pass

class Operator(EMSObject):
    def __init__(self): 
        super().__init__()
        #@TODO
    
    def update(): #TODO
        pass

class Ambulance(EMSObject):
    def __init__(self): 
        super().__init__()
        #@TODO
    
    def update(): #TODO
        pass


class Map():
    ''''
    Class to interact with the MAPBOX API
    Will contain useful map-related functions
    '''
    def __init__(self, app:EMS_Server):
       self.app = app
       self.TOKEN = "pk.eyJ1Ijoiam9zaHVhdG11IiwiYSI6ImNtODIxZWx3ejBwamMyaXBpZDVkZ3Y5YXMifQ.n0rtPaR1apUFhruHZA9ggA"
    
    def get_coordinates(self, address) -> tuple:
        """
        Attemps to fetch the coordiates of a given address as a pair of x,y corrdinates
        """
        encoded_addr:str = urllib.parse.quote(address)
        token:str = self.TOKEN

        url:str = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + encoded_addr + ".json?access_token=" + token 
        response = requests.get(url)

        if response.status_code == 200: # sucess
            data = response.json()
            features = data.get('features', [])
            if features:
                coords = features[0]['geometry']['coordinates']
                return (coords[1], coords[0])
        self.app.logger.error("Failed to geocode address: %s", address)
        return None
    
    def get_directions(self, start_pos: tuple, end_pos:tuple) -> dict:
        #@TODO
        pass
    
