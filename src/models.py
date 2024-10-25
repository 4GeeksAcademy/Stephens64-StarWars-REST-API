from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean, unique=False, nullable=False)
    favorites = db.relationship("Favorite", back_populates="user", lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # Do not serialize the password, as it's a security breach
        }


class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="favorites")
    favorite_character = db.relationship("Character", foreign_keys=[character_id])
    favorite_planet = db.relationship("Planet", foreign_keys=[planet_id])

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
        }


class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(400))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class Planet(db.Model):
    __tablename__ = "planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(400))

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
