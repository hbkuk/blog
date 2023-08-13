<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>  

##### 해당 글은 Slack 웹훅 설정 및 의존성 추가에 대해서 설명하지 않습니다.

### Slack 알람 기능을 구현하게 된 계기  

현재 [NOW](https://github.com/hbkuk/now-back-end) 프로젝트는 **일정기간 테스트를 한 후 정식으로 서비스할 계획이 있습니다.**  

그러므로, 안정적이고 효율적인 서비스 제공을 위해 **서비스에 오류가 발생했을 때 다음과 같은 대응방안**을 생각했습니다.

- **신속한 상황 공유**
- **정확한 문제 식별과 추적**  

따라서, 다음과 같이 **`internal server error` 발생 시에 Slack으로 알림을 보내주도록 설정**하고자 합니다.  

![Slack 알람](https://github.com/hbkuk/now-back-end/assets/109803585/46410897-d2d5-4b35-abfc-f0b9db122e9f)

<br>
---

### Global Exception Advice의 Exception을 처리하는 핸들러 메서드  

그렇다면 **Slack으로 알람을 보내도록하는 핸들러 메서드는 어떻게 정의**해야할까요?  

<br>

지난 포스팅에서는 [상속을 활용한 Global Exception Handler 리팩토링](https://starting-coding.tistory.com/660)에 대한 내용을 작성했었습니다.  

간략하게 설명드리자면, 

`Controller`에서 `Exception`을 처리하던 로직을 **Global Exception Handler로 위임 후 다음과 같은 4가지의 예외를 처리**하도록 했습니다.  

- `BadRequest`: 클라이언트의 요청이 서버에서 처리할 수 없는 형식 또는 구문
- `Unauthorized`: 클라이언트가 인증되지 않은 상태에서 보호된 리소스에 접근
- `Forbidden`: 클라이언트가 인증은 되었지만 요청한 리소스에 대한 접근 권한이 없는 경우
- `Exception`: **예기치 못한 상황 발생**   

<br>

그렇다면 **Slack으로 알람을 보내는 상황은 `Exception`이 발생한 상황**입니다.  

저는 이를 Slack으로 알람을 전송하기 위한 용도로 사용할 수 있게, **`@SlackLogger` 라는 이름의 어노테이션을 정의**해서 아래와 같이 추가해주었습니다.

![전역예외어드바이스](https://github.com/hbkuk/now-back-end/assets/109803585/a09c5417-7099-4119-9946-7a93d876f88b)


그렇다면, 해당 **`unHandledExceptionHandler` 메서드는 다음과 같은 2가지 일을 수행**하는데요.

- 기존:  **클라이언트에게 예외 코드와, 예외 메시지 응답**  
- 추가: **Slack 채널에 예외가 발생한 메세지가 담긴 알람 전송**

<br>

그럼 이제 `@SlackLogger` 어노테이션에 대해서 살펴보겠습니다.  

### `@SlackLogger` 어노테이션

![SlackLogger 어노테이션](https://github.com/hbkuk/now-back-end/assets/109803585/53baa2ae-aa3c-4db6-a03e-36776899a5ab) 

- **`@Retention(RetentionPolicy.RUNTIME)`**: **런타임 환경에서도 어노테이션 정보를 활용**할 수 있다는 의미
- **`@Target(ElementType.METHOD)`**: **메소드에만 적용**될 수 있다는 것을 의미  

따라서, Spring AOP를 통해 **예외 핸들러가 실행되기 전 Slack 채널에 알람을 보내도록 구현**할 수 있습니다.  

<br>
---  

### `@SlackLogger` 어노테이션이 적용된 메서드에 대한 Aspect  

우선, 클래스부터 정의해보도록 하겠습니다.  

![Aspect정의](https://github.com/hbkuk/now-back-end/assets/109803585/6d2d4be0-6ef0-4bf0-9941-bd1ffd2f56fe)  

**`AuthenticationConext` 컴포넌트**는 현재 **사용자의 인증 상태를 관리하는 컴포넌트**인데요.  
**요청 범위 스코프로 설정**되어, 각각의 HTTP 요청마다 **별도의 인스턴스가 생성되고 관리**됩니다.  

<br>

그 아래 **알림 메세지를 전송하는 컴포넌트**는, 실제로 **알림 메시지를 전송하는 객체**인데요.  

다음과 같이 **`AlertSender` 인터페이스를 정의**했고, 이를 구현한 **`SlackAlertSender` 객체**는 다음과 같습니다.  

```
// AlertSender.java
/**
 * 알림 메시지를 전송하는 인터페이스
 */
public interface AlertSender {

    void send(String message);
}
```  

```
// SlackAlertSender.java
@Component
public class SlackAlertSender implements AlertSender {

    private static final String REQUEST_URI = "https://hooks.slack.com/services";

    @Value("${slack.webhook.url}")
    private String hookUri;

    /**
     * 주어진 메시지를 Slack으로 전송
     *
     * @param message 전송할 메시지 내용
     */
    @Override
    public void send(final String message) {
        WebClient.create(REQUEST_URI)
                .post()
                .uri(hookUri)
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(new MessageRequest(message))
                .retrieve()
                .bodyToMono(Void.class)
                .subscribe();
    }
}
```


<br>

그 다음으로는 **`@Before` 어노테이션을 사용하여 메서드 실행 전 실행되는 어드바이스를 정의**했습니다. 

![어드바이스 정의](https://github.com/hbkuk/now-back-end/assets/109803585/b4bf8527-0a34-45eb-8641-ea7e441cbe72)

- **메서드의 인자 개수가 1이 아닌 경우**, **"Slack Logger Failed : Invalid Used" 경고 로그**를 기록하고 종료
- **Exception 타입인 경우**, **Exception 객체를 추출하여 알림을 전송하고 종료**
- **SlackAlarmFailedEvent 타입인 경우**, **실패한 알림 이벤트를 처리하여 알림을 전송하고 종료** 

<br>

여기서 `Exception`이 발생했을 때,  

우선적으로, 다음과 같이 **예외 객체에서 예외 정보를 추출 후 포장된 예외 객체를 생성 후 반환**하도록 했는데요.

```
@Getter
@RequiredArgsConstructor
public class ExceptionWrapper {

    private final String exceptionClassName;
    private final String exceptionMethodName;
    private final int exceptionLineNumber;
    private final String message;

    public static ExceptionWrapper extractExceptionWrapper(final Exception calledException) {
        StackTraceElement[] exceptionStackTrace = calledException.getStackTrace();
        String exceptionClassName = exceptionStackTrace[0].getClassName();
        String exceptionMethodName = exceptionStackTrace[0].getMethodName();
        int exceptionLineNumber = exceptionStackTrace[0].getLineNumber();
        String message = calledException.getMessage();

        return new ExceptionWrapper(exceptionClassName, exceptionMethodName, exceptionLineNumber, message);
    }
```  

그 이유는 **현재 사용자의 정보도 같이 Slack으로 알람을 보내도록 하기 위함**입니다. 

추후 **어떤 사용자로 인해서 `Exception`이 발생했는지 확인 후 추가적인 조치**를 할 수 있다고 생각했습니다. 

```
/**
* 현재 사용자의 정보를 추출
* 사용자 정보가 인증되지 않은 경우 "NO AUTH"로 표시
*
* @return 현재 사용자의 정보 (인증되지 않은 경우 "NO AUTH").
*/
private String extractMember() {
    try {
        return String.valueOf(authenticationContext.getPrincipal());
    } catch (InvalidAuthenticationException e) {
        return "NO AUTH";
    }
}
```  

<br>

따라서, 전체 코드는 다음과 같습니다.  

```
/**
 * {@code @SlackLogger} 어노테이션이 적용된 메서드에 대한 Aspect
 *
 * 예외와 실패한 현재 사용자의 정보와 알림 이벤트를 Slack으로 로그 전송
 */
@Aspect
@Component
@Slf4j
@RequiredArgsConstructor
public class SlackLoggerAspect {

    private final AuthenticationContext authenticationContext;
    private final AlertSender alertSender;

    /**
     * {@code @SlackLogger} 어노테이션이 적용된 메서드 실행 전, 예외 정보나 실패한 알림 이벤트를 로그로 전송
     * 예외의 경우 예외 래퍼(ExceptionWrapper)를 추출하여 알림을 전송
     *
     * @param joinPoint Aspect가 적용된 메서드의 조인 포인트
     */
    @Before("@annotation(com.now.common.alert.SlackLogger)")
    public void sendLogForError(final JoinPoint joinPoint) {
        Object[] args = joinPoint.getArgs();
        if (args.length != 1) {
            log.warn("Slack Logger Failed : Invalid Used");
            return;
        }

        if (args[0] instanceof Exception) {
            ExceptionWrapper exceptionWrapper = extractExceptionWrapper((Exception) args[0]);
            alertSender.send(MessageGenerator.generate(extractMember(), exceptionWrapper));
            return;
        }

        if (args[0] instanceof SlackAlarmFailedEvent) {
            alertSender.send(MessageGenerator.generateFailedAlarmMessage((SlackAlarmFailedEvent) args[0]));
        }
    }

    /**
     * 현재 사용자의 정보를 추출
     * 사용자 정보가 인증되지 않은 경우 "NO AUTH"로 표시
     *
     * @return 현재 사용자의 정보 (인증되지 않은 경우 "NO AUTH").
     */
    private String extractMember() {
        try {
            return authenticationContext.getPrincipal();
        } catch (InvalidAuthenticationException e) {
            return "NO AUTH";
        }
    }
}

```

<br>
---

### 마무리  

이렇게 Spring AOP로 Slack 알람을 구현해보았습니다.  

제가 어떻게 구현했는지 조금 감이 오시나요?  

모든 코드는 아래 링크에서 확인 가능합니다.  
[코드 링크](https://github.com/hbkuk/now-back-end/tree/main/src/main/java/com/now/common/alert)  

부족한 코드이지만, 지속적인 개선을 통해서 더 나은 코드를 작성하고자 합니다.  

긴 글 읽어주셔서 감사합니다.  

</div>