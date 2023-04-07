from app import generate_test_response
import json

def test_answer():
    response = generate_test_response()
    assert response.get("fail") == "false"