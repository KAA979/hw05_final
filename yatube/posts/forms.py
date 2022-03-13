from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        text = forms.CharField(label='Текст поста')
        group = forms.ChoiceField(label='Выбрать группу')
        image = forms.ImageField(label='Картинка')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        text = forms.CharField(label='Текст комментария')
