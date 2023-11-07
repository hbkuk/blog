<div class=markdown-body>


### Test Double 이란?

<p align="center">
  <img src="https://github.com/hbkuk/java-unit-testing/assets/109803585/23c46a59-8853-44c5-9314-494358ee107e"/>
</p> 

테스트를 목적으로 **Real Object를 흉내내는 모든 대역 객체**를 통틀어 **Test Double**이라고 합니다.

또한, 테스트 대역은 Dummy, Stub, Spy, Mock, Fake로 나눠집니다.

### Test Double의 필요성

테스트 하려는 객체가 여러 객체들 혹은 의존성(데이터베이스, 메일 등)으로 묶여있을 때, 테스트를 하기 위해서는 대역이 필요하게 됩니다.

- 테스트 수행 시 **외부 의존성에 영향을 주면 안되는 경우**
- 테스트 수행 시 외부 의존성의 응답을 **원하는 응답으로 만들어야 하는 경우**


### Test Double의 종류

#### Dummy
- 실제 사용되지는(호출되지는) 않는 객체
- 주로 **메서드 시그니처를 맞추기 위해 사용**  

```
public class DummyLogger implements Logger {
    public void log(String message) {
        // 아무 동작도 수행하지 않음
    }
}
```  

#### Fake
- 실제 프로덕션에 사용하는 구현체를 테스트에 사용하기에 적합하지 않을 때
- **테스트 용으로 작성된 Fake(가짜) 구현체** 사용  

```
public class FakeDatabaseConnection implements DatabaseConnection {
    private List<String> data = new ArrayList<>();

    public void connect() {
        // 데이터베이스 연결 로직
    }

    public void executeQuery(String query) {
        // 데이터베이스 쿼리를 수행하지 않고 데이터를 가짜 데이터 목록에 추가
        data.add(query);
    }

    public List<String> getExecutedQueries() {
        return data;
    }
}
```
#### Stub
- 테스트 동안 **설정된 응답을 반환하는 객체**
- 정해진 응답을 반환하도록 만드는 행위를 **Stubbing**이라고 함.

```
public interface Calculator {
    int add(int a, int b);
}

public class StubCalculator implements Calculator {
    @Override
    public int add(int a, int b) {
        // Stub: 항상 10 반환
        return 10;
    }
}

// 테스트 코드
public class CalculatorTest {
    @Test
    public void testAdditionWithStub() {
        Calculator calculator = new StubCalculator();
        int result = calculator.add(5, 7);
        assertEquals(10, result); // Stub이 10을 반환하므로 10과 비교
    }
}

```  

#### `Spy`
- Spy 객체는 **실제 객체와 동일**하지만 어떻게 호출되었는지에 대한 **정보를 기록하는 기능을 추가한 stub**  

```
@Test
void listSpy() {
    List<String> spy = spy(new ArrayList<>()); // spy 객체 생성

    // spy를 이용해서 메서드 호출 기록
    spy.add("item 1");
    spy.add("item 2");

    // 메서드 호출 횟수 확인(add 메서드 2번 호출되었는지 검증)
    Mockito.verify(spy, Mockito.times(2)).add(Mockito.anyString());

    // spy 리스트는 실제 리스트와 동일한 데이터 유지
    assertEquals(2, spy.size());
    assertEquals("item 1", spy.get(0)); // 실제 데이터 접근 가능
    assertEquals("item 2", spy.get(1));
}
```  

#### `Mock`
- **Stub과 Spy의 일부 기능을 결합**한 것
- 어떤 method call을, 어떤 파라미터로, 몇번 받게 될지를 미리 예상하여 Setting 해두는 객체
- **응답을 어떻게 반환할지도 설정(stubbing)** 해둘 수 있습니다.
```
@Test
void mockList() {
    ArrayList<String> mockList = mock(ArrayList.class);

    // 행동 재정의 or 응답 반환 설정(stubbing)
    when(mockList.get(0)).thenReturn("data 1");
    when(mockList.size()).thenReturn(2);

    // 검증
    assertThat(mockList.get(0)).isEqualTo("data 1");
    assertThat(mockList.size()).isEqualTo(2);
}
```

Spy와 Mock은 비슷하지만, 다른 부분이 몇가지 있습니다.
이에 대해서 다시 한번 정리해보면 좋을 것 같습니다.

### Spy와 Mock의 차이

#### Spy 

**`Spy`는 지정한 객체의 행동(Behavior)을 그대로 가지게 됩니다.**
즉, 해당 객체의 행동을 지정하지 않아도 되고, 만약 지정한다면 본래 객체의 행동을 재정의하게 됩니다.

```
@Test
void spyList() {
    ArrayList<String> spyList = spy(ArrayList.class);

    // 1차 검증
    assertThat(spyList.size()).isZero();

    // 데이터 추가
    spyList.add("data 1");
    spyList.add("data 2");

    // 2차 검증
    assertThat(spyList.get(0)).isEqualTo("data 1");
    assertThat(spyList.get(1)).isEqualTo("data 2");
    assertThat(spyList.size()).isEqualTo(2);

    // 행동 재정의 or 응답 반환 설정(stbbing)
    when(spyList.get(0)).thenReturn("data 10");
    when(spyList.size()).thenReturn(50);

    // 재 검증
    assertThat(spyList.get(0)).isEqualTo("data 10");
    assertThat(spyList.size()).isEqualTo(50);
}
```  


#### Mock Object

**`Mock`은 `Spy`와는 다르게 지정한 객체의 행동(Behavior)을 가지지 못합니다.**
직접 해당 객체의 행동을 when(), given() 등으로 지정해줘야 합니다.

```
@Test
void mockList_1() {
    ArrayList<String> mockList = mock(ArrayList.class);

    // 1차 검증
    assertNull(mockList.get(0));
    assertThat(mockList.size()).isZero();

    // 데이터 추가
    mockList.add("data 1");
    mockList.add("data 2");

    // 2차 검증
    assertNull(mockList.get(0));
    assertThat(mockList.size()).isZero();
}

@Test
void mockList_2() {
    ArrayList<String> mockList = mock(ArrayList.class);

    // 행동 재정의 or 응답 반환 설정(stubbing)
    when(mockList.get(0)).thenReturn("data 1");
    when(mockList.size()).thenReturn(2);

    // 검증
    assertThat(mockList.get(0)).isEqualTo("data 1");
    assertThat(mockList.size()).isEqualTo(2);
}
```

#### 참고자료
- https://umbum.dev/1233/
- https://velog.io/@dnjscksdn98/JUnit-Mockito-Spying
- https://azderica.github.io/00-test-mock-and-stub/
</div>