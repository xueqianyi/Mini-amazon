DROP TABLE IF EXISTS feedbackProduct;
DROP TABLE IF EXISTS feedbackSeller;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS productSeller;
DROP TABLE IF EXISTS lineItems;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS products;

DROP TYPE IF EXISTS fulfilmentStatus;
DROP TYPE IF EXISTS productCategory;
-- the order of dropping and creating are important, because of the foreign key constraints

create table users
(
    u_uid      serial primary key,

    u_email     varchar(256) unique          not null,
    u_firstname varchar(64)                  not null,
    u_lastname  varchar(64)                  not null,
    u_address   varchar(256)                 not null,
    u_password  varchar(256)                 not null, -- hash of the password
    u_balance   decimal(12, 2) default 0     not null,
    u_isSeller  boolean        default false not null,
    u_image     text                         null      --base64 encoded image
);

create table orders
(
    o_orderKey serial primary key,
    o_date     timestamp not null,
    o_uid      integer   not null,
    foreign key (o_uid) references users (u_uid)
);

CREATE TYPE fulfilmentStatus AS ENUM ('Processing', 'Shipped', 'Delivered');

-- TODO
CREATE TYPE productCategory AS ENUM (
    'Electronics',
    'Books',
    'Clothing',
    'Household',
    'Toys',
    'Food',
    'Sports',
    'Beauty',
    'Health',
    'Jewelry',
    'Outdoor',
    'Automotive',
    'Pet Supplies',
    'Office Supplies',
    'Music',
    'Movies',
    'Video Games',
    'Baby',
    'Furniture',
    'Shoes',
    'Accessories',
    'Home Decor',
    'Tools',
    'Garden',
    'Luggage',
    'Watches'
);

create table products
(
    p_pid         serial primary key,
    p_category    productCategory not null,
    p_productName varchar(256)    not null
);

create table lineItems
(
    li_orderKey   integer                               not null,
    li_sid        integer                               not null,
    li_pid        integer                               not null,
    foreign key (li_sid) references users (u_uid),
    foreign key (li_pid) references products (p_pid),
    foreign key (li_orderKey) references orders (o_orderKey),
    primary key (li_orderKey, li_sid, li_pid),

    li_amount     decimal(12, 2) check (li_amount >= 0) not null,
    li_number     integer check (li_number >= 0)        not null,
    li_fulfilment fulfilmentStatus                      not null,
    li_ship_date    timestamp                           null default null,
    li_deliver_date timestamp                           null default null
);

create table productSeller
(
    ps_pid             integer                                                  not null,
    ps_sid             integer                                                  not null,
    foreign key (ps_pid) references products (p_pid),
    foreign key (ps_sid) references users (u_uid),
    primary key (ps_pid, ps_sid),

    ps_stock           integer check (ps_stock >= 0)                            not null,
    ps_price           decimal(12, 2) check (ps_price >= 0)                     not null,
    ps_description     text                                                     null,
    ps_image           text                                                     null,
    ps_avgReviewRating decimal(3, 2) check (ps_avgReviewRating between 0 and 5) null,
    ps_totalSale       integer default 0 check (ps_totalSale >= 0)              not null

);

create table carts
(
    c_uid      integer                        not null,
    c_sid      integer                        not null,
    c_pid      integer                        not null,
    foreign key (c_uid) references users (u_uid),
    foreign key (c_sid) references users (u_uid),
    foreign key (c_pid) references products (p_pid),
    primary key (c_uid, c_sid, c_pid),
    c_date     timestamp not null,
    c_quantity integer check (c_quantity > 0) not null,
    c_status   boolean default false          not null
);

create table feedbackSeller
(
    fs_sid     integer                                        not null,
    fs_uid     integer                                        not null,
    foreign key (fs_sid) references users (u_uid),
    foreign key (fs_uid) references users (u_uid),
    primary key (fs_sid, fs_uid),

    fs_date    timestamp                                      not null,
    fs_content text                                           not null,
    fs_score   decimal(3, 2) check (fs_score between 0 and 5) not null,
    fs_image   text                                           null
);

create table feedbackProduct
(
    fp_pid     integer                                        not null,
    fp_sid     integer                                        not null,
    fp_uid     integer                                        not null,
    foreign key (fp_pid) references products (p_pid),
    foreign key (fp_sid) references users (u_uid),
    foreign key (fp_uid) references users (u_uid),
    primary key (fp_pid, fp_sid, fp_uid),
    fp_date    timestamp                                      not null,
    fp_content text                                           not null,
    fp_score   decimal(3, 2) check (fp_score between 0 and 5) not null,
    fp_image   text                                           null
);

-- TODO: we can add some indexes to improve performance