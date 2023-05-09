<div class="markdown-body">  

# Singleton Pattern  

객체의 인스턴스가 오직 1개만 생성되는 패턴을 의미한다.  

이를 구현하기 위해서는 다음과 같이 구현해야 한다.  
- `private 생성자`: 외부에서 생성자를 호출해서 객체를 생성할 수 없도록 한다.
- `static 인스턴스 변수`: 해당 클래스의 단일 인스턴스를 보유한 변수를 생성한다.  
- `생성 static 메서드`: 생성된 인스턴스를 가져오는 메서드를 만든다. 인스턴스가 없으면 인스턴스를 생성한다.  

위 내용으로 구현된 코드를 살펴보자.

```
public class Singleton {
    private static Singleton instance;

    private Singleton() {}

    public static Singleton getinstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```  
이정도도 괜찮지만, 사용했을 때 다음과 같은 **치명적인 문제점**이 발생한다.  
- 문제 1: 여러 Thread가 동시에 `getinstance()` 메서드에 접근한다면?
    - 결과: 여러 인스턴스가 생성될 수 있음.
- 문제 2: `Java Reflection API`를 활용해 private 생성자에 접근한다면?
    - 결과: 여러 인스턴스가 생성될 수 있음.
- 문제 3: 인스턴스를 `직렬화`한 다음 인스턴스로 `역직렬화` 한다면?
    - 결과: 여러 인스턴스가 생성될 수 있음.  

위와 같은 문제들을 보완한 몇가지 Singleton 패턴이 있다.  

순서대로, 차근차근 알아보도록 하자.

## Lazy Singleton  

```
Thread A:                       Thread B:
if (instance == null)           if (instance == null)
                                {
                                    instance = new LazySingleton();
                                }
instance = new LazySingleton();
```
우선 다이어그램을 보자.  

Thread A와 Thread B의 두 Thread에서 instance가 아직 **`null`일 때 동시에 `getinstance()` 메서드를 호출**한다면?

Thread A는 if 문을 먼저 실행하고 if 블록에 진입하여 **새 인스턴스를 생성**했지만...  
Thread A가 인스턴스를 반환하기 전, 

Thread B도 if 문을 실행하고, Thread A가 **생성한 이전 인스턴스를 덮어쓰는 LazySingleton의 새 인스턴스를 생성**했다면?

결과적으로, 두개의 인스턴스가 생성되어 단일 인스턴스에 대한 **Singleton 패턴의 요구 사항을 위반**하게 된다.

이것이 Lazy Initialization Singleton이 Thread로부터 안전하지 않고 **동시 환경에서 여러 인스턴스가 생성될 수 있는 이유**이다.

이 문제를 해결하려면 Thread-Safe Lazy Initialization Singleton 또는 Double-Checked Locking Singleton과 같은 다른 <u>Thread로부터 안전한 Singleton 패턴을 대신 사용</u>해야 한다.  

<br>  

### Thread-Safe Lazy Initialization Singleton  

```
Thread A:                               Thread B:
synchronized getinstance()  // Lock obtained by Thread A
{
    if (instance == null)   // Thread A creates instance
    {
        instance = new ThreadSafeLazySingleton();
    }
    // Thread A releases lock
    // and returns instance
    return instance;
}
                                    // Thread B is blocked
                                    // until Thread A releases the lock

                                    synchronized getinstance()  // Lock obtained by Thread B
                                        {
                                            // Thread B checks that instance is not null
                                            // and returns instance
                                            return instance;
                                        }

                                    // Thread B releases lock
```

Thread A는 `getinstance()` 메서드에 대한 **Lock을 획득하고 인스턴스가 존재하지 않으면 생성하고 인스턴스를 반환**한다.  
Thread A가 Lock을 해제할 때까지 **Thread B는 차단**된다.

Thread A가 Lock을 해제하면 Thread B는 Lock을 획득하고 인스턴스를 반환한다.  

<br>  

여기까지 이해했다면, 구현코드를 보자.  
기본 Singleton 코드와 차이는 없지만, `synchronized` 키워드를 사용하여 **여러 Thread가 동시에 접근하는 것을 금지**했다.
```
public class ThreadSafeLazySingleton {
    private static ThreadSafeLazySingleton instance;

    private ThreadSafeLazySingleton() {}

    public static synchronized ThreadSafeLazySingleton getinstance() {
        if (instance == null) {
            instance = new ThreadSafeLazySingleton();
        }
        return instance;
    }
}
```
<br>  

앞서 Lazy Initialization Singleton에서 발생할 수 있는 **동기화 관련 문제는 해결**했다.  
하지만, 메서드를 호출하기 위해서는 **Thread가 메서드를 종료할 때까지 접근할 수 없으며**, 이로 인해 **지연이 발생**하고 애플리케이션 성능에 영향을 줄 수 있다.

이를 해결할 수 있는 Double-Checked Locking Singleton 또는 Bill Pugh Singleton과 같은 패턴을 사용할 수 있다.  

<br>  

### Double Checked Locking Singleton  

```
Thread A                           Thread B

  +-----+                          +-----+
  |     |  getinstance()           |     |
  |     |------------------------->|     |
  |     |                          |  isNull(instance)
  |     |                          |----------------------->|
  |     |                          |     |
  |     |                          |   if (instance == null)
  |     |                          |   {
  |     |                          |       lock.acquire()
  |     |                          |       if (instance == null)
  |     |                          |       {
  |     |                          |           instance = new Singleton()
  |     |                          |       }
  |     |                          |       lock.release()
  |     |                          |   }
  |     |                          |     |
  |     |  return instance         |     |
  |     |<-------------------------|     |
  |     |                          |     |
  +-----+                          +-----+

```


앞서 Thread-Safe Lazy Initialization Singleton에서는 `getinstance()`에 대한 호출은 메서드에 대한 Lock을 획득하며 이는 Thread된 환경에서 <u>**성능 병목 현상**</u>이 발생 할 수 있다고 했다.    

그 이유는, Thread A가 Lock을 획득한 경우 Thread A가 Lock이 **해제할 때까지 Thread B가 차단**되기 때문이다.

DoubleCheckedLockingSingleton 구현에서 Lock은 `instance` 변수가 null인지 처음 확인할 때 **한 번만 실행 된다.**  

인스턴스가 아직 생성되지 않은 경우만 Lock이 획득된 다음 Singleton의 새 인스턴스를 생성하기 전에 instance 변수가 여전히 null인지 확인하기 위해 다시 확인합니다.  

구현코드를 살펴보자.  
```
public class DoubleCheckedLockingSingleton {
    private static volatile DoubleCheckedLockingSingleton instance;

    private DoubleCheckedLockingSingleton() {
        // private constructor
    }

    public static DoubleCheckedLockingSingleton getinstance() {
        if (instance == null) {
            synchronized (DoubleCheckedLockingSingleton.class) {
                if (instance == null) {
                    instance = new DoubleCheckedLockingSingleton();
                }
            }
        }
        return instance;
    }
}
```

인스턴스가 이미 생성되있는 경우 `getinstance()`에 대한 **후속 호출은 Lock을 획득할 필요가 없으므로** Thread가 많은 환경에서 성능을 향상시킬 수 있습니다.

<br>  

### Enum Singleton

```
       +-------------------------+           +----------------------+
       |         Client          |           |      Singleton       |
       +-------------------------+           +----------------------+
                    |                                    |
                    |                 +------------------|------------------+
                    |                 |                  |                  |
                    |                 |                  |                  |
                    |                 |       +----------|----------+       |
                    |                 |       |          |          |       |
                    |                 |       |          |          |       |
                    |                 |       |   Enum Singleton    |       |
                    |                 |       |          |          |       |
                    |                 |       |          |          |       |
                    |                 |       +----------|----------+       |
                    |                 |                  |                  |
                    |                 |                  |Creates Singleton |
                    |                 |                  |                  |
                    |                 |                  |                  |
        +-----------|-----------+     |                  |                  |
        |           V           |     |                  V                  |
+----------------------+        |     |          +-------------------+      |
|      Useless Code    |        |     |          |  Singleton Object |      |
+----------------------+        |     |          +-------------------+      |
                                |     |                                     |
                                +------+                                    |
                                                    
                                         (Eagerly Created at Enum Load Time)

```
Enum Singleton은 앞서 소개한 패턴에 비해 다음과 같은 장점이 있다.  
- `Thread 안정성`: Enum 값의 인스턴스는 JVM 내에 **하나만 존재하도록 보장**된다.
- `직렬화`: JVM에 의해 자동으로 직렬화 및 역직렬화되므로 역직렬화 후에도 **하나의 인스턴스만 존재**한다.
- `리플렉션`: Enum 값은 상수로 정의되므로 런타임에 **변경하거나 대체할 수 없다.**
- `단순성`: **구현이 간단**하다.  

위와 같이 장점이 너무나도 많지만, **치명적인 단점**도 존재한다.  

#### Enum Singleton의 문제는 지연 초기화가 될 수 없다는 것이다.

JVM에 의해 로드되는 즉시 **싱글톤 인스턴스가 생성**된다는 의미이다.  

클라이언트 코드에 실제로 싱글톤 인스턴스가 필요하지 않으면 이를 만드는 데 사용된 <u>**리소스가 낭비**</u>된다.

예를 들어 데이터베이스 연결이나 복잡한 데이터 구조와 같이 생성하는 데 많은 리소스가 필요한 싱글톤 객체를 생각해보자.  

열거형이 로드될 때 싱글톤이 무조건적으로 생성되지만 클라이언트 코드가 실제로 싱글톤을 사용할 필요가 없다면 해당 리소스는 낭비된다.
  
아래는 `Enum Singleton`을 구현한 예제 코드이다.
```
public enum EnumSingleton {
    instance;

    private String message = "Hello, world!";

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
```


대조적으로 Lazy Initialization Singleton 또는 Thread-Safe Lazy Initialization Singleton과 같은 다른 싱글톤 패턴은 지연 초기화를 허용한다.  

<br>  

### Bill Pugh Singleton
```
  Class Loader                 BillPughSingleton
       |                              |
       v                              v
  SingletonHelper (load)    private static Singleton instance = null;
       |                              |
       v                              v
  getinstance() (call)                |
       |                              |
       v                              v
  private static class SingletonHelper
  (load and initialize)
       |
       v
  instance = new Singleton()
```  
Bill Pugh Singleton은 다른 싱글톤 패턴에 비해 동기화 또는 이중 확인이 필요 없이 Thread로부터 안전한 방식으로 지연 초기화를 제공한다.  

이를 구현하기 위해서는 <u>**내부 클래스(inner Class)**</u>를 사용한다.  
우선, 코드를 보고나서 내부 클래스에 대해서 알아보자. 

```
public class BillPughSingleton {
    private BillPughSingleton() {};

    private static class SingletonHolder {
        private static final BillPughSingleton instance = new BillPughSingleton();
    }

    public static BillPughSingleton getinstance() {
        return SingletonHolder.instance;
    }
}
```
동작방식에 대해서 알아보자.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/87bcec31-cba1-4f33-aa0f-fdda29b1241e" alt="text" width="number" />
</p>  


클래스 로더는 `instance` 변수를 null로 초기화하는 BillPughSingleton 클래스를 로드한다.  

`getinstance()`가 호출되면 SingletonHelper 클래스의 초기화를 트리거한 다음 Singleton 클래스의 새 인스턴스로 instance 변수를 초기화한다. 

getinstance()에 대한 후속 호출은 단순히 이미 초기화된 instance 변수를 반환합니다.  

그렇다면, 어째서 내부 클래스를 사용하는 것일까?

내부 클래스는 요청 시, 즉 처음 사용될 때 **JVM(Java Virtual Machine)에 의해 로드된다.**  

이를 `지연 로딩` 또는 `지연 초기화`라고 한다.   

외부 클래스가 로드되면 내부 클래스는 **실제로 필요할 때까지 로드되지 않는다.** 이렇게 하면 프로그램의 초기 시작 시간과 메모리 사용량을 줄이는 데 도움이 될 수 있다.
