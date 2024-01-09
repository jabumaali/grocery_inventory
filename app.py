# Grocery inventory database application using
# python's sqlalchemy library.

from sqlalchemy import (create_engine, Column, Integer, 
                        String, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import csv
import datetime
import time

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

def clean_price(price_str):
    final_price = round(float(price_str)*100)
    return final_price

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
                current_prod = session.query(Product).filter(Product.product_name==row[0], Product.brand_id == session.query(Brands).filter(Brands.brand_name == row[4]).first().brand_id).first()
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
              \rN) New Product
              \rA) Analysis
              \rB) Backup
              \rQ) Exit Program""")
        choice = input('What would like to do? ')
        if choice in ['V', 'N', 'A', 'B', 'Q']:
            return choice
        else:
            print('\n Please choose one of the options above.')

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
            print('\n Please choose one of the options above.')
            
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
                            'Product ID', 'Product Name', 'Brand','Quantity','Price','Last Updated'))
                print ("{:<12} {:<30} {:<14} {:<14} {:<14} {:<14}".format(
                        the_product.product_id, the_product.product_name, the_brand.brand_name, the_product.product_quantity, 
                        "$"+"%.2f"%round(float(the_product.product_price/100),2), the_product.date_updated.strftime("%m/%d/%Y")))
                return 0
def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'V':
            view_product()
# strftime("%b %d, %Y")
        elif choice == 'N':
            continue

        elif choice == 'A':
            continue

        elif choice == 'B':
            continue

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