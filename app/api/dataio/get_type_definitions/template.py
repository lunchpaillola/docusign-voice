def get_template_definition():
    """Return Concerto definition for contract template type"""
    return {
        "$class": "concerto.metamodel@1.0.0.ConceptDeclaration",
        "name": "template",
        "isAbstract": False,
        "decorators": [
            {
                "$class": "concerto.metamodel@1.0.0.Decorator",
                "name": "Term",
                "arguments": [
                    {
                        "$class": "concerto.metamodel@1.0.0.DecoratorString",
                        "value": "Contract Template"
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
            "name": "templateId"
        },
        "properties": [
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "templateId",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Template ID"
                            }
                        ]
                    }
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "name",
                "isOptional": False,
                "isArray": False,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Template Name"
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
                ]
            },
            {
                "$class": "concerto.metamodel@1.0.0.StringProperty",
                "name": "fieldMappings",
                "isOptional": True,
                "isArray": True,
                "decorators": [
                    {
                        "$class": "concerto.metamodel@1.0.0.Decorator",
                        "name": "Term",
                        "arguments": [
                            {
                                "$class": "concerto.metamodel@1.0.0.DecoratorString",
                                "value": "Field Mappings"
                            }
                        ]
                    }
                ]
            }
        ]
    } 