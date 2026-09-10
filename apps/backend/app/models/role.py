import enum


class UserRole(str, enum.Enum):
    """
    Role-based access control enum for CircuitGPT users.
    """
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"
