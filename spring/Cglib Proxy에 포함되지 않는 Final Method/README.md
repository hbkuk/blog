<div class=markdown-body>

모든 코드는 [github](https://github.com/hbkuk/blod-code/tree/main/spring/aop-not-working)를 참고해주세요.

# `Cglib Proxy`에 포함되지 않는 `Final Method`

토이 프로젝트에서 **`Server Error` 발생 시에 Slack으로 알림**을 보내주도록 설정했었는데요.  
해당 설정을 사내에서 진행했던 프로젝트에 적용하려고 했습니다.  
(궁금하신 분들은 [Spring AOP로 Slack 알람 구현](https://starting-coding.tistory.com/670) 포스팅을 참고해주세요.)

토이 프로젝트에서 적용했던 설정을 사내 프로젝트에 그대로 적용했지만,  
개발 서버에 정상적으로 배포 후, 제보를 받았어요.

> 클라이언트에서 `Server Error` 응답을 받았지만,  
> 슬랙 채널로 알림이 오지 않는데요?  

분명, 
`local`(로컬) 환경에서 테스트를 진행했었고, `dev`(개발) 환경에 정상적으로 배포되었는데 말이죠.

디버깅을 해보면서 확인해보니, 특정 `Exception Handler Method`에서만 슬랙 채널로 알림을 발송하지 않았어요.  

음... 무엇이 문제였을까요?    

결론적으로는, 상위(부모) 클래스를 `override`한`Exception Handler Method`만 `Cglib Proxy`에 포함되지 않았던 것이었어요.  
해당 포스팅은 **왜 `Cglib Proxy` 포함되지 않았던 것인지?** 분석을 해보았던 내용을 정리해보았어요.

## 프로젝트는 어떤 구조였는지?

먼저, 공통된 예외를 처리하는 `GlobalExceptionHandler` 에 대해서 먼저 살펴보는 것이 좋겠네요.  
(사내 프로젝트의 코드를 그대로 가져올 수 없어서, 최대한 간략한 코드로 대체할게요.)

![Global Exception Adivce 구조](https://github.com/hbkuk/blog/assets/109803585/b88f4b2b-db7f-4234-ba63-17f3f7056467)

```
@RestControllerAdvice
public class GlobalExceptionAdvice extends ResponseEntityExceptionHandler {

    // @ExceptionHandler(value = {BadRequestException.class})
    // etc...

    @SlackLogger
    @ExceptionHandler(value = {RuntimeException.class})
    protected ResponseEntity<ErrorResponse> handleRuntimeException(RuntimeException e) {
        return ResponseEntity.badRequest().body(new ErrorResponse(40000, e.getMessage()));
    }

    @SlackLogger
    @Override
    protected ResponseEntity<Object> handleExceptionInternal(
            Exception ex,
            Object body,
            HttpHeaders headers,
            HttpStatus status,
            WebRequest request
    ) {
        String errorMessage = "An unexpected error occurred: " + ex.getMessage();
        return new ResponseEntity<>(errorMessage, headers, status);
    }
}
```

제보를 받은 후,  
디버깅을 해보면서 확인을 해보니 `handleExceptionInternal` 메서드에서만 슬랙 채널로 알림이 발송되지 않았어요.  

우선 `handleExceptionInternal`메서드에 왜 `@Override` 어노테이션이 적용되었는지 확인해볼게요.  

## `ResponseEntityExceptionHandler` 상속

`GlobalExceptionAdvice` 클래스는 `ResponseEntityExceptionHandler` 추상 클래스를 상속받는 구조입니다.  

<div style="text-align: center;">
  <img src="https://github.com/hbkuk/blog/assets/109803585/7b446e0d-0348-4491-8ccf-91bcf38458e4" alt="ResponseEntityExceptionHandler 상속 구조">
</div>

`ResponseEntityExceptionHandler` 클래스에 대해서 잘 모르시는 분들을 위해 간단하게 설명해 드려볼게요. 

`Spring MVC`에서는 기본적으로 예외를 처리하기 위한 `ResponseEntityExceptionHandler` 추상 클래스를 제공하고 있어요.   
처리하는 예외 클래스 종류는 다음과 같습니다.  

![ResponseEntityExceptionHandler의 ExceptionHandler 종류](https://github.com/hbkuk/blod-code/assets/109803585/806305e7-8d3b-49e0-8491-6d8bce547e25)  
  
다음과 같이 예외를 내부적으로 처리하고, `ResponseEntity`를 생성하는 기본 메서드도 선언되어 있는데요.      
예외가 발생하면 최종적으로 아래 메서드를 호출해요.  

```
// ResponseEntityExceptionHandler.java

protected ResponseEntity<Object> handleExceptionInternal(
		Exception ex, @Nullable Object body, HttpHeaders headers, HttpStatus status, WebRequest request) {

	if (HttpStatus.INTERNAL_SERVER_ERROR.equals(status)) {
		request.setAttribute(WebUtils.ERROR_EXCEPTION_ATTRIBUTE, ex, WebRequest.SCOPE_REQUEST);
	}
	return new ResponseEntity<>(body, headers, status);
}
```

그렇다면 상속을 통해 예외가 발생하면 `ResponseEntity`를 생성 후 사용자에게 응답하는데,  
`GlobalExceptionAdvice` 클래스에서 메서드를 재정의하는 것에 대해서 의문을 가지실 수 있을 것 같아요.  

![메서드를 재정의](https://github.com/hbkuk/blog/assets/109803585/a02da4ef-3105-48ce-9b08-54348ef5e9bb)

간단하게 설명드리자면, 프로젝트의 개발자분들과 에러 응답 형식을 협의했었어요.  
따라서, 사내 서비스의 에러 응답 형식에 맞게 변경하기 위함이었습니다.

그렇다면 왜 해당 메서드가 실행될 때만, 슬랙으로 알림이 발송되지 않았던 것일까요?  

혹시 놓치고 있었던 부분이 있었을까요?  

## 애플리케이션 실행 로그


```
// application.yml

logging:
  level:
    org.springframework: DEBUG
```

`Spring Application`을 실행해보면, 다음과 같은 로그를 확인할 수 있습니다.

![애플리케이션 실행 로그](https://github.com/hbkuk/blod-code/assets/109803585/1eca61d8-e003-4f37-8581-8914efc5569b)

```
2024-06-29 02:43:26.204 DEBUG 24868 --- [           main] o.s.b.f.s.DefaultListableBeanFactory     : Creating shared instance of singleton bean 'aopNotWorkingApplication'
2024-06-29 02:43:26.205 DEBUG 24868 --- [           main] o.s.b.f.s.DefaultListableBeanFactory     : Creating shared instance of singleton bean 'slackAlertSender'
2024-06-29 02:43:26.205 DEBUG 24868 --- [           main] o.s.b.f.s.DefaultListableBeanFactory     : Creating shared instance of singleton bean 'slackLoggerAspect'
2024-06-29 02:43:26.206 DEBUG 24868 --- [           main] o.s.b.f.s.DefaultListableBeanFactory     : Autowiring by type from bean name 'slackLoggerAspect' via constructor to bean named 'slackAlertSender'
2024-06-29 02:43:26.206 DEBUG 24868 --- [           main] o.s.b.f.s.DefaultListableBeanFactory     : Creating shared instance of singleton bean 'globalExceptionAdvice'
2024-06-29 02:43:26.211 DEBUG 24868 --- [           main] o.s.b.f.s.DefaultListableBeanFactory     : Autowiring by type from bean name 'globalExceptionAdvice' via constructor to bean named 'slackAlertSender'
2024-06-29 02:43:26.226 DEBUG 24868 --- [           main] o.s.aop.framework.CglibAopProxy          : Final method [public final org.springframework.http.ResponseEntity org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler.handleException(java.lang.Exception,org.springframework.web.context.request.WebRequest) throws java.lang.Exception] cannot get proxied via CGLIB: Calls to this method will NOT be routed to the target instance and might lead to NPEs against uninitialized fields in the proxy instance.
```

로그를 확인해보니,**`CGLIB`을 사용하여 프록시를 생성**할 때 경고가 발생한 것을 확인할 수 있었어요.  
경고 내용은,  `ResponseEntityExceptionHandler` 클래스의 `handleException` 메서드는 `final` 메서드이기 때문에 `CGLIB`을 사용하여 프록시할 수 없다는 것을 알려주고 있습니다.  

그렇다면 `CGLIB`이 도대체 뭐길래 프록시를 생성할 수 없다는 것일까요?    
우선, `CGLIB`이라는 것이 무엇인지 확인해볼게요.

## `CGLIB`

`Spring`에서 동적으로 프록시 객체를 생성하기 위해 사용되는 라이브러리입니다.  
(동적으로 프록시 객체를 생성하는 방법은 `JDK Dynamic Proxy`도 있습니다. 궁금하신 분들은 찾아보셔도 좋을 것 같아요.)

`CGLIB`이 어떻게 동작하는 확인해볼게요.

![CGLIB](https://github.com/hbkuk/blod-code/assets/109803585/7454fae3-a056-46c4-99a2-ce2ab1ba402b)

1. `Client`가 메서드를 요청 
2. `CGLIB`은 메서드 처리를 `MethodInterceptor`에게 위임
3. `MethodInterceptor`가 부가 기능 수행
4. `Target`에게 기능 위임

위 내용이 조금 어려울 수 있는데요.
간단하게 예제 코드로 만들어볼게요.


### `RealService` 클래스
```
@Slf4j
public class RealService {

    public void perform() {
        log.info("Performing real service...");
    }
}
```

### `LoggerInterceptor` 클래스: 메서드 호출 전후 로그
```
@Slf4j
public class LoggerInterceptor implements MethodInterceptor {

    private final Object target;

    public LoggerInterceptor(Object target) {
        this.target = target;
    }

    @Override
    public Object intercept(Object o, Method method, Object[] objects, MethodProxy methodProxy)
        throws Throwable {
        log.info("실제 Method 호출 전 logging");
        Object result = methodProxy.invoke(target, objects);
        log.info("실제 Method 호출 후 logging");
        
        return result;
    }
}
```

### 테스트 

```
public class CGLIBProxyTest {

    /**
     * CGLIB (Code Generation Library)
     * : 동적으로 프록시 객체를 생성하기 위한 라이브러리
     * 
     * Enhancer
     * : CGLIB의 주요 클래스 중 하나, 프록시 객체를 생성하기 위해 사용
     */
    @Test
    void CGLIB_프록시_테스트() {
        RealService 실제_서비스 = new RealService();

        // Enhancer를 사용하여 프록시 객체 생성
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(RealService.class);
        enhancer.setCallback(new LoggerInterceptor(실제_서비스));

        // 프록시 객체 생성 및 메소드 호출
        RealService 프록시_서비스 = (RealService) enhancer.create();
        프록시_서비스.perform();
    }
}
```

테스트 결과를 한번 살펴볼게요.
![테스트 결과](https://github.com/hbkuk/blod-code/assets/109803585/56f32b49-3653-47ab-b77f-fed2cf9b0853)

위처럼 `perform` 메서드를 호출하면, 실제 메서드 실행 전후에 로그가 출력되는 것을 확인할 수 있어요.  
또한, 테스트 코드를 살펴보면 인터페이스가 아닌 클래스를 상속받아 프록시 객체를 생성하는 것도 확인해볼 수 있어요.  

## `CGLIB`의 `Proxy` 객체를 생성하는 방식

`CGLIB`을 통해 프록시 객체를 생성하는 방식은 내부적으로 부모 클래스를 상속받아 진행됩니다.

따라서, `CGLIB`을 사용하여 프록시를 생성할 때 발생했던 경고의 원인을 이해할 수 있습니다.  
`final` 키워드가 붙은 메서드는 하위 클래스에서 오버라이딩할 수 없으므로, `CGLIB`을 사용하여 프록시를 생성할 수 없었던 것입니다.      
![image](https://github.com/hbkuk/blog/assets/109803585/e0f26628-f0fd-4274-b44e-7444e60b9877)

## 구조 변경

따라서,  
해당 프로젝트에서는 `Spring AOP`를 활용해서 관심사를 분리할 수 없으니, 의존성을 주입받아 슬랙 채널로 알림을 보내도록 구조를 변경했어요.   

![구조 변경](https://github.com/hbkuk/blog/assets/109803585/76905000-31a1-42ce-bde0-8a17b39ff6a7)

### 마무리

지금까지 `Final Method`가 `Cglib Proxy`에 포함되지 않은 이유에 대해서 정리해보았습니다.  
많은 분들에게 제 경험이 도움이 되었기를 바랍니다. :)

---
### 참고 
- [JDK Dynamic Proxy vs CGLIB Proxy](https://suyeonchoi.tistory.com/81)
- [Spring 에서 왜 Private Method 는 Cglib Proxy 에 포함이 되지않을까?](https://devroach.tistory.com/86)

</div>