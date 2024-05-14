from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import base64
from decimal import Decimal

num_users = 100
num_products = 1000
num_orders = 2000

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)

        with open('../app/static/default_avatar.png', 'rb') as img_file:
            default_avatar_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            prefix = "data:image/png;base64,"
            default_avatar_base64 = prefix + default_avatar_base64
            
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['address']
            balance = 100.00
            isSeller = True

            writer.writerow([uid, email, firstname, lastname, address, password, balance, isSeller, default_avatar_base64])

        print(f'{num_users} generated')

def gen_orders(num_users, num_orders):
    process_date_list = []
    with open('Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        
        for o_orderKey in range(num_orders):
            o_date = fake.date_time_between(start_date='-1y', end_date='now')
            o_uid = fake.random_int(min=0, max=num_users-1)        
                
            process_date_list.append(o_date)
            writer.writerow([o_orderKey, o_date, o_uid])
        
    print(f'{num_orders} generated')
    return process_date_list

def gen_products(num_products):
    # available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            category = fake.random_element(elements=(
                'Electronics', 'Books', 'Clothing', 'Household', 'Toys',
                'Food', 'Sports', 'Beauty', 'Health', 'Jewelry',
                'Outdoor', 'Automotive', 'Pet Supplies', 'Office Supplies',
                'Music', 'Movies', 'Video Games', 'Baby', 'Furniture',
                'Shoes', 'Accessories', 'Home Decor', 'Tools', 'Garden',
                'Luggage', 'Watches'
            ))
            name = fake.sentence(nb_words=4)[:-1]
            writer.writerow([pid, category, name])
            # available_pids.append(pid)
    print(f'{num_products} generated')




def gen_productSellers(num_products, num_users):
    with open('../app/static/book.png', 'rb') as img_file:
        book_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        prefix = "data:image/png;base64,"
        book_base64 = prefix + book_base64

    product_sellers = []
    
    with open('ProductSeller.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('ProductSeller...', end=' ', flush=True)


        for ps_pid in range(num_products):
            num_sellers = fake.random_int(min=1, max=5)
            used_sellers = set()

            for _ in range(num_sellers):
                while True:
                    ps_sid = fake.random_int(min=0, max=num_users-1)

                    if ps_sid not in used_sellers:
                        used_sellers.add(ps_sid)
                        break

                ps_stock = fake.random_int(min=0, max=1000)
                ps_price = Decimal(str(fake.pydecimal(left_digits=4, right_digits=2, min_value=0, max_value=9999)))
                ps_description = fake.paragraph(nb_sentences=3)
                ps_avgReviewRating = Decimal(str(fake.pydecimal(left_digits=1, right_digits=2, min_value=0, max_value=5)))
                ps_totalSale = fake.random_int(min=0, max=1000)

                # assume 50% of products have images
                ps_image = None
                if fake.boolean(chance_of_getting_true=50):
                    ps_image = book_base64
                writer.writerow([ps_pid, ps_sid, ps_stock, ps_price, ps_description, ps_image, ps_avgReviewRating, ps_totalSale])
                product_sellers.append((ps_pid, ps_sid, ps_price))
    print(f'{len(product_sellers)} product_sellers generated')
    return product_sellers



def gen_lineItems(num_orders, product_sellers, process_date_list):
    num_lineitems = 0
    with open('LineItems.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('LineItems...', end=' ', flush=True)

        for order_key in range(num_orders):
            num_items = fake.random_int(min=1, max=5)
            used_keys = set()

            for _ in range(num_items):
                while True:
                    ps_pid, ps_sid, ps_price = fake.random_element(elements=product_sellers)
                    key = (ps_sid, ps_pid)

                    if key not in used_keys:
                        used_keys.add(key)
                        break

                li_number = fake.random_int(min=1, max=10)
                li_amount = ps_price * li_number
                li_fulfilment = fake.random_element(elements=('Processing', 'Shipped', 'Delivered'))
                num_lineitems += 1
                process_date = process_date_list[order_key]
                if li_fulfilment == 'Processing':
                    li_ship_date = "1970-01-01 00:00:00"
                    li_deliver_date = "1970-01-01 00:00:00"
                elif li_fulfilment == 'Shipped':
                    li_ship_date = fake.date_time_between(start_date=process_date, end_date='now')
                    li_deliver_date = "1970-01-01 00:00:00"
                elif li_fulfilment == 'Delivered':
                    li_ship_date = fake.date_time_between(start_date=process_date, end_date='now')
                    li_deliver_date = fake.date_time_between(start_date=li_ship_date, end_date='now')
                
                writer.writerow([order_key, ps_sid, ps_pid, li_amount, li_number, li_fulfilment, li_ship_date, li_deliver_date])

    print(f'{num_lineitems} lineitems generated')


def gen_carts(num_users, product_sellers):
    generated_keys = 0
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)

        for c_uid in range(num_users):
            num_carts = fake.random_int(min=0, max=5)
            used_keys = set()

            for _ in range(num_carts):
                while True:
                    c_pid, c_sid, _ = fake.random_element(elements=product_sellers)
                    key = (c_pid, c_sid)

                    if key not in used_keys:
                        used_keys.add(key)
                        break

                c_date = fake.date_time_between(start_date='-1y', end_date='now')
                c_quantity = fake.random_int(min=1, max=10)
                c_status = fake.boolean()
                generated_keys += 1
                writer.writerow([c_uid, c_sid, c_pid, c_date, c_quantity, c_status])

    print(f'{generated_keys} carts generated')
    
    

def gen_feedbackProduct(num_users, product_sellers):
    generated_keys = 0
    with open('../app/static/feedback.png', 'rb') as img_file:
        feedback_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        prefix = "data:image/png;base64,"
        feedback_base64 = prefix + feedback_base64

    with open('FeedbackProduct.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Feedback...', end=' ', flush=True)

        for ps_pid, ps_sid, _ in product_sellers:
            num_feedbacks = fake.random_int(min=0, max=5)
            used_users = set()

            for _ in range(num_feedbacks):
                while True:
                    fp_uid = fake.random_int(min=0, max=num_users-1)

                    if fp_uid not in used_users:
                        used_users.add(fp_uid)
                        break

                fp_date = fake.date_time_between(start_date='-1y', end_date='now')
                fp_content = fake.paragraph(nb_sentences=3)
                fp_score = fake.pyfloat(left_digits=1, right_digits=2, min_value=0, max_value=5)

                fp_image = None
                if fake.boolean(chance_of_getting_true=50):
                    fp_image = feedback_base64
                generated_keys += 1
                writer.writerow([ps_pid, ps_sid, fp_uid, fp_date, fp_content, fp_score, fp_image])

    print(f'{generated_keys} feedbacks generated')
    
    
def gen_feedbackSeller(num_users, product_sellers):
    generated_keys = 0

    with open('../app/static/feedback.png', 'rb') as img_file:
        feedback_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        prefix = "data:image/png;base64,"
        feedback_base64 = prefix + feedback_base64

    with open('FeedbackSeller.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('FeedbackSeller...', end=' ', flush=True)

        used_sid = set()
        for _, ps_sid, _ in product_sellers:
            if ps_sid not in used_sid:
                used_sid.add(ps_sid)
                num_feedbacks = fake.random_int(min=0, max=5)
                used_users = set()

                for _ in range(num_feedbacks):
                    while True:
                        fs_uid = fake.random_int(min=0, max=num_users-1)
                        if fs_uid not in used_users:
                            used_users.add(fs_uid)
                            break

                    fs_date = fake.date_time_between(start_date='-1y', end_date='now')
                    fs_content = fake.paragraph(nb_sentences=3)
                    fs_score = fake.pyfloat(left_digits=1, right_digits=2, min_value=0, max_value=5)

                    fs_image = None
                    if fake.boolean(chance_of_getting_true=50):
                        fs_image = feedback_base64

                    generated_keys += 1
                    writer.writerow([ps_sid, fs_uid, fs_date, fs_content, fs_score, fs_image])

    print(f'{generated_keys} feedbacks generated')




gen_users(num_users)
gen_products(num_products)
process_date_list = gen_orders(num_users, num_orders)
product_sellers = gen_productSellers(num_products, num_users)
gen_lineItems(num_orders, product_sellers, process_date_list)
gen_carts(num_users, product_sellers)
gen_feedbackProduct(num_users, product_sellers)
gen_feedbackSeller(num_users, product_sellers)