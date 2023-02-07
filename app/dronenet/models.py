from dronenet import db


class Remote(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ip = db.Column(db.String(16), unique=True, nullable=False)
  name = db.Column(db.String(64), unique=False, nullable=False)

  def __repr__(self):
    return f"Remote({self.id}, '{self.ip}', '{self.name}')"
