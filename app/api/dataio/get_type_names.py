from flask import jsonify, request
from ...utils.errors import DataIOError, DataIOErrorCodes

def get_type_names():
    """Return supported data types"""
    try:
        if not request.is_json:
            raise DataIOError(
                code=DataIOErrorCodes.BAD_REQUEST,
                message="Request must be JSON",
                status_code=400
            )

        return jsonify({
            "typeNames": [
                {
                    "typeName": "contract",
                    "label": "Contract",
                    "description": "A contract document created in Notion ready for DocuSign"
                },
                {
                    "typeName": "signature_request",
                    "label": "Signature Request",
                    "description": "A DocuSign envelope status and tracking information"
                },
                {
                    "typeName": "template",
                    "label": "Contract Template",
                    "description": "Pre-configured contract templates with field mappings"
                },
                {
                    "typeName": "archive",
                    "label": "Archived Contract",
                    "description": "Signed and completed contracts with storage information"
                }
            ]
        })
    except DataIOError as e:
        raise
    except Exception as e:
        raise DataIOError(
            code=DataIOErrorCodes.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        ) 