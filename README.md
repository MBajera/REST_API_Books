# Books-REST-API

Deployed to Heroku: https://book-rest-api-ml.herokuapp.com/ 

GET /books - list of all books (view allows filtering and sorting (example: /books?published_date=1995, /books?sort=-published_date)

GET /books?author=Jan Kowalski&author=Anna Kowalska - list of books by assigned authors

GET /books/<bookId> - selected book

POST /db with body {"q": "war"} - download the data set from 'https://www.googleapis.com/books/v1/volumes?q=war' puts entries into the database (updating existing ones)