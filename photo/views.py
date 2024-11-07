from django.shortcuts import render
# django.views.genericからTemplateViewをインポート
from django.views.generic import TemplateView, ListView
# django.views.genericからCreateViewをインポート
from django.views.generic import CreateView
# django.urlsからreverse_lazyをインポート
from django.urls import reverse_lazy
# formsモジュールからPhotoPostFormをインポート
from .forms import PhotoPostForm
# method_decoratorをインポート
from django.utils.decorators import method_decorator
# login_requiredをインポート
from django.contrib.auth.decorators import login_required
from .models import PhotoPost
from django.views.generic import DetailView
from django.views.generic import DeleteView

class IndexView(ListView):
    '''トップページのビュー
    '''
    # index.htmlをレンダリングする
    template_name ='index.html'
    queryset = PhotoPost.objects.order_by('-posted_at')
    paginate_by = 9

# デコレーターにより、CreatePhotoViewへのアクセスはログインユーザーに限定される
# ログイン状態でなければsettings.pyのLOGIN_URLにリダイレクトされる
@method_decorator(login_required, name='dispatch')
class CreatePhotoView(CreateView):
    '''写真投稿ページのビュー
    
    PhotoPostFormで定義されているモデルとフィールドと連携して
    投稿データをデータベースに登録する
    
    Attributes:
      form_class: モデルとフィールドが登録されたフォームクラス
      template_name: レンダリングするテンプレート
      success_url: データベスへの登録完了後のリダイレクト先
    '''
    # forms.pyのPhotoPostFormをフォームクラスとして登録
    form_class = PhotoPostForm
    # レンダリングするテンプレート
    template_name = "post_photo.html"
    # フォームデータ登録完了後のリダイレクト先
    success_url = reverse_lazy('photo:post_done')

    def form_valid(self, form):
        '''CreateViewクラスのform_valid()をオーバーライド
        
        フォームのバリデーションを通過したときに呼ばれる
        フォームデータの登録をここで行う
        
        parameters:
          form(django.forms.Form):
            form_classに格納されているPhotoPostFormオブジェクト
        Return:
          HttpResponseRedirectオブジェクト:
            スーパークラスのform_valid()の戻り値を返すことで、
            success_urlで設定されているURLにリダイレクトさせる
        '''
        # commit=FalseにしてPOSTされたデータを取得
        postdata = form.save(commit=False)
        # 投稿ユーザーのidを取得してモデルのuserフィールドに格納
        postdata.user = self.request.user
        # 投稿データをデータベースに登録
        postdata.save()
        # 戻り値はスーパークラスのform_valid()の戻り値(HttpResponseRedirect)
        return super().form_valid(form)

class PostSuccessView(TemplateView):
    '''投稿完了ページのビュー
    
    Attributes:
      template_name: レンダリングするテンプレート
    '''
    # index.htmlをレンダリングする
    template_name ='post_success.html'
    
class CategoryView(ListView):
  template_name = 'index.html'
  paginate_by = 9
  
  def get_queryset(self):
    category_id = self.kwargs['category']
    categories = PhotoPost.objects.filter(
      category=category_id).order_by('-posted_at')
    return categories

class UserView(ListView):
  template_name = 'index.html'
  paginate_by = 9
  
  def det_queryset(self):
    user_id = self.kwargs['user']
    user_list = PhotoPost.objects.filter(
      user=user_id).order_by('-posted_at')
    return user_list
  
class DetailView(DetailView):
  template_name = 'detail.html'
  model = PhotoPost

class MypageView(ListView):
  template_name = 'mypage.html'
  paginate_by = 9
  
  def get_queryset(self):
    queryset = PhotoPost.objects.filter(
      user=self.request.user).order_by('-posted_at')
    return queryset

class PhotoDeleteView(DeleteView):
  model = PhotoPost
  template_name = 'photo_delete.html'
  success_url = reverse_lazy('photo:mypage')
  
  def delete(self,request,*args,**kwargs):
    return super().delete(request,*args,**kwargs)