from werkzeug.exceptions import NotFound
from sqlalchemy.orm.exc import NoResultFound


def get_object_or_404(db_session, model_cls, **filters):
    """
    Return object of model_cls based on filters.
    If no object is found, raise a 404
    """
    try:
        return db_session.query(model_cls).filter_by(**filters).one()

    except NoResultFound:
        model_cls_name = getattr(model_cls, "API_OBJECT_NAME", str(model_cls))
        raise NotFound("Couldn't find {} with filters: {}".format(
            model_cls_name, filters.items()))
