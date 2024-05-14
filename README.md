#  Mini-Amazon Project
Welcome to Mini-Amazon, a miniature version of the popular Amazon marketplace designed to emulate key functionalities from both the seller and buyer sides. This platform is divided into several modules, each with specific features that support the overall operation of the e-commerce system. Below is an overview of the subsystems and their functionalities.

[<img src="https://github.com/xueqianyi/Mini-amazon/assets/55613486/8d482e89-60fa-4a9b-8fa5-87a1223e848e" width="50%">](https://www.youtube.com/watch?v=0b6r3II_sNM "Now in Android: 55") 
## Main Features
### Account / Purchases
- **Registration and Login:** Users can create a new account or log in using an email and password.
- **User Profile Management:** Users can update their profile details such as email, full name, address, and password. Note that the email must be unique and the user ID is not editable.
- **Financial Transactions:** Users can top up or withdraw funds from their account balance, which starts at $0.
- **Purchase History:** Users can access their purchase history displayed in reverse chronological order. Each record links to a detailed order page.
- **Public and Seller Profiles**: Public profiles display essential user information. For users who are sellers, additional details like reviews are shown.
- **Security Measures:** Ensure all form submissions are secure and safeguard against SQL injection.
### Products
- **Product Browsing:** Users can browse products by categories, search by keywords, and apply various filters such as price or rating.
- **Product Details:** Each product has a dedicated page showing detailed information, stock availability from different sellers, and customer reviews.
- **Product Management:** Sellers can add and edit their product listings.
- **Advanced Features:** Potential enhancements include more sophisticated filtering options, a system for standardizing products across sellers, and different pricing models.
### Cart / Order
- **Shopping Cart:** Users can manage their shopping cart, adjust quantities, remove items, or save them for later purchase.
- **Checkout Process:** The system checks inventory and account balance before finalizing purchases. It updates inventory and balances upon order confirmation.
- **Order Details:** After purchase, the order page provides finalized details including price and fulfillment status.
- **Promotions:** Functionality for applying discount codes to specific items or entire orders is included.
### Inventory / Order Fulfillment
- **Inventory Management:** Sellers can view and manage their inventory, adjusting stock levels as necessary.
- **Order Fulfillment:** Sellers can view their order history, manage order fulfillment, and update the status of orders.
- **Analytics:** Provides sellers with insights into buyer interactions and sales metrics.
### Feedback / Messaging
- **Reviews and Ratings:** Users can submit and manage reviews for products and sellers, with limitations to prevent multiple reviews for the same item by one user.
- **Review Interface:** Users can access and edit their reviews through their account interface.
- **Aggregate Ratings:** The system calculates and displays average ratings for products and sellers, organizing reviews by rating or date.
## Quick Start
### Installing the skeleton
Run  `./install.sh`
This will install a bunch of things, set up an important file called `.flashenv`, and create a simple PostgreSQL database named `amazon` with our fake data generated automatically by `db/data/gen.py`.  
To change the database schema, modify `db/create.sql` and `db/load.sql` as needed.  Make sure you run `db/setup.sh` to reflect the changes.
### Running/Stopping the Website
To run your website, go into the repository directory and issue the following commands:
```
poetry shell
flask run
```
To stop your app, type <kbd>CTRL</kbd>-<kbd>C</kbd> in the container shell; 
