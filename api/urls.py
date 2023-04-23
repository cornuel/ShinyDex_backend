from django.urls import path, include
from . import views

urlpatterns = [
    path('getData', views.getData, name='getData'),
    path('getSumOfAllPokemon', views.getSumOfAllPokemon, name='getSumOfAllPokemon'),
    path('getSumOfOwnedPokemon', views.getSumOfOwnedPokemon, name='getSumOfOwnedPokemon'),
    path('getComplementaryType', views.getComplementaryType, name='getComplementaryType'),
    path('getUserData', views.getUserData, name='getUserData'),
    path('getUnownedPokemon', views.getUnownedPokemon, name='getUnownedPokemon'),
    path('getUserPkmnList', views.getUserPkmnList, name='getUserPkmnList'),
    path('postShinyData', views.postShinyData, name='postShinyData'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
]