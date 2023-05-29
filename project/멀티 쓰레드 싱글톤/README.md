<div class="markdown-body">  

## Servlet과 Servlet Container

`Servlet`은 **Servlet Container**가 시작할 때, **인스턴스를 하나만 생성하도록 다음과 같이 클래스를 정의**했습니다.  

```
/**
 * 클라이언트로부터 모든 요청을 수신하는 서블릿 컨테이너
 */
@Slf4j
@WebServlet(name = "dispatcher", urlPatterns = "/", loadOnStartup = 1)
public class DispatcherServlet extends HttpServlet {
    private Map<String, Controller> requestMap;

    @Override
    public void init() {
        requestMap = new HashMap<>();

        requestMap.put("/boards", new ShowBoardsController());
        requestMap.put("/board", new ShowBoardController());
        ...
    }

```  

위와 같은 코드를 보면 알 수 있듯이 멀티 쓰레드 환경에서 **여러 명의 사용자(클라이언트)가 인스턴스 하나를 재사용** 합니다.  

<br>  

매번 발생하지는 않지만,  

**여러명의 클라이언트가 동시에 같은 코드를 실행하는 경우 발생**할 수 있기 때문에, 해당 내용에 대해서 작성해 보려고 합니다.  

<br>

## 멀티 쓰레드 환경에서 발생하는 문제  

```
/**
 * 게시물 번호에 해당하는 게시물 View 담당
 */
public class ShowBoardController extends AbstractController {

    private BoardDTO boardDTO = null;
    private BoardService boardService = new BoardService(
                        new BoardDAO(), new CommentDAO(), new CategoryDAO(), new FileDAO());

    /**
     * 게시글 번호에 해당하는 게시글 정보를 응답합니다
     *
     * @catch 게시글 번호에 해당하는 게시물이 없는 경우 (NoSuchElementException) 에러페이지를 응답합니다
     */
    @Override
    public void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        try {
            boardDTO = boardService.findBoardWithDetails((Long.parseLong(req.getParameter("board_idx"))));
        } catch (NoSuchElementException e) {
            req.setAttribute("error_message", e.getMessage());
            req.getRequestDispatcher("/views/error/error404.jsp").forward(req, resp);
        }

        req.setAttribute("searchConditionQueryString", SearchConditionUtils.buildQueryString(req.getParameterMap()).toString());
        req.setAttribute("board", boardDTO);

        req.getRequestDispatcher("/views/boardView.jsp").forward(req, resp);
    }
}
```  

멀티 쓰레드 환경에서 문제가 발생하는 부분은 **`ShowBoardController`의 필드로 구현되어 있는 부분**입니다.  

어떠한 문제가 언제 발생하는지 확인해 보겠습니다.  

<br>

상황을 가정해보겠습니다.  

**사용자 A와 사용자 B는 다음과 같은 URI로 동시에 서버에 요청**합니다.  

<br>

**사용자 A**  
```
http://localhost:8080/board?board_idx=1
```  

**사용자 B**
```
http://localhost:8080/board?board_idx=7
```  

요청 URI에서 **파라미터 이름인 board_idx**는 **게시글 번호를 의미**합니다.  

**사용자 A는 1번 글**을, **사용자 B는 7번 글**을 요청했습니다.

<br>

하지만, 사용자 A와 사용자 B 브라우저에는 다음과 같이 동일한 화면이 출력됩니다.  

![동일한 응답](https://github.com/hbkuk/board-web/assets/109803585/5da4baa7-2cef-42d9-9e97-29578ce1db18)  

이 문제가 왜 발생하는지에 대해서 **정확히 이해**하고,  

이를 해결하기 위해서는 구현한 코드가 **메모리에서 어떻게 동작하는지** 이해해야 합니다.  

## 사용자 A가 요청했을 때 

![사용자 A](https://github.com/hbkuk/board-web/assets/109803585/2e0df218-009d-4ea8-a7f9-5903fb5376ec)  

먼저, **JVM**은 코드를 실행하기 위해서 메모리를 **스택과 힙 영역**으로 나눠서 관리합니다.  

스택과 힙 영역에 대해서 간단하게 정리하자면,

스택 영역은 각 메서드가 실행될 때 **메서드의 인자**, **로컬 변수**등을 관리하는 메모리 영역으로 각 쓰레드마다 서로 다른 스택 영역을 가집니다.  

힙 영역은 클래스의 **인스턴스 상태 데이터를 관리하는 영역**이므로, 쓰레드가 서로 공유할 수 있는 영역입니다.  

<br>

따라서, **ShowBoardController의 `execute()` 메서드가 실행**되면,  
`execute()` 메서드에 대한 스택 프레임의 로컬 변수 영역의 첫 번째 위치에 **자기 자신에 대한 메모리 위치**를 가르킵니다.  

ShowBoardController에 대한 **인스턴스는 힙에 생성**되어 있으며, 필드에 BoardDTO 가지기 때문에 힙에 생성되어 있는 **BoardDTO 인스턴스를 가르키는 구조**로 실행됩니다.  

### 사용자 A에 의해서, 1번 글에 해당하는 BoardDTO 인스턴스를 가르킨다

![사용자 A](https://github.com/hbkuk/board-web/assets/109803585/181bbad6-6a41-419e-ae91-603d9b160b1e))  

사용자 A가 요청했을 때는 별다른 특이사항이 없지만,  

**문제는 `execute()` 메서드가 완료되지 않은 시점**에서 **사용자 B의 요청에 의해 `execute()` 메서드가 실행될 경우** 발생합니다.  

<br>

사용자 B가 요청을 하면 ShowBoardController가 가르키는 `BoardDTO`는 **1번이 아닌 7번으로 바뀌게 됩니다.**  

따라서, 사용자 A의 본래 요청은 1번 글이었으나, 사용자 B의 요청에 의해서 7번글로 변경된다는 의미입니다.  

<br>

![사용자 B](https://github.com/hbkuk/board-web/assets/109803585/695b4af0-ec87-42ce-85a8-4ab1254c8f19)  

그렇다면 이 상황을 어떻게 해결했을까요?  


## 멀티 쓰레드 환경에서는 로컬 변수로 구현

클래스의 필드가 아닌, 로컬 변수로 구현하는 것입니다.  


![로컬 변수](https://github.com/hbkuk/board-web/assets/109803585/b725bcc2-2083-4301-b985-ebfacacb2a45)  

`execute()` 메서드의 로컬 변수로 구현하면, ShowBoardController가 인스턴스에 대한 참조를 가지지 않고 **메서드의 스택 프레임의 로컬 변수 영역에서 해당 인스턴스에 대한 참조를 가르키게 됩니다.**  

따라서, 쓰레드 간의 영향을 미치는 일은 발생하지 않습니다.  

## 마지막으로..

이번 계기로 구현한 소스코드가 메모리에서 어떻게 실행되는지 확인할 수 있었습니다.  

앞으로, 멀티 쓰레드 환경에서 상태 값을 가지는 객체는 주의 깊게 디버깅 하면서, 프로그래밍을 해보려고 합니다.  

감사합니다.









</div>