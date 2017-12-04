# Django Event Logger

A Django app to log events in database, on changes to a model field.

## Features
* Tracked models and fields can be customized in the JSON config
* Events can be selectively logged only if certain conditions on the object are satisfied, to avoid logging useless data
* Additional data (from global constants, object attributes) can also be logged along with field changes to give more context to the event

## Quickstart
#### To install Django Event Logger
```
git clone https://<user_name>@bitbucket.org/upgrad_dev/django_event_logger.git
cd django_event_logger/
python setup.py install
```
#### To include Django Event Logger in your Django Application
In your settings file:
```
INSTALLED_APPS += ('event_logger')
EVENT_LOGGER_OUTPUT_FORMAT = {} # Config for the different columns in the event logging table(more details below)
EVENT_LOGGER_TRACKED_FIELDS = {} # Config for specifying which models and fields to track and when (more details below)
```

## Config Description
#### Config for logging of additional attributes along with the events, such as request details
```
EVENT_LOGGER_OUTPUT_FORMAT = {
    "imports": ["<import statment>"], # List of import statements to fetch relevant objects and libraries (can include pre-processing steps as well)
    "columns": {
        "<column_name>": { # Name of column of the event table (Add more keys to get more columns)
            "object_name": "<Name of object, can be the one imported above>",
            "property": "<Property of the object that needs to be logged under the column_ame>",
            "default": "<default_value in case the above is None>"
        },
    }
```
#### Config for specifying which models and fields to be tracked along with the conditional logic on when to log their changes
```
EVENT_LOGGER_TRACKED_FIELDS = {
    "<app_name>": {
        "<model_name>": {
            "<field_name>": {
                "conditions": [ # List of list of conditions (Conditions in the outer list are combined by the AND operator, and conditions in the inner lists are combined by the OR operator)
                    [{
                        "property": "<property>.<nested_property>", # Property of the old_object which is going to be updated (supports nesting using '.' delimiter)
                        "operator": "==", # Operator to use for comparision
                        "value": "'<right_hand_side>'" # Value to compare the property (Can also be an object of the form: {"property": "<other_property"})
                    }],
                ]
            }
        }
    },
}
```
#### Sample Configs
```
EVENT_LOGGER_OUTPUT_FORMAT = {
    "imports": ["from ulogging.user_request import UserRequest"],
    "columns": {
        "api_base": {
            "object_name": "",
            "property": "",
            "default": "GradingAssessment"
        },
        "actor": {
            "object_name": "UserRequest",
            "property": "user_id",
        },
        "actor_role": {
            "object_name": "UserRequest",
            "property": "role",
        },
        "request_id": {
            "object_name": "UserRequest",
            "property": "request_id",
        },
        "session_id": {
            "object_name": "UserRequest",
            "property": "session_id",
        }
    }
}

EVENT_LOGGER_TRACKED_FIELDS = {
    "grades": {
        "Evaluation": {
            "status": {},
            "assigned_to": {}
        }
    },
    "testsessions": {
        "QuestionSession": {
            "status": {
                "conditions": [
                    [{
                        "property": "question.qtype",
                        "operator": "==",
                        "value": "'submission'"
                    }]
                ]
            }
        }
    }
}
```
