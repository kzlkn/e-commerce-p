from django.core.mail import send_mail
from django.http import FileResponse
from django.shortcuts import render, redirect
from .forms import CommentForm, ElectronicDeviceArticleForm, SupplementArticleForm, CustomerSupportForm
from .forms import SuperfoodArticleForm, BookArticleForm
import io
from .models import Article, Book, Comment, ElectronicDevice, Superfood, Supplement, get_related_article_from_article
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ShoppingCart.models import ShoppingCart
from Useradmin.models import get_extended_user_from_user


def about (request):
    return render(request, 'about.html')


def article_create(request, **kwargs):
    category = kwargs["category"]
    form = None

    # find correct form to show or use to create object in db
    match category:
        case "books":
            form = BookArticleForm
        case "electronics":
            form = ElectronicDeviceArticleForm
        case "superfoods":
            form = SuperfoodArticleForm
        case "supplements":
            form = SupplementArticleForm

    # handle creating article of correct category
    if request.method == "POST":
        extended_user = get_extended_user_from_user(request.user)
        form = form(request.POST)
        if extended_user is not None:
            form.instance.extended_user = extended_user
            if form.is_valid():  # create article
                data = form.cleaned_data

                match category:
                    case "books":
                        article = create_related_article(data, "BKS")
                        Book.objects.create(related_article=article,
                                            author=data['author'],
                                            pages=data['pages'],
                                            isbn=data['isbn'],
                                            genre=data['genre'],
                                            type=data['type'],
                                            image=request.FILES.get('image')
                                            )
                    case "electronics":
                        article = create_related_article(data, 'ECS')
                        ElectronicDevice.objects.create(related_article=article,
                                                        type=data['type'],
                                                        material=data['material'],
                                                        color=data['color'],
                                                        battery_life=data['battery_life'],
                                                        image=request.FILES.get('image')
                                                        )
                    case "superfoods":
                        article = create_related_article(data, 'NUT')
                        Superfood.objects.create(related_article=article,
                                                 weight=data['weight'],
                                                 vegan=data['vegan'],
                                                 ingredients=data['ingredients'],
                                                 image=request.FILES.get('image'))
                    case "supplements":
                        article = create_related_article(data, 'SUP')
                        Supplement.objects.create(related_article=article,
                                                  weight=data['weight'],
                                                  field_of_use=data['field_of_use'],
                                                  recommended_frequency_of_use=data[
                                                      'recommended_frequency_of_use'],
                                                  ingredients=data['ingredients'],
                                                  image=request.FILES.get('image'))

            else:
                print(form.errors)
            return redirect('article-list', 'all')
    else:
        # get name of category and transform it so it can be showed in view
        category = category[0].upper() + category[1:len(category)]
        context = {
            'category': category,
            'form': form}
        return render(request, 'article-create.html', context)


def article_delete(request, **kwargs):
    article_id = kwargs['pk']
    that_one_article = Article.objects.get(id=article_id)

    # only superusers are qualified to delete articles
    if request.user.is_anonymous or request.user.is_superuser is False:
        return redirect('article-list', 'all')
    if request.method == 'POST':
        Article.objects.filter(id=article_id).delete()
        return redirect('article-list', 'all')
    else:
        context = {'that_one_article': that_one_article}
        return render(request, 'article-delete.html', context)


def article_detail(request, **kwargs):
    article_id = kwargs['pk']
    that_one_article = Article.objects.get(id=article_id)
    comments = Comment.objects.filter(article=that_one_article)
    related_article = get_related_article_from_article(that_one_article)
    # description is split into paragraphs to present it accurately in view
    description = that_one_article.description.split("\n")

    """
    the article rating should be rounded to .5 so we do not need to have
    9 if statements in the views to find out which star image to show based on the rating
    so having the rounded article rating and the path to the related image as vars that are
    provided in the context for the review is much shorter 
    """
    # round article to nearest .5
    rounded_article_rating = None
    if that_one_article.average_review is not None:
        rounded_article_rating = round(that_one_article.average_review * 2) / 2
    # path to reference connected star rating image
    article_rating_path = f'Article/Star_rating_{rounded_article_rating}_of_5.png'

    if request.user.is_anonymous:
        extended_user = None
        user_has_commented = False
    else:
        extended_user = get_extended_user_from_user(request.user)
        user_has_commented = comments.filter(extended_user=extended_user).exists()

    if request.method == 'POST':
        # Add item to shopping cart if user is logged in
        if 'add-to-shopping-cart' in request.POST:
            if extended_user is not None:
                handle_adding_item_to_shopping_cart(extended_user, that_one_article)
            else:
                return redirect('login')

        # Add comment
        else:
            form = CommentForm(request.POST)
            if request.user.is_anonymous:
                return redirect('login')
            if extended_user is not None:
                form.instance.extended_user = extended_user
                form.instance.article = that_one_article
                if form.is_valid():
                    data = form.cleaned_data
                    # update article review
                    article_review = data['article_review']
                    that_one_article.set_average_review(article_review)
                    form.save()
                    return redirect("article-detail", article_id)
                else:
                    print(form.errors)

    context = {'that_one_article': that_one_article,
               'related_article': related_article,
               'description': description,
               'rounded_article_rating': rounded_article_rating,
               'article_rating_path': article_rating_path,
               'comments_for_that_one_article': comments,
               'user_has_commented': user_has_commented,
               'comment_form': CommentForm}
    return render(request, 'article-detail.html', context)


def article_list(request, **kwargs):
    is_search_for_review = False
    context = {}

    if request.method == "POST":
        # if user wants to add an item to shopping cart directly from the article list view
        if 'add-to-shopping-cart' in request.POST:
            # redirect to login if user is not logged in
            if request.user.is_anonymous:
                return redirect('login')
            extended_user = get_extended_user_from_user(request.user)
            article_id = request.POST.get('add-to-shopping-cart')
            item_to_add = Article.objects.get(id=article_id)
            handle_adding_item_to_shopping_cart(extended_user, item_to_add)
            category_to_redirect_to = kwargs['category']
            return redirect('article-list', category_to_redirect_to)

        # if user wants to search based on average review
        elif request.POST.get('general_search', "") == "":
            average_review = request.POST.get('average_review', "")
            if average_review == "":
                pass
            else:
                number_from_review = float(average_review)
                article = None

                if number_from_review == 1:
                    article = Article.objects.filter(average_review__lte=1.0)
                elif number_from_review == 2:
                    article = Article.objects.filter(average_review__lte=2.0).exclude(average_review__lte=1.0)
                elif number_from_review == 3:
                    article = Article.objects.filter(average_review__lte=3.0).exclude(average_review__lte=2.0)
                elif number_from_review == 4:
                    article = Article.objects.filter(average_review__lte=4.0).exclude(average_review__lte=3.0)
                elif number_from_review == 5:
                    article = Article.objects.filter(average_review__lte=5.0).exclude(average_review__lte=4.0)

                is_search_for_review = True
                context = {'search_expr': average_review, 'article': article,
                           'is_search_for_review': is_search_for_review}

        else:
            general_search = request.POST.get('general_search', "")
            if general_search == "":
                pass
            else:
                article = Article.objects.filter(name__contains=general_search)
                context = {'search_expr': general_search, 'article': article,
                           'is_search_for_review': is_search_for_review}

        return render(request, 'search.html', context)

    else:
        # could not fix bug where article without values was added everytime
        # so we decided we just don't show them anymore
        base_articles = Article.objects.exclude(name="")

        # category variable is used to determine which articles to show
        # and which item in the category navigation is underlined (see template)
        category = kwargs['category']
        if category == "books":
            base_articles = base_articles.filter(category="BKS")
        if category == "electronics":
            base_articles = base_articles.filter(category="ECS")
        if category == "superfoods":
            base_articles = base_articles.filter(category="NUT")
        if category == "supplements":
            base_articles = base_articles.filter(category="SUP")

        # to have all the info for articles we put base articles and their related specified articles
        # into a tuple an append this tuple to a list
        # first item in this tuple is the base article and the second item is the specified one
        all_articles = []
        for base_article in base_articles:
            related_article = get_related_article_from_article(base_article)
            all_articles.append((base_article, related_article))

        context = {'all_articles': all_articles, 'category': category}
        return render(request, 'article-list.html', context)


def article_edit(request, pk: str):
    article = Article.objects.get(id=int(pk))
    article_id = article.get_related_article_id()
    category = article.category
    form = None
    contentOfPage = None

    if category == "ECS":
        form = ElectronicDeviceArticleForm(request.POST or None, instance=article)
        contentOfPage = render(request, 'article-edit.html', {'form': form})
    elif category == "SUP":
        form = SupplementArticleForm(request.POST or None, instance=article)
        contentOfPage = render(request, 'article-edit.html', {'form': form})
    elif category == "NUT":
        form = SuperfoodArticleForm(request.POST or None, instance=article)
        contentOfPage = render(request, 'article-edit.html', {'form': form})
    elif category == "BKS":
        form = BookArticleForm(request.POST or None, instance=article)
        contentOfPage = render(request, 'article-edit.html', {'form': form})

    if form.is_valid():
        form.save()
        return redirect('article-detail', article_id)
    return contentOfPage


def article_pdf(request, pk: str):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)

    article = Article.objects.get(id=int(pk))
    lines = [
        "PDF DOWNLOAD",
        "Name: " + article.name,
        "Description: " + article.description,
        "Manufacturer: " + article.manufacturer,
        "Category: " + article.get_category_display(),
        "Age Restriction: " + article.get_ageRestriction_display(),
        "Delivered in: " + article.deliveryIn,
        "Price: " + article.price,
    ]

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    i = 40
    for line in lines:
        p.drawString(20, i, line)
        i += 20

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=article.name + '.pdf')


def comment_delete(request, **kwargs):
    comment_id = kwargs['pk']
    comment = Comment.objects.get(id=int(comment_id))
    article_id = comment.get_related_article_id()
    user = get_extended_user_from_user(request.user)
    if request.method == 'POST':
        if user == comment.extended_user or request.user.is_superuser:
            comment.delete()
            return redirect('article-detail', pk=article_id)
        else:
            return redirect('article-detail', pk=article_id)
    else:  # request.method == 'GET'
        context = {'that_one_comment': comment}
        return render(request, 'comment-delete.html', context)


def comment_edit(request, pk: str):
    comment = Comment.objects.get(id=int(pk))
    article_id = comment.get_related_article_id()
    that_one_article = Article.objects.get(id=article_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        data = form.cleaned_data
        # update article review
        article_review = data['article_review']
        that_one_article.set_average_review(article_review)
        form.save()
        return redirect('article-detail', article_id)
    return render(request, 'comment-edit.html', {'form': form})


def customer_support_inquiry(request):
    if request.method == 'POST':
        form = CustomerSupportForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            send_mail(
                'Customer Support Inquiry: ' + data['subject'],
                data['text'] + '\n' + 'Contact customer: ' + '\n' + data['user_contact'],
                None,
                ['fullfill.webshop@gmail.com'],
                fail_silently=False,
            )
        else:
            print(form.errors)
        return redirect('article-list', 'all')

    else:
        form = CustomerSupportForm
        context = {'form': form}
        return render(request, 'customer-support.html', context)


def customer_support_overview(request):
    reported_comments = Comment.objects.all().filter(report=True)
    articles_to_comments = {}
    user = get_extended_user_from_user(request.user)

    if reported_comments.exists():
        for comment in reported_comments:
            related_article = Article.objects.get(id=comment.get_related_article_id())
            if related_article in articles_to_comments:
                articles_to_comments[related_article].append(comment)
                print(articles_to_comments[related_article])
            else:
                articles_to_comments[related_article] = [comment]

    if user is not None and request.user.is_superuser:
        context = {'articles_to_comments': articles_to_comments}
        return render(request, 'customer-support-overview.html', context)
    else:
        return redirect('article-list', 'all')


def report(request, pk: str, true_or_false: str):
    comment = Comment.objects.get(id=int(pk))
    article_id = comment.get_related_article_id()
    user = get_extended_user_from_user(request.user)
    if user is not None and true_or_false == "true":
        comment.set_report(true_or_false)
        send_mail(
            'Abusive Content Report',
            f'User reported: {comment.extended_user.get_full_name_of_user()} \nBy: {user.get_full_name_of_user()}\n'
            f'Content of report: {comment.text}',
            None,
            ['fullfill.webshop@gmail.com'],
            fail_silently=False,
        )
    elif user is not None and true_or_false == "false":
        comment.set_report(true_or_false)
    return redirect('article-detail', pk=article_id)


def vote(request, pk: str, up_or_down: str):
    comment = Comment.objects.get(id=int(pk))
    article_id = comment.get_related_article_id()
    user = get_extended_user_from_user(request.user)

    if user is not None:
        if up_or_down == "up":
            if comment.get_user_has_downvoted(user) and not comment.get_user_has_upvoted(user):
                comment.remove_downvote(user)
                comment.vote(up_or_down, user)
            elif not comment.get_user_has_upvoted(user):
                comment.vote(up_or_down, user)

        elif up_or_down == "down":
            if comment.get_user_has_upvoted(user) and not comment.get_user_has_downvoted(user):
                comment.remove_upvote(user)
                comment.vote(up_or_down, user)
            elif not comment.get_user_has_downvoted(user):
                comment.vote(up_or_down, user)
    return redirect('article-detail', pk=article_id)


# --- Helper functions ---

def create_related_article(data, article_category):
    article = Article.objects.create(name=data['name'],
                                     subtitle=data['subtitle'],
                                     description=data['description'],
                                     manufacturer=data['manufacturer'],
                                     deliveryIn=data['deliveryIn'],
                                     category=article_category,
                                     ageRestriction=data['ageRestriction'],
                                     price=data['price'],
                                     quantity=data['quantity'])
    return article


def handle_adding_item_to_shopping_cart(extended_user, item_to_add):
    shopping_cart_items = ShoppingCart.get_items(extended_user)
    # only looks for duplicates when there are already items in shopping cart
    if shopping_cart_items.count() > 0:
        # checks if the product is already in shopping cart and
        # increments quantity by 1 instead of adding the item to
        # the shopping cart a second time
        potential_duplicate = shopping_cart_items.filter(product_id=item_to_add.id)
        if potential_duplicate.exists():
            potential_duplicate.get().increment_quantity()
            potential_duplicate.get().save()
        else:
            ShoppingCart.add_item(extended_user, item_to_add)
    else:
        ShoppingCart.add_item(extended_user, item_to_add)
