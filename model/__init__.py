from peewee import Model, SqliteDatabase, CharField, IntegerField, FloatField, ForeignKeyField, DateTimeField

# Database stuff
from playhouse.sqlite_ext import JSONField

db = SqliteDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class App(BaseModel):
    id = CharField(primary_key=True, unique=True)
    name = CharField()
    os = CharField()
    rank = IntegerField()
    rating = FloatField()
    ratings = IntegerField()
    availability = IntegerField()
    top25 = IntegerField()


class Version(BaseModel):
    app = ForeignKeyField(App, backref='versions')
    number = CharField()
    date = DateTimeField()


class Config(BaseModel):
    id = IntegerField(primary_key=True, unique=True)
    config = JSONField()
