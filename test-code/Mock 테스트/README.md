<div class="markdown-body">

##### 해당 글은 jsp/servlet 개발 환경에 해결했던 내용입니다.  

## 테스트 코드 작성을 위한 의존 관계 주입(DI)을 고려해야할 상황  

`BoardService`는 게시글 번호에 해당하는 게시글을 가져오기 위해서  **BoardDAO, CommentDAO, FileDAO에게 데이터 베이스 접근 로직을 위임**하고 있습니다.  

작성된 코드는 아래와 같습니다.

```
public BoardDTO findBoard(Long boardIdx) {
    BoardDTO boardDTO = boardDAO.findById(boardIdx);

    if( boardDTO == null ) {
        throw new NoSuchElementException("해당 글을 찾을 수 없습니다.");
    }

    boardDAO.increaseHitCount(boardIdx)
    boardDTO.setComments(commentDAO.findAllByBoardId(boardIdx));
    boardDTO.setFiles(fileDAO.findFilesByBoardId(boardIdx));

    return boardDTO;
}
```  

`BoardService`가 작업을 완료하기 위해 `BoardDAO`, `CommentDAO`, `FileDAO`에 의존하고 있으며, 이는 **의존관계를 가지고 있다는 의미입니다.**  

<br>

이와 같은 상황에서 테스트 코드를 작성하려고 할때 어떻게 해야할지 고민을 하게 됩니다.  

<br>

### BoardService는 BoardDAO, FileDAO에 대한 의존 관계를 가진다.  

```
public class BoardService {
    private static BoardService boardService;

    private BoardDAO boardDAO = BoardDAO.getInstance();
    private CommentDAO commentDAO = BoardDAO.getInstance();
    private FileDAO fileDAO = BoardDAO.getInstance();

    private BoardService() {};

    public static BoardService getInstance() {
        if (boardService == null) {
            boardService = new BoardService();
        }
        return boardSerivce;
    }
}
```  

현재 위와 같이 **싱글톤 패턴으로 구현된 클래스와 의존관계를 가지는 경우**, 다음과 같은 문제가 있습니다.
- 해당 클래스와 강한 의존관계를 가지기 떄문에 **테스트하기 어렵습니다.**
- 생성자를 private 구현하기 때문에 **상속을 할 수 없습니다.**  

따라서, 싱글톤 패턴을 사용하지 않으면서 인스턴스를 하나만 유지할 수 있는 **DI 구조로 변경**해 보겠습니다.  

<br>

```
public class BoardService {
    private BoardDAO boardDAO;
    private CommentDAO commentDAO;
    private FileDAO fileDAO;

    public BoardService(BoardDAO boardDAO, CommentDAO commentDAO, FileDAO fileDAO) {
        this.boardDAO = boardDAO;
        this.commentDAO = commentDAO;
        this.fileDAO = fileDAO;
    }
}
```  

<br>

### Mockito를 활용한 테스트 코드

데이터베이스가 없는 상태에서도 테스트가 가능하도록 지원하는 **`Mock` 테스트 프레임워크**를 사용해 보겠습니다.  

<br>

우선 **gradle 의존성을 추가**합니다.

```
// junit 5
implementation 'com.mikemybytes:junit5-formatted-source:0.2.0'
implementation 'com.mikemybytes:junit5-formatted-source-parent:0.2.0'
implementation 'com.mikemybytes:junit5-formatted-source-tests:0.2.0'

// mockito
testImplementation 'org.mockito:mockito-junit-jupiter:3.11.2'
```  

<br>  

Mockito를 활용해 **BoardService의 `findBoard()` 메서드를 테스트** 해보겠습니다.  

```
@ExtendWith(MockitoExtension.class)
public class ServiceTest {

    @Mock
    private BoardDAO boardDAO;
    @Mock
    private CommentDAO commentDAO;
    @Mock
    private FileDAO fileDAO;
    @Mock
    private CategoryDAO categoryDAO;

    private BoardService boardService;

    @BeforeEach
    void sertup() {
        boardService = new BoardService(boardDAO, commentDAO, categoryDAO, fileDAO);
    }

    @Nested
    @DisplayName("게시글이 가져올때")
    class getBoard {

        @Test
        @DisplayName("조회수가 증가되지 안았다면 예외가 발생한다")
        void find_by_id_exception() {
            // given
            Long boardIdx = 1L;

            when(boardDAO.findById(boardIdx)).thenReturn(null);

            // when
            assertThatExceptionOfType(NoSuchElementException.class)
                    .isThrownBy(() -> {boardService.findBoard(1);})
                    .withMessageMatching("해당 글을 찾을 수 없습니다.");
        }

        @Test
        @DisplayName("조회수 증가, 게시글 찾기, 모든 댓글 찾기, 모든 파일 찾기의 메서드가 순서대로 호출된다.")
        void board_click_triggers_method_calls() {
            // given
            Long boardIdx = 1L;
            BoardDTO boardDTO = new BoardDTO();
            when(boardDAO.findById(boardIdx)).thenReturn(boardDTO);

            // when
            boardService.findBoard(boardIdx);

            // then
            InOrder inOrder = inOrder(boardDAO, commentDAO, fileDAO);
            inOrder.verify(boardDAO).findById(boardIdx);
            inOrder.verify(boardDAO).increaseHitCount(boardIdx);
            inOrder.verify(commentDAO).findAllByBoardId(boardIdx);
            inOrder.verify(fileDAO).findFilesByBoardId(boardIdx);
            inOrder.verifyNoMoreInteractions();
        }

    }

```  

위 코드를 보면 Mockito는 [@Mock](https://site.mockito.org/) 어노테이션으로 설정한 클래스의 메서드를 호출했을 때 반환 값을 지정할 수 있습니다.  

또한, 클래스의 메서드가 호출되는지 여부를 verify() 메서드를 통해 검증하는 작업 또한 가능합니다.  

</div>