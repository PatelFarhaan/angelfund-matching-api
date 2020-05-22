import sys
sys.path.append("../")
from project.models import Startup, Investor


def investor_jwt_decoder(encoded_identifier):
    email = encoded_identifier["email"]
    model = encoded_identifier["model"]

    if model != "Investor":
        return {"result": False,
                "error": "invalid token"}

    user_obj = Investor.objects.filter(email=email).first()

    if not user_obj:
        return {"result": False,
                "error": "user not found"}
    return {
        "result": True,
        "user_obj": user_obj
    }


def startup_jwt_decoder(encoded_identifier):
    email = encoded_identifier["email"]
    model = encoded_identifier["model"]

    if model != "Startup":
        return {"result": False,
                "error": "invalid token"}

    user_obj = Startup.objects.filter(email=email).first()
    if not user_obj:
        return {"result": False,
                "error": "user not found"}
    return {
        "result": True,
        "user_obj": user_obj
    }