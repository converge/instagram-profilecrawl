"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

def get_user_info(browser):
  """Get the basic user info from the profile screen"""

  container = browser.find_element_by_class_name('_mesn5')
  img_container = browser.find_element_by_class_name('_b0acm')

  infos = container.find_elements_by_class_name('_t98z6')
  print ("infos: ", infos)
                          
  alias_name = container.find_element_by_class_name('_ienqf')\
                        .find_element_by_tag_name('h1').text
  try:
    bio = container.find_element_by_class_name('_tb97a')\
                        .find_element_by_tag_name('span').text                      
  except:
    print ("\nBio is empty")
    bio = ""
  print ("\nalias name: ", alias_name)
  print ("\nbio: ", bio,"\n")
  prof_img = img_container.find_element_by_tag_name('img').get_attribute('src')
  num_of_posts = int(infos[0].text.split(' ')[0].replace(',', ''))
  followers = infos[1].text.split(' ')[0].replace(',', '').replace('.', '')
  followers = int(followers.replace('k', '00').replace('m', '00000'))
  following = infos[2].text.split(' ')[0].replace(',', '').replace('.', '')
  following = int(following.replace('k', '00'))

  return alias_name, bio, prof_img, num_of_posts, followers, following


def extract_post_info(browser):
  """Get the information from the current post"""

  post = browser.find_element_by_class_name('_622au')

  #print('BEFORE IMG')

  imgs = post.find_elements_by_tag_name('img')
  img = ''

  if len(imgs) >= 2:
    img = imgs[1].get_attribute('src')

  likes = 0
  if len(post.find_elements_by_tag_name('section')) > 2:
    likes = post.find_elements_by_tag_name('section')[1]\
            .find_element_by_tag_name('div').text

    likes = likes.split(' ')

    #count the names if there is no number displayed
    if len(likes) > 2:
      likes = len([word for word in likes if word not in ['and', 'like', 'this']])
    else:
      likes = likes[0]
      likes = likes.replace(',', '').replace('.', '')
      likes = likes.replace('k', '00')

  # if more than 22 comment elements, use the second to see
  # how much comments, else count the li's

  # first element is the text, second either the first comment
  # or the button to display all the comments
  comments = []
  tags = []
  
  date = post.find_element_by_tag_name('time').get_attribute("datetime")
  print ("date is ", date)  
  
  
  if post.find_elements_by_tag_name('ul'):
    comment_list = post.find_element_by_tag_name('ul')
    comments = comment_list.find_elements_by_tag_name('li')

    if len(comments) > 1:
      # load hidden comments
      while (comments[1].text == 'load more comments'):
        comments[1].find_element_by_tag_name('button').click()
        comment_list = post.find_element_by_tag_name('ul')
        comments = comment_list.find_elements_by_tag_name('li')
      tags = comments[0].text + ' ' + comments[1].text
    else:
      tags = comments[0].text

    tags = findall(r'#[A-Za-z0-9]*', tags)


  return img, tags, int(likes), int(len(comments) - 1), date


def extract_information(browser, username):
  """Get all the information for the given username"""

  browser.get('https://www.instagram.com/' + username)

  try:
    alias_name, bio, prof_img, num_of_posts, followers, following \
    = get_user_info(browser)
  except:
    print ("\nError: Couldn't get user profile.\nTerminating")
    quit()
  prev_divs = browser.find_elements_by_class_name('_70iju')


  try:
    body_elem = browser.find_element_by_tag_name('body')

    #load_button = body_elem.find_element_by_xpath\
    #  ('//a[contains(@class, "_1cr2e _epyes")]')
    #body_elem.send_keys(Keys.END)
    #sleep(3)

    #load_button.click()

    links = []
    links2 = []

    
    #list links contains 30 links from the current view, as that is the maximum Instagram is showing at one time
    #list links2 contains all the links collected so far
    
    while (len(links2) < num_of_posts):
      
      prev_divs = browser.find_elements_by_tag_name('main')      
      links_elems = [div.find_elements_by_tag_name('a') for div in prev_divs]  
      links = sum([[link_elem.get_attribute('href')
        for link_elem in elems] for elems in links_elems], [])
      for link in links:
        if "accounts/login" not in link:
          links2.append(link) 
      links2 = list(set(links2))   
      print ("Scrolling profile ", len(links2), "/", num_of_posts)
      body_elem.send_keys(Keys.END)
      sleep(2)
   

  except NoSuchElementException as err:
    print('- Something went terribly wrong\n')

  post_infos = []

  counter = 1  
  for link in links2:
    browser.get(link)
    print ("\n", counter , "/", len(links2))
    counter = counter + 1
    print ("\nScrapping link: ", link)
    try:
      img, tags, likes, comments, date = extract_post_info(browser)

      post_infos.append({
        'img': img,
        'date': date,
        'tags': tags,
        'likes': likes,
        'comments': comments
      })
    except NoSuchElementException:
      print('- Could not get information from post: ' + link)

  information = {
    'alias': alias_name,
    'username': username,
    'bio': bio,
    'prof_img': prof_img,
    'num_of_posts': num_of_posts,
    'followers': followers,
    'following': following,
    'posts': post_infos
  }

  print ("\nFinished. The json file was saved in profiles directory.\n")
  return information
