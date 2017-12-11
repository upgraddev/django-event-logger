from event_logger.settings import *

# Add the tracking field config
# Track:
"""
Person.name
Owner.name, Owner.pet
Human.age, Human.is_female, Human.body_temp, Human.birth_date
PizzeOrder.status

"""
DEBUG=True

EVENT_LOGGER_OUTPUT_FORMAT = {
    
}

EVENT_LOGGER_TRACKED_FIELDS = {
    "tests": {
        "PizzaOrder": {
            "status": {}
        },
        "Person": {
        	"name": {}
        },
        "Owner": {
        	"name": {},
        	"pet_id": {}
        },
        "Human": {
        	"age": {},
        	"is_female": {},
        	"body_temp": {},
        	"birth_date": {}
        }
    }
}