from pydantic import BaseModel, EmailStr, Field


class UserSignup(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=255
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )


class UserLogin(BaseModel):
    email: EmailStr

    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"