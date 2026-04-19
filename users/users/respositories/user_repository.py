from beanie.operators import Or
from users.domain.models import User


class UserRepository:
    """
    Repository layer for performing database operations on User documents.

    This class abstracts direct access to the User model and provides
    reusable methods for querying, creating, updating, and deleting users.
    """

    async def get_by_id(self, user_id: str) -> User | None:
        """
        Retrieve a user by their unique database ID.

        Args:
            user_id (str): MongoDB document ID of the user.

        Returns:
            User | None: User instance if found, otherwise None.
        """
        return await User.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email address.

        Args:
            email (str): User's email address.

        Returns:
            User | None: User instance if found, otherwise None.
        """
        return await User.find_one(User.email == email)

    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by username.

        Args:
            username (str): User's username.

        Returns:
            User | None: User instance if found, otherwise None.
        """
        return await User.find_one(User.username == username)

    async def get_active_by_identifier(self, identifier: str) -> User | None:
        """
        Retrieve an active user by username or email.

        Args:
            identifier (str): Username or email used for lookup.

        Returns:
            User | None: Active user if found, otherwise None.
        """
        return await User.find_one(
            Or(User.email == identifier, User.username == identifier),
            User.is_active == True
        )

    async def get_by_identifier(self, identifier: str) -> User | None:
        """
        Retrieve a user by username or email regardless of activation status.

        Args:
            identifier (str): Username or email used for lookup.

        Returns:
            User | None: User instance if found, otherwise None.
        """
        return await User.find_one(
            Or(User.email == identifier, User.username == identifier)
        )

    async def get_by_activation_code(self, code: str) -> User | None:
        """
        Retrieve a user by activation code.

        Args:
            code (str): Activation code assigned to the user.

        Returns:
            User | None: User instance if found, otherwise None.
        """
        return await User.find_one(User.activation_code == code)

    async def get_by_reset_token(self, token: str) -> User | None:
        """
        Retrieve a user by password reset token.

        Args:
            token (str): Password reset token.

        Returns:
            User | None: User instance if found, otherwise None.
        """
        return await User.find_one(User.reset_password_token == token)

    async def create(self, user: User) -> User:
        """
        Insert a new user document into the database.

        Args:
            user (User): User instance to be created.

        Returns:
            User: Created user instance.
        """
        return await user.insert()

    async def save(self, user: User) -> User:
        """
        Save (update) an existing user document.

        Args:
            user (User): Modified user instance.

        Returns:
            User: Updated user instance.
        """
        return await user.save()

    async def delete(self, user: User) -> None:
        """
        Delete a user document from the database.

        Args:
            user (User): User instance to be deleted.

        Returns:
            None
        """
        await user.delete()