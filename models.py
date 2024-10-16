from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

db = SQLAlchemy()

class MessageGroupUser(db.Model):
    __tablename__ = 'MessageGroupUsers'
    id = mapped_column(db.Integer, primary_key=True)
    userId = mapped_column(db.Integer)
    groupId = mapped_column(db.Integer)
    emailOrPhone= mapped_column(db.String)
    isActive = mapped_column(db.Boolean)
    def to_json(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "groupId": self.groupId,
        }