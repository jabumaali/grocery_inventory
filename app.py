# Grocery inventory database application using
# python's sqlalchemy library.

from sqlalchemy import (create_engine, Column, Integer, 
                        String, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import csv
import datetime
from time import sleep

engine = create_engine ("sqlite:///inventory.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Brands(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String)
    # logs = relationship("Logbook", back_populates="animal",
                        # cascade="all, delete, delete-orphan")
    
    def __repr__(self):
        return f"""
        \nBrand ID = {self.brand_id}\r
        Brand Name = {self.brand_name}
        """

class Product(Base):
    __tablename__ = "product"

    product_id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.brand_id"))
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated = Column(Date)
    
    # logs = relationship("Logbook", back_populates="animal",
                        # cascade="all, delete, delete-orphan")
    
    def __repr__(self):
        return f"""
    \nProduct ID = {self.product_id}\r
    Brand ID = {self.brand_id}\r
    Product Name = {self.product_name}\r
    Product Quantity = {self.product_quantity}\r
    Product Price = {self.product_price}\r
    Date Updated = {self.date_updated}\r
    """

def add_prod():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
            if product_in_db == None:
                if row[0] == "product_name":
                    continue
                else:
                    print(row)
                    prodname = row[0]
                    price = clean_price(row[1][1:])
                    quantity = row[2]
                    dateup = datetime.datetime.strptime(row[3], '%m/%d/%Y')
                    brandid = session.query(Brands).filter(Brands.brand_name == row[4]).first().brand_id
                    new_prod = Product(product_name=prodname, product_price=price, product_quantity = quantity, date_updated = dateup, brand_id = brandid)
                    session.add(new_prod)
            else:
                current_prod = session.query(Product).filter(Product.product_name==row[0], 
                        Product.brand_id == session.query(Brands).filter(Brands.brand_name == row[4]).first().brand_id).first()
                if datetime.datetime.combine(current_prod.date_updated, datetime.datetime.min.time()) < datetime.datetime.strptime(row[3], '%m/%d/%Y'):
                    current_prod.product_price = clean_price(row[1][1:])
                    current_prod.product_quantity = row[2]
                    current_prod.date_updated = datetime.datetime.strptime(row[3], '%m/%d/%Y')
        session.commit()

def add_brands():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            brand_in_db = session.query(Brands).filter(Brands.brand_name==row[0]).one_or_none()
            if brand_in_db == None:
                if row[0] == "brand_name":
                    continue
                else:
                    print(row)
                    brand = row[0]
                    new_brand = Brands(brand_name = brand)
                    session.add(new_brand)
        session.commit()

def menu():
    while True:
        print("""
              \n----Grocery Inventory----
              \rV) View Product Details
              \rV2) VIEW ALL
              \rN) New Product
              \rE) Edit/Delete Product
              \rA) Analysis
              \rB) Backup
              \rQ) Exit Program""")
        choice = input('What would like to do? ')
        if choice in ['V', 'V2', 'N', 'E', 'A', 'B', 'Q']:
            return choice
        else:
            print('\nPlease choose one of the options above.')

def submenu():
    while True:
        print("""
              \n1) Edit
              \r2) Delete
              \r3) Return to Main Menu
              """)
        choice = input('What would like to do? ')
        if choice in ['1', '2', '3']:
            return choice
        else:
            print('\nPlease choose one of the options above.')

def clean_price(price_str):
    final_price = round(float(price_str)*100)
    return final_price

def view_product():
    id_options = []
    for product in session.query(Product):
        id_options.append(product.product_id)
    while True:
        print(f'Your options are {id_options}.')
        try:
            id_choice = int(input('Please select your product ID: '))
            if id_choice not in id_options:
                raise ValueError
        except ValueError:
            print('Error: Please enter a valid product ID.')
        else:
            if id_choice in id_options:
                the_product = session.query(Product).filter(Product.product_id==id_choice).first()
                the_brand = session.query(Brands).filter(Brands.brand_id == the_product.brand_id).first()
                print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
                            'Product ID', 'Product Name', 'Brand', 'Quantity', 'Price', 'Last Updated'))
                print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
                        the_product.product_id, the_product.product_name, the_brand.brand_name, the_product.product_quantity, 
                        "$"+'%.2f'%round(float(the_product.product_price/100),2), the_product.date_updated.strftime("%m/%d/%Y")))
                return 0

def view_all():
    print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
                            'Product ID', 'Product Name', 'Brand', 'Quantity', 'Price', 'Last Updated'))
    for the_product in session.query(Product).all():
        the_brand = session.query(Brands).filter(Brands.brand_id == the_product.brand_id).first()
        print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
                the_product.product_id, the_product.product_name, the_brand.brand_name, the_product.product_quantity, 
                "$"+'%.2f'%round(float(the_product.product_price/100),2), the_product.date_updated.strftime("%m/%d/%Y")))
        

    return 0
    
def add_product():
    name = input('Product Name: ')
    new_brand = input('Brand Name: ')
    brand_exists = False
    for brand in session.query(Brands).all():
        if new_brand == brand.brand_name:
            brandid = brand.brand_id
            brand_exists = True
    if brand_exists == False:
        session.add(Brands(brand_name = new_brand))
        session.commit()
        knownbrand = session.query(Brands).filter(Brands.brand_name == new_brand).first()
        brandid = knownbrand.brand_id
    # NEED to check if product also exists. If repeat product, new entry in inventory.
    product_exists = False
    for productx in session.query(Product).all():
        if productx.product_name == name:
            product_exists = True
            prodid = productx.product_id
            break
    if product_exists and brand_exists:
        print(f'This product and brand already exists (ID = {prodid}). Please edit the product.')
        return 0
    quantity = input('Quantity: ')
    price = input('Please enter the price in the following format.\nEx: Enter $5.30 as 5.30\nPrice: ')
    price = clean_price(price)
    dateup = datetime.date.today()
    new_prod = Product(product_name=name, product_price=price, product_quantity = quantity, date_updated = dateup, brand_id = brandid)
    session.add(new_prod)
    session.commit()

def edit_product(brandid, prodid):
    the_product = session.query(Product).filter(Product.product_id == prodid, Product.brand_id == brandid).first()
    quantity = input('Quantity: ')
    curr_price = "$"+'%.2f'%round(float(the_product.product_price/100),2)
    price = input(f"""Please enter the price in the following format.
                  \nEx: Enter $5.30 as 5.30
                  \nCURRENT PRICE: {curr_price}
                  \nPrice: """)
    price = clean_price(price)
    dateup = datetime.date.today()
    the_product.product_quantity = quantity
    the_product.product_price = price
    the_product.date_updated = dateup
    session.commit()
    the_brand = session.query(Brands).filter(Brands.brand_id == the_product.brand_id).first()
    print('Your product has been updated!\n')
    print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
                'Product ID', 'Product Name', 'Brand', 'Quantity', 'Price', 'Last Updated'))
    print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
            the_product.product_id, the_product.product_name, the_brand.brand_name, the_product.product_quantity, 
            "$"+'%.2f'%round(float(the_product.product_price/100),2), the_product.date_updated.strftime("%m/%d/%Y")))
    sleep(1.5)

def delete_product(brandid, prodid):
    the_product = session.query(Product).filter(Product.product_id == prodid, Product.brand_id == brandid).first()
    session.delete(the_product)
    session.commit()
    print('Your product has been deleted.')
    sleep(1.5)

def prod_analysis():
    most_exp = session.query(Product).order_by(Product.product_price.desc()).first()
    print(f'\nThe most expensive item is {most_exp.product_name} at $'
          +'%.2f'%round(float(most_exp.product_price/100),2)+'.')
    least_exp = session.query(Product).order_by(Product.product_price).first()
    print(f'\nThe least expensive item is {least_exp.product_name} at $'
          +'%.2f'%round(float(least_exp.product_price/100),2)+'.')
    all_brands = []
    for brand in session.query(Brands).all():
        all_brands.append(brand.brand_id)
    brand_totals = [0]*(max(all_brands)+1)
    for product in session.query(Product).all():
        for i in all_brands:
            if product.brand_id == i:
                brand_totals[i] += product.product_quantity
    temp, i, index = 0, 0, 0
    for x in brand_totals:
        if x > temp:
            temp = x
            index = i
        i += 1
    most_quantity = temp
    most_brand = session.query(Brands).filter(Brands.brand_id == index).first().brand_name
    print(f'\n{most_brand} has the most products, with a current total of {most_quantity}.')

    #Extra: Most recent change.
    recent = session.query(Product).order_by(Product.date_updated.desc()).first()
    print(f"\nThe last edit to the inventory was made to {recent.product_name} on {recent.date_updated.strftime("%m/%d/%Y")}.")

    #Extra: Average price (not weighted).
    total, num = 0, 0
    for prod in session.query(Product).all():
        total += prod.product_price
        num += 1
    avg = total/num
    print(f"\nThe average product price is ${round(float(avg/100),2):.2f}.")

def backup_db():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            bfieldnames = row
            break
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            pfieldnames = row
            break
    #NOTE: 'w' overwrites file. 'a' would append.
    with open('brands_backup.csv', 'w') as csvfile: 
        brandwriter = csv.writer(csvfile, lineterminator='\r')
        brandwriter.writerow(bfieldnames)
        for brand in session.query(Brands.brand_name).all():
            brandwriter.writerow(brand)
    with open('inventory_backup.csv', 'w') as csvfile:
        prodwriter = csv.writer(csvfile, delimiter = ',', lineterminator='\r')
        prodwriter.writerow(pfieldnames)
        data = session.query(Product).all() #err
        for the_product in session.query(Product).all():
            the_brand = session.query(Brands).filter(Brands.brand_id == the_product.brand_id).first()
            curr_prod = [the_product.product_name, "$"+'%.2f'%round(float(the_product.product_price/100),2),
                         the_product.product_quantity, the_product.date_updated.strftime("%m/%d/%Y"), the_brand.brand_name]
            prodwriter.writerow(curr_prod)
    print("\nDatabase successfully backed up!")
    sleep(1.5)


def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'V':
            view_product()

        elif choice == 'V2':
            view_all()

        elif choice == 'N':
            add_product()
            
        elif choice == 'E':
            prodname = input('Product name: ')
            brandname = input('Brand name: ')
            brand_exists = False
            for brand in session.query(Brands).all():
                if brandname == brand.brand_name:
                    brandid = brand.brand_id
                    brand_exists = True
            product_exists = False
            for productx in session.query(Product).all():
                if prodname == productx.product_name:
                    product_exists = True
                    prodid = productx.product_id
            if brand_exists and product_exists:
                subchoice = submenu()
                if subchoice == '1':
                    edit_product(brandid, prodid)
                if subchoice == '2':
                    delete_product(brandid, prodid)
            else:
                print('Could not find product & brand. Please try again.')

        elif choice == 'A':
            prod_analysis()

        elif choice == 'B':
            backup_db()

        elif choice == 'Q':
            print("\nGoodbye! ^_^")
            app_running = False

        else:
            print("\nPlease enter one of the options above.")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_brands()
    add_prod()
    
    app()
