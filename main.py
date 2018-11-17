#!/usr/bin/python

# Copyright 2018, Gurobi Optimization, LLC

# Solve the classic diet model, showing how to add constraints
# to an existing model.

from gurobipy import *

# Nutritional food information base on:
# USDA Dietary Guidelines(2005)
# http://www.health.gov/DietaryGuidelines/dga2005/

categories, minNutrition, maxNutrition = multidict({
  'calories': [1800, 2200],
  'protein':  [91, GRB.INFINITY],
  'fat':      [0, 65],
  'carbohydrates':   [130, GRB.INFINITY] })

foods, cost = multidict({
  'hamburger': 2.49,
  'chicken':   2.89,
  'hot dog':   1.50,
  'fries':     1.89,
  'macaroni':  2.09,
  'pizza':     1.99,
  'salad':     2.49,
  'milk':      0.89,
  'ice cream': 1.59})

# Nutrition values for the foods
nutritionValues = {
  ('hamburger', 'calories'): 410,
  ('hamburger', 'protein'):  24,
  ('hamburger', 'fat'):      26,
  ('hamburger', 'carbohydrates'):   40,
  ('chicken',   'calories'): 420,
  ('chicken',   'protein'):  32,
  ('chicken',   'fat'):      10,
  ('chicken',   'carbohydrates'):   0,
  ('hot dog',   'calories'): 560,
  ('hot dog',   'protein'):  20,
  ('hot dog',   'fat'):      32,
  ('hot dog',   'carbohydrates'):   45,
  ('fries',     'calories'): 380,
  ('fries',     'protein'):  4,
  ('fries',     'fat'):      19,
  ('fries',     'carbohydrates'):   39,
  ('macaroni',  'calories'): 320,
  ('macaroni',  'protein'):  12,
  ('macaroni',  'fat'):      10,
  ('macaroni',  'carbohydrates'):   75,
  ('pizza',     'calories'): 320,
  ('pizza',     'protein'):  15,
  ('pizza',     'fat'):      12,
  ('pizza',     'carbohydrates'):   37,
  ('salad',     'calories'): 320,
  ('salad',     'protein'):  31,
  ('salad',     'fat'):      12,
  ('salad',     'carbohydrates'):   25,
  ('milk',      'calories'): 100,
  ('milk',      'protein'):  8,
  ('milk',      'fat'):      2.5,
  ('milk',      'carbohydrates'):   13,
  ('ice cream', 'calories'): 330,
  ('ice cream', 'protein'):  8,
  ('ice cream', 'fat'):      10,
  ('ice cream', 'carbohydrates'):   32}

# Model
m = Model("diet")

# Create decision variables for the foods to buy
buy = m.addVars(foods, name="buy")
penalized_objective = QuadExpr();
for food, price in zip(buy.select(), cost.select()):
  penalized_objective.add(price*food*food)

# You could use Python looping constructs and m.addVar() to create
# these decision variables instead.  The following would be equivalent
#
# buy = {}
# for f in foods:
#   buy[f] = m.addVar(name=f)

# The objective is to minimize the costs
#1: To set to normal objective function with no penalization
#m.setObjective(buy.prod(cost), GRB.MINIMIZE)
#2: To set to food amount penalized objective
m.setObjective(penalized_objective, GRB.MINIMIZE)

# Using looping constructs, the preceding statement would be:
#
# m.setObjective(sum(buy[f]*cost[f] for f in foods), GRB.MINIMIZE)

# Nutrition constraints
m.addConstrs(
    (quicksum(nutritionValues[f,c] * buy[f] for f in foods)
    	== [minNutrition[c], maxNutrition[c]]
     for c in categories), "_")

# Using looping constructs, the preceding statement would be:
#
# for c in categories:
#  m.addRange(
#     sum(nutritionValues[f,c] * buy[f] for f in foods), minNutrition[c], maxNutrition[c], c)

def printSolution():
    if m.status == GRB.Status.OPTIMAL:
        print('\nCost: %g' % m.objVal)
        print('\nBuy:')
        buyx = m.getAttr('x', buy)
        for f in foods:
            if buy[f].x > 0.0001:
                print('%s %g' % (f, buyx[f]))
    else:
        print('No solution')

# Solve
m.optimize()
printSolution()

# print('\nAdding constraint: at most 6 servings of dairy')
# m.addConstr(buy.sum(['milk','ice cream']) <= 6, "limit_dairy")
#
# # Solve
# m.optimize()
# printSolution()