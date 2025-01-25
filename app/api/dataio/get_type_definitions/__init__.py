from flask import request, jsonify
from ....utils.errors import DataIOError, DataIOErrorCodes
from .contract import get_contract_definition
from .signature import get_signature_definition
from .template import get_template_definition
from .archive import get_archive_definition
import json

def get_type_definitions():
    """Return Concerto definitions for requested types"""
    try:
        print("\n=== GetTypeDefinitions Request ===")
        
        if not request.is_json:
            print("❌ Error: Request is not JSON")
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="Request must be JSON",
                status_code=400
            )

        request_data = request.get_json()
        type_names = request_data.get('typeNames')
        print("Requested types:", type_names)
        
        if not type_names or not isinstance(type_names, list):
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="typeNames must be a non-empty array",
                status_code=400
            )

        declarations = []
        errors = []
        
        type_handlers = {
            'contract': get_contract_definition,
            'signature_request': get_signature_definition,
            'template': get_template_definition,
            'archive': get_archive_definition
        }
        
        for type_name in type_names:
            print(f"\nProcessing type: {type_name}")
            try:
                if type_name in type_handlers:
                    print(f"✅ Adding {type_name} declaration")
                    declarations.append(type_handlers[type_name]())
                else:
                    print(f"❌ Unsupported type: {type_name}")
                    errors.append({
                        "typeName": type_name,
                        "code": DataIOErrorCodes.NOT_FOUND,
                        "message": f"Type '{type_name}' is not supported"
                    })
            except Exception as e:
                print(f"❌ Error processing type {type_name}: {str(e)}")
                errors.append({
                    "typeName": type_name,
                    "code": DataIOErrorCodes.SCHEMA_RETRIEVAL_FAILED,
                    "message": f"Failed to process type '{type_name}': {str(e)}"
                })
        
        response_data = {
            "declarations": declarations,
            "errors": errors
        }
        
        return jsonify(response_data)
        
    except DataIOError as e:
        print(f"\n❌ DataIOError: {e.code} - {e.message}")
        raise
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise DataIOError(
            code=DataIOErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        ) 