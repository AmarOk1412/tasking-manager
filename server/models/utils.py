from flask import current_app
from geoalchemy2 import Geometry
from geoalchemy2.functions import GenericFunction


class InvalidGeoJson(Exception):
    """
    Custom exception to notify caller they have supplied Invalid GeoJson
    """
    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class InvalidData(Exception):
    """
    Custom exception to notify caller they have supplied Invalid data to a model
    """
    def __init__(self, message):
        if current_app:
            current_app.logger.error(message)


class ST_SetSRID(GenericFunction):
    """
    Exposes PostGIS ST_SetSRID function
    """
    name = 'ST_SetSRID'
    type = Geometry


class ST_GeomFromGeoJSON(GenericFunction):
    """
    Exposes PostGIS ST_GeomFromGeoJSON function
    """
    name = 'ST_GeomFromGeoJSON'
    type = Geometry
