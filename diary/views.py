import logging
import datetime

from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView,FormView
from .models import Diary
from .forms import InquiryForm, DiaryCreateForm
from django.contrib.auth.decorators import login_required
import subprocess

logger = logging.getLogger(__name__)
# Create your views here.


class IndexView(TemplateView):
    template_name = "index.html"


class InquiryView(FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('inquriy send by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)


class DiaryListView(ListView):
    model = Diary
    template_name = 'diary_list.html'
    paginate_by = 2

    def get_queryset(self):
        diaries = Diary.objects.filter(user=self.request.user).order_by('-created_at')
        return diaries


class DiaryDetailView(LoginRequiredMixin, DetailView):
    model = Diary
    template_name = 'diary_detail.html'


class DiaryCreateView(LoginRequiredMixin, CreateView):
    model = Diary
    template_name = 'diary_create.html'
    form_class = DiaryCreateForm
    success_url = reverse_lazy('diary:diary_list')

    def form_valid(self, form):
        diary = form.save(commit=False)
        diary.user = self.request.user
        diary.save()
        messages.success(self.request, '日記を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '日記の作成に失敗しました。')
        return super().form.invalid(form)


class DiaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Diary
    template_name = 'diary_update.html'
    form_class = DiaryCreateForm

    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '日記の更新に失敗しました。')
        return super().form_invalid(form)

class DiaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Diary
    template_name = 'diary_delete.html'
    success_url = reverse_lazy('diary:diary_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '日記を削除しました。')
        return super().delete(request, *args, **kwargs)

@login_required
def DiaryBackup(request):
    message = []
    rc_code = None
    date = datetime.date.today().strftime('%Y%m%d')
    cmd = 'python manage.py backup_diary'
    rc_code = subprocess.call(cmd, shell=True)
    if rc_code == 0:
        message = 'バックアップが正常終了しました。'
        backup_name = 'backupdiary' + date + '.csv'
    else:
        message = 'バックアップが異常終了しました。'
    return render(request, 'result.html', {'message': message, 'backup_name': backup_name})
