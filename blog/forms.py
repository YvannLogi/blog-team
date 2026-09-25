from django import forms

from .models import Post, Comment

INPUT_CLASSES = (
    'w-full rounded-lg border border-gray-300 px-4 py-2 '
    'focus:border-black focus:outline-none focus:ring-2 focus:ring-black/20'
)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['guest_name', 'title', 'content', 'categories']
        widgets = {
            'guest_name': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Your first name',
            }),
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'The title of your post',
            }),
            'content': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Tell your story…',
                'rows': 8,
            }),
            'categories': forms.CheckboxSelectMultiple(attrs={
                'class': 'h-4 w-4 accent-black',
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None and user.is_authenticated:
            del self.fields['guest_name']
        else:
            self.fields['guest_name'].required = True

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {'content': ''}
        widgets = {
            'content': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Write a comment…',
                'rows': 3,
            }),
        }
