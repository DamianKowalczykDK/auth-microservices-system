from beanie.operators import Or
from users.domain.models import User

class UserRepository:

    async def get_by_id(self, user_id: str) -> User | None:
        return await User.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email)

    async def get_by_username(self, username: str) -> User | None:
        return await User.find_one(User.username == username)

    async def get_active_by_identifier(self, identifier: str) -> User | None:
        return await User.find_one(
            Or(User.email == identifier, User.username == identifier),
            User.active == True
        )

    async def get_by_identifier(self, identifier: str) -> User | None:
        return await User.find_one(Or(User.email == identifier, User.username == identifier))

    async def get_by_activation_code(self, code: str) -> User | None:
        return await User.find_one(User.activation_code == code)

    async def get_by_reset_token(self, token: str) -> User | None:
        return await User.find_one(User.reset_password_token == token)


    async def create(self, user: User) -> User:
        return await user.insert()

    async def save(self, user: User) -> User:
        return await user.save()

    async def delete(self, user: User) -> None:
        return await user.delete()
