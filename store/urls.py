from django.urls import path
from . import views

# app_name = 'store'

urlpatterns = [
    path('', views.index, name="index"),
    path('books/', views.bookListView, name="book-list"),
    path('book/<int:bid>/', views.bookDetailView, name='book-detail' ),
    path('books/loaned/', views.viewLoanedBooks, name="view-loaned"),
    path('books/loan/', views.loanBookView, name="loan-book"),
    path('books/return/', views.returnBookView, name="return-book"),
    path('book/<int:bid>/rate/', views.rateBookView, name='rate-book'),
]
