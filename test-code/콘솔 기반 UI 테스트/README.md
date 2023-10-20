<div class=markdown-body>

#### 콘솔 기반 UI 테스트를 하게 된 계기

이전까지 상태 값을 가지는 **도메인 클래스를 구현할 때 TDD로 구현**을 해서 깔끔하게 잘 해왔다고 생각한다.
다만, UI 로직에 대해서는 고민만 했을 뿐... '굳이..?' 라는 생각에 지금까지 제대로 된 테스트를 하지 않았다.

최근, 취업을 위해 **사전과제를 진행**했었다.
해당 과제는, csv 파일(key-value 형태)을 읽어서 사용자로부터 입력받은 key 값에 해당하는 value를 출력하는 내용이었다.

이 또한 상태 값을 가지는 도메인 클래스를 구현할 때는 비교적 깔끔하게 잘 해왔다고 생각하지만,
**UI 로직에 대해서는 수동적으로 테스트를 하고 제출**했었다.

시간적 여유가 없어서, 제출했지만.. 근래 **UI 로직에 대한 테스트를 못한 것에 대한 아쉬움이 남아서 '어떻게 테스트를 해야 할까?' 에 대한 생각**이 머릿속에서 떠나질 않았다.

예를 들면, 콘솔를 통해 사용자가 제대로 된 문자열을 입력할 떄까지, `숫자를 입력해 주세요 : `라고 출력이 되는지 확인하는 테스트와 같은 것을 하고 싶었다.
![검증 대상 메서드](https://github.com/hbkuk/baseball-game-by-tdd/assets/109803585/6d9578f5-bb8c-4928-b908-b259736cd105)

<p align="center">
  <img src="https://github.com/hbkuk/baseball-game-by-tdd/assets/109803585/2b117758-cf2f-4d8e-8c34-dc77b0bbed0b" alt="text" width="number" />
</p> 

<br>

#### System in

콘솔로부터 사용자의 입력 값을 받을 때에는 `Scanner` 객체를 사용한다.
```
Scanner sc = new Scanner(System.in);
```

<br>

이때, Scanner 객체를 생성할 때, 인자로 전달하는 `System.in`은 **콘솔 창에 입력 값을 `InputStream`으로 담는 역할**을 한다.

이러한 동작방식을 이용해서, 테스트 코드를 실행하기 전, **System에 미리 InputStream 형식의 데이터를 넣어주면 되는 거 아닌가?**

```
private void setInputStreamInSystem(String inputA) {
    String input = inputA + System.lineSeparator();
    InputStream in = new ByteArrayInputStream(input.getBytes());
    System.setIn(in);
}
```  

<br>

테스트 코드가 실행되기 전, 위와 같은 메서드가 실행될 수 있게 만든다면 **콘솔에 입력하는 값을 대체**할 수 있다.
```
@DisplayName("숫자로 구성된 값을 전달하면 결과를 출력한다.")
@Test
void playSingleGame() {
    setInputStreamInSystem("312", "123");

    GameManager gameManager = new GameManager(new Scanner(System.in));
    gameManager.playSingleGame(new Balls(Arrays.asList(1, 2, 3)));

    // 검증 ...
}

private void setInputStreamInSystem(String inputA, String inputB) {
    String input = inputA + System.lineSeparator() + inputB + System.lineSeparator();
    InputStream in = new ByteArrayInputStream(input.getBytes());
    System.setIn(in);
}
```


#### System out

그렇다면, 사용자가 입력한 값에 따라서 **콘솔에 출력되는 값을 테스트하려고 한다면?**

<br>

표준 출력인 **`System.out`을 잡아서 콘솔에 출력되는 내용을 `ByteArrayOutputStream`에 담는 방법**을 사용하면 되지 않을까?

**`out.toString()`으로 변환하여 비교하고자 하는 값과 비교**해서 처리하면 될 것 같다.

```
OutputStream out;

@BeforeEach
void setUp() {
    out = new ByteArrayOutputStream();
    System.setOut(new PrintStream(out));
}

@DisplayName("숫자로 구성된 값을 전달하면 결과를 출력한다.")
@Test
void playSingleGame() {
    setInputStreamInSystem("312", "123");

    GameManager gameManager = new GameManager(new Scanner(System.in));
    gameManager.playSingleGame(new Balls(Arrays.asList(1, 2, 3)));

    assertThat(out.toString()).contains("Ball 3", "All Strike!!!");
}

private void assertExpectedOutput(String format) {
    String expectedOutput = String.format(format);
    assertEquals(expectedOutput, out.toString());
}
```

#### 마무리

'어떻게 하면 UI 로직에 대한 테스트 코드를 작성할 수 있지?'에서 비롯되어 고민해보는 시간을 가져봤다.
앞으로 검증할 필요가 있을 때는 이러한 방식으로 검증하고자 한다.

다음부터는 이전보다 더 나은 코드를 작성해보자.

</div>