from flask import request, jsonify, Response
from database.models import app, PersonStatus, Person, Custom, Menu, Product, Details  # , Address, Details, Ingredient

from validation.schemas import *
from flask_cors import CORS
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from flask_httpauth import HTTPBasicAuth
import json

app.debug = True

CORS(app)

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(u_email, u_password):
    user_to_verify = Person.query.filter_by(email=u_email).first()
    if not user_to_verify:
        return None
    if check_password_hash(user_to_verify.password, u_password):
        print("email: " + u_email + ", password: " + u_password)
        return user_to_verify
    else:
        return None


@auth.error_handler
def auth_error_handler(status):
    message = ""
    if status == 401:
        message = "Wrong email or password"
    if status == 403:
        message = "Access denied"
    return {"code": status, "message": message}, status


@auth.get_user_roles
def get_user_roles(user_to_get_role):
    print(user_to_get_role.role.value)
    return user_to_get_role.role.value


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            result = 0
            if 0 == len(kwargs):
                result = func()
            else:
                result = func(**kwargs)
            if result.__class__ != Response and result[1] >= 400:
                return {"code": result[1],
                        "message": result[0]
                        }, result[1]
            else:
                return result
        except ValidationError as err:
            return {"code": 412,
                    "message": err.messages
                    }, 412
        except IntegrityError as err:
            return {"code": 409,
                    "message": err.args
                    }, 409

    wrapper.__name__ = func.__name__
    return wrapper


def get_all_people():
    return Person.query.all()


def get_all_products():
    return Product.query.all()


@app.route("/")
def home():
    return 'Home'


@app.route("/user", methods=['POST'])
@error_handler
def user():
    if request.method == 'POST' and request.is_json:
        data_user = PersonSchema().load(request.json)
        new_user = add_input(Person, **data_user)
        return jsonify(PersonSchema().dump(new_user)), 201
        # find_email = Person.query.filter_by(email=data_user.email).first()
        # return {"id": data_user.id}
    else:
        return {
            'message': "Incorrect request"
        }, 400


@app.route("/user/login", methods=['POST'])
@error_handler
@auth.login_required(role=['client', 'manager'])
def login():
    if request.method == 'POST' and request.is_json:
        login_data = request.get_json()
        user_login = Person.query.filter_by(email=login_data['email']).first()

        if user_login is None:
            return {
                "message": "There is no user with such email"
            }, 412
        elif not check_password_hash(user_login.password, login_data['password']):
            return {
                "message": "Incorrect password"
            }, 412
        else:
            return {
                "id": user_login.id,
                "message": "Success"
            }, 201
    else:
        return {
            'message': "Incorrect request"
        }, 400


@app.route("/user/logout", methods=['DELETE'])
@auth.login_required(role=['client', 'manager'])
def logout():
    if request.method == 'DELETE':
        return {
            "message": "Success"
        }, 200
    else:
        return {
            'message': "Incorrect request"
        }, 400


@app.route("/user/<int:user_id>", methods=['PUT'])
@error_handler
@auth.login_required(role=['client', 'manager'])
def user_update(user_id):
    current_user = auth.current_user()
    print(user_id, current_user.id)
    if current_user.id != int(user_id):
        return "Access denied", 403
    if request.method == 'PUT':
        person_data = PersonToUpdateSchema().load(request.json)
        person_to_update = Person.query.filter_by(id=user_id).first()
        if not person_to_update:
            return {
                "message": "Client not found"
            }, 404
        else:
            update_input(person_to_update, **person_data)
            return jsonify(PersonToUpdateSchema().dump(person_to_update)), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/user/<int:user_id>", methods=['GET', 'DELETE'])
@error_handler
@auth.login_required(role=['client', 'manager'])
def user_to(user_id):
    current_user = auth.current_user()
    print(user_id, current_user.id)
    if request.method == 'GET':
        u_role = current_user.role.value
        if u_role == 'client' and current_user.id != int(user_id):
            return "Access denied", 403

        person_to_get_info = Person.query.filter_by(id=user_id).first()
        if person_to_get_info is None:
            return {
                "message": "There is no user with such id"
            }, 404
        else:
            return jsonify(PersonSchema().dump(person_to_get_info)), 200
    elif request.method == 'DELETE':
        if current_user.id != int(user_id):
            return "Access denied", 403
        elif current_user.id == int(user_id):
            person_to_delete = Person.query.filter_by(id=user_id).first()
            order_to_delete = Custom.query.filter_by(user_id=user_id).all()
            if person_to_delete is None:
                return {
                    "message": "There is no user with such id"
                }, 404
            else:
                for i in order_to_delete:
                    details_to_delete = Details.query.filter_by(custom_id=i.id).all()
                    for j in details_to_delete:
                        delete_input(j)
                    delete_input(i)
                delete_input(person_to_delete)
                return {
                    "message": "Success"
                }, 201
        else:
            return {
                "message": "You try to delete another user"
            }
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/user/<int:user_id>/makeManager", methods=['PUT'])
@auth.login_required(role='manager')
def make_m(user_id):
    user_to_work = Person.query.filter_by(id=user_id).first()
    if request.method == 'PUT':
        if user_to_work is None:
            return {
                "message": "User not found"
            }, 404
        elif user_to_work.role == PersonStatus.manager:
            return {
                "message": "The user already has role manager"
            }, 408
        else:
            user_to_work.role = PersonStatus.manager.value
            db.session.commit()
            return {
                "message": "Success"
            }, 201
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/user/getAll", methods=['GET'])
@auth.login_required(role='manager')
def get_all_user():
    if request.method == 'GET':
        return json.dumps([p.as_dict() for p in Person.query.all()],
                          indent=4, sort_keys=True, default=str), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/custom", methods=['POST'])
@error_handler
@auth.login_required(role='client')
def custom():
    current_user = auth.current_user()
    if request.method == 'POST' and request.is_json:
        custom_data = CustomSchema().load(request.json)
        new_custom = Custom(**custom_data)
        new_custom.time = datetime.datetime.now()
        if new_custom.user_id != current_user.id:
            return "Access denied", 403
        db.session.add(new_custom)
        db.session.commit()
        return jsonify(CustomSchema().dump(new_custom)), 201
        # find_email = Person.query.filter_by(email=data_user.email).first()
        # return {"id": new_custom.id}, 201
    else:
        return {
            'message': "Incorrect request"
        }, 400


@app.route("/custom/<int:custom_id>", methods=['GET', 'DELETE', 'PUT'])
@error_handler
@auth.login_required(role=['client', 'manager'])
def custom_to(custom_id):
    current_user = auth.current_user()
    u_role = current_user.role.value
    custom_info = Custom.query.filter_by(id=custom_id).first()
    if request.method == 'GET':
        custom_to_get_info = Custom.query.filter_by(id=custom_id).first()
        if not custom_to_get_info:
            return {
                "message": "There is no custom with such id"
            }, 404
        elif u_role == 'client' and current_user.id != custom_info.user_id:
            return "Access denied", 403
        else:
            return jsonify(CustomSchema().dump(custom_to_get_info)), 200
    elif request.method == 'DELETE':
        custom_to_delete = Custom.query.filter_by(id=custom_id).first()
        if current_user.id != custom_info.user_id:
            return "Access denied", 403

        if custom_to_delete is None:
            return {
                "message": "There is no user with such id"
            }, 404
        else:
            details_to_delete = Details.query.filter_by(custom_id=custom_id).all()
            for i in details_to_delete:
                delete_input(i)
            delete_input(custom_to_delete)
            return {
                "message": "Success"
            }, 201
    elif request.method == 'PUT' and request.is_json:
        custom_data = CustomToUpdateSchema().load(request.json)
        custom_to_update = Custom.query.filter_by(id=custom_id).first()
        if current_user.id != custom_info.user_id:
            return "Access denied", 403

        if custom_to_update is None:
            return {
                "message": "Custom not found"
            }, 404
        else:
            for key, value in custom_data.items():
                setattr(custom_to_update, key, value)
            custom_to_update.time = datetime.datetime.now()
            db.session.commit()
            return jsonify(CustomToUpdateSchema().dump(custom_to_update)), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/custom/<int:custom_id>/updateStatus", methods=['PUT'])
@error_handler
@auth.login_required(role='manager')
def update_cust_status(custom_id):
    if request.method == 'PUT':
        status_data = CustomUpdateStatusSchema().load(request.json)
        status_to_update = Custom.query.filter_by(id=custom_id).first()
        if status_to_update is None:
            return {
                "message": "Custom not found"
            }, 404
        else:
            update_input(status_to_update, **status_data)
            return jsonify(CustomUpdateStatusSchema().dump(status_to_update)), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/custom/getAll", methods=['GET'])
@auth.login_required(role='manager')
def get_all_cust():
    if request.method == 'GET':
        return json.dumps([p.as_dict() for p in Custom.query.all()],
                          indent=4, sort_keys=True, default=str), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/menu", methods=['POST'])
@error_handler
@auth.login_required(role='manager')
def menu():
    if request.method == 'POST' and request.is_json:
        menu_data = MenuSchema().load(request.json)
        new_menu = add_input(Menu, **menu_data)
        return jsonify(MenuSchema().dump(new_menu)), 201
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/menu/<int:menu_id>", methods=['GET'])
@error_handler
def menu_to_get(menu_id):
    menu_to_get_info = Menu.query.filter_by(id=menu_id).first()
    if menu_to_get_info is None:
        return {
            "message": "There is no menu item with such id"
        }, 404
    else:
        return jsonify(MenuSchema().dump(menu_to_get_info)), 200


@app.route("/menu/<int:menu_id>", methods=['DELETE', 'PUT'])
@error_handler
@auth.login_required(role='manager')
def menu_to(menu_id):
    if request.method == 'DELETE':
        menu_to_delete = Menu.query.filter_by(id=menu_id).first()
        if menu_to_delete is None:
            return {
                "message": "There is no menu item with such id"
            }, 404
        else:
            delete_input(menu_to_delete)
            return {
                "message": "Success"
            }, 201
    elif request.method == 'PUT' and request.is_json:
        menu_data = MenuToUpdateSchema().load(request.json)
        menu_to_update = Menu.query.filter_by(id=menu_id).first()
        if menu_to_update is None:
            return {
                "message": "Menu item not found"
            }, 404
        else:
            update_input(menu_to_update, **menu_data)
            return jsonify(MenuToUpdateSchema().dump(menu_to_update)), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/menu//<int:menu_id>/AddToDemand", methods=['PUT'])
@auth.login_required(role=['client', 'manager'])
def add_to_demand(menu_id):
    if request.method == 'PUT':
        menu_to_demand = Menu.query.filter_by(id=menu_id).first()
        if menu_to_demand is None:
            return {
                "message": "Menu item not found"
            }, 404
        else:
            menu_to_demand.demand = True
            db.session.commit()
            return {
                "message": "Success"
            }, 201

    else:
        return {
            "message": "Incorrect request"
        }, 404


@app.route("/menu/getAll", methods=['GET'])
def get_all_menu():
    if request.method == 'GET':
        return json.dumps([p.as_dict() for p in Menu.query.all()],
                          indent=4, sort_keys=True, default=str), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/product", methods=['POST'])
@error_handler
@auth.login_required(role='manager')
def product():
    if request.method == 'POST' and request.is_json:
        product_data = ProductSchema().load(request.json)
        new_product = add_input(Product, **product_data)
        return jsonify(ProductSchema().dump(new_product)), 201
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/product/<int:product_id>", methods=['GET', 'DELETE', 'PUT'])
@auth.login_required(role='manager')
def product_to(product_id):
    if request.method == 'GET':
        product_to_get_info = Product.query.filter_by(id=product_id).first()
        if product_to_get_info is None:
            return {
                "message": "There is no menu item with such id"
            }, 404
        else:
            return jsonify(ProductSchema().dump(product_to_get_info)), 200
    elif request.method == 'DELETE':
        product_to_delete = Product.query.filter_by(id=product_id).first()
        if product_to_delete is None:
            return {
                "message": "There is no menu item with such id"
            }, 404
        else:
            delete_input(product_to_delete)
            return {
                "message": "Success"
            }, 201
    elif request.method == 'PUT' and request.is_json:
        product_data = ProductToUpdateSchema().load(request.json)
        product_to_update = Product.query.filter_by(id=product_id).first()
        if product_to_update is None:
            return {
                "message": "Menu item not found"
            }, 404
        else:
            update_input(product_to_update, **product_data)
            return jsonify(MenuToUpdateSchema().dump(product_to_update)), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/product/getAll", methods=['GET'])
@auth.login_required(role='manager')
def get_all_prod():
    if request.method == 'GET':
        return json.dumps([p.as_dict() for p in Product.query.all()],
                          indent=4, sort_keys=True, default=str), 200
    else:
        return {
            "message": "Incorrect request"
        }, 400


@app.route("/api/v1/hello-world-<value>")
def hello_world(value):
    return "Hello world " + value, 200


if __name__ == "__main__":
    app.run()
