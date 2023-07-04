<div class=markdown-body>  

##### 해당 글은 SpringBoot 개발 환경에 해결했던 내용입니다.  

## 존재하지 않는 API 요청의 응답

### 배경
SPA(Single Page Application) 기반 게시판 프로젝트에서 프론트, 백엔드 작업을 진행하다보니, 

**프런트에서 무언가를 요청**을 하면, 항상 **적절한 메시지를 응답**해줘야 한다는 생각을 가지게 되었습니다.

예를 들면, **프론트에서 요청 url을 실수로 잘못 입력**했을 경우, 
**서버에서는 해당 요청에 대해서 맵핑하지 않았으므로** 다음과 같은 응답을 받게 됩니다.

![기존 응답](https://github.com/hbkuk/now-back-end/assets/109803585/e8d0c4f0-95a3-4853-bef8-03f858d0b498)

위와 같은 상황에서 **아래와 같은 응답으로 개선**하고자 합니다.  

![기존 응답](https://github.com/hbkuk/now-back-end/assets/109803585/cc0aeaed-2d03-48d9-a248-0b904181011e)

---

## DispatcherServlet 들여다보기

`DispatcherServlet`의 `doDispatch` 메서드에서는  
**`mappedHandler`가 존재하지 않을 때 `noHandlerFound` 메서드가 실행**됩니다.  

이 메서드는 **`throwExceptionIfNoHandlerFound` 값에 따라 예외를 throw할지 여부를 결정**합니다.

**기본 설정은 false이므로, 404 응답**만을 보냅니다. 

```
public class DispatcherServlet {
  protected void doDispatch(...) throws Exception {
      // Determine handler for the current request.
      mappedHandler = getHandler(processedRequest);
      if (mappedHandler == null) {
          noHandlerFound(processedRequest, response);
          return;
      }
  }
  
  protected void noHandlerFound(HttpServletRequest request, HttpServletResponse response) throws Exception {
    if (this.throwExceptionIfNoHandlerFound) {
      throw new NoHandlerFoundException(request.getMethod(), getRequestUri(request),
        new ServletServerHttpRequest(request).getHeaders());
    }
    else {
      response.sendError(HttpServletResponse.SC_NOT_FOUND);
    }
  }
}
```  

그렇다면 **해당 설정을 `true`로 변경한다면 해결할 수 있을 것**으로 보입니다.  

설정을 해보겠습니다.

## DispatcherServletAutoConfiguration 설정 확인하기  

`DispatcherServletAutoConfiguration`은 **Spring Boot에서 해당 설정을 제공하기 위해 사용**됩니다. 

 **`setThrowExceptionIfNoHandlerFound` 메서드는 DispatcherServlet Bean을 생성할 때 DispatcherServletAutoConfiguration에서 적용**됩니다.  
 
 이 설정은 **`WebMvcProperties`의 속성에 따라 결정**됩니다.

 ```
 // DispatcherServletAutoConfiguration
@Bean(name = DEFAULT_DISPATCHER_SERVLET_BEAN_NAME)
public DispatcherServlet dispatcherServlet(WebMvcProperties webMvcProperties) {
  DispatcherServlet dispatcherServlet = new DispatcherServlet();
  dispatcherServlet.setDispatchOptionsRequest(webMvcProperties.isDispatchOptionsRequest());
  dispatcherServlet.setDispatchTraceRequest(webMvcProperties.isDispatchTraceRequest());
  dispatcherServlet.setThrowExceptionIfNoHandlerFound(webMvcProperties.isThrowExceptionIfNoHandlerFound());
  dispatcherServlet.setPublishEvents(webMvcProperties.isPublishRequestHandledEvents());
  dispatcherServlet.setEnableLoggingRequestDetails(webMvcProperties.isLogRequestDetails());
  return dispatcherServlet;
}
 ```  
 
## WebMvcProperties 설정하기  

 ```
 @ConfigurationProperties(prefix = "spring.mvc")
public class WebMvcProperties {
  private boolean throwExceptionIfNoHandlerFound = false;
  // 생략
}
 ```  

`@ConfigurationProperties`의 설정은 외부 properties에 prefix에 해당하는 값들을 읽어드려 사용할 수 있습니다.  

즉, `application.properties`에 **`spring.mvc.throw-exception-if-no-handler-found=true` 설정**을 하면 됩니다.

### ResourceHttpRequestHandler 가 매핑 

 현재까지 매핑되는 핸들러가 없다고 생각하고 설정을 했지만, 실제로는 **핸들러가 맵핑**되고 있습니다.  

 ![맵핑되는 핸들러](https://github.com/hbkuk/now-back-end/assets/109803585/6d060efb-146d-4b2f-85f8-11da790fb6ae)

 **존재하지 않는 요청 URL에 `ResourceHttpRequestHandler` 가 맵핑**되고 있었습니다. 
 
즉, 기본적으로 맵핑되는 **URL이 없으면 resource를 조회**하도록 설계되어 있고, 존재하지 않았을 때 **404의 에러 메시지를 응답**하는 것이다.  

### 모든 경우에서의 ResourceHandler 매핑 끄기
`WebMvcAutoConfiguration`의 `addResourceHandler` 메소드를 살펴보면 됩니다. 

`ResourceProperties`의 `addMapping`을 false로 설정하면 간단하게 해당 설정을 진행할 수 있습니다. 
SpringBoot의 버전에 따라, properties를 관리하는 방식이 다르므로 확인해보고 버전에 맞게 설정을 진행하면 됩니다.
``2.3.3 버전: spring.resources.add-mappings=false``
``2.4.5 버전: spring.web.resources.add-mappings=false``

### GlobalExceptionHandler에서 NoHandlerFoundException 처리
지금까지 과정을 진행함으로써, 잘못된 url의 요청이 왔을 때 NoHandlerFoundException을 throw하도록 수정했습니다.

이를 아래 코드와 같이 **`GlobalExceptionHandler`에서 예외를 처리**하도록 로직을 구현하면 됩니다.

```
@Slf4j
@ControllerAdvice
@RestController
public class GlobalExceptionHandler {
    ...

    /**
     * NoHandlerFoundException 예외처리
     *
     * @param e 발생한 NoHandlerFoundException 예외 객체
     * @return 응답 결과
     */
    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity handleNoHandlerFoundException(NoHandlerFoundException e) {
        log.error(e.getMessage());
        ErrorResponse errorResponse = new ErrorResponse(ErrorCode.INVALID_REQUEST);
        errorResponse.setDetail(ErrorCode.INVALID_REQUEST.getMessage());

        return new ResponseEntity<>(errorResponse, HttpStatus.NOT_FOUND);
    }
}
```

위 코드에서 **`ErrorResponse` 객체를 생성**할 때 **인자로 `ErrorCode.INVALID_REQUEST`를 전달하여 초기화**합니다.  

```
package com.study.ebsoft.exception;

// TODO: refactor: Bundle FIle
/**
 * API 예외 코드를 정의한 열거형입니다.
 */
public enum ErrorCode {
    INVALID_PARAM("PARAM-001", "형식에 맞지 않는 파라미터 전달"),
    INVALID_PASSWORD("BOARD-003", "잘못된 비밀번호"),

    INVALID_REQUEST("REQUEST-001", "잘못된 요청입니다.");
    ...

    private final String code;
    private final String message;

```


</div>