<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>

## Global Exception Handler

[SpringBoot 환경에서의 사용자 정의 예외 처리](https://starting-coding.tistory.com/652)  

이전 포스팅에서는 기존 Controller에서 Exception을 처리하던 로직을 **Global Exception Handler**로 위임 후 **`ErrorResponse` 객체를 생성해 응답**했습니다.  

<br>

하지만, **예외 클래스가 많아질수록 `GlobalExceptionHandler`에서 다음과 같은 문제**가 발생했습니다.  

- **코드 중복 발생**
    - 각 예외 클래스에서 코드를 중복하여 구현하면서 예외 처리 로직이 반복되어 작성
- **가독성 저하**
    - 예외를 처리하는 핸들러 메소드들이 여러 곳에 흩어져 있으면 가독성이 떨어지며 로직 파악이 어려움
- **확장성 제한**
    - 새로운 종류의 예외가 필요할 때마다 관련 핸들러 메소드를 개별적으로 작성  


왜 이런 상황이 발생했는지 확인해보겠습니다.  

<br>

우선, 예외가 발생하는 상황입니다.  

아래는 **`CommunityService` 객체**이며, 게시글을 수정할 때 **해당 게시글과 회원 정보를 먼저 확인**한다고 생각하시면 됩니다.

![예외 발생](https://github.com/hbkuk/now-back-end/assets/109803585/2772cd4f-dc34-4183-9f9c-5f32dc2e6117)  

<br> 

해당 **서비스 객체에서 예외가 발생했다고 가정**해보겠습니다.

그렇다면, 그 **예외를 처리하는 곳은 `GlobalExceptionHandler`** 일텐데요.  

어떻게 처리하는지 확인해보겠습니다.  

![동일한 로직](https://github.com/hbkuk/now-back-end/assets/109803585/859608f4-cfd8-47a8-bcd7-0abfe22f327e)  


두 개의 **핸들러 메서드의 중복되는 부분**은 다음과 같습니다.  

- **로그 기록**: 두 핸들러 메서드 모두 `log.error(e.getMessage(), e)`를 사용하여 예외를 로그에 기록합니다.
- **`ErrorResponse` 객체 생성**:  `ErrorResponse` 객체를 생성하고, 해당 메시지를 detail에 설정
- **HTTP 상태 코드**: `HttpStatus.BAD_REQUEST`를 반환하여 클라이언트에게 잘못된 요청을 나타내는 상태 코드 전달  

그렇다면, 우선적으로 중복되는 부분을 확인 후 **공통 로직을 메서드롤 추출해서 재사용**할 수 있습니다.  

```
@ExceptionHandler(InvalidMemberException.class)
public ResponseEntity<ErrorResponse> handleInvalidMemberException(InvalidMemberException e) {
    return handleException(e, HttpStatus.BAD_REQUEST);
}

@ExceptionHandler(InvalidPostException.class)
public ResponseEntity<ErrorResponse> handleInvalidPostException(InvalidPostException e) {
    return handleException(e, HttpStatus.BAD_REQUEST);
}

private ResponseEntity<ErrorResponse> handleException(Exception e, HttpStatus status) {
    log.error(e.getMessage(), e);

    ErrorResponse errorResponse = new ErrorResponse(ErrorCode.INVALID_DATA, e.getMessage());
    errorResponse.setDetail(e.getMessage());

    return new ResponseEntity<>(errorResponse, status);
}
```  

하지만, 향후 새로운 종류의 예외가 추가된다면 **`GlobalExceptionHandler`의 코드는 얼마나 방대**해질까요?  

<br>

## 상속을 통한 코드 재사용  

지금까지 봤던 예외 클래스를 클래스 다이어그램으로 표현해보겠습니다.  

![초기 상속구조](https://github.com/hbkuk/now-back-end/assets/109803585/f7f25857-f796-4a4b-abb4-2d6cecd4272f)  

현재는 **모든 예외 클래스가 `RuntimeException` 을 상속**받고 있습니다.  

<br>

그렇다면, **계층 구조를 형성해서 예외 처리를 체계적으로 관리할 수 있게 구조를 변경**하면 되지 않을까요?

저는 **예외를 크게 4가지 범주**로 나누어 생각해보았습니다.

- `BadRequest`: 클라이언트의 요청이 **서버에서 처리할 수 없는 형식 또는 구문**
- `Unauthorized`:  클라이언트가 **인증되지 않은 상태**에서 보호된 리소스에 접근
- `Forbidden`: 클라이언트가 **인증은 되었지만 요청한 리소스에 대한 접근 권한이 없는 경우**
- `Exception`: **예기치 못한 상황 발생**  



따라서, 4가지 범주로 나눈 것들 중 **`Exception` 은 제외한 나머지 3가지 예외에 대해서 `RuntimeException`을 상속**받도록 구조를 변경해보도록 하겠습니다.  

![개선된 상속구조](https://github.com/hbkuk/now-back-end/assets/109803585/450a7b16-45ac-4346-bb93-7000d69d80ba)  


이렇게 구조를 변경하면, `GlobalExceptionHandler`에서는 어떻게 이 예외를 처리하면 될까요?  

<br>


## 공통된 예외를 처리하는 GlobalExceptionHandler

![개선된 전역 예외 핸들러](https://github.com/hbkuk/now-back-end/assets/109803585/7d768676-fcbd-4130-ac4c-4b6666612722)  

상위 클래스인 **`BadRequestException`, `UnauthorizedException`, `ForbiddenException` 을 선언**하고 이를 상속하여 **여러 하위 클래스**를 만들면 됩니다.

이러한 계층 구조를 통해 **더 많은 예외 타입이 필요한 경우 계속해서 확장**할 수 있습니다.  

<br>

하지만, 여기서도 해결하지 못한 부분이 있는데요.  

그것은, **HTTP 상태코드는 예외 클래스마다 고정**되어 있지만, **`HTTP Body`에 어떠한 내용을 담아서 보내야하는지 결정**을 해야한다는 것입니다. 

또한, 그 내용은 `GlobalExceptionHandler`에서 결정하는 것이 아닌 **처음 예외를 던지는 객체에서 결정**해야합니다.  

<br>

## 처음 예외를 던지는 객체에서 ErrorType 결정  

아래는 이전에 봤던 **서비스 객체의 커뮤니티 게시글을 가져 메서드**인데요.

```
public Community getCommunity(Long postIdx) {
    Community community = postRepository.findCommunity(postIdx);
    if (community == null) {
        throw new InvalidPostException(ErrorType.NOT_FOUND_POST);
    }

    return community;
}
```  

위 코드에서 `InvalidPostException`을 던질 때 **`ErrorType.NOT_FOUND_POST`을 인자로 전달**하고 있습니다.  

이는, 예외를 발생시킬 때 사용되는 상수이며 **발생한 상황을 설명하기 위해 사용자 정의 예외 클래스에 정보를 전달**하는 데 사용됩니다.  

<br>

잠시 확인해보고 넘어가겠습니다.  

![에러타입 enum](https://github.com/hbkuk/now-back-end/assets/109803585/a65a5764-3122-4343-82fb-5b5aa21f4a0b)  

<br>

그렇다면, `InvalidPostException`이 상속받고 있는 **`BadRequestException`에게 어떻게 전달**을 해야할까요? 

```
/**
 * 게시글을 찾을 수 없는 상황에서 던져지는 Unchecked Exception.
 */
public class InvalidPostException extends BadRequestException {
    public InvalidPostException(ErrorType errorType) {
        super(errorType);
    }
}
```  

현재, `ErrorType`을 매개변수로 받아와서 **상위 클래스인 `BadRequestException`의 생성자를 호출**하고 있습니다.  

<br>

```
@Getter
public class BadRequestException extends RuntimeException {

    private final int code;

    public BadRequestException(final ErrorType errorType) {
        super(errorType.getMessage());
        this.code = errorType.getCode();
    }
}
```

`BadRequestException`의 생성자는 상위 클래스인 **`RuntimeException`의 생성자를 호출**하면서 **예외 메시지를 설정**하고 **code를 초기화**합니다.  

그렇다면, **`GlobalExceptionAdvice` 에서는 ErrorResponse 객체를 생성**하여 해당 예외의 **code와 message를 담아 클라이언트에게 응답**할 수 있습니다.  

```
// ErrorResponse.java
@NoArgsConstructor(access = AccessLevel.PRIVATE)
@Getter
public class ErrorResponse {

    private int errorCode;
    private String message;

    public ErrorResponse(final int errorCode, final String message) {
        this.errorCode = errorCode;
        this.message = message;
    }

    @Override
    public String toString() {
        return "ErrorResponse{" +
                "errorCode=" + errorCode +
                ", message='" + message + '\'' +
                '}';
    }
}
```

```
@ExceptionHandler(BadRequestException.class)
public ResponseEntity<ErrorResponse> badRequestExceptionHandler(final BadRequestException e) {
    log.warn("Bad Request Exception", e);
    return ResponseEntity.badRequest().body(new ErrorResponse(e.getCode(), e.getMessage()));
}
```  

## 마무리 

메서드의 수량이 점점 많아지고, 어떻게 리팩토링을 할지 고민이 있었습니다.  

이러한 구조로 해결한 것이 정답은 아니겠지만, 충분히 고민하고 이를 해결했던 경험이 생겨서 개인적으로는 만족합니다.  

앞으로도 가독성, 확장성을 고려한 리팩토링은 끊임없이 진행하려고 합니다.  

<br>

긴글 읽어주셔서 감사합니다.




</div>