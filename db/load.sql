\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV
-- since id is auto-generated; we need the next command to adjust the counter
-- for auto-generation so next INSERT will not clash with ids loaded above:
SELECT pg_catalog.setval('public.users_u_uid_seq',
                         (SELECT MAX(u_uid)+1 FROM Users),
                         false);

\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.products_p_pid_seq',
                         (SELECT MAX(p_pid)+1 FROM Products),
                         false);

\COPY Orders FROM 'Orders.csv' WITH DELIMITER ',' NULL '' CSV
SELECT pg_catalog.setval('public.orders_o_orderKey_seq',
                         (SELECT MAX(o_orderKey)+1 FROM Orders),
                         false);

\COPY ProductSeller FROM 'ProductSeller.csv' WITH DELIMITER ',' NULL '' CSV

\COPY LineItems FROM 'LineItems.csv' WITH DELIMITER ',' NULL '' CSV

\COPY Carts FROM 'Carts.csv' WITH DELIMITER ',' NULL '' CSV

\COPY FeedbackProduct FROM 'FeedbackProduct.csv' WITH DELIMITER ',' NULL '' CSV

\COPY FeedbackSeller FROM 'FeedbackSeller.csv' WITH DELIMITER ',' NULL '' CSV

UPDATE LineItems
SET li_ship_date = NULL
WHERE li_ship_date = '1970-01-01 00:00:00';

UPDATE LineItems
SET li_deliver_date = NULL
WHERE li_deliver_date = '1970-01-01 00:00:00';