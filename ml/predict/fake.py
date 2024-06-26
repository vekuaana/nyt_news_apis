from fastapi import FastAPI
from pydantic import BaseModel


def calculator(operation, x, y):
    if operation == 'Addition':
        return x+y


class User_input(BaseModel):
    operation: str
    x: float
    y: float


app = FastAPI()


@app.post("/calculate")
def operate(input: User_input):
    result = calculator(input.operation, input.x, input.y)
    return result
