from fastapi import HTTPException, status


class DatabaseUnreachableError(HTTPException):
    def __init__(self, e: Exception) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database Error: {e}",
        )


class EntityNotFoundError(HTTPException):
    def __init__(self, entity: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} not found"
        )


class EntityAlreadyExistsError(HTTPException):
    def __init__(self, entity: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{entity} already exists"
        )


class EntityRelationDoesNotExistError(HTTPException):
    def __init__(self, entity: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid relation for {entity}"
        )
