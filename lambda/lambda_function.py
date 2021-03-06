# -*- coding: utf-8 -*-
import requests
import logging
import json
import os

from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
import ask_sdk_core.utils as ask_utils
from ask_sdk_model import Response

from setup import API_KEY

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "http://luke-lopez-cgm.herokuapp.com"
ENDPOINT = "/api/v1/entries/sgv.json"
TOKEN = "?token=" + API_KEY
DIRECTIONS = {
    "Flat": "steady",
    "FortyFiveUp": "rising",
    "FortyFiveDown": "falling",
    "SingleUp": "single up",
    "DoubleUp": "double up",
    "SingleDown": "single down",
    "DoubleDown": "double down",
    "NONE": "no slope",
    "NOT_COMPUTABLE": "the slope is not computable",
    "RATE_OUT_OF_RANGE": "the rate is out of range"
}


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome, you can say Hello or Help. Which would you like to try?"
        response = (handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response)

        logger.info(response)
        return (
            response
        )


class BloodSugarIntentHandler(AbstractRequestHandler):
    """Handler for Blood Sugar Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("BloodSugarIntent")(handler_input)

    def handle(self, handler_input):
        res = requests.get(BASE_URL + ENDPOINT + TOKEN)

        if res.status_code == 200:
            data = json.loads(res.content)[0]
            input_subject = ask_utils.request_util.get_slot(
                handler_input,
                "subject"
            ).value

            subject = "your" if input_subject == "my" else "luke's"
            blood_sugar = str(data["sgv"])
            direction = DIRECTIONS.get(data["direction"], "no direction found")

            speak_output = f"{subject} blood sugar is {blood_sugar} and {direction}."
        else:
            logger.error(
                f"Status Code: {res.status_code} Reason: {res.reason}")
            speak_output = "I couldn't get the reading. Please try again!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(BloodSugarIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
