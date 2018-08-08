from app import app, db
import os
from flask import redirect, render_template, url_for, session, flash, request
from app.models import Product
import stripe
from app.stripe_info import stripe_keys

@app.route('/')
def index():
  context = {
    'title': 'Site Name',
    'Products':Product.query.all()
  }
  print(os.getenv('STRIPE_PUBLISHABLE_KEY'))
  return render_template('index.html', **context)

@app.route('/cart')
def cart():
  if 'cart' not in session or not session['cart']:
    flash("Your cart is empty. Start spending, think of the economy")
    return redirect(url_for('index'))
  items=session['cart']
  dict_of_items = {}
  total_price=0
  for item in items:
    product = Product.query.get(item)
    total_price+=product.price
    if product.id in dict_of_items:
      dict_of_items[product.id]["qty"]+=1
    else:
      dict_of_items[product.id]= {"id": product.id,
                                  "name": product.name,
                                  "qty":1,
                                  "price": product.price,
                                  "image":product.image
                                  }
  session['paymentTotal'] = total_price
  session["shopping_cart"]=dict_of_items
  context={
    'title':'Shopping Cart'
    ,'display_cart':dict_of_items
    ,'total':total_price
    ,'key':stripe_keys['publishable_key']
    # ,'Product':product
    # ,'Product':Product.query.all()
  }
  return render_template('cart.html', **context)

@app.route('/charge', methods=["POST"])
def charge():
  amount = 500
  customer = stripe.Customer.create(
    email='email@example.com',
    source=request.form['stripeToken']
  )

  charge = stripe.Charge.create(
    customer=customer.id,
    amount=amount,
    currency='usd',
    description='test charge'
  )
  session['chargeAmount']=amount
  session["cart"].clear() #???
  return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
  context={
    'amount':session['chargeAmount']
  }
  return render_template('thanks.html',**context)

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
  if 'cart' not in session:
    session["cart"]=[]
  session["cart"].append(id)
  flash("item added to cart")
  return redirect(url_for('index'))

@app.route('/remove_item/<int:id>')
def remove_item(id):
  session["cart"].remove(id)
  flash("item removed from cart")
  return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
  session["cart"].clear()
  flash("Cart has been Cleared")
  return redirect(url_for('cart'))