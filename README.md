# Book Review Website

Book review site made with Flask, SQL, HTML/CSS, and the Goodread's API.

## Features
* Login/Register/Logout: Creates sessions and accounts to post reviews, no duplicate usernames
* Books display: Lists books based on queries that serve as links to a dedicated page.
* Search: Queries through books based on certain searches (ISBN, author, title).
* Review posting: Users can post one (and only one) review per book.
* View reviews: All reviews made by users are displayed on the dedicated book page.
* API: JSON file for books containing review count and average rating as well as information about the book can be reached through /api/ISBN.
* Goodreads API: Review count and average rating from Goodreads for books can be found on the dedicated page.

## File Descriptions

* templates/: contains all .html files for the site. Contains 2 layout files used for flask inheritance.
* application.py: Flask application. Framework for the website.
* books.csv: CSV file of books and related data.
* import.py: Imports books.csv into database.
* create.sql: Creates tables in the database.