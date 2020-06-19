SELECT
    books.isbn,
    books.title,
    authors.name,
    ts_rank(
        to_tsvector('english', books.title) || to_tsvector('english', authors.name),
        to_tsquery('english', '<replace with query>')
    ) AS rank
FROM books
JOIN authors ON authors.id = books.author_id
WHERE
    to_tsvector('english', books.title) || to_tsvector('english', authors.name) @@
    to_tsquery('english', '<replace with query>')
OR
    books.isbn LIKE '%<replace with query>%'
ORDER BY rank DESC
LIMIT 10