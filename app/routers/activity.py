from fastapi import APIRouter, status, Depends
from app.dependencies import Firebase, get_db
from app.schemas import Activity, ActivityPatch, Message, Tags

router = APIRouter(
    prefix="/activity",
    tags=[Tags.Activity]
)

# CRUD para Activity
@router.post('/', 
    status_code=status.HTTP_201_CREATED, 
    response_model=Activity,
    response_description='Activity created successfully',
    summary='Create a Activity',
    responses={
        409: {
            'description': "Conflict with any of the entity's rules."
        },
        500: {
            'description': "Internal server error."
        }
    }
)
async def create_activity(activity: Activity, db: Firebase=Depends(get_db)) -> Activity:    
    return await db.create(activity)
    
@router.get('/', 
    status_code=status.HTTP_200_OK, 
    response_model=list[Activity],
    response_description='All Activities retrieved successfully',
    summary='Get all Activities',
    description='Retrieve all registered activities.',
    responses={
        500: {
            'description': "Internal server error."
        }
    }
)
async def get_all_activities(db: Firebase=Depends(get_db)) -> list[Activity]:
    return await db.get_all()

@router.patch('/{id}', 
    status_code=status.HTTP_200_OK, 
    response_model=Activity, 
    response_description='Activity updated successfully',
    summary='Update a Activity',
    responses={
        404: {
            'description': "ID not found."
        },
        409: {
            'description': "Conflict with any of the entity's rules."
        },
        500: {
            'description': "Internal server error."
        }
    }
)
async def update_activity(id: str, activity_patch: ActivityPatch, db: Firebase=Depends(get_db)) -> Activity:
    return await db.update(id, activity_patch)

@router.delete('/{id}', 
    status_code=status.HTTP_200_OK, 
    response_model=Message,
    response_description='Activity deleted successfully',
    summary='Delete a Activity',
    description='Provide a valid Activity ID to exclude its corresponding information.',
    responses={
        200: {
            'content': { 
                'application/json': {
                    'example': {
                        'detail': "Activity deleted successfully"
                    }
                }
            }
        },
        404: {
            'description': "ID not found."
        },
        409: {
            'description': "Conflict with any of the entity's rules."
        },
        500: {
            'description': "Internal server error."
        }
    }
)
async def delete_activity(id: str, db: Firebase=Depends(get_db)) -> Message:
    return await db.delete(id)