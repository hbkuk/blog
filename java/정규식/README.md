<div class="markdown-body">  

# 정규식(정규표현식)  
요구사항에 따른 개발을 진행하다보면 **사용자로부터 입력한 값을 검증**하거나,  
입력한 값으로부터 **특정 부분을 추출하는 상황**이 빈번히 발생한다.  

예를 들면, 요구사항은 다음과 같다.  
**좌표 정보는 괄호"(", ")"로 둘러쌓여 있으며 쉼표(,)로 x값과 y값을 구분한다.**  
- "(1, 10)"
    - x: 1
    - y: 10
- "(5, 20)"
    - x: 5
    - y: 20
- "(3, 5)"
    - x: 3
    - y: 5  
<br>  
 
java.lang.String 클래스의 split(), replaceALl() 등과 같이 문자열을 다루는 메서드를 사용해서 처리할 수도 있지만...  
java.util.regex 패키지에서 제공하는 **Pattern 클래스와 Matcher 클래스**를 사용하면 이를 해결해 보자.

### Pattern 클래스와 Matcher 클래스  

우선, 각 클래스에서 제공하는 메서드에 대해서 살펴보자.  

#### Pattern 클래스
- compile(String regex): 정규표현식으로부터 **pattern을 생성**(컴파일이라고 함.)
- matcher(CharSequence input): 입력된 문자열로부터 패턴을 찾는 **Matcher 객체 생성**
- pattern(): 컴파일된 정규표현식을 **String 타입으로 반환**
- matches(String regex, CharSequence input): **문자열이 정규식과 완벽히 일치하는 확인**  

#### Matcher 클래스
- matcher(): **문자열이 패턴과 일치**하는지 확인
- lookingAt(): **문자열이 패턴으로 시작**하는지 확인
- find(): **문자열에서 패턴을 찾음**
- find(int start): **start 위치에서부터 패턴을 찾음**
- group(): 패턴과 일치(매칭)되는 **그룹을 반환**
- group(int group): 패턴과 일치(매칭)되는 그룹 중 **번호에 해당하는 그룹을 반환**  

<br>  
우선, 좌표를 추출하기 위해서 정규표현식을 만들어보자.  

`String regex = "\\((\\d+),(\\d+)\\)";`  

각각의 문자가 어떤 의미인지 다음과 같이 설명한다.

- `\\(`: **여는 괄호**를 찾는다. 
    - 백슬래시는 여는 괄호의 의미를 이스케이프하는 데 사용.
- `(\\d+)`: **하나 이상의 숫자(0-9)와 일치시키고, 그룹을 만듬**.
    - `\\d`는 0에서 9까지의 숫자와 일치하는 특수 문자를 의미.
    - `+`는 하나 이상을 의미.
    - 백슬래시는 정규식에서 d 문자의 의미를 이스케이프하는 데 사용.
- `,`: **쉼표 문자와 일치한다.**
- `\\)`: **닫는 괄호 문자를 찾는다.**
    - 백슬래시는 닫는 괄호의 의미를 이스케이프하는 데 사용.  
<br>

이제 다 알아봤고, 테스트 코드를 작성해보자. 

```
@Test
@DisplayName("패턴 클래스의 matches 메서드()를 통해서 정규식과 입력값을 비교")
void coordinate_custom_regex_test() {
    // given
    String regex = "\\((\\d+),(\\d+)\\)";

    //when
    boolean actual = Pattern.matches(regex, "(100,300)");

    //then
    assertThat(actual).isTrue();
}
```
```
@Test
@DisplayName("패턴 클래스의 compile() 메서드를 통해 최초 1회 Matcher 클래스를 만들고, 이후 입력값과 비교")
void coordinate_custom_regex_test2() {
    // given
    Pattern pattern = Pattern.compile("\\((\\d+),(\\d+)\\)");

    //when
    Matcher matcher = pattern.matcher("(100,300)");

    //then
    assertThat(matcher.find()).isEqualTo(true);
}
``` 

<br>

잠시, 여기서 **find() 메서드와 matches() 메서드** 사용 시 주의해야할 점이 있다.  

입력 문자열이 현재 `"(100,300)"` 이지만,  
`"aaa(100,300)"` 혹은 `"(100,300)bbb"` 등으로 바꾼다면 테스트는 어떻게 될까?  
  
`matches()`는 false를 반환하지만 `find()`는 여전히 true를 반환한다.


#### 결론적으로  

- `matches()` 메서드는 **전체 입력 문자열**이 정규식과 일치하는지 확인
- `find()` 메서드는 **패턴과 일치하는지만** 확인  

다시 이어서 진행해보자...

<br>  

### 두개의 테스트코드의 차이점이 뭘까?  

1번째 테스트 코드를 살펴보자.  
`Pattern.matches()` 메서드를 사용해서, 문자열이 정규식과 일치하는지 확인하고 있다.

2번째 테스트 코드를 살펴보자.  
정규 표현식을 `Pattern` 객체로 컴파일 후 `Matcher` 객체의 `find()` 메서드를 통해 일치하는 확인하고 있다.  

<br>  

특정 입력 문자열에 대해서만 확인하는 경우 `Pattern.matches()`를 사용하는 것이 더 간단하고 간결한 접근 방식일 수 있다.

정규 표현식을 `Pattern` 객체로 컴파일(compile() 메서드를 사용)하는 것은 상대적으로 비용이 많이 드는 작업이지만, 

**정규식을 여러 번 재사용해야한다면?** 정규식을 최초 한 번만 컴파일하는 것이 효율적이다.  

<br>
다음은 여러 개의 파라미터를 테스트할 수 있는 방법이다. 한 번 살펴봤으면 좋겠다.  

```
@ParameterizedTest
@CsvSource(value = {"(1,3):true", "(100,300):true", "(1,2:false", "1,3):false", "1,2:false"}, delimiter = ':')
@DisplayName("정규식을 통해 검증하고, 입력값에 따른 기대값이 맞는지 확인")
void coordinate_custom_regex_test3(String input, Boolean expected) {
    // given
    Pattern pattern = Pattern.compile("\\((\\d+),(\\d+)\\)");

    //when
    Matcher matcher = pattern.matcher(input);

    //then
    assertThat(matcher.find()).isEqualTo(expected);
}
```  

<br>  

### group(), group(int group) 메서드도 사용해보자.  

```
    @Test
    @DisplayName("matcher.group() 메서드를 활용한 정규식과 일치하는 문자열 그룹을 확인")
    void group_test() {
        // given
        String input = "입력하신 좌표는 (1,2) 입니다.";
        Pattern pattern = Pattern.compile("\\((\\d+),(\\d+)\\)");

        //when
        Matcher matcher = pattern.matcher(input);

        //then
        assertThat(matcher.find()).isTrue();
        assertThat(matcher.group()).isEqualTo("(1,2)");
    }
```
```
@Test
@DisplayName("matcher.group(int group) 메서드를 활용한 정규식과 일치하는 문자열 그룹을 확인")
void group_test2() {
    // given
    String input = "입력하신 좌표는 (50,60) 입니다.";
    Pattern pattern = Pattern.compile("\\((\\d+),(\\d+)\\)");

    //when
    Matcher matcher = pattern.matcher(input);

    //then
    assertThat(matcher.find()).isTrue();
    assertThat(matcher.group(1)).isEqualTo("50");
    assertThat(matcher.group(2)).isEqualTo("60");
}
```
</div>