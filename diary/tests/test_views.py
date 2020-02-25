from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from ..models import Diary


class LoggedInTestCase(TestCase):
    """各テストクラスで共通の事前準備処理をオーバーライドした独自のTestCaseクラス"""

    def setUp(self):
        "テストメソッド実行前の事前設定"
        self.password = 'admin'

        self.test_user = get_user_model().objects.create_user(
            username='admin',
            email='admin@example.com',
            password=self.password
        )

        # テストユーザーでログインする
        self.client.login(email=self.test_user.email, password=self.password)


class TestDiaryCreateView(LoggedInTestCase):
    """DiaryCreateVie用のテストクラス"""

    def test_create_diary_success(self):
        """日記新規作成処理が成功することを検証"""

        params = {'title': 'testTitle', 'content': 'testContent',
                  'photo1': '', 'photo2': '', 'photo3': ''}

        # 新規日記作成処理(post)を実行
        response = self.client.post(reverse_lazy('diary:diary_create'), params)

        # 日記リストページへのリダイレクトを検証
        self.assertRedirects(response, reverse_lazy('diary:diary_list'))

        # 日記データがDBに登録されたかを検証
        self.assertEqual(Diary.objects.filter(title='testTitle').count(), 1)

    # def test_create_diary_failure(self):

    #     response = self.client.post(reverse_lazy('diary:diary_create'))

    #     self. assertFormError(response, 'form', 'title', 'このフィールドは必須です。')


class TestDiaryUpdateView(LoggedInTestCase):
    """DiaryUpdateView用のテストクラス"""

    def test_update_diary_success(self):
        """日記編集処理が成功することを検証"""

        # テスト用日記データの作成
        diary = Diary.objects.create(user=self.test_user, title='beforeUpdate')

        params = {'title': 'afterUpdate'}

        # 日記編集処理(post)を実行
        response = self.client.post(reverse_lazy(
            'diary:diary_update', kwargs={'pk': diary.pk}), params)

        # 日記詳細ページへのリダイレクトを検証
        self.assertRedirects(response, reverse_lazy(
            'diary:diary_detail', kwargs={'pk': diary.pk}))

        # 日記データが編鐘されたかを検証
        self.assertEqual(Diary.objects.get(pk=diary.pk).title, 'afterUpdate')

    def test_update_diary_failure(self):
        """日記編集処理が失敗することを検証"""

        # 日記編集処理(post)を実行
        response = self.client.post(reverse_lazy(
            'diary:diary_update', kwargs={'pk': 999}))

        # 存在しない日記データを編集しようとしてエラーになることを検証
        self.assertEqual(response.status_code, 404)


class TestDiaryDelete(LoggedInTestCase):
    """DiaryDeleteView用のテストクラス"""

    def test_delete_diary_success(self):
        """日記削除処理が成功することを検証"""

        # テスト用日記データの作成
        diary = Diary.objects.create(user=self.test_user, title='testTitle')

        # 日記削除処理(post)を実行
        response = self.client.post(reverse_lazy(
            'diary:diary_delete', kwargs={'pk': diary.pk}))

        # 日記リストページへのリダイレクトを検証
        self.assertRedirects(response, reverse_lazy('diary:diary_list'))

        # 日記データが削除されたかを検証
        self.assertEqual(Diary.objects.filter(pk=diary.pk).count(), 0)

    def test_delte_diary_failure(self):
        """日記削除処理が失敗することを検証"""

        # 日記削除処理(post)を実行
        response = self.client.post(reverse_lazy(
            'diary:diary_delete', kwargs={'pk': 999}))

        # 存在しない日記データを削除しようとしてエラーになることを検証
        self.assertEqual(response.status_code, 404)
