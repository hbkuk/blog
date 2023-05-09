<div class="markdown-body">  

# Function<T, R> interface  

![Function](https://github.com/hbkuk/blog/assets/109803585/e1d109b8-20df-4783-a76c-91adce8f43e2)


위 사진은 `Function<T,R>` 인터페이스에 대한 설명이다.  

`Function<T,R>` 인터페이스에서는 `apply` 추상 메서드가 존재한다.  

인자로 `T`를 받아 `R`을 리턴한다.  

기본적인 내용이다. 앞으로 설명할 예제에는 람다식이 존재한다.  

그렇다면, 람다식(Lambda Expression)에 대해서 알고 가자  

<br>  

### 람다식(Lambda Expression)

람다식(Lambda Expression)이란 함수를 하나의 식(expression)으로 표현한 것이다.  
함수를 람다식으로 표현하면 메소드의 이름이 필요 없기 때문에, 람다식은 이름이 없는 함수인 익명 함수(Anonymous Function)의 한 종류라고 볼 수 있다.  

기존의 메서드를 선언하는 방식과 람다 방식의 차이를 코드로 살펴보자.
  
```
// 기존의 방식
반환티입 메소드명 (매개변수, ...) {
	실행문
}

// 예시
public String hello() {
    return "Hello World!";
}
```

다음은 람다 방식으로 구현한 예제 코드이다.  
메서드명이 생략되며, 괄호() 와 화살표-> 기호를 이용해 함수를 선언한다.

```
// 람다 방식
(매개변수, ... ) -> { 실행문 ... }

// 예시
() -> "Hello World!";
```  
 
<br>  

## Function<T, R> interface를 사용해서 요구사항 해결


### 정수 입력을 받아 출력으로 2를 곱한 입력을 반환하는 람다 함수를 구현해보자.

```
Function<Integer, Integer> multiplyByTwo = x -> x * 2;
```  

- 테스트 코드  

```
@ParameterizedTest
@CsvSource(value = {"1:2", "5:10", "50:100"}, delimiter = ':')
void multiplyByTwo(int number, int result) {
    // given
    Function<Integer, Integer> multiplyByTwo = x -> x * 2;

    //when
    int acture = multiplyByTwo.apply(number);

    //thenm
    assertEquals(acture, result);
}
```  
<br>  

### 정수 목록을 입력으로 받아 목록에 있는 모든 짝수의 합을 반환하는 함수를 구현해보자.  


```
Function<List<Integer>, Integer> sumEvenNumbers = nums -> {
    return nums.stream()
                .filter(number -> number % 2 == 0)
                .mapToInt(Integer::intValue)
                .sum();
};
```  

- 테스트 코드  

```
@Test
@DisplayName("Function API를 활용한 모든 짝수의 합을 반환")
void sum_of_even_numbers2() {
    // given
    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

    //when
    Function<List<Integer>, Integer> sumEvenNumbers = nums -> {
        return nums.stream()
                    .filter(number -> number % 2 == 0)
                    .mapToInt(Integer::intValue)
                    .sum();
    };

    //then
    assertEquals(sumEvenNumbers.apply(numbers), 30);
}
```  

### 문자열 목록을 입력으로 받고 입력 목록에 있는 모든 문자열의 길이 목록을 반환하는 함수 구현  

```
Function<List<String>, Integer> sumStringLength = strings -> {
    return strings.stream()
            .map(value -> value.length())
            .mapToInt(Integer::intValue)
            .sum();
};
```  

- 테스트 코드  


```
@Test
@DisplayName("문자열 목록을 입력받고, 모든 문자열의 길이를 반환")
void sum_of_all_String_length() {
    // given
    List<String> fruits = Arrays.asList("apple", "peach", "waterMelon", "strawberry");

    //when
    Function<List<String>, Integer> sumStringLength = strings -> {
        return strings.stream()
                .map(value -> value.length())
                .mapToInt(Integer::intValue)
                .sum();
    };

    //then
    assertEquals(sumStringLength.apply(fruits), 30);
}
```  

### 정수 목록을 입력으로 받아 목록의 최대값을 반환하는 함수를 구현  

```
Function<List<Integer>, Integer> find_max_value = nums -> {
    return nums.stream()
            .mapToInt(x -> x)
            .max()
            .orElseThrow(NoSuchElementException::new);
};
```  

- 테스트 코드  

```
@Test
@DisplayName("정수 목록을 입력으로 받아 목록의 최대값을 반환")
void find_max_value() {
    // given
    List<Integer> numbers = Arrays.asList(100, 10, 500, 1000, 30, 0, -1, 400);

    // when
    Function<List<Integer>, Integer> find_max_value = nums -> {
        return nums.stream()
                .mapToInt(x -> x)
                .max()
                .orElseThrow(NoSuchElementException::new);
    };

    // then
    assertEquals( find_max_value.apply(numbers), 1000);
}
```  

### 문자열 목록을 입력으로 받아 문자 "A"로 시작하는 모든 문자열 목록을 반환하는 함수를 구현

```
BiFunction<List<String>, String, List<String>> find_startswith_s = (strings, targetString) -> {
    return strings.stream()
                .filter(string -> string.toLowerCase().startsWith(targetString.toLowerCase()))
                .collect(Collectors.toList());
};
```  

- 테스트 코드

```
@Test
@DisplayName("문자열 목록을 입력으로 받아 소문자 's'로 시작하는 모든 문자열 목록을 반환")
void find_startswith_s() {
    // given
    List<String> fruits = Arrays.asList("apple", "peach", "waterMelon", "strawberry","sugarApple");

    // when
    BiFunction<List<String>, String, List<String>> find_startswith_s = (strings, targetString) -> {
        return strings.stream()
                    .filter(string -> string.toLowerCase().startsWith(targetString.toLowerCase()))
                    .collect(Collectors.toList());
    };

    // then
    assertThat(find_startswith_s.apply(fruits, "s"))
                .contains("strawberry")
                .contains("sugarApple")
                .doesNotContain("apple");
}
```







</div>