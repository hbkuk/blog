<div class=markdown-body>  

##### 해당 글은 SpringBoot 개발 환경에 해결했던 내용입니다.  

## 예외를 발생시킬만한 상황  

게시판 프로젝트를 진행하다보면 **예외를 발생시킬만한 상황**이 있습니다.  

<br>

예를들어,

- **BoardNotFound e**
    - 사용자로부터 전달받은 **게시물 번호에 해당하는 게시물이 DB에 없을때**
- **InvalidPassword e**
    - 사용자가 글을 수정 및 삭제에 사용하는 **비밀번호가 DB에 저장된 비밀번호와 다를때**
- ...  

위와 같이 다양한 상황이 있을 수 있습니다.  

<br>

## 실제 구현코드  

위에서 언급한 **BoardNotFound e가 발생하는 실제 구현코드**는 어떻게 될까요?  

우선, 아래 코드는 BoarController의 HTTP **GET 요청을 처리하는 핸들러 메서드**이며,  
요청한 **게시물 번호에 해당하는 게시글을 찾고, JSON 형식으로 응답을 반환**합니다.

```
    /**
     * 게시글 번호에 해당하는 게시글 정보를 응답합니다
     *
     * @param boardIdx 게시물 번호
     * @param response 응답 맵 객체
     * @return 응답 결과
     */
    @GetMapping("/api/board/{boardIdx}")
    public ResponseEntity<Object> findBoard(@PathVariable("boardIdx") Long boardIdx, 
                                            Map<String, Object> response) {
        log.debug("findBoard 호출 -> 게시글 번호 : {}", boardIdx);

        response.put("board", boardService.findByBoardIdx(boardIdx));
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
```  

다음으로는 **BoardService 클래스의 구현코드** 입니다.

boardRepository.findByBoardIdx(boardIdx)를 호출해서 **게시물 번호에 해당하는 게시물**을 가져옵니다.  

<br>

만약, 가져온 **board 객체가 null인 경우**, 즉 조회된 게시물이 없는 경우에는 **BoardNotFoundException**을 **throw** 하고 있습니다.  

```
    /**
     * 게시물 번호를 인자로 받아 해당 게시물을 가져온 후 조회수를 1 증가시킨 후 리턴합니다.
     *
     * @param boardIdx 게시물 번호
     * @return 게시물 번호에 해당하는 게시물이 있다면 Board, 그렇지 않다면 BoardNotFoundException 던집니다.
     */
    public Board findByBoardIdx(Long boardIdx) {
        Board board = boardRepository.findByBoardIdx(boardIdx);
        if (board == null) {
            throw new BoardNotFoundException("해당 글을 찾을 수 없습니다.");
        }
        boardRepository.increaseHit(boardIdx);
        return board;
    }
```  

<br>  

## 상황 정리  

현재까지의 상황을 다시 정리하자면,


**컨트롤러**는 요청한 **게시물 번호에 해당하는 게시물 번호를 서비스에게 찾으라고 일을 시킵니다.**  
해당 객체를 응답으로 반환합니다.

**서비스**는 레포지토리에게 **게시물 번호에 건내주면서 게시글을 찾으라고 일을 시킵니다.**  
게시물 번호에 해당하는 **게시물이 없다면 BoardNotFoundException을 발생** 시킵니다.  

<br> 

이 상황에서 **예외를 캐치하지 않는다면, 예외는 상위 호출자로 전파**됩니다.  
일반적으로 Spring MVC에서는 예외가 전파되면 **Spring의 기본 예외 처리 메커니즘이 적용**됩니다.  
따라서, 사용자는 아래와 같은 **에러를 JSON으로 받게 됩니다.**  

![에러 발생 메시지](https://github.com/hbkuk/board-web-spring/assets/109803585/54c22fc9-47cf-4f13-a50d-caec928a1b70)  

Spring의 기본 예외 처리 메커니즘에 따르게 된다면 **다음과 같은 문제점이 발생**합니다.  

- **에러 메시지 노출**: 클라이언트에게 예외의 **상세 정보가 노출**되므로, 보안상의 문제로 인한 악의적인 사용자는 이러한 정보를 악용하여 시스템에 대한 공격을 시도할 수 있습니다.
- **에러 처리의 일관성**: 서버의 **예외 처리가 일관되지 않으면, 클라이언트는 서로 다른 형식의 에러 응답을 처리**해야 합니다.

따라서, **예외를 적절하게 catch 후 처리**함으로써, 예측 가능한 **에러 응답을 제공하고 예외 정보를 적절하게 관리**해야 합니다.  

<br>

## 적절한 예외처리?  

예외처리를 위한 개선된 코드는 **BoardNotFoundException이 발생하면 해당 예외를 컨트롤러에서 catch 후 처리하는 구조**입니다. 

![서버 예외처리](https://github.com/hbkuk/board-web-spring/assets/109803585/d7288056-b360-461f-9361-7c38d585cde8) 

위 코드에서는 **e.getMessage()를 통해 예외 메시지**를 얻고, **HttpStatus.NOT_FOUND 상태코드**를 **ResponseEntity에 담아 클라이언트에게 반환**합니다.  

<br>

![응답 받은 사용자](https://github.com/hbkuk/board-web-spring/assets/109803585/80e8910d-ee46-414e-807d-4e0f17622cc4))  

<br>

## 동일한 HTTP Status Code(상태 코드)의 문제점

위에서 작성한 것과 같이 예외를 처리한다면 **다음과 같은 상황을 고려**해 봐야합니다.

- **Comment(댓글)이 존재하지 않다면 메시지와 함께 404 (NotFound)를 반환**한다.
- **File(댓글)이 존재하지 않다면 메시지와 함께 404 (NotFound)를 반환**한다.
- **Image(댓글)이 존재하지 않다면 메시지와 함께 404 (NotFound)를 반환**한다.

클라이언트에서는 어떤 예외인지에 따라서 **다르게 처리하는 로직이 요구**됩니다.
이때, 매번 **동일한 HTTP Status Code**라면 **Error Message를 참조해서 처리해야하는 상황이 발생**합니다.  

이러한 방법도 나쁘지는 않지만, **클라이언트와 서버가 불필요하게 결속**됨을 의미하고 **유지보수 측면에서 굉장히 불편**합니다.

<br>

따라서 해당 **서비스에서 정의한 Code가 필요한 상황**입니다.

가령 **클라이언트 측이 로그인에 실패한 경우 다음과 같은 응답을 반환**할 수 있다.  

```
{
    "error": "auth-0001",
    "message": "Incorrect username and password",
    "detail": "Ensure that the username and password included in the request are correct"
}
```  

<br>

### ErrorResponse: 예외 정보를 전달할 객체  

```
/**
 * API 예외 응답을 나타내는 클래스입니다.
 */
@Getter
@Setter
public class ErrorResponse {
    private String errorCode;
    private String message;
    private String detail;

    /**
     * ErrorResponse 생성자입니다.
     *
     * @param errorCode 예외 코드
     */
    public ErrorResponse(ErrorCode errorCode) {
        this.errorCode = errorCode.getCode();
        this.message = errorCode.getMessage();
    }
}

```  

필드에 대한 설명을 드리자면..

- **errorCode**: ErrorCode를 나타내는 필드
- **message**: 예외 메시지를 나타내는 필드
- **detail**: 추가적인 상세 정보를 담을 수 있는 필드  

해당 객체의 생성자는 **ErrorCode를 받아서 필드를 초기화**합니다.  

그렇다면, ErrorCode는 어떻게 구현하면 좋을까요?

<br>

### ErrorCode

```
/**
 * API 예외 코드를 정의한 열거형입니다.
 */
public enum ErrorCode {
    BOARD_NOT_FOUND("BOARD-002", "게시물을 찾을 수 없음"),
    INVALID_PASSWORD("BOARD-003", "잘못된 비밀번호");

    private final String code;
    private final String message;

    /**
     * ErrorCode 생성자입니다.
     *
     * @param code    예외 코드
     * @param message 예외 메시지
     */
    ErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }

    /**
     * 예외 코드를 반환합니다.
     *
     * @return 예외 코드
     */
    public String getCode() {
        return code;
    }

    /**
     * 예외 메시지를 반환합니다.
     *
     * @return 예외 메시지
     */
    public String getMessage() {
        return message;
    }
}
```  

그렇다면 예외가 발생했을 때 **어떻게 ErrorResponse 객체를 생성해서 응답으로 내려줄 수 있는지 확인**해보겠습니다.  

물론, 이전에 설명했던 것과 동일하게 **컨트롤러에서 catch 후 처리하는 것도 좋지만**, 

스프링 프레임워크에서 제공하는 기능 중 **@ControllerAdvice 어노테이션**을 사용하여 **전역 예외 처리를 담당하는 클래스**를 통해서 처리해보도록 하겠습니다.

<br>

```
@Slf4j
@ControllerAdvice // 전역 예외 처리를 담당하는 클래스, 컨트롤러에서 발생하는 예외를 처리
@RestController // JSON 형식으로 응답을 반환하는 컨트롤러
public class GlobalExceptionHandler {
    /**
     * BoardNotFoundException 예외 처리
     *
     * 예를 들어,
     *      게시글을 보기, 수정, 삭제 하려고 했을때, 해당 게시글이 없을 경우 예외를 던집니다.
     *
     * @param e 발생한 BoardNotFoundException 예외 객체
     * @return 응답 결과
     */
    @ExceptionHandler(BoardNotFoundException.class)
    public ResponseEntity handleBoardNotFoundException(BoardNotFoundException e) {
        log.error(e.getMessage());
        ErrorResponse errorResponse = new ErrorResponse(ErrorCode.BOARD_NOT_FOUND); // ErrorResponse 객체 생성
        errorResponse.setDetail(e.getMessage());

        return new ResponseEntity<>(errorResponse, HttpStatus.NOT_FOUND); // ErrorResponse 객체와 HttpStatus.NOT_FOUND를 함께 ResponseEntity로 감싸서 응답으로 반환
    }
}
```  


### 예외 발생 시 응답

![개선 후 응답](https://github.com/hbkuk/board-web-spring/assets/109803585/f9db0073-672a-4981-acd0-aba09f94ab16)























</div>