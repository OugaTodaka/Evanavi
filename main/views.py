from django.views.generic import *
from .models import *
from django.shortcuts import get_object_or_404, render, redirect
from .forms import UserDataForm, EvaForm
import matplotlib.pyplot as plt
import numpy as np
from django.http import HttpResponse
from io import BytesIO
from .models import Status
from django.contrib.auth.decorators import login_required

class HomeView(ListView):
    model = Eva
    template_name = "main/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

def user_data_view(request):
    # ログイン中のユーザーのUserDataを取得（なければ新規作成する準備）
    try:
        user_data = UserData.objects.get(username=request.user)
    except UserData.DoesNotExist:
        user_data = None

    if request.method == 'POST':
        # 既存データがある場合はインスタンスを渡す
        form = UserDataForm(request.POST, instance=user_data, user=request.user)
        if form.is_valid():
            user_data = form.save(commit=False)
            user_data.username = request.user  # ForeignKeyとしてUserモデルをセット
            user_data.save()
            return redirect('main:home')  # 適切なリダイレクト先に変更
    else:
        # 既存データがある場合はインスタンスを渡してフォームを作成
        form = UserDataForm(instance=user_data, user=request.user)

    return render(request, 'main/user_data_form.html', {'form': form})

def eva_view(request):
    # ログインしているユーザーのデータを取得
    current_user_data = get_object_or_404(UserData, username=request.user)
    current_group_code = current_user_data.group_code  # ログインユーザーのグループコードを取得

    if request.method == 'POST':
        form = EvaForm(request.POST, from_user=request.user, group_code=current_group_code)  # from_user と group_code を渡す
        if form.is_valid():
            eva = form.save(commit=False)
            eva.from_user = request.user  # ログインユーザーが評価を行う
            eva.save()
            return redirect('main:home')  # 適切なリダイレクト先に変更
    else:
        form = EvaForm(from_user=request.user, group_code=current_group_code)  # from_user と group_code を渡す

    return render(request, 'main/eva_form.html', {
        'form': form,
    })


@login_required  # ログインが必要なビューにするためのデコレーター
def status_view(request):
    # ログイン中のユーザーのステータスを取得
    status, created = Status.objects.get_or_create(user=request.user, defaults={
        'sociability': 1,
        'knowledge': 1,
        'qualification': 1,
    })
    
    # テンプレートにステータス情報を渡す
    return render(request, 'main/status.html', {'status': status})

def radar_chart_view(request):
    status = get_object_or_404(Status, user=request.user)

    # データ設定（五段階評価）
    labels = ['社交性', '知識', '資格']
    values = [status.sociability, status.knowledge, status.qualification]
    values += values[:1]  # 閉じた形にするために最初の値を追加

    # レーダーチャートの設定
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.25)
    ax.plot(angles, values, color='blue', linewidth=2)

    ax.set_ylim(0, 5)


    ax.set_yticklabels([])  # Y軸ラベル非表示
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    # グラフをバッファに保存
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    return HttpResponse(buf, content_type='image/png')
