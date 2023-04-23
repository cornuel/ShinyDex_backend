from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from base.models import Pokemon, ShinyHunter
from django.contrib.auth.models import User
from .serializers import PokemonSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.db.models import Q
import pyrebase
from rest_framework.authtoken.models import Token
from decouple import config
import logging
from django.db.models.query import QuerySet
from datetime import datetime
import jwt

from .filters import PokemonFilter

config = {
    "apiKey": config('FIREBASE_API_KEY'),
    "authDomain": config('FIREBASE_AUTH_DOMAIN'),
    "databaseURL": config('FIREBASE_DATABASE_URL'),
    "storageBucket": config('FIREBASE_STORAGE_BUCKET'),
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@api_view(['POST'])
def login(request):
    """
    Logs in a user with the given email and password.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: A JSON response containing a token if the login is successful,
            or an error message otherwise.
    """
    email = request.data['email']
    password = request.data['password']

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        token = jwt.encode({'user_id': user['idToken']}, 'secret_key', algorithm='HS256')
        return Response({"token": token})
    except Exception as e:
        return Response({"token": "Invalid email or password"})


@api_view(['POST'])
def signup(request):
    """
    Creates a new user account with the given email and password.

    Args:
        request (Request): The HTTP request object containing user data.

    Returns:
        Response: A JSON response indicating success or error.
    """
    email = request.data['email']
    password = request.data['password']

    try:
        user = auth.create_user_with_email_and_password(email, password)
        firebase_uid = user['localId']
        # print(firebase_uid)
        # Populate the shinyhunters node in Firebase database
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {"date_created": date_created}
        db.child("shinyhunters").child(firebase_uid).set(data=data, token=user['idToken'])
        return Response({"Success": "Success"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Error": "User already exists"}, status=status.HTTP_200_OK)

def get_user_id_from_request(request):
    """
    Extracts the user ID from a JWT token in a Django request object.
    Returns None if the token is not present or invalid.

    Args:
        request (HttpRequest): The Django request object.

    Returns:
        str: The user ID extracted from the JWT token, or None if the token is not present or invalid.
    """
    # Extract the bearer token from the request headers
    bearer_token = request.META.get('HTTP_AUTHORIZATION', None)
    if not bearer_token:
        return None

    try:
        # Extract the JWT token from the bearer token
        token = bearer_token.split(' ')[1]

        # Decode the JWT token to extract the user ID
        decoded_token = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        user_id = decoded_token['user_id']
        return user_id
    except:
        return None
    
@api_view(['POST'])
def getData(request):
    """Retrieve and sort Pokemon data from the database based on criteria.

    Parameters:
    - request: Django request object with POST data containing the following keys (all optional):
        - order_by: string representing the attribute to sort the data by (default 'regional_number')
        - sort_order: string representing the sort order ('asc' or 'desc', default 'asc')
        - type_1: string representing the first type of the Pokemon to filter by (default None)
        - type_2: string representing the second type of the Pokemon to filter by (default None)

    Returns:
    - Response: Django Response object containing a JSON list of Pokemon objects, sorted by the specified attribute and order.
    """

    order_by = request.data.get('order_by', 'regional_number')
    sort_order = request.data.get('sort_order', 'asc')
    type_1 = request.data.get('type_1')
    type_2 = request.data.get('type_2')
    
    user_id = get_user_id_from_request(request)
    if user_id:
        # Get the user's Firebase UID using their user ID
        # Besoin pour ecrire dans le node shinyhunters
        # user_info = firebase.auth().get_account_info(user_id)
        # firebase_uid = user_info['users'][0]['localId']
        
        data = db.child("pokemons").get(token=user_id)
        
        data_filtered = []
        for d in data.each():
            if type_1 is not None and type_2 is not None:
                if d.val().get('type_1') == type_1 or d.val().get('type_2') == type_1:
                    if d.val().get('type_1') == type_2 or d.val().get('type_2') == type_2:
                        data_filtered.append(d.val())
            elif type_1 is not None:
                if d.val().get('type_1') == type_1 or d.val().get('type_2') == type_1:
                    data_filtered.append(d.val())
            else :
                data_filtered.append(d.val())

            #  orderBy parameter only works on direct child nodes.
            # stat_atq field is not a direct child node of the pokemons location in the database,
            # but rather a child node of each individual pokemon record.
            # To sort the data by the stat_atq field,
            # you will need to retrieve all the data from the database and sort it in your code.

        if sort_order == 'desc':
            data_ordered = sorted(data_filtered, key=lambda x: x[order_by], reverse=True)
        else:
            data_ordered = sorted(data_filtered, key=lambda x: x[order_by], reverse=False)

        return Response(data_ordered)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def getUserData(request):
    """
    Retrieves user's pokemon data from Firebase using their Firebase UID extracted from the 
    bearer token in the request headers. Filters the retrieved data based on the user's 
    specified pokemon types, and orders the filtered data based on a specified attribute 
    and sort order. Returns a Response object that contains the ordered data in JSON format.

    Parameters:
    - request: Django request object with POST data containing the following keys (all optional):
        - order_by: string representing the attribute to sort the data by (default 'regional_number')
        - sort_order: string representing the sort order ('asc' or 'desc', default 'asc')
        - type_1: string representing the first type of the Pokemon to filter by (default None)
        - type_2: string representing the second type of the Pokemon to filter by (default None)

    Returns:
        A Response object containing the ordered data in JSON format.
    """
    user_id = get_user_id_from_request(request)
    
    if user_id:
        order_by = request.data.get('order_by', 'regional_number')
        sort_order = request.data.get('sort_order', 'asc')
        type_1 = request.data.get('type_1')
        type_2 = request.data.get('type_2')

        user_info = firebase.auth().get_account_info(user_id)
        firebase_uid = user_info['users'][0]['localId']
        
        # get the user's pokemon data from Firebase using their unique ID
        user_pokemon_data = db.child("shinyhunters").child(firebase_uid).child("pokemons").get(token=user_id).val()
        
        user_pokemon_list = list(user_pokemon_data.values())
        
        data = db.child("pokemons").get(token=user_id).val()
        
        user_data = [pokemon for pokemon in data if pokemon['national_number'] in user_pokemon_list]
        
        data_filtered = []
        for d in user_data:
            if type_1 is not None and type_2 is not None:
                if d.get('type_1') == type_1 or d.get('type_1') == type_2:
                    if d.get('type_2') == type_1 or d.get('type_2') == type_2:
                        data_filtered.append(d)
            elif type_1 is not None:
                if d.get('type_1') == type_1 or d.get('type_2') == type_1:
                    data_filtered.append(d)
            elif type_2 is not None:
                if d.get('type_1') == type_2 or d.get('type_2') == type_2:
                    data_filtered.append(d)
            else :
                data_filtered.append(d)

        if sort_order == 'desc':
            data_ordered = sorted(data_filtered, key=lambda x: x[order_by], reverse=True)
        else:
            data_ordered = sorted(data_filtered, key=lambda x: x[order_by], reverse=False)

        return Response(data_ordered)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def getUnownedPokemon(request):
    """
    Retrieves user's unowned pokemon data from Firebase using their Firebase UID extracted from the 
    bearer token in the request headers. Filters the retrieved data based on the user's 
    specified pokemon types, and orders the filtered data based on a specified attribute 
    and sort order. Returns a Response object that contains the ordered data in JSON format.

    Parameters:
    - request: Django request object with POST data containing the following keys (all optional):
        - order_by: string representing the attribute to sort the data by (default 'regional_number')
        - sort_order: string representing the sort order ('asc' or 'desc', default 'asc')
        - type_1: string representing the first type of the Pokemon to filter by (default None)
        - type_2: string representing the second type of the Pokemon to filter by (default None)

    Returns:
        A Response object containing the ordered data in JSON format.
    """
    user_id = get_user_id_from_request(request)
    
    if user_id:
        order_by = request.data.get('order_by', 'regional_number')
        sort_order = request.data.get('sort_order', 'asc')
        type_1 = request.data.get('type_1')
        type_2 = request.data.get('type_2')
        
        user_info = firebase.auth().get_account_info(user_id)
        firebase_uid = user_info['users'][0]['localId']

        # get the user's pokemon data from Firebase using their unique ID
        user_pokemon_data = db.child("shinyhunters").child(firebase_uid).child("pokemons").get(token=user_id).val()
        
        user_pokemon_list = list(user_pokemon_data.values())
        
        data = db.child("pokemons").get(token=user_id).val()
        
        user_unowned_data = [pokemon for pokemon in data if pokemon['national_number'] not in user_pokemon_list]
        
        data_filtered = []
        for d in user_unowned_data:
            if type_1 is not None and type_2 is not None:
                if d.get('type_1') == type_1 or d.get('type_1') == type_2:
                    if d.get('type_2') == type_1 or d.get('type_2') == type_2:
                        data_filtered.append(d)
            elif type_1 is not None:
                if d.get('type_1') == type_1 or d.get('type_2') == type_1:
                    data_filtered.append(d)
            elif type_2 is not None:
                if d.get('type_1') == type_2 or d.get('type_2') == type_2:
                    data_filtered.append(d)
            else :
                data_filtered.append(d)

        if sort_order == 'desc':
            data_ordered = sorted(data_filtered, key=lambda x: x[order_by], reverse=True)
        else:
            data_ordered = sorted(data_filtered, key=lambda x: x[order_by], reverse=False)

        return Response(data_ordered)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
def getComplementaryType(request):
    """
    Given a Pokemon type, this function retrieves all compatible types
    from a Firebase database and returns a list of unique types.

    Args:
        request (Request): A POST request with a 'type' parameter.

    Returns:
        JsonResponse: A JSON response containing a list of compatible types.
    """
    user_id = get_user_id_from_request(request)
    
    if user_id:
        type = request.data.get('type')

        # Get the compatible types from Firebase
        compatible_types = db.child("pokemons").order_by_child(
            "type_1").equal_to(type).get(token=user_id)
        compatible_types2 = db.child("pokemons").order_by_child(
            "type_2").equal_to(type).get(token=user_id)

        # Create a list of unique types from the compatible types
        types = []
        for t in compatible_types.each():
            if t.val()['type_1'] != 'NA' and t.val()['type_1'] != type and t.val()['type_1'] not in types:
                types.append(t.val()['type_1'])
            if t.val()['type_2'] != 'NA' and t.val()['type_2'] != type and t.val()['type_2'] not in types:
                types.append(t.val()['type_2'])
        for t in compatible_types2.each():
            if t.val()['type_1'] != 'NA' and t.val()['type_1'] != type and t.val()['type_1'] not in types:
                types.append(t.val()['type_1'])
            if t.val()['type_2'] != 'NA' and t.val()['type_2'] != type and t.val()['type_2'] not in types:
                types.append(t.val()['type_2'])

        # Return the list of types as a response
        return JsonResponse(types, safe=False)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def getSumOfAllPokemon(request):
    """
    This function receives a POST request and returns the sum of all the
    pokemons stored in the database.

    Args:
        request: The POST request object.

    Returns:
        A JsonResponse object containing the sum of all the pokemons in the
        database, with 'safe' set to False.
    """
    user_id = get_user_id_from_request(request)
    
    if user_id:
        sum = len(db.child("pokemons").get(token=user_id).val())
        return JsonResponse(sum, safe=False)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

# Create a vue that return the sum of owned pokemon by the user
@api_view(['POST'])
def getSumOfOwnedPokemon(request):
    """
    This function receives a POST request and returns the sum of all the
    pokemons stored by one user in the database.

    Args:
        request: The POST request object.

    Returns:
        A JsonResponse object containing the sum of all the pokemons owned by the user
        , with 'safe' set to False.
    """
    user_id = get_user_id_from_request(request)
    
    if user_id:
        # Extract the user's ID from the bearer token
        firebase_uid = firebase.auth().get_account_info(user_id)['users'][0]['localId']
        
        # get the user's pokemon data from Firebase using their unique ID
        pokemon_data = db.child("shinyhunters").child(firebase_uid).child("pokemons").get(token=user_id).val()
        
        if pokemon_data:
            sum = len(pokemon_data)
        else:
            sum = 0
        return JsonResponse(sum, safe=False)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def getUserPkmnList(request):
    """
    Returns a JSON response containing the list of pokemons owned by the user
    whose Firebase UID is extracted from the bearer token in the request headers.

    Parameters:
    request (HttpRequest): the HTTP request object, containing the bearer token
    in the 'Authorization' header.

    Returns:
    JsonResponse: a JSON response containing the list of pokemons owned by the user,
    retrieved from Firebase using their unique ID.
    """
    
    user_id = get_user_id_from_request(request)
    
    if user_id:
        # Extract the user's ID from the bearer token
        firebase_uid = firebase.auth().get_account_info(user_id)['users'][0]['localId']
        
        # get the user's pokemon data from Firebase using their unique ID
        pokemon_data = db.child("shinyhunters").child(firebase_uid).child("pokemons").get(token=user_id).val()
        
        if pokemon_data :
            pokemon_list = list(pokemon_data.values())
            return JsonResponse(pokemon_list, safe=False)
        else:
            return JsonResponse({}, safe=False)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def postShinyData(request):
    """
    Add or remove a pokemon from the user's shinyhunters list.

    The user is identified using a bearer token extracted from the
    HTTP_AUTHORIZATION header. The pokemon to be added or removed is
    specified in the request body.

    Returns a success message and a 200 status code if the operation
    was successful.
    """
    user_id = get_user_id_from_request(request)
    
    if user_id:
        # Extract the user's ID from the bearer token
        firebase_uid = firebase.auth().get_account_info(user_id)['users'][0]['localId']

        # Extract the pokemon from the request body
        pkmn = int(request.data.get('pkmn'))

        # Check if the pokemon is already in the user's shinyhunters list
        pokemons = db.child("shinyhunters").child(firebase_uid).child('pokemons').get(token=user_id).val()
        if pokemons is not None and pkmn in pokemons.values():
            # The pokemon already exists, remove it from the user's list
            for key, value in pokemons.items():
                if value == pkmn:
                    db.child("shinyhunters").child(firebase_uid).child('pokemons').child(key).remove(token=user_id)
                    return Response({"Success": "removed"}, status=status.HTTP_200_OK)
        else:
            # The pokemon doesn't exist, add it to the user's list
            db.child("shinyhunters").child(firebase_uid).child('pokemons').push(data=pkmn, token=user_id)
            return Response({"Success": "added"}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)