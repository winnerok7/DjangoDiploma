from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.http import HttpResponse,Http404
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.core.signing import BadSignature
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .utilities import signer
from .models import CmnUser, SubHeading, Ad, Comment
from.forms import UserInfoChange, UserRegister, SearchForm, AdForm, AIFormSet,UserCommentForm,GuestCommentForm
# Create your views here.
def main(request):
    return render(request,'main/main.html')

def contacts(request):
    return render(request, 'main/contacts.html')

def about(request):
    return render(request, 'main/about.html')

def index(request):
    ads = Ad.objects.filter(is_active=True)[:10]
    context = {'ads':ads}
    return render(request, 'main/index.html',context)

def other_page(request, page):
    try:
        template = get_template('main/'+page+'.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

@login_required
def profile(request):
    ads = Ad.objects.filter(author=request.user.pk)
    context = {'ads':ads}
    return render(request,'main/profile.html',context)

@login_required
def profile_ad_page(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    addimg = ad.addimage_set.all()
    context = {'bb': ad, 'ais': addimg}
    return render(request, 'main/profile_ad_page.html', context)

@login_required
def profile_ad_add(request):
    if request.method=="POST":
        form = AdForm(request.POST,request.FILES)
        formset= {}
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST,request.FILES,instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request,messages.SUCCESS,'Ad is added')
                return redirect('main:profile')
    else:
        form = AdForm(initial={'author':request.user.pk})
        formset = AIFormSet()
    context = {'form':form, 'formset':formset}
    return render(request,'main/profile_ad_add.html', context)

@login_required
def profile_ad_change(request,pk):
    ad = get_object_or_404(Ad,pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST,request.FILES,instance=ad)
        formset ={}
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST,request.FILES,intance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request,messages.SUCCESS,'Ad was changed')
                return redirect('main:profile')
    else:
        form = AdForm(instance=ad)
        formset = AIFormSet(instance=ad)
    context = {'form':form,'formset':formset}
    return render(request,'main/profile_ad_change.html',context)

@login_required
def profile_ad_delete(request, pk):
    ad = get_object_or_404(Ad,pk=pk)
    if request.method == 'POST':
        ad.delete()
        messages.add_message(request,messages.SUCCESS,'Ad was deleted')
        return redirect('main:profile')
    else:
        context = {'ad':ad}
        return render(request,'main/profile_ad_delete.html',context)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(CmnUser, username=username)
    if user.is_activated:
        template = 'main/activated_user.html'
    else:
        template = 'main/activation_final.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

def by_heading(request,pk):
    heading =  get_object_or_404(SubHeading,pk=pk)
    ads = Ad.objects.filter(is_active=True,heading=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ads = ads.filter(q)
    else:
        keyword=''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(ads,2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'heading':heading,'page':page,'ads':page.object_list,'form':form}
    return render(request,'main/by_heading.html',context)

def detail(request, heading_pk, pk):
    ad = Ad.objects.get(pk=pk)
    addimg = ad.addimage_set.all()
    comments = Comment.objects.filter(ad=pk,is_active=True)
    initial = {'ad':ad.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == "POST":
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request,messages.SUCCESS,'Comment was added')
        else:
            form = c_form
            messages.add_message(request,messages.SUCCESS,'Comment wasn`t added')
    context = {'ad':ad,'addimg':addimg,'comments':comments, 'form':form}
    return render(request,'main/detail.html',context)


class UserLogin(LoginView):
    template_name = 'main/login.html'

class UserLogOut(LogoutView, LoginRequiredMixin):
    template_name = 'main/logout.html'

class UserInfo(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = CmnUser
    template_name = 'main/info.html'
    form_class = UserInfoChange
    success_url = reverse_lazy('main:profile')
    success_message = 'Info was changed'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request,*args,**kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset,pk=self.user_id)

class ChangePassword(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/change_password.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Password was changed successfully'

class RegisterUser(CreateView):
    model = CmnUser
    template_name = 'main/register.html'
    form_class = UserRegister
    success_url = reverse_lazy('main:register_final')

class RegisterFinal(TemplateView):
    template_name = 'main/reg_final.html'


class DeleteUser(LoginRequiredMixin, DeleteView):
    model = CmnUser
    template_name = 'main/del_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request,messages.SUCCESS, 'User was deleted')
        return super().post(request,*args,**kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset,pk=self.user_id)





