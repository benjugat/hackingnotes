------
title: Insecure Deserialization
category: Web
order: 22
---

**Serialization** is the process of converting complex data structures, such as objects and their fields, into a "flatter" format that can be sent and received as a sequential stream of bytes.
**Deserialization** is the process of resptoring this byte stream to fully functional replica of the original object, in the exact state as when it was serialized.

![](/hackingnotes/images/deserialization-diagram.jpg)

Be aware that when working with different programming languages, serialization may be referred to as *marshalling* (Ruby) or *pickling* (Python). These terms are synonymous with "serialization" in this context. 

**Insecure deserialization** is when user-controllable data is deserialized by a website. This potentially enables an attacker to manipulate serialized objects in order to pass harmful data into the application code. 

# Identifying serialized objects

Serialized data can be identified relatively easily if you know the format that different languages use.

## PHP serialization format

PHP uses a mostly human-readable string format, with letters representing the data type and numbers representing the length of each entry. For example, consider a User object with the attributes: 

```
$user->name = "carlos";
$user->isLoggedIn = true;
```

When serialized, this object may look something like this: 

```
O:4:"User":2:{s:4:"name":s:6:"benjugat"; s:10:"isAdmin":b:0;}
```

This can be interpreted as follows: 

* `O:4:"User"` - An object with the 4-character class name "User"
* `2` - the object has 2 attributes
* `s:4:"name"` - The key of the first attribute is the 4-character string "name"
* `s:6:"benjugat"` - The value of the first attribute is the 6-character string "benjugat"
* `s:10:"isAdmin"` - The key of the second attribute is the 10-character string "isAdmin"
* `b:0` - The value of the second attribute is the boolean value false

The native PHP methods for serialization are `serialize()` and `unserialize()`.

## Java serialization format

Some languages, such as Java, use binary serialization formats. This is more difficult to read, but you can still identify serialized data if you know how to recognize a few tell-tale signs.

Java objects always begin with the same bytes, which are encoded as `ac ed` in hexadecimal or `rO0` in Base64.

Any class that implements the interface `java.io.Serializable` can be serialized and deserialized. If you have source code access, take note of any code that uses the `readObject()` method, which is used to read and deserialize data from an `InputStream`. 


# Manipulating serialized objects

## Modifying object attributes

We can modify the attributes of an object such as the example shown before to obtain privilege rights such as admin.

```
O:4:"User":2:{s:4:"name":s:6:"benjugat"; s:10:"isAdmin":b:0;}
```

So the boolean attribute `isAdmin` can me modified to `true`.

```
O:4:"User":2:{s:4:"name":s:6:"benjugat"; s:10:"isAdmin":b:1;}
```

## Modifying data types

We've seen how you can modify attribute values in serialized objects, but it's also possible to supply unexpected data types.

**PHP-based logic** is particularly vulnerable to this kind of manipulation due to the behavior of its **loose comparison operator (==)** when comparing different data types. It is also known as **PHP type juggling**.

![](/hackingnotes/images/phpstrict.png)

![](/hackingnotes/images/phploose.png)


In PHP 8 and later, the `0 == "Example string"` comparison evaluates to `false` because strings are no longer implicitly converted to `0` during comparisons. As a result, this exploit is not possible on these versions of PHP.

The behavior when comparing an alphanumeric string that starts with a number remains the same in PHP 8. As such, `5 == "5 of something"` is still treated as `5 == 5`.

> **Note**: Remember to update any type labels and lenght indicators in the serialized data.

# Magic methods

Magic methods are a special subset of methods that you do not have to explicitly invoke. Instead, they are invoked automatically whenever a particular event or scenario occurs. Magic methods are a common feature of object-oriented programming in various languages. They are sometimes indicated by prefixing or surrounding the method name with double-underscores. 

One of the most common examples in PHP is `__construct()`, which is invoked whenever an object of the class is instantiated, similar to Python's `__init__`. 

Magic methods are widely used and do not represent a vulnerability on their own. But they can become dangerous when the code that they execute handles attacker-controllable data, for example, from a deserialized object. This can be exploited by an attacker to automatically invoke methods on the deserialized data when the corresponding conditions are met. 

Most importantly in this context, some languages have magic methods that are invoked automatically during the deserialization process. For example, PHP's `unserialize()` method looks for and invokes an object's `__wakeup()` magic method. 

# Injecting arbitrary objects

It is possible to exploit insecure deserialization by simply editing the object supplied by the website. However, injecting arbitrary object types can open up many more possibilities.

Deserialization methods do not typically check what they are deserializing. This means that you can pass in objects of any serializable class that is available to the website, and the object will be deserialized. This effectively allows an attacker to create instances of arbitrary classes. The fact that this object is not of the expected class does not matter. The unexpected object type might cause an exception in the application logic, but the malicious object will already be instantiated by then.

