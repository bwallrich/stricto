# Stricto

Strict Dict with schema validation embedded

## Installation

> [!TIP]
> Soon


## Quick start

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

```python
# example
from stricto import int

a = Int()
a.set(22) # -> ok
a.set(23.1) # raise an error
a.set("the number of the beast") # raise an error

# WARNING
a = "the number of the beast" # works ! the affectation of "a" change. Now it is a string. This is python.
```

## json

use ```.getvalue()``` to extract a dict from a Dict and do th json.dumps like usual.


```python
# example
from stricto import int, List, String, Dict, Error
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
