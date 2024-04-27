<div class="markdown-body">  

# 어떻게 하면 가독성 좋은 코드 코드가 될까? - 빌더 패턴(Builder Pattern)

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

만약, 클라이언트를 통해 parameter를 전달받아 객체를 생성한다면 코드는 어떻게 될까요?  

```
Board simpleBoard = new Board("JAVA", "제목 1", "테스터 1", "내용 1", "qlalfqjsgh1!");  
```  

위와 같은 코드로 쓸겁니다.  

이정도 복잡도 까지는 코드를 뜯어보면 이해할 수 있을겁니다.

<br>

하지만, 요구사항이 증가하면서 **태그 같은 기능이 추가**된다고 가정해보겠습니다.  

이 태그 필드는 위와같은 심플한 게시판에서 사용하는 것이 아닌, **태그 게시판에서만 사용**할 수 있다고 가정하면 됩니다.  

```
private final String tag;
```  
<br>  

새로운 요구사항으로 추가된 필드를 활용해서, 태그 게시판에서는 아래와 같이 객체를 생성한다면 어떻게 될까요?  

```
Board tagBoard = new Board("JAVA", "제목 1", "테스터 1", "내용 1", "qlalfqjsgh1!", "java");
```  

<br>  

어지럽습니다.  

두 코드를 비교해보면 한눈에 알아차리기 쉽지 않습니다.  

**코드의 가독성이 떨어집니다.**    

<br>

또한, 요구사항이 추가되면 그에따라 **생성자를 오버로딩(Overloading)** 해야합니다.  

프로그램이 거대해질수록 **복잡도가 배로 증가한다고 예상**할 수 있습니다.  

<br>  

따라서, 향후 시스템 확장을 고려해보면서, 아래와 같은 시도를 해봤습니다.  
  
- **자바빈 패턴(JavaBeans Pattern)**
- **빌더 패턴**  

<br>

## 자바빈 패턴  

<br>

이 패턴은 `setter`메서드를 이용해 생성 코드를 읽기 좋게 만드는 것입니다.  

```
Board tagBoard = new Board();

tagBoard.setCategory("JAVA");
tagBoard.setTitle("제목 1");
tagBoard.setWriter("테스터 1");
...
```  

코드를 보면, 각 인자의 의미를 정확히 파악할 수 있습니다.  

또한, 복잡하게 여러 개의 생성자를 만들지 않아도 된다는 장점이 있습니다.  

<br>

하지만, 다음과 같은 단점이 존재합니다.  

- 최초의 생성자 호출로 **객체 생성이 끝나지 않았다.**
- `setter()` 메서드가 있으므로 **변경 불가능(immutable)클래스를 만들 수가 없다.**

<br>  

## 빌더 패턴(Builder Pattern)  

다음으로는 빌더 패턴입니다.  

우선, 코드를 보시죠.  

```
@Getter
public class Board {
    private final long boardId;
    private final Category category;
    private final String title;
    private final String writer;
    private final String content;
    private final String password;
    private final int hit;
    private final LocalDateTime regDate;

    private Board(Builder builder) {
        this.boardId = builder.boardId;
        this.category = builder.category;
        this.title = builder.title;
        this.writer = builder.writer;
        this.content = builder.content;
        this.password = builder.password;
        this.hit = builder.hit;
        this.regDate = builder.regDate;
    }

    public static class Builder {
        private long boardId = 0;
        private Category category;
        private String title;
        private String writer;
        private String content;
        private String password;
        private int hit = 0;
        private LocalDateTime regDate = LocalDateTime.now();

        public Builder() {
        }

        public Builder category(Category category) {
            this.category = category;
            return this;
        }

        public Builder title(String title) {
            this.title = title;
            return this;
        }

        public Builder writer(String writer) {
            this.writer = writer;
            return this;
        }

        public Builder content(String content) {
            this.content = content;
            return this;
        }

        public Builder password(String password) {
            this.password = password;
            return this;
        }

        public Builder boardId(long boardId) {
            this.boardId = boardId;
            return this;
        }

        public Builder hit(int hit) {
            this.hit = hit;
            return this;
        }

        public Builder regDate(LocalDateTime regDate) {
            this.regDate = regDate;
            return this;
        }

        public Board build() {
            return new Board(this);
        }
    }
}

```  

이러한 빌더 패턴을 기반으로 객체를 정의한다면, 아래와 같은 코드로 객체를 생성할 수 있습니다.  

```
Board board = new Board.Builder()
        .category(Category.JAVA)
        .title("제목 1")
        .writer("테스터")
        .content("내용 1")
        .password("rkskekfkakqkt!1")
        .build();
```  

이러한 빌드 패턴 기반의 객체는 다음과 같은 장점이 있습니다.  

- 객체를 생성할때, 각 인자가 어떤 의미인지 알기 쉬운 코드가 됩니다.  
- `setter` 메소드가 없으므로 변경 불가능 객체를 만들 수 있습니다.
- 한 번에 객체를 생성하므로 객체 일관성이 깨지지 않습니다.  

따라서, 빌더 패턴으로 프로젝트에 적용시켜 아래와 같은 테스트 코드를 작성했습니다.  

```
import com.study.model.Board;
import com.study.model.Category;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

@DisplayName("Board 도메인의")
public class BoardTest {

    @Nested
    @DisplayName("카테고리는")
    class category {

        @Test
        @DisplayName("필수로 선택되어야 한다.")
        void not_null_category() {
            // given
            Board board = new Board.Builder()
                    .category(Category.JAVA)
                    .title("제목 1")
                    .writer("테스터")
                    .content("내용 1")
                    .password("rkskekfkakqkt!1")
                    .build();

            // when
            Category category = board.getCategory();

            //then
            assertThat(category).isNotNull();
        }

        @Test
        @DisplayName("선택되지 않으면 예외가 발생한다.")
        void null_category() {
            // when
            assertThatExceptionOfType(IllegalArgumentException.class)
                    .isThrownBy(() -> {
                        new Board.Builder()
                                .title("제목 1")
                                .writer("테스터")
                                .content("내용 1")
                                .password("rkskekfkakqkt!1")
                                .build();
                    }).withMessageMatching("카테고리는 선택되어야 합니다.");
        }
    }

    @Nested
    @DisplayName("제목은")
    class title {

        @Test
        @DisplayName("4글자 이상, 100글자 미만이여야 한다.")
        void title_length_valid() {
            // given
            String shortTitle = "가나다라";
            String longTitle = "가나다라";
            while (longTitle.length() < 99) {
                longTitle += "나";
            }

            // when
            new Board.Builder()
                    .category(Category.JAVA)
                    .title(shortTitle)
                    .writer("테스터")
                    .content("내용 1")
                    .password("rkskekfkakqkt!1")
                    .build();

            new Board.Builder()
                    .category(Category.JAVA)
                    .title(longTitle)
                    .writer("테스터")
                    .content("내용 1")
                    .password("rkskekfkakqkt!1")
                    .build();
        }

        @Test
        @DisplayName("4글자 미만, 100글자 이상인 경우 예외가 발생한다.")
        void title_length_invalid() {
            // given
            String shortTitle = "가나다";
            String longTitleSource = "가나다라";
            while (longTitleSource.length() < 100) {
                longTitleSource += "나";
            }
            String longTitle = longTitleSource;

            // when
            assertThatExceptionOfType(IllegalArgumentException.class)
                    .isThrownBy(() -> {
                        Board board = new Board.Builder()
                                .category(Category.JAVA)
                                .title(shortTitle)
                                .writer("테스터")
                                .content("내용 1")
                                .password("rkskekfkakqkt!1")
                                .build();})
                    .withMessageMatching("제목은 4글자 미만, 100글자 이상을 입력할 수 없습니다.");

            assertThatExceptionOfType(IllegalArgumentException.class)
                    .isThrownBy(() -> {
                        Board board = new Board.Builder()
                                .category(Category.JAVA)
                                .title(longTitle)
                                .writer("테스터")
                                .content("내용 1")
                                .password("rkskekfkakqkt!1")
                                .build();})
                    .withMessageMatching("제목은 4글자 미만, 100글자 이상을 입력할 수 없습니다.");
        }

    }

    @Nested
    @DisplayName("작성자는")
    class writer {

        @DisplayName("3글자 이상 5글자 미만이여야 한다.")
        @ParameterizedTest
        @ValueSource(strings = {"bob", "jany", "테스터", "내이름은"})
        void writer_length_valid(String writer) {
            // given
            Board board = new Board.Builder()
                    .category(Category.JAVA)
                    .title("제목 1")
                    .writer(writer)
                    .content("내용 1")
                    .password("rkskekfkakqkt!1")
                    .build();
        }

        @DisplayName("3글자 미만 5글자 이상인 경우 예외가 발생한다.")
        @ParameterizedTest
        @ValueSource(strings = {"j", "bo", "가나다라마", "가나다라마바"})
        void writer_length_invalid(String writer) {

            assertThatExceptionOfType(IllegalArgumentException.class)
                    .isThrownBy(() -> {
                        new Board.Builder()
                            .category(Category.JAVA)
                            .title("제목 1")
                            .writer(writer)
                            .content("내용 1")
                            .password("rkskekfkakqkt!1")
                            .build();})
                    .withMessageMatching("작성자를 3글자 미만 5글자 이상을 입력할 수 없습니다.");

        }
    }

    @Nested
    @DisplayName("비밀번호의")
    class password {

        @Nested
        @DisplayName("길이는")
        class length_of {

            @DisplayName("4글자 이상 16글자 미만이여야 한다.")
            @ParameterizedTest
            @ValueSource(strings = {"rk!1", "rkskek!1", "rkskekfkakqkt!1", "!2rkskekfkakqkt"})
            void writer_length_valid(String password) {
                // given
                Board board = new Board.Builder()
                        .category(Category.JAVA)
                        .title("제목 1")
                        .writer("jany")
                        .content("내용 1")
                        .password(password)
                        .build();
            }
        }

            @DisplayName("4글자 미만 16글자 이상일 경우 예외가 발생한다.")
            @ParameterizedTest
            @ValueSource(strings = {"r!1", "rkskekfkakqktk1!", "rkskekfkakqktk1!!", "rkskekfkakqktk1@@"})
            void writer_length_valid(String password) {

                assertThatExceptionOfType(IllegalArgumentException.class)
                        .isThrownBy(() -> {
                            Board board = new Board.Builder()
                                    .category(Category.JAVA)
                                    .title("제목 1")
                                    .writer("jany")
                                    .content("내용 1")
                                    .password(password)
                                    .build();
                        })
                        .withMessageMatching("패스워드는 4글자 미만 16글자 이상일 수 없습니다.");
        }

        @Nested
        @DisplayName("필수 조건은")
        class requirement {

            @DisplayName("영문, 숫자, 특수문자가 포함되어 있어야 한다.")
            @ParameterizedTest
            @ValueSource(strings = {"rkskekfkakqkk1!", "rkskekfk@#$!1", "rkskekfk%$#!1", "ndasn11432#@$!@"})
            void password_regex_pass(String password) {
                // given
                Board board = new Board.Builder()
                        .category(Category.JAVA)
                        .title("제목 1")
                        .writer("jany")
                        .content("내용 1")
                        .password(password)
                        .build();
            }

            @DisplayName("영문, 숫자, 특수문자가 포함되어 있지 않다면 예외가 발생한다.")
            @ParameterizedTest
            @ValueSource(strings = {"rkskekfkakqkk!", "rkskekfk211", "rkskekfk", "11432!#@$@"})
            void password_regex_fail(String password) {
                assertThatExceptionOfType(IllegalArgumentException.class)
                        .isThrownBy(() -> {
                            Board board = new Board.Builder()
                                    .category(Category.JAVA)
                                    .title("제목 1")
                                    .writer("jany")
                                    .content("내용 1")
                                    .password(password)
                                    .build();})
                        .withMessageMatching("패스워드는 영문, 숫자, 특수문자가 포함되어 있어야 합니다.");
            }

        }

        @Nested
        @DisplayName("내용은")
        class content {

            @Test
            @DisplayName("4글자 이상 2000글자 미만이여야 한다.")
            void content_length_valid() {
                // given
                String shortContent = "가나다라";
                String longContent = "가나다라";
                while (longContent.length() < 1999) {
                    longContent += "나";
                }

                // when
                new Board.Builder()
                        .category(Category.JAVA)
                        .title("제목 1")
                        .writer("테스터")
                        .content(shortContent)
                        .password("rkskekfkakqkt!1")
                        .build();

                new Board.Builder()
                        .category(Category.JAVA)
                        .title("제목 1")
                        .writer("테스터")
                        .content(longContent)
                        .password("rkskekfkakqkt!1")
                        .build();
            }

            @Test
            @DisplayName("4글자 미만 2000글자 이상일 경우 예외가 발생한다.")
            void content_length_invalid() {

                String shortContent = "가나다";
                String longContentSource = "가나다라";
                while (longContentSource.length() < 2000) {
                    longContentSource += "나";
                }
                String longContent = longContentSource;

                assertThatExceptionOfType(IllegalArgumentException.class)
                        .isThrownBy(() -> {
                            new Board.Builder()
                                    .category(Category.JAVA)
                                    .title("제목 1")
                                    .writer("테스터")
                                    .content(shortContent)
                                    .password("rkskekfkakqkt!1")
                                    .build();})
                        .withMessageMatching("내용은 4글자 미만 2000글자를 초과할 수 없습니다.");

                assertThatExceptionOfType(IllegalArgumentException.class)
                        .isThrownBy(() -> {
                            new Board.Builder()
                                    .category(Category.JAVA)
                                    .title("제목 1")
                                    .writer("테스터")
                                    .content(longContent)
                                    .password("rkskekfkakqkt!1")
                                    .build();})
                        .withMessageMatching("내용은 4글자 미만 2000글자를 초과할 수 없습니다.");
            }
        }
    }
}

```
 </div>