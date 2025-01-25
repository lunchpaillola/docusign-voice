def get_contract_definition():
    """Return Concerto definition for contract type"""
    return {
        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
        "name": "contract",
        "isAbstract": False,
        "decorators": [
            {
                "$class": "concerto.metamodel@1.0.0.Decorator",
                "name": "Term",
                "arguments": [
                    {
                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                        "value": "Contract"
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
            "name": "id"
        },
        "properties": [
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "id",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Contract ID"
                            }
                        ]
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "title",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Contract Title"
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
                "lengthValidator": {
                    "$class": "concerto.metamodel@1.0.0.StringLengthValidator",
                    "maxLength": 100
                }
            },
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "notionPageId",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Notion Page ID"
                            }
                        ]
                    }
                ]
            }
        ]
    } 