from peewee import *
import hashlib
import random

db = SqliteDatabase('db.sqlite3')

def r(count=100):
    s = ''
    for _ in range(count):
        s += str(random.randint(0, 9))
    return hashlib.sha256(s.encode('utf8')).hexdigest()

class User(Model):
    username = CharField(unique=True)
    nickname = CharField(null=True)
    hashed_password = CharField(null=True)
    salt = CharField(null=True)
    iter_count = IntegerField(default=0)

    _ITER_STEP = 500

    class Meta:
        database = db

    def _hash(self, password, salt, count):
        s = password
        for _ in range(count):
            s = hashlib.sha256((salt + s).encode('utf8')).hexdigest()
        return s

    def setPassword(self, password):
        if not self.salt:
            self.salt = r()

        s = self._hash(password, self.salt, self._ITER_STEP)
        self.hashed_password = s
        self.iter_count = 500
        self.save()

    def validate(self, password):
        if not self.hashed_password:
            return False
        attempt = self._hash(password, self.salt, self.iter_count)
        return attempt == self.hashed_password
        
class Session(Model):
    token = CharField()
    user = ForeignKeyField(User)
    expired_by = DateTimeField()

    class Meta:
        database = db

    @classmethod
    def validate(cls, token):
        current = datetime.datetime.now()
        try:
            session = cls.get(cls.token == token,
                              cls.expired_by > current)
        except Session.DoesNotExist:
            return False

        return session.user

