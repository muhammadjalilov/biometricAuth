import os
import uuid

from deepface import DeepFace
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from PIL import Image

from .forms import LoginForm, RegisterForm
from .models import Account


class HomeView(TemplateView):
    template_name = "home.html"


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if request.FILES.get("checker_image"):
            if form.is_valid():
                user: Account = form.save()
                user.checker_image = request.FILES["checker_image"]
                user.save()
                messages.success(request, "Вы успешно зарегистрированы!")
                return redirect("login")
            else:
                messages.error(
                    request,
                    "Регистрация не удалась. Проверьте форму на наличие ошибок.",
                )
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "login.html"

    def form_valid(self, form):
        user: Account = form.get_user()
        uploaded_image = form.cleaned_data.get("image")
        if not uploaded_image:
            messages.error(self.request, message="Изображение не загружается!")
            return self.form_invalid(form)

        temp_dir = os.path.join(settings.BASE_DIR, "media", "temp_images")
        os.makedirs(temp_dir, exist_ok=True)

        temp_filename = f"{uuid.uuid4()}.jpg"
        temp_filepath = os.path.join(temp_dir, temp_filename)

        if uploaded_image:
            try:
                with Image.open(uploaded_image) as img:
                    rgb_img = img.convert("RGB")
                    rgb_img.save(temp_filepath)
            except Exception as e:
                messages.error(
                    self.request, f"Освещение недостаточно хорошее, лицо не различимо."
                )
                return self.form_invalid(form)

            if not os.path.exists(temp_filepath):
                messages.error(self.request, "Temporary image could not be saved.")
                return self.form_invalid(form)

        abs_checker_image_path = os.path.join(
            settings.BASE_DIR, "media", str(user.checker_image)
        )

        try:
            check = DeepFace.verify(
                temp_filepath, abs_checker_image_path, model_name="Facenet512"
            )
            if not check.get("verified"):
                messages.error(self.request, "Изображения не совпадают!")
                return self.form_invalid(form)
            messages.success(self.request, "Вы зашли успешно в систему!")
        except Exception as e:
            print(f"DeepFace error: {e}")
            messages.error(
                self.request, f"Освещение недостаточно хорошее, лицо не различимо."
            )
            return self.form_invalid(form)
        finally:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=username, password=password)

        if not user:
            messages.error(self.request, "Неправильное имя пользователя или пароль.")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect("home")
