# Why Override equals(), hashCode() Method?  

<br>

일반화하는 것은 아니지만,  

대부분의 웹 개발자라면, **`equals()` 메서드를 재정의하는 이유**에 대해서 알고 있을 것이다.  

이부분에 대해서 정리해보자.  

<br>

Java에서 모든 클래스는 **`Object` 클래스를 상속**받는다. 

Object 클래스의 메서드 중 **`equals()` 메서드가 정의**되어 있으며,  
이는 모든 클래스가 해당 메서드를 사용할 수 있다는 의미이다. 

그렇다면, Object 클래스의 equals() 메서드에 대해서 알고가자.  

<br>

 Object Class 
- `boolean equals(Object o)`  

<br>

이 메서드는 **두 개의 참조 주소를 기반으로 객체가 동일한지 여부를 확인**하는 데 사용된다.  

 두 객체가 동일한 경우 **true**를 반환하고 그렇지 않으면 **false**를 반환한다.  

<br>

**즉, 두 객체가 동일한 참조를 공유하는 경우에만 동일한 것으로 간주된다.**  

---

예를 들어, 다음과 같이 **Car 클래스가 있고 name 이라는 필드**를 가지는 경우

```
class Car {
    private final String name;

    public Car(String name) {
        this.name = name;
    }
}
```

다음과 같이 두 객체를 생성했을 때, 두 객체를 equals() 메서드로 비교해보자.

두 객체는 동일할까?

```
Car carA new Car("K5");
boolean acture = carA.equals(new Car("K5"));
```

필드 name은 같지만, 참조 주소값이 다르기 때문에 다르다.  

객체를 생성하면 해당 객체를 가르키는 **예측하기 어려운 참조 주소 값이 할당**된다. 

<br>

만약, 필드의 name이 같은 경우 동일한 객체로 판단하고 싶다면 어떻게 해야할까?  

<br>

상위 클래스(Object)의 메서드인, **`equals()` 메서드를 재정의(Override)** 하면된다. 

```
@Override
public boolean equals(Object o) {
    if (this == o)
        return true;
    if (o == null || getClass() != o.getClass())
        return false;
    Car car = (Car) o;
    return Objects.equals(name, car.name);
}
```  

현재, 위와 같이 `equals()` 메서드만 재정의 해두었다.  

<br>

그렇다면, **Car 객체의 필드 name만 비교해서, 같으면 true, 틀리면 false를 반환**한다.  

아래 테스트는 성공한다.  

```
@Test
void equals_car() {

    // given
    String carName = "K5";

    // when
    Car k5 = new Car(carName);

    // then
    assertThat(k5).isEqualTo(new Car(carName));
}
```  

List에 넣어서, size를 확인해보자.  

당연히 2일 것이다.  

```
@Test
void list_add_car() {

    // given
    List<Car> cars = new ArrayList<>();

    // when
    cars.add(new Car("k5"));
    cars.add(new Car("k5"));

    // then
    assertThat(cars).hasSize(2);
}
```  

그렇다면 **중복을 허용하지 않는 Set 인터페이스**를 구현한 **HashSet 클래스**를 만들어서 넣어보자.  

```
@Disabled("사이즈를 1을 예상하지만, 2가 나오는 실패하는 테스트")
@Test
void set_add_car() {

    // given
    Set<Car> cars = new HashSet<>();

    // when
    cars.add(new Car("k5"));
    cars.add(new Car("k5"));

    // then
    assertThat(cars).hasSize(1);
}
```  

우리는 Set 컬렉션의 사이즈를 1을 예상해서 테스트를 실행했다.  

테스트는 실패했다.  

<br>

무슨 문제일까?  

<br>

위에서 **Set 인터페이스를 구현한 hashSet 클래스**를 만들었다.  

HashMap, HashSet, HashTable 등의 클래스는 객체가 논리적으로 같은지 비교할 때 다음과 같은 과정을 거친다.  

<br>

![동일한지 비교](https://github.com/hbkuk/blog/assets/109803585/82994172-aef3-425f-81a5-eec0a5888ed3)  

1. 두 객체의 `hashCode()` 값을 비교
    - 같으면 true
    - 다르면 false
2. `equals()` 메서드를 이용한 비교
    - 같으면 true
    - 다르면 false  

<br>

두가지의 비교에서 true라는 결과가 확인되었을 때만, **동등한 객체라고 판단**한다.  

<br>

그렇다면, 모든 클래스가 상속하는 **Object 클래스의 `hashCode()` 메서드**는 어떻게 동작할까?  

<br>

**객체의 참조 주소를 기반으로 hashCode를 생성한다.**  

그렇다면, 우리는 다시 Car클래스를 살펴보자.  

```
class Car {
    private final String name;

    public Car(String name) {
        this.name = name;
    }
}
```

필드 name이 동일한 두 객체가 동일한 hashCode를 가질려면 어떻게 재정의해주면 될까?

필드 name으로 hash 코드가 생성되도록 재정의 해주면된다.

```
@Override
public int hashCode() {
    return Objects.hash(name);
}
```

그렇다면, 아래 테스트는 성공할 것이다.  

```
@Test
void set_add_car() {

    // given
    Set<Car> cars = new HashSet<>();

    // when
    cars.add(new Car("k5"));
    cars.add(new Car("k5"));

    // then
    assertThat(cars).hasSize(1);
}
```  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/cd63bdb6-da78-4f9d-bc6c-25330353bda6" alt="text" width="number" />
</p>

이렇게 `equals()`, `hashCode()` 를 왜 재정의를 해야하는지 알아봤다.  

지금까지 대충... 이럴 것이다 라는 마음으로 재정의해서 사용했다.  

이 글을 쓴 시점에서는 누군가 물어보면 말할 정도로 이해했다.  

긴 글을 읽어주셔서 감사드린다.  








