import json
from rest_framework.renderers import JSONRenderer

class PokemonJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)
        
        if errors is not None:
            return super(PokemonJSONRenderer, self).render(data)
        return json.dumps({
            'pkmns': data
        })