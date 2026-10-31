from api import app
from fastapi.middleware.cors import CORSMiddleware

# cors config not for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],                     # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],                     # Allow all HTTP methods
    allow_headers=["*"],                     # Allow all headers
)

