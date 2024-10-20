from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

db = SQLAlchemy()

class Job():
    messageGroupId = ''
    templateId = ''
    content = ''
    timestamp =  None
    def __init__(self,messageGroupId,templateId,timestamp,content):
        self.messageGroupId = messageGroupId
        self.templateId = templateId
        self.timestamp = timestamp
        self.content = content

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
    
class MessageGroup(db.Model):
    __tablename__ = 'MessageGroups'
    id = mapped_column(db.Integer, primary_key=True)
    name = mapped_column(db.String)
    category = mapped_column(db.String)