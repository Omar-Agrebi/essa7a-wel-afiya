"""System-wide enums and constants."""
from enum import Enum

class OpportunityType(str, Enum):
    """Enum for the different types of opportunities."""
    internship = "internship"
    scholarship = "scholarship"
    project = "project"
    course = "course"
    postdoc = "postdoc"

class OpportunityCategory(str, Enum):
    """Enum for the domain categories of opportunities."""
    AI = "AI"
    Data_Science = "Data Science"
    Cybersecurity = "Cybersecurity"
    Software_Engineering = "Software Engineering"
    Other = "Other"

class UserLevel(str, Enum):
    """Enum for academic and professional levels."""
    bachelor = "bachelor"
    master = "master"
    phd = "phd"
    professional = "professional"

class NotificationStatus(str, Enum):
    """Enum representing the read status of a notification."""
    unread = "unread"
    read = "read"
    dismissed = "dismissed"
