from constant import *

### DATA LOADING

def read_region_file(region_filename):
  """
  Read a file containing several recipes for a region.

  The recipes are separated by '**' and the sections of a recipe are separated by '##'.

  Parameters
  ----------
  region_filename: file (.txt)
    File containing all the recipes for the corresponding region
  
  """
  with open(region_filename, 'r') as file:
    data = file.read().rstrip()

  # Split recipes
  recipes = data.split('**')
  
  # Split ingredients
  recipes = [recipe.split('##') for recipe in recipes]

  # Remove newlines at the start & end of each section of a recipe
  recipes = [[x.strip('\n') for x in recipe] for recipe in recipes]

  return recipes


### DATA PROCESSING

def process_ingredient(ingredient):
  """
  Create a tuple of the form (quantity, unit, content, category) for an ingredient.

  The ingredient can only have the following formats in the list of ingredients of a recipe:
    - quantity unit content (e.g. "50 g beurre", "1 bout. vin Chablis)
    - quantity content (e.g. "5 pommes de terre")
    - content (e.g. "amandes", "bouquet garni")

  Parameters
  ----------
  ingredient: string
    Ingredient string, part of an ingredient list in a recipe.

  """
  (quantity, unit, content, category) = ('-', '-', '-', '-')
  ing_list = ingredient.split(' ')

  # Check whether the ingredient has a quantity
  if ing_list[0].replace('.', '').isdigit() or ing_list[0].replace('-', '').isdigit():
    quantity = ing_list[0]

    # Check whether the ingredient has a unit (if it has a quantity)
    for u in Units:
      if unit == '-' and u in ' '.join(ing_list[1:]):
        # remove the extra spaces added for the small unit (e.g. 'l ')
        unit = u.strip()
    
    # The rest of the ingredient is the content
    if unit == '-':
      content = ' '.join(ing_list[1:])
    else:
      unit_nb_words = len(unit.split(' '))
      content = ' '.join(ing_list[1+unit_nb_words:])

  # The ingredient does not start with a quantity
  else:
    content = ingredient

  # Remove starting "de " and "d'" from the content
  content_list = content.split(' ')
  if (content_list[0] == 'de'): 
    content = ' '.join(content_list[1:])
  if (content_list[0].startswith("d'")):
    content_list[0] = content_list[0][2:]
    content = ' '.join(content_list)

  # Find the category of the ingredient, '-' if none
  category = extract_category_from_ingredient(content)

  return (quantity, unit, content, category)  


def extract_category_from_ingredient(ingredient_content):
  """
  Find the category of an ingredient.

  Parameters
  ----------
  ingredient_content: string
    Ingredient content string, part of an ingredient list in a recipe.  
  """
  category = '-'

  # Remove extra "d'" that could hide the main ingredient
  ingredient_content = ingredient_content.replace("d'", '')

  # Go through all the categories
  for cat in Categories.keys():

    # Go through all the elements belonging to the category
    for elem in Categories[cat]:

      # Ensure that each ingredient has one category
      if category == '-':

        # Handle "simple" ingredient
        if len(elem.split(' ')) == 1 and elem in ingredient_content.split(' '):
          category = cat
        # Handle "composed" ingredient (e.g. pomme de terre)
        elif len(elem.split(' ')) > 1 and elem in ingredient_content:
          category = cat
  
  return category


def process_ingredients_from_recipe(recipe):
  """
  Create the set of ingredient tuples for a given recipe.

  Parameters
  ----------
  recipe: pandas.core.series.Series
    Recipe containing at list a field "ingredients" containing the full list of ingredient
    it uses, each separated by a newline.

  """
  ing_tuples = set()

  for ingredient in recipe['ingredients'].split('\n'):
    ing_tuples.add(process_ingredient(ingredient))
  
  return ing_tuples


### EXPLORATORY DATA ANALYSIS

def collect_all_ingredient_contents(recipes_df):
  """
  Create the set of all the ingredient contents from the given recipes.

  Parameters
  ----------
  recipes_df: pandas.core.frame.DataFrame
    DataFrame of recipes where each recipe contains at list a field "ingredients" with
    the full list of ingredient it uses, each separated by a newline.

  """
  contents = set()

  for _, recipe in recipes_df.iterrows():
    for ingredient in recipe['ingredients'].split('\n'):
      (_, _, content, _) = process_ingredient(ingredient)
      contents.add(content)
  
  return contents


def ingredients_frequency(recipes_df):
  """
  Create a dictionary to count the number of occurrances of each ingredient in the given recipes.
  Sort it in reverse order of occurences.

  Parameters
  ----------
  recipes_df: pandas.core.frame.DataFrame
    DataFrame of recipes where each recipe contains at list a field "ingredients" with
    the full list of ingredient it uses, each separated by a newline.

  """
  ingredients_cnt = dict()

  for _, recipe in recipes_df.iterrows():
    for ingredient in recipe['ingredients'].split('\n'):
      (_, _, content, _) = process_ingredient(ingredient)

      if content in ingredients_cnt.keys():
          ingredients_cnt[content] += 1

      elif content+'s' in ingredients_cnt.keys():
          ingredients_cnt[content+'s'] += 1

      else:
        ingredients_cnt[content] = 1
  
  # Sort in reverse order of occurences
  ingredients_cnt = {k: v for k, v in sorted(ingredients_cnt.items(), key = lambda i: i[1], reverse= True)}
  
  return ingredients_cnt


def categories_frequency(recipes_df):
  """
  Create a dictionary to count the number of occurrances of each category in the given recipes.
  Sort it in reverse order of occurences.

  Parameters
  ----------
  recipes_df: pandas.core.frame.DataFrame
    DataFrame of recipes where each recipe contains at list a field "ingredients" with
    the full list of ingredient it uses, each separated by a newline.

  """
  categories_cnt = dict()

  for _, recipe in recipes_df.iterrows():
    for ingredient in recipe['ingredients'].split('\n'):
      (_, _, _, category) = process_ingredient(ingredient)

      if category in categories_cnt.keys():
          categories_cnt[category] += 1
      else:
        categories_cnt[category] = 1
  
  # Sort in reverse order of occurences
  categories_cnt = {k: v for k, v in sorted(categories_cnt.items(), key = lambda i: i[1], reverse= True)}
  
  return categories_cnt

from itertools import islice

def take(n, iterable):
    """Return the first n items of the iterable as a list."""
    return list(islice(iterable, n))