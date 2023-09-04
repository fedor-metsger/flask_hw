
import flask
import pydantic
from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import Session, Advert

app = flask.Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


def validate(validation_schema, validation_data):
    try:
        model = validation_schema(**validation_data)
        return model.dict(exclude_none=True)
    except pydantic.ValidationError as err:
        raise HttpError(400, err.errors())


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"status": "error", "description": er.message})
    response.status_code = er.status_code
    return response


def get_advert(session, advert_id):
    advert = session.get(Advert, advert_id)
    if advert is None:
        raise HttpError(404, "Advertisement not found")
    return advert


class AdvertView(MethodView):
    def get(self, advert_id):
        with Session() as session:
            advert = get_advert(session, advert_id)
            return jsonify(
                {
                    "id": advert.id,
                    "title": advert.title,
                    "creation_time": advert.creation_time.isoformat(),
                }
            )

    def post(self):
        with Session() as session:
            advert = Advert(**request.json)
            session.add(advert)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, "Advert already exists")
            return jsonify({"id": advert.id})

    def patch(self, advert_id):
        if "creation_time" in request.json:
            raise HttpError(409, "Can not update creation time")
        with Session() as session:
            advert = get_advert(session, advert_id)
            for field, value in request.json.items():
                setattr(advert, field, value)
            session.add(advert)
            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, "Advert already exists")
            return jsonify({"id": advert.id,
                            "title": advert.title,
                            "creation_time": advert.creation_time
                            })

    def delete(self, advert_id):
        with Session() as session:
            advert = get_advert(session, advert_id)
            session.delete(advert)
            session.commit()
            return jsonify({"status": "success"})


advert_view = AdvertView.as_view("advert")
app.add_url_rule(
    "/advert/<int:advert_id>", view_func=advert_view, methods=["GET", "PATCH", "DELETE"]
)
app.add_url_rule("/advert/", view_func=advert_view, methods=["POST"])

if __name__ == "__main__":
    app.run()