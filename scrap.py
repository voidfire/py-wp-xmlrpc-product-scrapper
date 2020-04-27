from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import re, urllib, os, sys, time, mimetypes, xmlrpclib, errno, magic

driver = webdriver.Chrome()

# Add the URL of the product page you want to scrap
driver.get("https://www.test.com/example-category")
driver.implicitly_wait(10)

# Add your Site URL and Details
client = Client('http://wp-ep.test/xmlrpc.php', 'admin', 'secret')
existingPostTitles = []

# All the magic runs in this function and its loops
def getProductTitle():
	productsJs=[]
    # Target by xpath the box that has the products elements in it
	productlist = driver.find_element_by_xpath('/html/body/div/div[3]/div/div/section/div/section/ul')
	productsJs = productlist.find_elements_by_tag_name('article')
	print 'Found ' + str(len(productsJs)) + ' Products'
	description = ''
    # We Fetch all current products and return the existingPostTitles for comparison before import
	getAllPosts()
    # Iterating throught the products in the box
	for p in productsJs:
        # Target the title & url of one product
		prod_title = p.find_element_by_xpath('div/div/header/h3/a').text
		rurl = p.find_element_by_xpath('div/div/header/h3/a').get_attribute('href')
	 	print 'Checking if ' + prod_title + ' exists'
        
        # Checking Scraped Title against existing in our WordPress and if exists we move to next product
		post_id=find_id(prod_title, existingPostTitles)
		if post_id == True:
			print "Sorry, we already have such a post():"
			print '\n'
			continue

        # Open Product URL to get Description and Image link
		print 'Found Product URL: ' + rurl
		openProductWindow(rurl)
		description = getProductDescription()
	 	print 'Found Product Description: ' + description
	 	img_url = getImageLink()
		print 'Found Image Url: ' + img_url
		print 'Downloading Image'
		print 'Zzz 3 secs.. Uploading..'
		time.sleep(3)
		attachment_id = imageUpload(img_url)

		makeWpPost(prod_title, description, attachment_id)
		driver.close()
		time.sleep(5)
		driver.switch_to.window(driver.window_handles[0])

# Gets All Existing WP Products 
def getAllPosts():
	offset = 0
	increment = 10
	while True:
		filter = { 'post_type': 'product', 'offset' : offset }
		postz = client.call(GetPosts(filter))
		if len(postz) == 0:
			break  # no more posts returned
		for post in postz:
			existingPostTitles.append(post.title)
		offset = offset + increment

# Check Scrapped product title agains Existing Product Titles
def find_id(prod_title, existingPostTitles):
	while True:
		for post in existingPostTitles:
			if post == prod_title:
				print post
				return(True)
		return(False)

# Open Product in new tab and switch to it
def openProductWindow(rurl):
	driver.execute_script('window.open("'+ rurl +'","_blank");')
	driver.switch_to_window(driver.window_handles[-1])

# Get Product Description
def getProductDescription():
	driver.implicitly_wait(5)
    # Target Product Description from single product page
	description = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div/div/div[2]/ul/li[2]').text
	return description

# Get Product Image Link
def getImageLink():
    # Target Image with XPATH
	img_url = driver.find_element_by_xpath('//*[@id="cloudZoom"]').get_attribute("href")
	return img_url

# Download Image and prepare for upload
def imageUpload(img_url):
	cleanImgUrl = img_url.split('?')[0]
	imageName = img_url.split('/')[-1]
	cleanImgName = imageName.split('?')[0]
    # Cloudflare proxy may get in the way without a useragent
	urllib.URLopener.version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
	fileImg = urllib.urlretrieve(cleanImgUrl, cleanImgName)
	imageType = mimetypes.guess_type(cleanImgUrl)[0]
	print imageType

    # Add your Site URL and Details 
	client = Client('http://wp-ep.test/xmlrpc.php', 'admin', 'secret')

	data = {
				'name': cleanImgName,
				'type': imageType,
			}

	with open(cleanImgName, 'rb') as img:
		data['bits'] = xmlrpc_client.Binary(img.read())
	
	print data
	response = client.call(media.UploadFile(data))
	return response['id']

# Prepare Object with the scraped data and upload to WordPress
def makeWpPost(prod_title, description, attachment_id):
	post = WordPressPost() 
	post.title = prod_title
	post.content = description
	post.post_type = "product"
	post.post_status = "draft"
	post.thumbnail = attachment_id
	addpost = client.call(posts.NewPost(post))
	print 'Product added: ' + prod_title
	print '\n'

# Starts the main function
getProductTitle()