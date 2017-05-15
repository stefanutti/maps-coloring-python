import random
import os

if ['one', 'two', 'three'] == ['one', 'two', 'three']:  print("true")
if ['one', 'two', 'three'] == ['one', 'three', 'two']:  print("Nah")
if ['one', 'two', 'three'] == ['one', 'two', 'three', 'three']:  print("Nah")
if ['one', 'two', 'three'] == ['one', 'two', 'three', 'four']:  print("Nah")
if ['one', 'two', 'three'] == ['one', 'two', 'four']:  print("Nah")
if ['one', 'two', 'three'] == ['one']:  print("Nah")
if ['one', 'two', 'three'] == ['one', 'two', 'three']:  print("true")

if [(1,2),(3,3)] == [(1,2),(3,3)]:  print("true")
if [(1,2),(3,3)] == [(3,3),(3,3)]:  print("Nah")
if [(1,2),(3,3)] == [(3,3),(1,2)]:  print("Nah")
