import os
from flask import Flask, render_template, redirect, flash, request, session, url_for
from db import get_user_by_email, create_user, get_user_by_id, create_model, get_all_models, get_model_by_id, get_models_by_category, delete_user
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "fsjh.kdfjasfsjdfjnd_hahj%"

UPLOAD_FOLDER = 'static/uploads/models'
ALLOWED_EXTENSIONS = {'gltf', 'glb'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/catalog")
def catalog():
    category = request.args.get('category')
    if category:
        models = get_models_by_category(category)
    else:
        models = get_all_models()
        
    return render_template("catalog.html", models=models, active_category=category)


@app.route("/search", methods=['POST'])
def search():
    category_query = request.form.get("category")
    
    if category_query:
        models = get_models_by_category(category_query)
        
        return render_template("catalog.html", models=models, active_category=category_query)
    
    return redirect("/catalog")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get("user_id"):
        return redirect("/profile")
    
    if request.method == "GET":
        return render_template("register.html")
    
    form = dict(request.form)
    existing_user = get_user_by_email(form.get("email"))
    if existing_user:
        flash("Пользователь с такой почтой уже зарегистрирован")
        return redirect("/login")
    
    user_id = create_user(form)
    session["user_id"] = user_id
    return redirect("/profile")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get("user_id"):
        return redirect("/profile")

    if request.method == "GET":
        return render_template("login.html")
    
    form = dict(request.form)
    existing_user = get_user_by_email(form.get("email"))
    
    if existing_user and existing_user["password"] == form.get("password"):
        session["user_id"] = existing_user["id"]
        return redirect("/profile")
    
    flash("Неверный email или пароль")
    return render_template("login.html")

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    
    if not user_id:
        flash("Нужно войти в аккаунт")
        return redirect("/login")
    
    user_data = get_user_by_id(user_id)
    if user_data:
        prin = 7 * "*"
        return render_template("profile.html", data=user_data, data_password=prin)
    
    return redirect("/register")

@app.route("/logout")    
def logout():
    session.pop("user_id", None)
    return redirect("/")


@app.route("/delet_profile", methods=["GET", "POST"])
def delete_profile():

    if not session.get("user_id"):
        flash("Действие может выполнить только авторизованный пользователь")
        return redirect("/login")
    
    user_id = session.get("user_id")
    user_data = get_user_by_id(user_id)

    if not user_data:
        flash("Пользователь не найден")
        return redirect("/")

    if request.method == "GET":
        return render_template("delete_profile.html")
    
    form_data = dict(request.form)
    password = form_data.get("password")

    if not password:
        flash("Введите пароль для подтверждения удаления", "error")
        return render_template("delete_profile.html")
    

    if user_data["password"] != password:
        flash("Неверный пароль. Попробуйте еще раз.", "error")
        return render_template("delete_profile.html")
    
    delete_user(user_id)
    session.pop("user_id")    
    flash("Ваш профиль был успешно удален", "success")
    return redirect("/")



@app.route("/upload", methods=['GET', 'POST'])
def upload():
    user_id = session.get("user_id")
    if not user_id:
        flash("Нужно войти в аккаунт")
        return redirect("/login")
    
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")
        file = request.files.get("model_file")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_name = f"{user_id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))
            
            file_path = f"uploads/models/{save_name}"
            create_model(title, category, description, file_path, user_id)
            
            flash("Модель успешно опубликована!")
            return redirect("/catalog")
        else:
            flash("Ошибка: недопустимый формат файла (нужны .gltf или .glb)")
            
    return render_template("upload.html")



@app.route("/model/<int:model_id>")
def model_detail(model_id):
    model_data = get_model_by_id(model_id)
    if not model_data:
        return "Модель не найдена", 404
    return render_template("model.html", model=model_data)


@app.route('/privacy')
def privacy():
    return render_template('policy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')

app.run(debug=True)