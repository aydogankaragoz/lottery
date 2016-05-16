from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import random

engine = create_engine('postgres://vejogzkz:GTWPD_h4llOA8KWk2GqQpjQ6epZEdS5B@pellefant.db.elephantsql.com:5432/vejogzkz', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def init_db():
    Base.metadata.create_all(engine)


class Registiration(Base):
    __tablename__ = "registirations"

    email = Column(String(100), primary_key=True, nullable=False)
    name = Column(String(100))

    def __init__(self, email, fullname):
        self.email = email
        self.name = fullname

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('hello.html')


@app.route('/register', methods=['POST'])
def register():
    print request
    name = request.form['name']
    email = request.form['email']
    try:
        new_registiration = Registiration(email, name)
        session.add(new_registiration)
        session.commit()
        registered = True
    except IntegrityError:
        session.rollback()
        registered = False
    return render_template('confirmation.html',
                           registered=registered,
                           email=email,
                           name=name)


@app.route("/winner")
def winner():
    registirations = session.query(Registiration).all()
    number_of_registirations = len(registirations)
    if number_of_registirations < 3:
        return render_template('too_little_registirations.html',
                               number_of_registirations=number_of_registirations)
    registirations_list = []
    for registiration in registirations:
        registirations_list.append({'name': registiration.name,
                                    'email': registiration.email,
                                    'winner': False})

    winner_index = random.randint(0, number_of_registirations - 1)
    print winner_index
    registirations_list[winner_index]['winner'] = True
    return render_template('winner.html',
                           registirations=registirations_list,
                           winner_name=registirations_list[winner_index]['name'])


@app.route('/resetdb', methods=['POST'])
def reset_db():
    print "in reset"
    session.query(Registiration).delete()
    session.commit()
    return redirect(url_for("hello"))

if __name__ == "__main__":
    app.run(debug=True)
