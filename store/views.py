from django.shortcuts import render
from django.shortcuts import get_object_or_404
from . import models
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import HttpResponseBadRequest

# Create your views here.

def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name = 'store/book_detail.html'
    context = {
        'book': None,
        'num_available': None,
        'average_rating': None,
        'user_rating': None,
    }
    # START YOUR CODE HERE
    # Get the book by id or return a 404 error if not found
    book = get_object_or_404(models.Book, id=bid)
    print("book hai ye :", book)

    # Get the number of available copies of the book
    num_available = models.BookCopy.objects.filter(book=book, status=True).count()

    average_rating = book.average_rating()
    user_rating = None
    if request.user.is_authenticated:
        user_rating_obj = models.BookRating.objects.filter(book=book, user=request.user).last()
        if user_rating_obj:
            user_rating = user_rating_obj.rating

    context["book"] = book
    context["num_available"] = num_available
    context["average_rating"] = average_rating
    context["user_rating"] = user_rating

    return render(request, template_name, context=context)


@csrf_exempt
def bookListView(request):
    template_name = 'store/book_list.html'
    context = {
        'books': None, # set this to the list of required books upon filtering using the GET parameters
                       # (i.e. the book search feature will also be implemented in this view)
    }
    get_data = request.GET
    # START YOUR CODE HERE
    searched_title = get_data.get('title', '')
    searched_author = get_data.get('author', '')
    searched_genre = get_data.get('genre', '')
    print(f"Title : {searched_title}, author : {searched_author} & genre : {searched_genre}")
    # Filter books based on query parameters (title and author)
    searched_books = models.Book.objects.filter(
        title__icontains=searched_title,
        author__icontains=searched_author,
        genre__icontains=searched_genre
    )
    context["books"] = searched_books
    print("Books :", searched_books)

    return render(request, template_name, context=context)

# @login_required
# def index(request):
#     return render(request, 'store/book_detail.html')

@login_required
def viewLoanedBooks(request):
    template_name = 'store/loaned_books.html'
    context = {
        'books': None,
    }
    '''
    The above key 'books' in the context dictionary should contain a list of instances of the 
    BookCopy model. Only those book copies should be included which have been loaned by the user.
    '''
    # START YOUR CODE HERE
    # book copies that have been loaned by the current user
    books = models.BookCopy.objects.filter(borrower=request.user)
    context["books"] = books

    return render(request, template_name, context=context)

@csrf_exempt
@login_required
def loanBookView(request):
    response_data = {
        'message': None,
    }
    '''
    Check if an instance of the asked book is available.
    If yes, then set the message to 'success', otherwise 'failure'
    '''
    # START YOUR CODE HERE
    if request.method == 'POST':
        print("I am under post request")
        # User will specify which book to take under loan, for eg; The Atomic Habbits
        book_id = request.POST.get('bid')
        book = get_object_or_404(models.Book, id=book_id)

        try:
            # All the copies of book which user has specified with True status will be filtered and the fisrt one out of it will be stored in the "book_copy" variable
            book_copy = models.BookCopy.objects.filter(book=book, status=True).first()
            print("Book copy :", book_copy)
            if book_copy:
                # Book copy found and available for loan
                book_copy.status = False
                book_copy.borrow_date = timezone.now().date()
                book_copy.borrower = request.user
                book_copy.save()
                response_data['message'] = 'success'
            else:
                # Book copy not available for loan
                response_data['message'] = 'failure'
        except Exception as e:
            # Exception occurred while processing the request
            response_data['message'] = 'error'

    return JsonResponse(response_data)

'''
FILL IN THE BELOW VIEW BY YOURSELF.
This view will return the issued book.
You need to accept the book id as argument from a post request.
You additionally need to complete the returnBook function in the loaned_books.html file
to make this feature complete
''' 
@csrf_exempt
@login_required
def returnBookView(request):
    print("we atrehbjhgftf")
    response_data = {
        'message': None,
    }

    if request.method == 'POST':
        book_id = request.POST.get('bid')
        print("ID :", book_id)

        try:
            book_copy = models.BookCopy.objects.get(id=book_id, borrower=request.user)
            print("copy :", book_copy)
            book_copy.status = True
            book_copy.borrow_date = None
            book_copy.borrower = None
            book_copy.save()
            response_data['message'] = 'success'
        except models.BookCopy.DoesNotExist:
            # Book copy not found or not borrowed by the current user
            response_data['message'] = 'failure'

    return JsonResponse(response_data)


# Handling User ratings
@login_required
@csrf_exempt
def rateBookView(request, bid):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        try:
            rating = int(rating)
            if 0 <= rating <= 10:
                book = get_object_or_404(models.Book, id=bid)

                # Check if the user has already rated the book, if yes, update the rating.
                rating_obj, created = models.BookRating.objects.get_or_create(book=book, user=request.user)
                if not created:
                    book.rating_total -= rating_obj.rating
                    book.rating_count -= 1
                    rating_obj.rating = rating
                else:
                    rating_obj.rating = rating

                book.rating_total += rating
                book.rating_count += 1
                book.save()
                rating_obj.save()

                return JsonResponse({'message': 'success'})
            else:
                return JsonResponse({'message': 'failure', 'error': 'Invalid rating'})
        except ValueError:
            return JsonResponse({'message': 'failure', 'error': 'Invalid rating'})

    return HttpResponseBadRequest('Invalid Request')


