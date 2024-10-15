from django import forms

from user.models import User
from .models import UserData, Eva

# UserDataのフォーム
class UserDataForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='生年月日'
    )
    graduate_Year = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='卒業年'
    )
    class Meta:
        model = UserData
        fields = ['name', 'tel', 'email', 'zip_code', 'address1', 'address2', 'gender', 'birth_date', 'school_name', 'graduate_Year', 'group_code']
        labels = {
            'name': '氏名',
            'tel': '電話番号',
            'email': 'メールアドレス',
            'zip_code': '郵便番号',
            'address1': '都道府県',
            'address2': '市区町村',
            'gender': '性別',
            'birth_date': '生年月日',
            'school_name': '学校名',
            'graduate_Year': '卒業年度',
            'group_code': 'グループコード',
        }
        widgets = {
            'zip_code': forms.TextInput(attrs={'id': 'zip_code'}),
            'address1': forms.TextInput(attrs={'id': 'address1'}),
            'address2': forms.TextInput(attrs={'id': 'address2'}),
            'gender': forms.RadioSelect,  # ラジオボタンで性別を選択
        }
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # 'user' を引数として受け取る
        super(UserDataForm, self).__init__(*args, **kwargs)

        if user:
            # ログインしているユーザーの情報を自動的に初期値にセット
            self.fields['name'].initial = user.username
            self.fields['email'].initial = user.email

# Evaのフォーム
class EvaForm(forms.ModelForm):
    class Meta:
        model = Eva
        fields = ['for_user', 'detail']
        labels = {
            'for_user': '評価対象',
            'detail': '評価内容',
        }

    def __init__(self, *args, **kwargs):
        from_user = kwargs.pop('from_user', None)  # 評価を行うユーザーを受け取る
        group_code = kwargs.pop('group_code', None)  # グループコードを受け取る
        super(EvaForm, self).__init__(*args, **kwargs)

        if from_user and group_code:
            # 同じグループコードのユーザーのみ表示
            self.fields['for_user'].queryset = User.objects.filter(
                userdata__group_code=group_code
            )
        else:
            self.fields['for_user'].queryset = User.objects.none()  # 何も選択できない状態
            

# フィルター用のフォーム
class JobFilterForm(forms.Form):
    localGovernmentCode = forms.IntegerField(required=False, label='地方公共団体コード(都道府県・市区町村)')
    # workLocationPrefecture = forms.CharField(required=False, label='都道府県')
    # workLocationCity = forms.CharField(required=False, label='市区町村')
    # salaryMin = forms.IntegerField(required=False, label="最低給与")
    # salaryMax = forms.IntegerField(required=False, label="最高給与")
    
    # EMPLOYMENT_TYPE_CHOICES = [
    #     ('', '指定なし'),
    #     ('100','正社員'),
    #     ('110','新卒採用'),
    #     ('120','パート・アルバイト'),
    #     ('130','派遣社員'),
    #     ('140','インターン'),
    #     ('150','ボランティア'),
    #     ('160','契約社員'),
    #     ('170','業務委託'),
    #     ('180','プロボノ'),
    # ]
    # employmentTypeCode = forms.ChoiceField(
    #     choices=EMPLOYMENT_TYPE_CHOICES, required=False, label="雇用形態"
    # )

    # # 職種フィールド
    # occupationName = forms.CharField(required=False, label="職種")

    # # 加入保険フィールド
    # insuranceNote = forms.CharField(required=False, label="加入保険")
    
    # 表示件数フィールド
    results = forms.IntegerField(required=False, label="表示件数(1~1000件)")
    
# メールアドレスで評価を検索するためのフォーム
class EvaluationSearchForm(forms.Form):
    email = forms.EmailField(required=False, label='メールアドレスで検索')

