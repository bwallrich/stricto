#! /bin/env python3
#
import unittest
import context

from stricto import List, Int, String, Error


        
def pair_only(value, o):
    return value+1 if value % 2 else value

def check_pair(value , o):
    return False if value % 2 else True


class test_List(unittest.TestCase):

    def test_Error_Type(self):
        a=List( Int() )
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception._message, 'Must be a list')
        with self.assertRaises(Error) as e:
            a.set([ "toto" ])
        self.assertEqual(e.exception._message, 'Must be a int')
        a.set([ 11 ])
        self.assertEqual(a[0], 11)

    def test_none(self):
        a=List( Int(), notNull=True )
        a.set([])
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception._message, 'Cannot be empty')
        a=List( Int() )
        a.set(None)
        self.assertEqual(a, None)

    def test_none_append(self):
        a=List( Int() )
        a.set(None)
        self.assertEqual(a, None)
        a.append(12)
        self.assertEqual(a[0], 12)
        
    def test_none_extend(self):
        a=List( Int() )
        a.set(None)
        self.assertEqual(a, None)
        a.extend([ 12, 32 ])
        self.assertEqual(a[0], 12)

    def test_pop(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        b=a.pop()
        self.assertEqual(b, 32)
        self.assertEqual(len(a), 1)

    def test_pop_index(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        b=a.pop(0)
        self.assertEqual(b, 12)
        self.assertEqual(len(a), 1)

    def test_del(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        del a[0]
        self.assertEqual(a[0], 32)
        self.assertEqual(len(a), 1)

    def test_remove(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        with self.assertRaises(ValueError) as e:
            a.remove(44)
        self.assertEqual(e.exception.args[0], 'list.remove(x): x not in list')
        a.remove(32)
        self.assertEqual(a[0], 12)
        self.assertEqual(len(a), 1)

    def test_setItem(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 12)
        a[0]=22
        self.assertEqual(a[0], 22)

    def test_setItem_slice(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 12)
        a[0:1]=[ 22, 44 ]
        self.assertEqual(a[0], 22)
        self.assertEqual(a[1], 44)
        a[0:3]=[ 22, 44, 66, 88 ]
        self.assertEqual(len(a), 4)
        self.assertEqual(a[0], 22)
        self.assertEqual(a[3], 88)

    def test_insert(self):
        a=List( Int() )
        a.set([ 12, 32 ])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 12)
        a.insert(0, 23)
        self.assertEqual(len(a), 3)
        self.assertEqual(a[0], 23)
        self.assertEqual(a[1], 12)
        self.assertEqual(a[2], 32)

    def test_insert_none(self):
        a=List( Int() )
        a.insert(0, 23)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 23)

        a=List( Int() )
        a.insert(10, 23)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 23)

    def test_sort(self):
        a=List( String() )
        a.set(['Ford', 'BMW', 'Volvo'])
        a.sort()
        self.assertEqual(a[0], 'BMW')
        self.assertEqual(a[2], 'Volvo')
        a.sort(reverse=True)
        self.assertEqual(a[0], 'Volvo')
        self.assertEqual(a[2], 'BMW')

    def test_add(self):
        a=List( String() )
        a.set(['Ford', 'BMW', 'Volvo'])
        b = a + [ "Renault" ]
        self.assertEqual(len(b), 4)
        self.assertEqual(type(b), List)

    def test_ref(self):
        a=List( String() )
        a.set(['Ford', 'BMW', 'Volvo'])
        b = a
        b[1]='Renault'
        self.assertEqual(a[1], 'Renault')
        self.assertEqual(b[1], 'Renault')


    def test_copy(self):
        a=List( String() )
        a.set(['Ford', 'BMW', 'Volvo'])
        b = a.copy()
        b[1]='Renault'
        self.assertEqual(a[1], 'BMW')
        self.assertEqual(b[1], 'Renault')