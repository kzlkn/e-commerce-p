from django import forms
from .models import Article, Comment, ElectronicDevice, Superfood, Supplement, Book, CustomerSupportRequest


class BookArticleForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'subtitle', 'description', 'manufacturer', 'deliveryIn', 'ageRestriction',
                  'price', 'author', 'pages', 'isbn', 'genre', 'type', 'quantity', 'image']
        widgets = {
            'ageRestriction': forms.Select(choices=Article.AGE_RESTRICTION),
            'description': forms.Textarea(),
            'genre': forms.Select(choices=Book.GENRES),
            'type': forms.Select(choices=Book.TYPES)
        }


class ElectronicDeviceArticleForm(forms.ModelForm):
    class Meta:
        model = ElectronicDevice
        fields = ['name', 'subtitle', 'description', 'manufacturer', 'deliveryIn', 'ageRestriction',
                  'price', 'type', 'material', 'color', 'battery_life', 'quantity', 'image']
        widgets = {
            'ageRestriction': forms.Select(choices=Article.AGE_RESTRICTION),
            'description': forms.Textarea(),
            'type': forms.Select(choices=ElectronicDevice.TYPES),
        }


class SuperfoodArticleForm(forms.ModelForm):
    class Meta:
        model = Superfood
        fields = ['name', 'subtitle', 'description', 'manufacturer', 'deliveryIn', 'ageRestriction',
                  'price', 'weight', 'ingredients', 'vegan', 'quantity', 'image']
        widgets = {
            'ageRestriction': forms.Select(choices=Article.AGE_RESTRICTION),
            'description': forms.Textarea(),
            'vegan': forms.CheckboxInput()
        }


class SupplementArticleForm(forms.ModelForm):
    class Meta:
        model = Supplement
        fields = ['name', 'subtitle', 'description', 'manufacturer', 'deliveryIn', 'ageRestriction',
                  'price', 'weight', 'field_of_use', 'recommended_frequency_of_use', 'ingredients',
                  'quantity', 'image']
        widgets = {
            'ageRestriction': forms.Select(choices=Article.AGE_RESTRICTION),
            'description': forms.Textarea(),
            'field_of_use': forms.Select(choices=Supplement.FIELDS_OF_USE),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['article_review', 'title', 'text']
        widgets = {
            'extended_user': forms.HiddenInput(),
            'book': forms.HiddenInput(),
            'review': forms.Select(choices=Comment.REVIEW_STARS),
        }


class CustomerSupportForm(forms.ModelForm):
    class Meta:
        model = CustomerSupportRequest
        fields = ['subject', 'text', 'user_contact']
