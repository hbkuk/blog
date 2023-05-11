<div class = "markdown-body">

# Comparable과 Comparator 인터페이스  

우선, 사전적인 의미부터 알고가자.

- `Comparable<T>` 인터페이스
    - `int compareTo(T o)`: **해당 객체와 전달된 객체의 순서를 비교**함.  

<br>  

Java에서는 같은 타입의 인스턴스를 서로 비교해야만 하는 클래스들은 모두 **Comparable 인터페이스를 구현**하고 있다.  

따라서, Boolean을 제외한 래퍼 클래스나, String, Time, Data와 같은 클래스의 인스턴스는 모두 **정렬이 가능**하다.  

- `Comparator<T>` 인터페이스
    - `int compare(T o1, T o2)`: **전달된 두 객체의 순서를 비교**함.  

<br>  

Comparable 인터페이스와 같이 **객체를 정렬**하는 데 사용되는 인터페이스이다.  

두 인터페이스의 추상 메서드를 구현하는 이유는 오로지 <u>**객체를 비교할 수 있게 만드는 것**</u>이다.  

<br>

**무슨말일까?**  

<br>

primitive 타입의 실수 변수(byte, int, double 등등..)의 경우 **부등호를 갖고 쉽게 두 변수를 비교가 가능**하나,

커스텀 객체를 서로 비교한다고 생각해보자.  

<br>  

**예를 들면, 키와 몸무게를 가지고 있는 `Student`(학생) 클래스가 있다고 가정해보자.**  


```
public class Student {

    private int height;
    private int weight;

    public Student(int height, int weight) {
        this.height = height;
        this.weight = weight;
    }

    public int getHeight() {
        return height;
    }

    public int getWeight() {
        return weight;
    }
}
```  

```
Student a = new Student(170 ,60)
Student a = new Student(172 ,58)
```  

위 a와 b 두 객체를 어떻게 비교할 것인가?  

<br>  

누군가 정해주지 않는 이상 이 두 객체를 비교할 수 없다.  

그러므로, 키와 몸무게 중 어떤 항목을 기준으로 **대소관계를 판단**할지 정해줘야한다.  

<br>

(물론, 이를 비교할 메서드를 생성할 순 있지만, 이렇게 안하는 이유는 잠시 후 설명한다.)  

<br>

이러한 상황에서 `Comparable`과 `Comparator` 인터페이스가 유용하게 사용된다.  

우선 집고 넘어가야 하는 부분이 있다.  

- Comparable은 **자기 자신과 매개변수의 객체를 비교**한다.
- Comparator는 **두 매개변수를 서로 비교**한다.  

<br>


먼저 `Student` 클래스에서 `Comparable`을 구현해보자.  

```
public class Student implements Comparable<Student> {

    private int height;
    private int weight;

    public Student(int height, int weight) {
        this.height = height;
        this.weight = weight;
    }

    @Override
    public int compareTo(Student other) {
        return this.height - other.height;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Student student = (Student) o;
        return height == student.height && weight == student.weight;
    }

    @Override
    public int hashCode() {
        return Objects.hash(height, weight);
    }
}
```  

`Comparable` 인터페이스를 사용하려면 추상 메서드인 `compareTo()` 메서드를 구현해야 한다.  

<br>  

여기서는 우선 height를 기준으로 비교하고자 한다.  

위에서 `compareTo()` 메서드의 return 값이 `this.height - other.height`인 이유에 대해서 궁금할 수 있다.

이 후 설명하게 될 정렬과의 관계를 설명할 때 자세히 설명한다.  

<br>  

간략하게 설명하자면, 정렬(`Arrays.sort()`, `Collections.sort()` 메서드)을 할때 **두 수를 비교해서 위치교환**이 이루어진다는 것이다. 

즉, **선행 요소**와 **후행 요소**를 비교하게 되는데, 단지 **크냐, 같냐, 작냐**를 확인하고 위치교환이 이루어진다.  

- return -> 양수: 자신보다 큰 숫자
- return -> 0: 자신이랑 같은 숫자
- return -> 음수: 자신보다 작은 숫자  

우선, **자기 자신을 기준으로 매개변수의 값과 비교한 후 반환**한다고 이해하자.  

아래 테스트는 성공한다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/2ddb034b-73d0-4091-afaa-0123e7105214" alt="text" width="number" />
</p>  

<br>  

### Comparator\<T>  

위에서 본 `Comparable`과 비슷하면서도 다르다.

자기 자신이 아닌 **두 개의 파라미터를 서로 비교**하는 것이다. 

`Comparator` 인터페이스는 다음과 같이 추상 메서드인 `compare()` 메서드를 구현해야한다.

```
public class Student implements Comparator<Student> {

    private int height;
    private int weight;

    public Student(int height, int weight) {
        this.height = height;
        this.weight = weight;
    }

    public int getHeight() {
        return height;
    }

    public int getWeight() {
        return weight;
    }

    @Override
    public int compare(Student studentA, Student studentB) {
        return studentA.getWeight() - studentB.getWeight();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Student student = (Student) o;
        return height == student.height && weight == student.weight;
    }

    @Override
    public int hashCode() {
        return Objects.hash(height, weight);
    }
}

```  

<br>  

두 개의 파라미터를 서로 비교한다고?  

코드를 보면서 살펴보자.  

```
class StudentTest {
    @Test
    void compare_student() {

        // given
        Student kim = new Student(100, 200);
        Student hong = new Student(200, 300);
        Student hwang = new Student(150, 300);

        // when
        int flag = kim.compare(hong, hwang);

        // then
        assertThat(flag > 0).isTrue();
    }
}
```  

여기서 `kim`은 `hong`과 `hwang`을 비교하고, **자기 자신은 해당 과정에서 아무런 영향을 끼치지 않는다.**  

물론, `kim` 객체의 `compare()` 메서드를 통해 비교하지만, `kim` 객체의 값과는 아무런 관련없이 **두 객체의 비교 값**을 반환한다.  

<br>

이또한, 다음과 같이 자신과 다른 객체를 비교할 수 있다.  

이 부분은 되게 어색하다.  

```
int flag = kim.compare(kim, hong);
```  

두 객체를 비교를 위해서 하나의 객체를 생성하는.. 메모리를 낭비하는 셈이다.  

우리는 이럴때, 이름이 없는 클래스인, `익명 클래스`를 활용할 수 있다.  

우선 `Student` 클래스를 아무것도 구현하지 않는 형태로, 다음과 같이 변경한다.  

```
public class Student {

    private int height;
    private int weight;

    public Student(int height, int weight) {
        this.height = height;
        this.weight = weight;
    }

    public int getHeight() {
        return height;
    }

    public int getWeight() {
        return weight;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Student student = (Student) o;
        return height == student.height && weight == student.weight;
    }

    @Override
    public int hashCode() {
        return Objects.hash(height, weight);
    }
}
```  

<br> 
다음과 같이 익명 클래스를 정의하고, 사용할 수 있다.  

이를 통해 Student 클래스는 `Comparator` 인터페이스를 구현할 필요가 없어진다.  

```
class StudentTest {

    @Test
    void compare_student() {

        Comparator<Student> comp = new Comparator<Student>() {
            @Override
            public int compare(Student studentA, Student studentB) {
                return studentA.getWeight() - studentB.getWeight();
            }
        };

        // given
        Student kim = new Student(100, 200);
        Student hong = new Student(200, 300);

        // when
        int flag = comp.compare(kim, hong);

        // then
        assertThat(flag < 0).isTrue();
    }
}
```  

<br>

### Comparable, Comparator과 정렬과의 관계  

Java에서의 정렬은 특별한 정의가 되어있지 않는 한 '**오름차순**'을 기준으로 한다.

따라서, `Arrays.sort()`와 `Collections.sort()` 모두 기본적으로 **오름차순을 기준으로 정렬**된다는 것이다.  

위에서 언급했지만, **두 원소를 비교하는 정렬 알고리즘**을 사용하게 된다.  

<br>

선행 요소가 1이고, 후행요소 10이면 비교했을때는 -9라는 **음수값**이 나온다.

따라서, 선행 원소가 후행원소보다 **작다는 결론**이 나오게 된다.

그렇다면, 순서는 그대로 유지하면된다.  

<br>

만약, 선행 원소가 후행 원소보다 크다면? **두 원소의 위치**를 바꿔야한다.  

앞서 primitive type의 경우 이미 대소 비교가 가능하지만, 객체를 정렬하고자 한다면 너무나 당연히도 두 요소를 비교하기 위해서는 Comparable을 통한 `compareTo()` 혹은, Comparator을 통한 `compare()` 메소드를 활용하여 두 객체의 대소 비교를 한다는 것이다.  

다음 사진은 `Arrays.sort()` 메소드에서의 정렬 알고리즘인 `Merge Sort` 중 일부분이다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/bf6e9927-f265-420a-964d-9b2114ed9705" alt="text" width="number" />
</p>  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/3463bd92-4533-4a82-80b0-5d3cb81962e5" alt="text" width="number" />
</p>  
</div>