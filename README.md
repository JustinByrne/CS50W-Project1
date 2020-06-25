# Project 1

Web Programming with Python and JavaScript

## Installation

### System Requirements

This site has a few system requirements. Majority of this are python related

* python 3
* pip 3
* postgresql database

### Installing Bookful

To install the requirements run the following

`pip3 install -r requirements.txt`

Then to setup the database run this

`python3 -c "import migrate; migrate.up()"`

## APIs being used

- [Goodreads](https://www.goodreads.com/api) - for book review counts
- [Open Library](https://openlibrary.org/dev/docs/api/covers) - for book cover images
