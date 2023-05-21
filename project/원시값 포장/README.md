<div class=markdown-body>

# 어떻게 하면 가독성 좋은 코드 코드가 될까? - 원시값을 포장한 도메인 객체  

게시판을 주제로 한 프로젝트를 진행 중에 있습니다.  

요구사항을 분석 후 **도메인 객체**를 아래와 같이 설계했습니다.  

```
public class Board {
    private final long boardId = 0;
    private final String category;
    private final String title;
    private final String writer;
    private final String content;
    private final String password;
    private final int hit = 0;
    private final LocalDateTime regDate = LocalDateTime.now();

    public Board(long boardId, String category, String title, 
            String writer, String content, String password, int hit, LocalDateTime regDate) {
        this.boardId = boardId;
        this.category = category;
        this.title = title;
        this.writer = writer;
        this.content = content;
        this.password = password;
        this.hit = hit;
        this.regDate = regDate;
    }
}  
```  

<br>

**`Board` 라는 도메인 객체**는 다음과 같은 요구사항에 충족해야 합니다. 

즉, **유효성 검증이 진행**되어야 한다는 의미입니다.  

<br>

요구사항을 분석해보니, 다음과 같이 정리했습니다.

- 카테고리는 필수적으로 선택되어야 함.
- 제목은 필수로 선택되어야만 함.
    - 4글자 이상, 100글자 미만이어야 함.
- 작성자는 필수적으로 선택되어야 함.
    - 3글자 이상, 5글자 미만어야 함.
- 비밀번호는 필수적으로 입력되어야 함.
    - 4글자 이상, 16글자 미만이어야 함.
    - 영문/숫자/특수문자가 포함되어야 함.
- 내용은 필수로 선택되어야만 함.
    - 4글자 이상, 2000글자 미만이어야 함.  

<br>

그렇다면, 해당 **검증 로직은 어디서 진행**되어야 할까요?  


## 도메인 내에서 검증하자  

필자는 유효성 검사를 **해당 도메인 객체에서 진행되어야 한다고 생각합니다.**  

그 이유는, **해당 도메인에서 책임을 갖고** 유효성 검사를 처리한 후에, **필요로 하는 객체로 전달**한다.  

따라서, 다음과 같이 검증 로직을 구성해봤습니다.  



```
public class Board {
    private final long boardId = 0;
    private final String category;
    private final String title;
    private final String writer;
    private final String content;
    private final String password;
    private final int hit = 0;
    private final LocalDateTime regDate = LocalDateTime.now();

    public Board(long boardId, String category, String title, 
            String writer, String content, String password, int hit, LocalDateTime regDate) {

        if (Category.isInvalidCategory(this.category)) {
            throw new IllegalArgumentException("카테고리는 선택되어야 합니다.");
        }
        if (title.length() < 4 || title.length() > 99) {
            throw new IllegalArgumentException("제목은 4글자 미만, 100글자 이상을 입력할 수 없습니다.");
        }
        if (writer.length() < 3 || writer.length() > 4 ) {
            throw new IllegalArgumentException("작성자를 3글자 미만 5글자 이상을 입력할 수 없습니다.");
        }
        if (password.length() < 4 || password.length() > 15) {
            throw new IllegalArgumentException("패스워드는 4글자 미만 16글자 이상일 수 없습니다.");
        }
        String PASSWORD_PATTERN = "^(?=.*[a-zA-Z])(?=.*\\d)(?=.*[@#$%^&+=!]).*$";
        Pattern pattern = Pattern.compile(PASSWORD_PATTERN);
        if (!pattern.matcher(password).matches()) {
            throw new IllegalArgumentException("패스워드는 영문, 숫자, 특수문자가 포함되어 있어야 합니다.");
        }
        if (content.length() < 4 || content.length() > 1999) {
            throw new IllegalArgumentException("내용은 4글자 미만 2000글자를 초과할 수 없습니다.");
        }

        this.boardId = boardId;
        this.category = category;
        this.title = title;
        this.writer = writer;
        this.content = content;
        this.password = password;
        this.hit = hit;
        this.regDate = regDate;

    }
}

```  

<br>

하지만, 위와 같이 검증해야 할 데이터가 많아지게 된다면 또 다른 객체로 분리해야 할 때라고 생각합니다.  

따라서, **원시값을 포장한 객체**를 만들어서 **해당 객체 내에서 유효성 검사를 위임**했습니다.  

<br>

```
public class Board {
    private final BoardId boardId;
    private final Category category;
    private final Title title;
    private final Writer writer;
    private final Content content;
    private final Password password;
    private final Hit hit;
    private final RegDate regDate;
...



public class BoardId {
    private static final int MIN_BOARDID_VALUE = 0;
    private long boardId = 0;

    public BoardId(int value) {
        if(value < MIN_BOARDID_VALUE) {
            throw new IllegalArgumentException("글 번호는 음수일 수 없습니다.");
        }
        this.boardId = value;
    }
...

public class Content {

    private String content;

    public Content(String content) {
        if (content.length() < 4 || content.length() > 1999) {
            throw new IllegalArgumentException("내용은 4글자 미만 2000글자를 초과할 수 없습니다.");
        }
        this.content = content;
    }
...

public class Hit {
    private static final int MIN_HIT_VALUE = 0;
    private int hit = 0;

    public Hit(int hit) {
        if (hit < MIN_HIT_VALUE) {
            throw new IllegalArgumentException("조회수는 음수일 수 없습니다.");
        }
        this.hit = hit;
    }
...
```  

각각의 객체로 유효성 검사를 위임하니, 다음과 같은 테스트가 가능해졌습니다.


```
@DisplayName("BoardId 클래스는")
public class BoardIdTest {

    @DisplayName("생성자의 매개변수는 정수만 허용된다.")
    @ParameterizedTest
    @ValueSource(ints = {1, 100, 2000, 3000, 40000, 50000})
    void create_boardId(int number) {
        BoardId boardId = new BoardId(number);

        assertThat(boardId).isEqualTo(new BoardId(number));
    }

    @ParameterizedTest
    @ValueSource(ints = {-1, -2, -3, -1000, -20000})
    @DisplayName("음수가 전달될 경우 예외가 발생한다.")
    void invalid_boardId(int number) {
        assertThatExceptionOfType(IllegalArgumentException.class)
                .isThrownBy(() -> {
                    new BoardId(number);
                })
                .withMessageMatching("글 번호는 음수일 수 없습니다.");
    }
}


@DisplayName("글 내용은")
public class ContentTest {

    @Test
    void create_content() {
        Content content = new Content("내용입니다.");

        assertThat(content).isEqualTo(new Content("내용입니다."));
    }

    @DisplayName("4글자 미만일 경우 예외가 발생한다.")
    @ParameterizedTest
    @ValueSource(strings = {"가", "a", "가나", "ab", "가나다", "abc"})
    void invalid_content_shorter_than(String text) {
        assertThatExceptionOfType(IllegalArgumentException.class)
                .isThrownBy(() -> {
                    new Content(text);
                })
                .withMessageMatching("내용은 4글자 미만 2000글자를 초과할 수 없습니다.");
    }

    @DisplayName("2000글자 이상인 경우 예외가 발생한다.")
    @Test
    void invalid_content_more_than() {
        StringBuilder longContentSource = new StringBuilder("가나다라");
        while (longContentSource.length() < 2000) {
            longContentSource.append("나");
        }

        assertThatExceptionOfType(IllegalArgumentException.class)
                .isThrownBy(() -> {
                    new Content(longContentSource.toString());
                })
                .withMessageMatching("내용은 4글자 미만 2000글자를 초과할 수 없습니다.");
    }
}
...
```




</div>