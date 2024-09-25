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
