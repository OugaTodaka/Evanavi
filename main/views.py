from functools import wraps
import json
from django.views.generic import *
from .models import *
from django.shortcuts import get_object_or_404, render, redirect
from .forms import EvaluationSearchForm, JobFilterForm, UserDataForm, EvaForm
import matplotlib.pyplot as plt
import numpy as np
from django.http import HttpResponse, HttpResponseForbidden
from io import BytesIO
from .models import Status
from django.contrib.auth.decorators import login_required
import requests
from django.db.models import F, Case, When, ExpressionWrapper, IntegerField
from django.contrib import messages
import openai
from django.utils.decorators import method_decorator
from google.cloud import translate_v3 as translate
from google.cloud import language_v1
import os
from google.oauth2 import service_account

# メイン画面
class HomeView(TemplateView):
    template_name = "main/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ユーザーがログイン中の場合のみコンテキストを追加
        if self.request.user.is_authenticated:
            status, created = Status.objects.get_or_create(
                user=self.request.user,
                defaults={
                    'sociability': 1,
                    'knowledge': 1,
                    'qualification': 1,
                }
            )
            context['status'] = status
        
        # ログインしていない場合は、特に何も追加しない
        return context

# レーダーチャートでステータスを表示する
def radar_chart_view(request):
    status = get_object_or_404(Status, user=request.user)

    # データ設定（五段階評価）
    labels = ['sociability', 'knowledge', 'qualification']
    values = [status.sociability, status.knowledge, status.qualification]
    values += values[:1]  # 閉じた形にするために最初の値を追加

    # レーダーチャートの設定
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='aqua', alpha=0.25)
    ax.plot(angles, values, color='aqua', linewidth=2)

    # Y軸の範囲設定とラベルの設定（1から5まで）
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])  # 目盛りを設定
    ax.set_yticklabels([1, 2, 3, 4, 5])  # それぞれにラベルを設定

    # X軸（ラベルの設定）
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    # グラフをバッファに保存
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf, content_type='image/png')

# Yahoo求人を取得して表示
@login_required
def job_list_view(request):
    form = JobFilterForm(request.GET)
    jobs = []
    error = None

    if form.is_valid():
        app_id = "dj00aiZpPTNFUFF1QjJFdXRjdyZzPWNvbnN1bWVyc2VjcmV0Jng9NmE-"
        base_url = 'https://job.yahooapis.jp/v1/furusato/jobinfo/'
        
        params = {
            'appid': app_id,
            'localGovernmentCode': form.cleaned_data.get('localGovernmentCode'),
            # 'workLocationPrefecture': form.cleaned_data.get('workLocationPrefecture'),
            # 'workLocationCity': form.cleaned_data.get('workLocationCity'),
            'fields': 'full',
            'start': 1,
            'results': form.cleaned_data.get('results'),
            # 'salaryMin': form.cleaned_data.get('salaryMin'),
            # 'salaryMax': form.cleaned_data.get('salaryMax'),
            # 'employmentTypeCode': form.cleaned_data.get('employmentTypeCode'),
            # 'occupationName': form.cleaned_data.get('occupationName'),
            # 'insuranceNote': form.cleaned_data.get('insuranceNote')
        }
        
        # 空でないパラメーターをparamsに追加する
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            jobs = data.get('results', [])
            total = data.get('total', 0)
            count = data.get('count', 0)
        except requests.RequestException as e:
            total = 0
            count = 0
            error = f"APIリクエストエラー: {str(e)}"
        except ValueError as e:
            total = 0
            count = 0
            error = f"JSONデコードエラー: {str(e)}"

    return render(request, 'main/job_list.html', {'form': form, 'jobs': jobs, 'total': total, 'count': count, 'error': error})



# ユーザ情報が登録されているか確認するための関数
def user_data_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            UserData.objects.get(username=request.user)
        except UserData.DoesNotExist:
            messages.warning(request, 'ユーザ情報を登録してください。')
            return redirect('main:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ユーザ情報を登録・更新するためのビュー
@login_required
def user_data_view(request):
    try:
        user_data = UserData.objects.get(username=request.user)
    except UserData.DoesNotExist:
        user_data = None

    if request.method == 'POST':
        form = UserDataForm(request.POST, instance=user_data, user=request.user)
        if form.is_valid():
            user_data = form.save(commit=False)
            user_data.username = request.user
            user_data.save()
            return redirect('main:home')
    else:
        form = UserDataForm(instance=user_data, user=request.user)

    return render(request, 'main/user_data_form.html', {'form': form})


CREDENTIALS_PATH = 'C:/Users/t_toyota/Desktop/feisty-return-443904-j8-ca40d8e38658.json'
CREDENTIALS = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)


def translate_text(text, target_language='en'):
    """
    指定されたテキストを指定言語に翻訳
    
    Args:
        text (str): 翻訳する元のテキスト
        target_language (str): 翻訳先の言語コード（デフォルトは英語）
    
    Returns:
        str: 翻訳されたテキスト
    """
    # Translate APIクライアントの初期化
    client = translate.TranslationServiceClient(credentials=CREDENTIALS)
    parent = f"projects/{CREDENTIALS.project_id}/locations/global"

    # 翻訳リクエストを実行
    response = client.translate_text(
        parent=parent,
        contents=[text],
        mime_type="text/plain",  # テキスト形式
        target_language_code=target_language,
    )
    return response.translations[0].translated_text



def analyze_translated_text(translated_text):
    """
    翻訳されたテキストを分析
    
    Args:
        translated_text (str): 翻訳されたテキスト
    
    Returns:
        dict: NLP分析結果
    """
    # Natural Language APIクライアントの初期化
    client = language_v1.LanguageServiceClient(credentials=CREDENTIALS)
    
    # テキスト文書を作成
    document = language_v1.Document(
        content=translated_text,
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    
    # センチメント分析
    sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
    
    # エンティティ分析
    entities = client.analyze_entities(request={'document': document}).entities
    
    # カテゴリ分析（英語テキストでのみ実行）
    try:
        categories = client.classify_text(request={'document': document}).categories
    except Exception:
        categories = []
    
    return {
        'original_text': translated_text,
        'sentiment_score': sentiment.score,
        'sentiment_magnitude': sentiment.magnitude,
        'entities': [
            {
                'name': entity.name,
                'type': language_v1.Entity.Type(entity.type_).name,
                'salience': entity.salience
            } for entity in entities
        ],
        'categories': [
            {
                'name': category.name,
                'confidence': category.confidence
            } for category in categories
        ]
    }


def process_japanese_evaluation(japanese_text):
    """
    日本語テキストを翻訳し、NLP分析を実行
    
    Args:
        japanese_text (str): 日本語の評価テキスト
    
    Returns:
        dict: 翻訳および分析結果
    """
    # テキストを英語に翻訳
    translated_text = translate_text(japanese_text)
    
    # 翻訳されたテキストを分析
    analysis_result = analyze_translated_text(translated_text)
    
    return {
        'original_japanese': japanese_text,
        'translated_text': analysis_result['original_text'],
        'sentiment_score': analysis_result['sentiment_score'],
        'sentiment_magnitude': analysis_result['sentiment_magnitude'],
        'entities': analysis_result['entities'],
        'categories': analysis_result['categories']
    }


@user_data_required
@login_required
def eva_view(request):
    current_user_data = get_object_or_404(UserData, username=request.user)
    current_group_code = current_user_data.group_code

    if request.method == 'POST':
        form = EvaForm(request.POST, from_user=request.user, group_code=current_group_code)
        if form.is_valid():
            eva = form.save(commit=False)
            eva.from_user = request.user

            # テキスト分析の実行
            nlp_analysis = process_japanese_evaluation(eva.detail)
            
            # NLPスコアに基づいたステータス更新ロジック
            target_status = get_object_or_404(Status, user=eva.for_user)
            
            # センチメントスコアに基づくポイント付与
            if nlp_analysis['sentiment_score'] > 0.5:
                target_status.sociability_point += 2
                target_status.knowledge_point += 1
            
            # エンティティ分析に基づく専門性評価
            professional_entities = [
                entity for entity in nlp_analysis['entities'] 
                if entity['type'] in ['PROFESSIONAL_TERM', 'SKILL', 'WORK_OF_ART']
            ]
            if professional_entities:
                target_status.qualification_point += len(professional_entities)
            
            # カテゴリ分析に基づく追加評価
            for category in nlp_analysis['categories']:
                if category['confidence'] > 0.7:
                    if 'Leadership' in category['name']:
                        target_status.sociability_point += 3
                    elif 'Technology' in category['name']:
                        target_status.knowledge_point += 3
                    elif 'Professional Development' in category['name']:
                        target_status.qualification_point += 3
            
            # 既存のレベルアップロジックを保持
            if target_status.sociability_point > 0 and target_status.sociability_point % 10 == 0 and target_status.sociability < 5:
                target_status.sociability += 1
            
            if target_status.knowledge_point > 0 and target_status.knowledge_point % 10 == 0 and target_status.knowledge < 5:
                target_status.knowledge += 1
            
            if target_status.qualification_point > 0 and target_status.qualification_point % 10 == 0 and target_status.qualification < 5:
                target_status.qualification += 1
            
            target_status.save()
            eva.save()
            return redirect('main:home')
    else:
        form = EvaForm(from_user=request.user, group_code=current_group_code)
    
    return render(request, 'main/eva_form.html', {
        'form': form,
    })

# 評価を取得して表示する
@method_decorator([login_required, user_data_required], name='dispatch')
class EvaluationListView(ListView):
    model = Eva
    template_name = 'main/view_evaluation.html'
    context_object_name = 'evaluations'
    paginate_by = 9

    def get_queryset(self):
        # 自分が評価されたものを取得
        queryset = Eva.objects.filter(for_user=self.request.user)
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if email:
                queryset = queryset.filter(from_user__email__icontains=email)
        return queryset

    def get_form(self):
        return EvaluationSearchForm(self.request.GET or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()

        # ステータス情報を取得してコンテキストに追加
        status, created = Status.objects.get_or_create(user=self.request.user, defaults={
            'sociability': 1,
            'knowledge': 1,
            'qualification': 1,
        })
        context['status'] = status
        return context
    
# JSONファイルからAPIキーを読み込む関数
def load_api_key_from_json(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
        return config.get("openai_api_key")

# JSONファイルのパス
json_file_path = 'C:/Users/t_toyota/Desktop/openAI_api.json'

# APIキーをロード
api_key = load_api_key_from_json(json_file_path)

# OpenAI APIキーを設定
openai.api_key = api_key

@login_required
@user_data_required
def generate_self_promotion(request):
    current_user = request.user
    evaluations = Eva.objects.filter(for_user=current_user)

    # 評価内容を結合してプロンプトを作成
    evaluation_details = "\n".join([eva.detail for eva in evaluations])

    prompt = f"以下の評価をもとに自己PRを作成してください:\n{evaluation_details}\n自己PR:"

    # OpenAI APIへのリクエスト
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # 生成された自己PRを取得
    self_promotion = response['choices'][0]['message']['content']

    # 生成された自己PRをセッションに保存しておく（ダウンロード時に利用）
    request.session['self_promotion'] = self_promotion

    return render(request, 'main/self_promotion.html', {'self_promotion': self_promotion})

@login_required
@user_data_required
def download_self_promotion(request, format):
    # セッションから自己PRを取得
    self_promotion = request.session.get('self_promotion')

    if not self_promotion:
        return HttpResponse("自己PRが見つかりません。もう一度生成してください。", status=400)

    # ダウンロードフォーマットに応じてレスポンスを作成
    if format == 'txt':
        # テキスト形式でダウンロード
        response = HttpResponse(self_promotion, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="self_promotion.txt"'
    elif format == 'json':
        # JSON形式でダウンロード
        self_promotion_data = {"self_promotion": self_promotion}
        response = HttpResponse(json.dumps(self_promotion_data, ensure_ascii=False), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="self_promotion.json"'
    else:
        return HttpResponse(status=400)  # 対応していないフォーマットの場合

    return response