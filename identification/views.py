import os
from tensorflow.keras.models import load_model
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from PIL import Image
import numpy as np
from django.conf import settings

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

labels = ["飛行機","自動車", "鳥", "猫", "鹿", "犬", "カエル", "馬", "船", "トラック"]
n_class = len(labels)
img_size = 32
n_result = 3  # 上位3つの結果を表示

class IdentificationIndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, "identification/index.html")


class IdentificationResultView(TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect("/identification")


    def post(self, request, *args, **kwargs):
        # ファイルの存在と形式を確認
        file = request.FILES
        if len(file) == 0:
            context = {
                'msg' : "File doesn't exist!"
            }
            return render(request, "identification/index.html", context)
        filename = request.FILES['uploadFile']
        str_filename = str(filename)

        if not self.allowed_file(str_filename):
            context = {
                'msg' : str_filename + ": File not allowed!"
            }
            return render(request, "identification/index.html", context)

        # ファイルの保存
        fs = FileSystemStorage()
        fs.save(filename.name, filename)
        
        filepath = os.path.join(settings.MEDIA_ROOT, str_filename)

        # 画像の読み込み
        image = Image.open(filepath)
        image = image.convert("RGB")
        image = image.resize((img_size, img_size))
        x = np.array(image, dtype=float)
        x = x.reshape(1, img_size, img_size, 3) / 255

        # 予測
        model = load_model("/Applications/project/image_identification/identification/image_classifier.h5")
        y = model.predict(x)[0]
        sorted_idx = np.argsort(y)[::-1]  # 降順でソート
        result = ""
        for i in range(n_result):
            idx = sorted_idx[i]
            ratio = y[idx]
            label = labels[idx]
            result += "<p>" + str(round(ratio*100, 1)) + "%の確率で" + label + "です。</p>"
            context = {
                "filepath" : settings.MEDIA_URL + str_filename,
                "result"   : result
            }
        return render(request, "identification/result.html", context)
        
    def allowed_file(self, filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        
    