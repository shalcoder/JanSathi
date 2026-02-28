from .router import route_request

def execute_agent(request_data: dict):
    return route_request(request_data["message"])
