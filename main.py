#!/usr/bin/python
import argparse

from gurobipy import *
from datetime import datetime

# Nutritional food information base on:
# MyFitnessPal open source nutritional database
# https://www.myfitnesspal.com/
# Accessed: 2018-11-28

# Nutritional food price base on:
# Real Canadian Superstore
# https://www.realcanadiansuperstore.ca/
# Accessed: 2018-11-28


# To run scripts:
# main.py -p <penalization: quadratic or none> -w <weighted: yes or no>
# (ex. "main.py -p qudratic -w yes")

categories, minNutrition, maxNutrition = multidict({
  'calories': [1800, 2200],
  'protein':  [91, GRB.INFINITY],
  'fat':      [0, 65],
  'carbohydrates':   [130, GRB.INFINITY] })

# per serving cost in Canadian Dollars:
foods, costs = multidict({
  'meatball': 2.49,
  'chicken': 2.89,
  'meat pie': 1.50,
  'potatoes': 1.89,
  'pasta': 2.09,
  'pizza': 1.99,
  'salad': 2.49,
  'milk': 0.89,
  'ice cream': 1.59})

# Per serving nutrition:
nutritionValues = {
  ('meatball', 'calories'): 410,
  ('meatball', 'protein'): 24,
  ('meatball', 'fat'): 26,
  ('meatball', 'carbohydrates'): 40,
  ('chicken',   'calories'): 420,
  ('chicken',   'protein'): 32,
  ('chicken',   'fat'): 10,
  ('chicken',   'carbohydrates'): 0,
  ('meat pie',   'calories'): 560,
  ('meat pie',   'protein'): 20,
  ('meat pie',   'fat'): 32,
  ('meat pie',   'carbohydrates'): 45,
  ('potatoes',     'calories'): 380,
  ('potatoes',     'protein'): 4,
  ('potatoes',     'fat'): 9,
  ('potatoes',     'carbohydrates'): 39,
  ('pasta',  'calories'): 320,
  ('pasta',  'protein'): 12,
  ('pasta',  'fat'): 10,
  ('pasta',  'carbohydrates'): 75,
  ('pizza',     'calories'): 320,
  ('pizza',     'protein'): 15,
  ('pizza',     'fat'): 12,
  ('pizza',     'carbohydrates'): 37,
  ('salad',     'calories'): 320,
  ('salad',     'protein'): 31,
  ('salad',     'fat'): 12,
  ('salad',     'carbohydrates'): 25,
  ('milk',      'calories'): 100,
  ('milk',      'protein'): 8,
  ('milk',      'fat'): 2.5,
  ('milk',      'carbohydrates'): 13,
  ('ice cream', 'calories'): 330,
  ('ice cream', 'protein'): 8,
  ('ice cream', 'fat'): 10,
  ('ice cream', 'carbohydrates'): 32}

foods, costs_multiplier = multidict({
  'meatball': 1,
  'chicken': lambda x: 1 + math.sin(x),
  'meat pie': 1,
  'potatoes': 1,
  'pasta': 1,
  'pizza': 1,
  'salad': lambda x: 1 + math.sin(x),
  'milk': 1,
  'ice cream': 1})

def function_costs(time=0):
    for food_name in list(costs):
        multiplier=costs_multiplier[food_name]
        if callable(multiplier):
            costs[food_name] = costs[food_name] * multiplier(time)
        else:
            costs[food_name] = costs[food_name] * multiplier

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--penalty', required=False)
parser.add_argument('-w', '--weighted', required=False)

io_args = parser.parse_args()
penalty = io_args.penalty
weighted = io_args.weighted

# Model
m = Model("diet")

# Create decision variables for the foods to buy
buy = m.addVars(foods, name="buy")

if weighted == "yes":
    #finds day in the year (e.g. if Jan 2 -> 2)
    day_of_year = datetime.now().timetuple().tm_yday
    function_costs(time=(day_of_year/365.0)*2*math.pi)

# The objective is to minimize the costs
if penalty == "none":
    # 1: To set to normal objective function with no penalization
    m.setObjective(buy.prod(costs), GRB.MINIMIZE)
elif penalty == "quadratic":
    penalized_objective = QuadExpr()
    for food, price in zip(buy.select(), costs.select()):
        penalized_objective.add(price * food + (.5) * food * food)
    # 2: To set to food amount penalized objective
    m.setObjective(penalized_objective, GRB.MINIMIZE)
else:
    m.setObjective(buy.prod(costs), GRB.MINIMIZE)

# Nutrition constraints
m.addConstrs(
    (quicksum(nutritionValues[f,c] * buy[f] for f in foods)
        == [minNutrition[c], maxNutrition[c]]
     for c in categories), "_")

def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nOptimal Solution: %g' % m.objVal)
        print('\nTO EAT (servings):')
        buyx = m.getAttr('x', buy)
        cost = 0
        for f in foods:
            if buy[f].x > 0.1:
                print('%s %g' % (f, buyx[f]))
                cost += buyx[f] * costs[f]

        print('\nCost of chicken: %g' % costs["chicken"])
        print('Cost of salad: %g' % costs["salad"])
        print('\nMinimum cost: %g' % cost)
    else:
        print('No solution')

    print(m.X)

# Solve
m.optimize()
printSolution()