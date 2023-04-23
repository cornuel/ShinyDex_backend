import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

# Initialize Firebase SDK
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://shinyhuntclone-default-rtdb.europe-west1.firebasedatabase.app'
})

# Import data from JSON file
with open('data.json', 'r') as f:
    data = json.load(f)
    ref = db.reference('/pokemons')
    ref.set(data)
