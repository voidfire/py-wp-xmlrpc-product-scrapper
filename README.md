# py-wp-xmlrpc-product-scrapper
A Python 2.7 script to scrape products from javascript sites using Selenium/Chrome and Import to Wordpress via XML-RPC

This is a quick and dirty, simple script for learning and fun purposes if you hack it, it will serve you.

It uses the [python-wordpress-xmlrpc](https://python-wordpress-xmlrpc.readthedocs.io/) library to communicate with WordPress and [Selenium](https://pypi.org/project/selenium/) WebDriver Testing Library to open your browser and navigate to the site.


Clone the script
```
git clone https://github.com/voidfire/py-wp-xmlrpc-product-scrapper.git && 
```

```
cd py-wp-xmlrpc-product-scrapper
```

## Install Dependencies
Install python-wordpress-xmlrpc
```
pip install python-wordpress-xmlrpc
```
Install Selenium 
```
pip install -U selenium
```

Run with
```
python scrap.py
```

All of the high level logic is inside the first function the fuctions below are called in it
You will need to target your elements by xpath (can be found with Chrome's inspect element on the elements you need)
The Script assumes the page you want to scrap has a rectangle with all the products in it.
You will need XPATH for 
1.    The gallery/rectangle element
2.    The Single Product title and link
3.    The Product Image URL and Description text from within the product's page.

