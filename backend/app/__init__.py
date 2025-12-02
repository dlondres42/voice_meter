"""
FastAPI Voice Meter Backend

A modular speech analysis application with:
- Automatic language detection (PT-BR / EN-US)
- Advanced speech metrics based on research
- RESTful API endpoints
- PostgreSQL persistence

Package Structure:
    - api/        : API endpoints and routers
    - common/     : Shared constants and exceptions
    - core/       : Core configuration
    - db/         : Database setup and base classes
    - dto/        : Data Transfer Objects (dataclasses)
    - enums/      : Application enumerations
    - interfaces/ : Abstract base classes and protocols
    - models/     : SQLAlchemy ORM models
    - schemas/    : Pydantic schemas for validation
    - services/   : Business logic services
    - utils/      : Utility functions
"""

__version__ = "2.0.0"
__author__ = "Voice Meter Team"
