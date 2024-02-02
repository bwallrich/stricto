# Stricto

Strict Dict with schema validation embedded

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


print(a.num) # 22
a.name = 666 # -> raise a typeError
print (a) # print like a dict

a.nicknames.append(666) # -> raise a typeError
a.nicknames.append("Eddy")
a.nickname[1] # -> Eddy

b=a # b is a reference on a
c=a.copy() # c is a different object : c is a copy

c == b # return True
b.nicknames.pop()
c == b # return False
```

## Basic types

All basic calss from python are implemented in ```stricto```.

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
from stricto import Int

a = Int()
a.set(22) # -> ok
a.set(23.1) # raise an error
a.set("the number of the beast") # raise an error

# WARNING
a = "the number of the beast" # works ! the affectation of "a" change. Now it is a string. This is python.
```

## json


use ```.getvalue()``` to extract a dict from a Dict and do the *json.dumps* like usual.


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

sa = json.dumps(a.getValue()) # json dumps 
b.set( json.loads(sa) ) 
b == a # return True
```

## Types

### All types

available options for all types ares :

| Option | Default | Description |
| - | - | - |
| ```notNull=True\|False``` | False | cannot be None or inexistent |
| ```required=True\|False``` | False | similar to ```notNull``` |
| ```description="whatever you want"``` | None | a description of this object |
| ```default=666``` | None | the default value |
| ```in=[ 1, 2, 3, 5 ]\|func``` | None | the value must be one of those elements. See [in function](#in-or-union) for mor details |
| ```union=[ 1, 2, 3, 5 ]\|func``` | None | similar to ```in```  |
| ```transform=func``` | None | a [function](#functions) to [transform](#transform) the value before setting it |
| ```constraint=func``` | None | a [function](#functions) to check the value before setting it |
| ```constraints=[func]``` | None | a list of [functions](#functions) to check the value before setting it |
| ```onchange=func``` | None | a [function](#functions) to trigger when the value change |
| ```onChange=func``` | None | similar to ```onchange``` |
| ```set=func``` | None | a read only value, calculated from other .See [set or compute function](#set-or-compute) |
| ```compute=func``` | None | similar to ```set``` |

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

newAge = client.age+1 # -> raise an Error (newAge is implicitly an Int( min=21, max=120))
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

```In()``` is not a type, but an **union**

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

 a ```func``` can return a value to adapt the result

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

### in or union

Please see [in or union function](#all-types)


```python
# example
from stricto import Dict, Int, String

def build_union(value, o):
    """
    return the size in month for babies or for adult 
    (a stupid example)

    value : the current value given (32 in this example).
    o     : the full object
    """
    if o.age < 2:
        return [ 3, 6, 12, 18, 24 ]
    return [ 32, 36, 38, 40 ]

a=Dict({
    "age" : Int(),
    "size" : Int( in=build_union )
})

a.set{ "age" : 1, "size" : 32 } # -> raise an error
a.set{ "age" : 3, "size" : 32 } # -> Ok
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

a.b = 3 # -> raise an error

a.c = 2
print(a.b) # -> 3
print(a.d) # -> 4
```

## Tests

```bash
cd tests/
python -m unittest -v
```