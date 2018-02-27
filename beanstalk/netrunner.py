import requests


BASE_URI = 'https://netrunnerdb.com/api/2.0/public'

class NRDBResource(object):
    """
    This object represents a resource in the NetrunnerDB API.
    """
    location = None

    def __init__(self):
        pass

    def all(self, **params):
        uri = BASE_URI + self.location
        return requests.get(uri, params=params).json()

    def fetch(self, key, **params):
        # Hack. Chop off last character to make instace uri.
        instance_location = self.location[:-1]
        uri = BASE_URI + instance_location + '/{}'.format(key)
        print('Fetching {}'.format(uri))
        return requests.get(uri, params=params).json()


class Cards(NRDBResource):
    location = '/cards'

class Factions(NRDBResource):
    location = '/factions'

class Packs(NRDBResource):
    location = '/packs'
