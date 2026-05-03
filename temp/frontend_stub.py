from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()


class StartResponse(BaseModel):
    first_item: dict


@app.post('/api/v1/diagnostic/start', response_model=StartResponse)
async def diagnostic_start():
    return {
        'first_item': {
            'id': str(uuid4()),
            'question': 'What is 2+2?',
            'options': ['1','2','3','4'],
        }
    }


@app.post('/api/v1/diagnostic/session/{session_id}/respond')
async def diagnostic_respond(session_id: str):
    return {'status': 'ok'}
