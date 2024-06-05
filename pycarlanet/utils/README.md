# utils decorators

## DecoratorSingleton
singleton with @, access to instance using Class.instance
```python
@DecoratorSingleton
class MySingleton:
    def __init__(self):
        ...

MySingleton()
MySingleton.instance

```

## InstanceExist(cls)
check with simple @ if the singleton class is instantiated
```python
@DecoratorSingleton
class MySingleton:
    def __init__(self):
        ...

@InstanceExist(MySingleton)
def takeInstance():
    return MySingleton.instance

try:
    print(f"retireved {takeInstance()}")
except Exception as e:
    print(f"error {e}")

MySingleton()

try:
    print(f"retireved {takeInstance()}")
except Exception as e:
    print(f"error {e}")
```
```
out:
    'error Violated prerequisites of method 'takeInstance' -> instance of singleton class 'DecoratorSingleton' do not exist'
    'retireved <__main__.MySingleton object at 0x77c1ec2bf5e0>'
```