from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserRoleSchema(BaseModel):

    role_id: int
    role_name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class UserSchema(BaseModel):

    user_id: int
    user_name: str
    roles: list[UserRoleSchema]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurrentUserSchema(BaseModel):

    user_id: int
    user_name: str
    roles: list[UserRoleSchema]

class Credentials(BaseModel):

    user_name: str
    password: str