import peewee

database = peewee.SqliteDatabase(None)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField()
    is_admin = peewee.BooleanField()


class Auth(BaseModel):
    user = peewee.ForeignKeyField(User,
                                  backref='auth',
                                  unique=True,
                                  primary_key=True)
    password_sha512 = peewee.CharField(max_length=128)
    login_token = peewee.CharField(max_length=128, default='')
    login_date = peewee.DateTimeField(null=True)


class Auction(BaseModel):
    id = peewee.AutoField(primary_key=True)
    name = peewee.CharField()
    start_price = peewee.DecimalField(max_digits=40, decimal_places=2)
    start_time = peewee.DateTimeField()
    seller = peewee.ForeignKeyField(model=User)
    buyer = peewee.ForeignKeyField(model=User, null=True)
    ended = peewee.BooleanField(default=False)
    end_time = peewee.DateTimeField(null=True)


class DatabaseHandler:
    def __init__(self):
        from config import GLOBAL_CONFIG
        global database
        database.init(GLOBAL_CONFIG.dbpath)
        self.database = database
        self.database.connect()
        self.database.create_tables([User, Auth, Auction])
