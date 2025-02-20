from fastapi import APIRouter, status, Depends
from app.schemas import Message
from app.metadata import Tags

router = APIRouter(
    prefix="/healthcheck",
    tags=[Tags.Healthcheck]
)


@router.get("/ping",
    status_code=status.HTTP_200_OK, 
    response_model=Message,
    response_description='pong!',
    summary='Check if the API is running',
    responses={
        200: {
            'content': { 
                'application/json': {
                    'example': {
                        'detail': "pong!"
                    }
                }
            }
        },
        500: {
            'description': "Internal server error"
        }
    })
def ping():
    return Message(detail='pong!')