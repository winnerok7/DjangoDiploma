from django.contrib import admin
import datetime

from .models import CmnUser, SubHeading, SuperHeading,Ad, AddImage, Comment
from .utilities import send_activn
from .forms import SubHeadingForm

# Register your models here.

def send_activns(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activn(rec)
    modeladmin.message_user(request,'Email was posted')
send_activns.short_description = \
'Отправка писем с требованиями активации'

class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Прошли активацию?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
                   ('activated', 'Прошли'),
                   ('threedays', 'Не прошли более 3 дней'),
                   ('week', 'Не прошли более недели'),
               )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False,
                                   date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False,
                                   date_joined__date__lt=d)

class CmnUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter,)
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('alert_message', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activns,)

admin.site.register(CmnUser, CmnUserAdmin)

class SubHeadingInline(admin.TabularInline):
    model = SubHeading

class SuperHeadingPanel(admin.ModelAdmin):
    exclude = ('super_heading',)
    inlines = (SubHeadingInline,)

admin.site.register(SuperHeading,SuperHeadingPanel)

class SubHeadingPanel(admin.ModelAdmin):
    form = SubHeadingForm

admin.site.register(SubHeading,SubHeadingPanel)

class AddImageInline(admin.TabularInline):
    model = AddImage

class AdPanel(admin.ModelAdmin):
    list_display = ('heading','title','content','author','created_at')
    fields = (('heading', 'author'), 'title', 'content', 'price',
    'contacts', 'image', 'is_active')
    inlines = (AddImageInline,)

admin.site.register(Ad,AdPanel)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at', 'is_active')
    list_display_links = ('author', 'content')
    list_filter = ('is_active',)
    search_fields = ('author', 'content',)
    date_hierarchy = 'created_at'
    fields = ('author', 'content', 'is_active', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Comment, CommentAdmin)




