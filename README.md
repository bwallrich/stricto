# stricto

![pylink](https://img.shields.io/github/actions/workflow/status/bwallrich/stricto/pylint.yml)
![test](https://img.shields.io/github/actions/workflow/status/bwallrich/stricto/test.yml)

Strict json structure with schema validation

The way to use is very simple, see [Quickstart](#quickstart) for a basic setup.

The main difference with [jsonschema](https://github.com/python-jsonschema/jsonschema) is that the schema is directly in types of data. You don't have to *validate* them.


## Installation

```bash
pip install git+https://github.com/bwallrich/stricto
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
print(a.address) # { "num" : 22, "street" : "acacia avenue" }

a.name = 666 # -> raise a typeError (must be a string)

print (a) # { "name" : "Edward", ... }

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

All basic class from python are implemented in ```stricto```.

| python class | type in stricto |
| - | - |
| bool | Bool() |
| int | Int() |
| float | Float() |
| string | String() |
| list | List() |
| dict | Dict() |
| | In() |

```python
# example
from stricto import Dict, Int

a = Int()
a.set(22) # -> ok
a.set(23.1) # raise an error
a.set("the number of the beast") # raise an error

# WARNING
a = "the number of the beast" # works ! the affectation of "a" change. Now it is a string. This is python.

# Inside a Dict().
test=Dict({
    "a" : Int()
})

test.a = 22 # -> ok
test.a = 23.1 # raise an error
test.a = "the number of the beast" # raise an error

```

## json


use ```.get_value()``` to extract a dict from a Dict and do the *json.dumps* like usual.


```python
# example
from stricto import Int, List, String, Dict, Error
import json

model={
    "b" : Int(),
    "e" : List( String())
}
a=Dict(model)
b=Dict(model)
a.set({ "b" : 1, "e" : [ "aa", "bb"]})

sa = json.dumps(a.get_value()) # json dumps 
b.set( json.loads(sa) ) 
b == a # return True
```

## Types and options

### All types

available options for all types ares :

| Option | Default | Description |
| - | - | - |
| ```notNone=True\|False``` | False | cannot be **None** |
| ```required=True\|False``` | False | similar to ```notNone``` |
| ```description="whatever you want"``` | None | a description of this object |
| ```default=666``` | None | the default value |
| ```in=[ 1, 2, 3, 5 ]\|func``` | None | the value must be one of those elements |
| ```union=[ 1, 2, 3, 5 ]\|func``` | None | similar to ```in```  |
| ```transform=func``` | None | a [function](#functions) to [transform](#transform) the value before setting it |
| ```constraint=func``` | None | a [constraints](#constraints) to check the value before setting it |
| ```constraints=[func]``` | None | a list of [constraints](#constraints) to check the value before setting it |
| ```onchange=func``` | None | a [onchange](#onchange) function trigged when the value change |
| ```onChange=func``` | None | similar to ```onchange``` |
| ```set=func``` | None | a read only value, calculated from other .See [set or compute function](#set-or-compute) |
| ```compute=func``` | None | similar to ```set``` |
| ```exists=func``` | True | a function to say if the object "exists", depending on values from other attributs. See  [exists](#exists) for details |

See [functions](#functions) for mor details and examples how to use them.

### Int()

```Int( options )``` is for integer.

```Int( options )``` use [generic options](#all-types).

available specific options for Int() ares :

| Option | Default | Description |
| - | - | - |
| ```min=``` | None | minimum value |
| ```minimum=21``` | None | similar to ```min``` |
| ```max=99``` | None | maximum value |
| ```maximum=99``` | None | similar to ```max=99``` |

```python
# example
from stricto import Dict, Int, String

client = Dict{
    "age" : Int( min=21, max=120)
}

client.age = 12  # -> raise an error
client.age = 120  # -> Ok

newAge = client.age+1 # -> raise an Error ( > max ) newAge is implicitly an Int( min=21, max=120))
newAge = 1+client.age # -> Ok (newAge is implicitly an int)
```

### String()

```String( options )``` is for strings.

```String( options )``` use [generic options](#all-types).

available specific options for Int() ares :

| Option | Default | Description |
| - | - | - |
| ```pattern=regexp``` | None | must match this regexp |
| ```patterns=[reg1, reg2]``` | None | must match all regexps |
| ```regexp=``` | None | similar to ```pattern``` |

Examples

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

### In()

```In( [ Array of types ] )``` is not a type, but an **union** of diffferent types.

```In( options )``` use [generic options](#all-types).


```python
# example
from stricto import In, Int, String

a = In( [ Int(), String() ] )

a.set("hello") # -> OK
a.count('h') # -> return 1

a.set(12) # -> OK
a.bit_length() # -> return 4
a.count('h') # -> return None

a.set(3.14) # -> raise an error
```

## Functions

 a ```func``` can return a value to adapt the result. It can bee a lambda too.

### transform

 Please see [transform function](#all-types)

```python
# example
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
print(company.name) # -> "WORLDCOMPAGNY"
```

### set or compute

```python
# example
from stricto import Dict, Int, String

a=Dict({
    "b" : Int( default = 0, set=lambda o: o.c+1 ),
    "d" : Int( default = 0, set=lambda o: o.b+1 ),
    "c" : Int( ),
})

# "b" and "d" cannot be modified by hand. the are recalculated every time another value 
# change in the Dict.

a.b = 3 # -> raise an error

a.c = 2
print(a.b) # -> 3
print(a.d) # -> 4
```

### constraints

```python
# example
from stricto import Dict, Int, String



def check_pair(value, o): # pylint: disable=unused-argument
    """
    return true if pair
    """
    return not value % 2

a=Dict({
    "b" : Int( default = 0, constraint=check_pair ),        # check before setting
    "d" : Int( constraint=lambda value, o : not value % 2 ), # same as above, with a lambda
    "c" : Int( constraints=[ check_pair ] ),                # A list of constraints
})

a.b = 2 # OK
a.c = 3 # -> raise an error
```



### onchange

```python
# example
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
a.b = 3-1   # -> nothing displayed
```

### exists

A function wich must return ```True|False``` to say if this key exists.

```python
# example
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
    "gender" : String( default = 'Male', in=[ 'Male', 'Female' ]),
    "female_infos" : Dict(
        {
        "number_of_litter" : Int(default=0, required=True)
        # ... some other attributes

    }, exists=check_if_female )
})

a.set({ "name" : "Felix", "gender" : "Male" }
a.female_infos   # -> None
a.female_infos.number_of_litter = 2 # -> Raise an Error

a.gender = "Female"
a.female_infos.number_of_litter = 2 # -> Ok
a.female_infos # -> { "number_of_litter" : 2 }
```

## Tests

```bash
python -m unittest
```
