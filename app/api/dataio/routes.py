from . import dataio
from .get_type_names import get_type_names
from .get_type_definitions import get_type_definitions

# Register routes
dataio.add_url_rule('/getTypeNames', 'get_type_names', get_type_names, methods=['POST'])
dataio.add_url_rule('/getTypeDefinitions', 'get_type_definitions', get_type_definitions, methods=['POST']) 