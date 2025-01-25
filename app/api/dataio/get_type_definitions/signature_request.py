def get_signature_definition():
    """Return Concerto definition for signature request type"""
    return {
        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
        "name": "signature_request",
        "isAbstract": False,
        "decorators": [
            {
                "$class": "concerto.metamodel@1.0.0.Decorator",
                "name": "Term",
                "arguments": [
                    {
                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                        "value": "Signature Request"
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.Decorator",
                "name": "Crud",
                "arguments": [
                    {
                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                        "value": "Createable,Readable,Updateable"
                    }
                ]
            }
        ],
        "identified": {
            "$class": "concerto.metamodel@1.0.0.IdentifiedBy",
            "name": "envelopeId"
        },
        "properties": [
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "envelopeId",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "DocuSign Envelope ID"
                            }
                        ]
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "status",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Signature Status"
                            }
                        ]
                    },
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Crud",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Readable,Updateable"
                            }
                        ]
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.RelationshipProperty",
                "name": "contract",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Associated Contract"
                            }
                        ]
                    }
                ],
                "type": {
                    "$class": "concerto.metamodel@1.0.0.TypeIdentifier",
                    "name": "contract"
                }
            }
        ]
    } 