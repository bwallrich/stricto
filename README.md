# stricto

![release](https://img.shields.io/github/v/release/bwallrich/stricto.svg?label=latest)


![pylint](https://img.shields.io/github/actions/workflow/status/bwallrich/stricto/pylint.yml?label=linter) ![test](https://img.shields.io/github/actions/workflow/status/bwallrich/stricto/test.yml?label=test)

Strict json structure with schema validation

The way to use is very simple, see [Quickstart](#quickstart) for a basic setup.

The main difference with [jsonschema](https://github.com/python-jsonschema/jsonschema) is that the schema is directly in types of data. You don't have to *validate* them.


## Installation

```bash
pip install stricto
```

## Quickstart

```python
from stricto import Dict, Int, String, List

a=Dict({
    "name" : String(),
    "address" : Dict({
        "num" : Int(),
        "street" : String()
    }),
    "nicknames" : List( String() )
})


a.set({ 
    "name" : "Edward",
    "address" : {
        "num" : 22, 
        "street" : "acacia avenue"
    },
    "nicknames" : [ "Ed" ]
})


print(a.address.num) # 22
print(a.address) # { "num" : 22, "street" : "acacia avenue" }

a.name = 666 # -> raise a typeError (must be a string)

print (a) # { "name" : "Edward", ... }

a.nicknames.append(666) # -> raise a typeError (must be a string)
a.nicknames.append("Eddy")
a.nickname[1] # -> Eddy

b=a # b is a reference on a
c=a.copy() # c is a different object : c is a copy

c == b # return True (you can test and do operators directly on objects)
b.nicknames.pop()
c == b # return False
```

## Basic types

All Python basic classes are implemented in ```stricto```.

| python class | type in stricto |
| - | - |
| bool | Bool() |
| int | [Int()](#int) |
| float | Float() |
| string | [String()](#string) |
| list | [List()](#list) |
| dict | Dict() |
| tuple | [Tuple()](#tuple) |
| bytes | Bytes() |
| | [In()](#in) |
| datetime | Datetime() |

### Example
```python
from stricto import Dict, Int

a = Int()
a.set(22) # -> ok
a.set(23.1) # raise an error
a.set("the number of the beast") # raise an error

# WARNING
a = "the number of the beast" # works ! the affectation of "a" change. Now it is a string. This is python.

# Inside a Dict().
test=Dict({
    "a" : Int()
})

test.a = 22 # -> ok
test.a = 23.1 # raise an error
test.a = "the number of the beast" # raise an error
```

## JSON
```python
# example
from stricto import Int, List, String, Dict, Error, StrictoEncoder
import json

model={
    "b" : Int(),
    "e" : List( String())
}
a=Dict(model)
b=Dict(model)
a.set({ "b" : 1, "e" : [ "aa", "bb"]})

sa = json.dumps(a, cls=StrictoEncoder) # json dumps. Need to user StrictoEncoder for specific types (see extend)
b.set( json.loads(sa) ) 
b == a # return True
```

## Types
### Common options

Commonly available options for any type are:

| Option | Default | Description |
| - | - | - |
| ```required=True\|False``` | False | Check whether the field must have a value. |
| ```description="whatever you want"``` | None | Set a description for the item |
| ```default=666``` | None | set a default value |
| ```in=[ 1, 2, 3, 5 ]\|func``` | None | Value must be in the list or pass the function check. |
| ```union=[ 1, 2, 3, 5 ]\|func``` | None | Alias for ```in```  |
| ```transform=func``` | None | Set a [function](#functions) that [transforms](#transform) the value before assignment. |
| ```constraint=func``` | None | Set a function to [check](#constraints) the value before asssignment. |
| ```constraints=[func]``` | None | Same as above but for a list of [constraints](#constraints) |
| ```onchange=func``` | None | set [onchange](#onchange) a function that will be trigged when the value change. |
| ```onChange=func``` | None | Alias for ```onchange``` |
| ```set=func``` | None | For read-only items ; set a function that will compute the value from others attributes. See [set or compute function](#set) |
| ```compute=func``` | None | Alias for ```set``` |
| ```exists=func``` | True | Set a function to check whether the object exists based on values from other attributes. See  [exists](#exists) for details |
| ```can_read=func``` | True | Set a function to check whether the object is readable. see  [can_read](#can_read) for details |
| ```can_modify=func``` | True | Set a function to check whether the object is changeable (read-only value). see  [can_modify](#can_modify) for details |
| ```on=(event_name, function)``` | None | Register a function to be trigged when the specified event occurs. see  [events](#events) for details |
| ```views=[ "view1", "!view2" ]``` | [] | Define the views this attribute is included or excluded from.. see  [views](#views) for details |

See [functions](#functions) for mor details and examples how to use them.

### Int()
```Int( options )``` maps the Python built-in `int` type.

In addition to the [generic options](#types), it supports specific options:

| Option | Default | Description |
| - | - | - |
| ```min=``` | None | Minimum value |
| ```minimum=21``` | None | Alias for  ```min``` |
| ```max=99``` | None | Maximum value |
| ```maximum=99``` | None | Alias for ```max=99``` |

#### Example
```python
# example
from stricto import Dict, Int, String

client = Dict{
    "age" : Int( min=21, max=120)
}

client.age = 12  # -> raise an error
client.age = 120  # -> Ok

newAge = client.age+1 # -> raise an Error ( > max ) newAge is implicitly an Int( min=21, max=120))
newAge = 1+client.age # -> Ok (newAge is implicitly an int)
```

### String()

```String( options )``` maps the Python built-in `str` string type.

In addition to the [generic options](#types), it supports specific options:

| Option | Default | Description |
| - | - | - |
| ```pattern=regexp``` | None | Must match this `regexp` |
| ```patterns=[reg1, reg2]``` | None | Must match all the regular expressions in the list |
| ```regexp=``` | None | Alias for ```pattern``` |

#### Example
```python
a=String( pattern='^A' )
a.set('Foo')        # -> raise an error
a.set('AZERTY')     # OK

# list of regexp
a=String( patterns=[ '^A', r'.*Z$' ] )
a.set('Allo')        # -> raise an error
a.set('AtoZ')        # OK

# function return a regexp
a=String( pattern=lambda self, value, root : r'.*Z$')
a.set('Allo')        # -> raise an error
a.set('AtoZ')        # OK

```

### List()
```List( options )``` maps the Python built-in `list` type.

In addition to the [generic options](#types), it supports specific options:

| Option | Default | Description |
| - | - | - |
| ```min=``` | None | Minimum number of elements in the list |
| ```minimum=21``` | None | Alias for  ```min``` |
| ```max=99``` | None | Maximum number of elements in the list |
| ```maximum=99``` | None | Alias for `max` |
| ```uniq=True``` | None | Forbid duplicate values |

#### Example
```python
# example
from stricto import Dict, List

client = Dict{
    "nicknames" : List( String(), default=[], uniq=True, min=0, max=3)
}

client.nicknames = [ "Ed", "Eddy", "Edward" ]  # -> raise an error
client.nicknames = [ "Ed" ]  # -> Ok
client.nicknames.append( "Ed" ) # -> raise an error (must be uniq)
```

### Tuple()
```Tuple( options )``` maps the Python built-in `tuple` type.

It supports all the [generic options](#types).

#### Example
```python
# example
from stricto import Dict, Tuple

client = Dict{
    "address" : Tuple( (Int(), String()) )
}

print(client.address) # -> None
client.address = ( 12, "accacia avenue" )  # -> Ok
client.address[1] # -> "acacia avenue"
client.address[0] = 13  # -> raise an error like a standard tuple
client.address = ( 13, "accacia avenue" )  # -> Ok
```

### In()
```In( [ Array of types ] )``` builds the union of several types ; in other words, it allows the attribute to be set with values of different types.

It supports all the [generic options](#types).

#### Example
```python
# example
from stricto import In, Int, String

a = In( [ Int(), String() ] )

a.set("hello") # -> OK
a.count('h') # -> return 1

a.set(12) # -> OK
a.bit_length() # -> return 4
a.count('h') # -> return None

a.set(3.14) # -> raise an error
```

## Functions

A `func` can return a value to modify the result. It can also be a lambda.

### transform

Please refer to [transform function](#types)

#### Example
```python
# example
from stricto import Dict, Int, String

def upper(value, o):
    """
    transform the value into upper

    value : the current value given ("worldcompagny" in this example).
    o     : the full object
    """
    return value.upper()

company=Dict({
    "name" : String( transform=upper ),
})

company.name="worldcompagny"
print(company.name) # -> "WORLDCOMPAGNY"
```

### set

It allows to define a function that will compute the field's value.

This computed field is read-only.

#### Example
```python
# example
from stricto import Dict, Int, String

a=Dict({
    "b" : Int( default = 0, set=lambda o: o.c+1 ),
    "d" : Int( default = 0, set=lambda o: o.b+1 ),
    "c" : Int( ),
})

# "b" and "d" cannot be modified by hand. the are recalculated every time another value 
# change in the Dict.

a.b = 3 # -> raise an error

a.c = 2
print(a.b) # -> 3
print(a.d) # -> 4
```

### constraints
It allows to define a function that checks whether the constraint on the attribute's value is respected.

#### Example
```python
# example
from stricto import Dict, Int, String


def check_pair(value, o): # pylint: disable=unused-argument
    """
    return true if pair
    """
    return not value % 2

a=Dict({
    "b" : Int( default = 0, constraint=check_pair ),        # check before setting
    "d" : Int( constraint=lambda value, o : not value % 2 ), # same as above, with a lambda
    "c" : Int( constraints=[ check_pair ] ),                # A list of constraints
})

a.b = 2 # OK
a.c = 3 # -> raise an error
```

### onchange
It allows to define a listener function about the attribute value change event.

#### Example
```python
from stricto import Dict, Int, String

def change_test(old_value, value, o): # pylint: disable=unused-argument
    """
    just a change option
    old_value   -> The previous value
    value       -> the new one
    o           -> the root object = a in our example
    """
    print(f"The value of b as changed from {old_value} to {value}")

a=Dict({
    "b" : Int( default = 0, onchange=change_test )
})

a.b = 2     # -> output "The value of b as changed from 0 to 2"
a.b = 3-1   # -> nothing displayed
```

### exists
It allows to define a function that checks the attribute's existence.

#### Example
```python
# example
from stricto import Dict, Int, String

def check_if_female(value, o):
    """
    return true if Female
    """
    if o.gender == "Male":
        return False
    return True

cat=Dict({
    "name" : String(),
    "gender" : String( default = 'Male', in=[ 'Male', 'Female' ]),
    "female_infos" : Dict(
        {
        "number_of_litter" : Int(default=0, required=True)
        # ... some other attributes

    }, exists=check_if_female )
})

cat.set({ "name" : "Felix", "gender" : "Male" }
cat.female_infos   # -> None
cat.female_infos.number_of_litter = 2 # -> Raise an Error

cat.gender = "Female"
cat.female_infos.number_of_litter = 2 # -> Ok
cat.female_infos # -> { "number_of_litter" : 2 }
```


## Permissions
Each attribute can have its own set of permissions.
A Permission is materialized by a ```can_<permission>``` parameter for the attribute.

Currently 2 permissions are defined:

| Permission | description |
| - | - |
| can_read | read : The ability to read the attribute's value |
| can_modify | modify : The ability to modify the attribute |

The developer is free to add any permission he needs.

### can_read

It allows to define a function that checks whether the attribute is readable ; returns a boolean.

It shall not be confused with [exists](#exists) : an attribute can exist but not be readable for such user.

#### Example
```python
# example
from stricto import Dict, Int, String

current_user_name="John"

def can_see_and_modify_salary(value, o):

    """
    return true if can read the salary
    """
    global current_user_name
    if current_user_name == o.name:
        return True
    return False


user=Dict({
    "name" : String(),
    "salary" : Int( default=0, can_read=can_see_and_modify_salary, can_modify=can_see_and_modify_salary ),
})

user.set({ "name" : "John", "salary" : 20000 }
user.salary   # -> 20000

user.name="Jack"
user.salary # -> raise an error
```


## selectors

You can use json selectors to find the object according to [rfc9535](https://datatracker.ietf.org/doc/rfc9535/)

### select, multi_select

You can use select() for a single selection or multi_select() for a list of selections

```python
from stricto import Int, List, String, Dict, Error

a = Dict(
    {
        "a": Int(default=1),
        "b": Dict({
            "l" : List( Dict({
                "i" : String()
            }) )
        }),
        "c": Tuple( (Int(), String()) )
    }
)
a.set({ "a" : 12, "b" : { "l" : [ { "i" : "fir"}, { "i" : "sec"}, ] }, "c" : ( 22, "h") })

a.select('$.a') # 12

# To make the difference :

a.select('$.f.d') # None
a.f.d # -> raise an error

a.select("$.b.l[0].i") # "fir"
a.select("$.*.l.i") # ["fir", "sec"]
a.select("$.*.l[0:2].i") # ["fir", "sec"]

# multi_select
a.multi_select( [ "$.a", "$.c" ] ) # [ 12 , ( 22, "h") ]

```


## Matching

You can match an object with some kind of filters. 

Matching is done with ```match( dict )``` method.

Available operators are :

| operator | syntax | example | description |
| - | - | - | - |
| $and | ( "$and", [ condition, condition ] ) | ( "\$and", [ ( "\$gt", 1 ), ( "\$lt" : 2 )]) | Do an *and* on conditions |
| $or | ( "$or", [ condition, condition ] ) |  ( "\$or", [ ( "\$gt", 10 ), ( "$eq" : 0 )]) | Do an *or* on conditions |
| $eq | ( "$eq", value ) |  ( "\$eq", "toto" ) | Equality |
| $ne | ( "$ne", value ) |  ( "\$ne", "toto" ) | Not equal |
| $lt | ( "$lt", value ) |  ( "\$lt", 1 ) | Less than |
| $lte | ( "$lte", value ) |  ( "\$lte", 1 ) | Less than or equal |
| $gt | ( "$gt", value ) |  ( "\$gt", 1 ) | Greater than |
| $gte | ( "$gte", value ) |  ( "\$gte", 1 ) | Greater than or equal |
| $not | ( "$not", condition ) |  ( "\$not", ... ) | Not |
| $reg | ( "$reg", regexp ) |  ( "\$reg", r'Jo' ) | A regular expression; match only on strings (match "start with Jo" in this example.) |
| $contains | ( "$contains", condition ) |  ( "\$contains", ( "$reg", r'^Jo' ) ) | a list contains one or more elements matching the condition |



### Example

```python
from stricto import Int, List, String, Dict, Error

a = Dict(
    {
        "name"    : String()
        "surname" : String()
        "incomes" : Dict({
                "salary" : Int(),
                "royalties" : Int(),
                
        }),
    }
)

a.set( { "name" : "John", "surname" : "Doe", "incomes" : { "salary" : 50000 }})

# Match with equality 
a.match( { "surname" : "Doe" } ) -> return True
a.match( { "incomes" : { "salary" : 20000 } } ) -> return False

# Match with operators
a.match( { "incomes" : { "salary" : ( "$gt", 20000 ) } } ) -> return True
```

## patch

You can patch object in the sense of https://datatracker.ietf.org/doc/html/rfc6902, but with a merge of [selectors]](#selectors).

### Example
```python
from stricto import Int, List, String, Dict, Error

a = Dict(
    {
        "name"    : String()
        "surname" : String()
        "incomes" : Dict({
                "salary" : Int(),
                "royalties" : Int(),
                
        }),
    }
)

a.set( { "name" : "John", "surname" : "Doe", "incomes" : { "salary" : 50000 }})

a.patch( 'replace', '$.name', "Jenny" )
# equivalent of a.name = Jenny

```

## Events

A stricto object can be trigged by custom events.

### Example
```python
import random
from stricto import Dict, Int, String

def random( event_name, root, me ):
    me.set(random.randint(1, 6))


user=Dict({
    "name" : String(),
    "dice1" : Int( default=1, on=('roll' , random) ),
    "dice2" : Int( default=1, on=[ ('roll' , random)] ),
})


user.set({ "name" : "dice1and2" })
# Later
user.trigg('roll')
user.dice1 # -> A number 1-6
user.dice2 # -> A number 1-6
```

## Views

```Views``` allows to define partial versions of a Stricto Item, i.e. versions that include only a subset of the attributes. 

You can specify in views :

* Belong *explicitely* to a view with ```views=[ "my_view" ]```
* Belong *explicitely* not to be in a view with ```views=[ "!my_view" ]```

You can specify in ```get_view()``` :

* an view with all fields excepts those explixitely marked with a "!"with ```get_view("my_view")```
* an explicite view (only those explicitely marked in view) with ```get_view("+my_view")```


### Example
```python
from stricto import Dict, Int, String

# ISO 3166 country reference
country=Dict({
    "name" : String( view=[ "short" ] ),
    "a2" : String( view=[ "short" ] ),
    "a3" : String(),
    "num" : String(),
    "flag_url" : String( set=lambda o: f"https://flagcdn.com/256x192/{o.a2}.png", view=["!save", "short" ] ),
})

country.set({ "name" : "Ukraine", "a2" : "UA", a3 : "UKR", "num" : "804" })

# Whant only fields explicitely in view "short"
v = country.get_view("+short")
# type(v) is a Dict
# v = { "name" : "Ukraine", "a2" : "UA", "flag_url" : "https://flagcdn.com/256x192/UA.png" }

# Whant all fields excepts those with "!short". so all
l = country.get_view("short")
# l == country

s = country.get_view("save")
# type(s) is a Dict
# s = { "name" : "Ukraine", "a2" : "UA", a3 : "UKR", "num" : "804" }
l = country.get_view("+save")
# l == None

l = country.get_view("blabla")
# l == country
l = country.get_view("+blabla")
# l == None
```

## Schemas

You can extract a schema as a ```dict```.


### Example
```python
import stricto

def check_pair():
    pass

a = Dict(
    {
        "b": List(String()),
        "c": In([String(), Int( constraint=check_pair )]),
        "d": Tuple([String(require=True), Bool()]),
    }
)
b = Dict(
    {
        "b": List(String()),
        "c": In([String(), Int( constraints=[check_pair])]),
        "d": Tuple([String(), Bool()]),
    }
)

a.get_schema() == b.get_schema() # False, a.d and b.d differs.
```

You can also extend an existing schema :

```python
# Adding a new 'key' in the previous schema
a.add_to_model(
            "e", String()
        )
a.e='it works !'
# now a.e exists

a.remove_model( 'e' )
a.e # raise an error.
```


## Extended types
An extented type is a type that inherits some of its properties from a *parent* type.

### Using Extend

You can define your own *stricto compatible type* using ```Extend```.

For that, you have to extend your type from ```Extend```, and define methods for encoding and decoding the object.

You have to the ```__repr__``` funtion too.


#### Example
In the example below we define a *Datetime* type, which extends the *datetime* Python type.

```python
from datetime import datetime
from stricto import Extend


class Datetime(Extend):
    """
    A specific class to play with datetime
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must pass the type (datetime) in args for Extend
        """
        super().__init__(datetime, **kwargs)

    def __json_encode__(self):
        """
        Called by the specific Encoder
        to encode datetime
        """
        return self.get_value().isoformat()

    def __json_decode__(self, value):
        """
        Called by the specific Decoder
        to decode a datetime
        """
        return self._type.fromisoformat(value)


a=Datetime()
a.set(datetime(2000, 1, 1))
a.year # 2000 
```

### Using Dict

By this way, you have the possibility to define the type's custom structure.

#### Example
```python
from stricto import Dict, Float

class Complex(Dict):
    """
    A specific class to play with Dict
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must define the struct
        """
        super().__init__(
            {
            "real": Float(), 
            "imag": Float()
            },
            **kwargs)

    def __repr__(self):
        return f"({self.real}+{self.imag}i)"

    def __add__(self, other):
        """
        add two complex
        """
        if not isinstance(other, Complex):
            raise TypeError("can only add Complex")

        r = self.__copy__()
        r.real = self.real + other.real
        r.imag = self.imag + other.imag
        return r

a = Dict({"b": Complex(), "c": Int(default=0)})
a.b.real = 12.0
a.b.imag = 9.0
self.assertEqual(repr(a.b), "(12.0+9.0i)")
```

## Tests & co

For personal use only

```bash
# all tests
python -m unittest tests
# or for only some tests
python -m unittest tests/test_bool.py
# or for a specific test
python -m unittest tests.TestDict.test_simple_type

# reformat
python -m black .

# pylint
pylint $(git ls-files '*.py')

# coverage
coverage run -m unittest tests
coverage html # report under htmlcov/index.html
firefox htmlcov/index.html
```

### Building a new release

For personal use only

```bash
# Modify changelog
# modify pyproject.toml
git add -u
git commit -am 'preparing 0.0.x'
git push
git tag -a 0.0.x -m '0.0.x'
git push origin tag 0.0.x

# publish a new relase in github interface, based on tag 
```


