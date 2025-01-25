def get_archive_definition():
    """Return Concerto definition for archived contract type"""
    return {
        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
        "name": "archive",
        "isAbstract": False,
        "decorators": [
            {
                "$class": "concerto.metamodel@1.0.0.Decorator",
                "name": "Term",
                "arguments": [
                    {
                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                        "value": "Archived Contract"
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.Decorator",
                "name": "Crud",
                "arguments": [
                    {
                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                        "value": "Createable,Readable"
                    }
                ]
            }
        ],
        "identified": {
            "$class": "concerto.metamodel@1.0.0.IdentifiedBy",
            "name": "archiveId"
        },
        "properties": [
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "archiveId",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Archive ID"
                            }
                        ]
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "storageUrl",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Storage URL"
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
                                "value": "Original Contract"
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