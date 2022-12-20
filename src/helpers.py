from multiset import *

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

def create_ingredient_tuple(ingredient):
  """
  Create a tuple of the form (quantity, unit, content) for an ingredient.

  The ingredient can only have the following formats in the list of ingredients of a recipe:
    - quantity unit content (e.g. "50 g beurre", "1 bout. vin Chablis)
    - quantity content (e.g. "5 pommes de terre")
    - content (e.g. "amandes", "bouquet garni")

  Parameters
  ----------
  ingredient: string
    Ingredient string part of an ingredient list in a recipe.

  """
  (quantity, unit, content) = ('-', '-', '-')
  ing_list = ingredient.split(' ')

  # Check whether the ingredient has a quantity
  if ing_list[0].replace('.', '').isdigit() or ing_list[0].replace('-', '').isdigit():
    quantity = ing_list[0]

    # Check whether the ingredient has a unit (if it has a quantity)
    for u in Units:
      if unit == '-' and u in ' '.join(ing_list[1:]):
        unit = u
    
    # The rest of the ingredient is the content
    if unit == '-':
      content = ' '.join(ing_list[1:])
    else:
      content = ' '.join(ing_list[2:])

  # The ingredient does not start with a quantity
  else:
    content = ingredient

  return (quantity, unit, content)
  

def ingredient_tuples_from_recipe(recipe):
  """
  Create the set of ingredient tuples for a given recipe.

  Parameters
  ----------
  recipe: pandas.core.series.Series
    Recipe containing at list a field "Ingredients" containing the full list of ingredient
    it uses, each separated by a newline.

  """
  ing_tuples = set()

  for ingredient in recipe['ingredients'].split('\n'):
    ing_tuples.add(create_ingredient_tuple(ingredient))
  
  return ing_tuples


def collect_all_ingredient_contents(recipes_df):
  """
  Create the set of all the ingredient contents from the given recipes.

  Parameters
  ----------
  recipes_df: pandas.core.frame.DataFrame
    DataFrame of recipes where each recipe contains at list a field "Ingredients" with
    the full list of ingredient it uses, each separated by a newline.

  """
  contents = set()

  for _, recipe in recipes_df.iterrows():
    for ingredient in recipe['ingredients'].split('\n'):
      (_, _, content) = create_ingredient_tuple(ingredient)
      contents.add(content)
  
  return contents

def collect_ingredient_multiset(recipes_df):
  """
  Create the set of all the ingredient contents from the given recipes.

  Parameters
  ----------
  recipes_df: pandas.core.frame.DataFrame
    DataFrame of recipes where each recipe contains at list a field "Ingredients" with
    the full list of ingredient it uses, each separated by a newline.

  """
  contents_multiset = Multiset()

  for _, recipe in recipes_df.iterrows():
    for ingredient in recipe['ingredients'].split('\n'):
      (_, _, content) = create_ingredient_tuple(ingredient)
      contents_multiset.update(content)
  
  return contents_multiset

def ingredient_count(recipes_df):
  """
  Create a dictionary to count the number occurrance of each ingredient

  Parameters
  ----------
  recipes_df: pandas.core.frame.DataFrame
    DataFrame of recipes where each recipe contains at list a field "Ingredients" with
    the full list of ingredient it uses, each separated by a newline.

  """
  contents_cnt = dict()

  for _, recipe in recipes_df.iterrows():
    for ingredient in recipe['ingredients'].split('\n'):
      (_, _, content) = create_ingredient_tuple(ingredient)
      if content in contents_cnt.keys():
          contents_cnt[content] += 1
      elif content+'s' in contents_cnt.keys():
          contents_cnt[content+'s'] += 1
      else:
        contents_cnt[content] = 1
  
  return contents_cnt