<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>

### 디버깅을 위한 로깅(logging)  

프로젝트를 진행하다보니,  

애플리케이션이 **정상적으로 동작하는지 확인하기 위한 목적** 혹은  
**문제가 발생했을 때 원인을 파악하기 위한 디버깅을 목적**으로 메시지를 출력했습니다.  

이때 사용했던 **라이브러리는 Lombok**이며, **`@Slf4j` 어노테이션을 사용**했습니다.

<br>

### Contoller 핸들러 메서드에서 공통으로 등장하는 로깅 코드  

아래와 같이 **모든 `Controller` 핸들러 메서드에서는 무조건 로깅하는 코드가 포함**되어야 했습니다.  

![로깅](https://github.com/hbkuk/now-back-end/assets/109803585/464fe49e-332c-4fb5-a55c-dd8295c1d2bd)  

<br>  

이러한 상황이 발생하다보니 다음과 같은 문제점을 발견했습니다.  

- **로깅 코드 반복**
- **핵심 로직의 가독성 저하**

그렇다면, 전에 문서만 봐두고 써보진 않은 **`Spring AOP`를 통해 이러한 문제를 해결할 수 있지 않을까?** 라는 고민을 하게되었습니다.  

<br>

### 관심 분리를 위한 클래스 선언

**스프링 프레임워크**에서는 AOP를 구현할 때 사용하라는 의미로 **`@Aspect` 어노테이션을 제공**합니다.  

따라서 아래와 같은 클래스를 선언했습니다.  

![AOP 클래스 선언](https://github.com/hbkuk/now-back-end/assets/109803585/2969c5b7-c1ef-457b-9a69-ccf2df5ad52f)

<br>  

다음으로는, **메서드 레벨의 어노테이션을 기반으로 포인트컷(Pointcut)을 정의**했습니다.  

- <small>*포인트컷: 필터링된 조인포인트(클라이언트가 호출하는 모든 비즈니스 로직)를 의미*</small>

![포인트컷](https://github.com/hbkuk/now-back-end/assets/109803585/b8b3a824-0974-4901-a983-a65275fa4eb2)


<br>  

이렇게 정의된 포인트컷들은 **AOP 어드바이스(Advice)에서 사용**됩니다.  

- <small>*어드바이스: 횡단 관심에 해당하는 공통 기능의 코드를 의미, 동작시점을 before, after, after-returning, after-throwing, around 중 지정 가능*</small> 

따라서, **어드바이스인 횡단 관심사(cross-cutting concern)를 언제, 어디서, 어떻게 적용할지를 정의**를 해야합니다.  

#### 어드바이스 정의 - 요청 로그 기록

![Before](https://github.com/hbkuk/now-back-end/assets/109803585/9977939e-f8ca-4e0d-81f3-72a964c1390c)

**`postMapping()` 또는 `putMapping()` 포인트컷에 의해 선택된 메서드들이 실행되기 전에 실행**되는 메서드입니다.  

**`@Before` 어노테이션으로 선언되었기 때문에 메서드 실행 전에 수행**되며, 컨트롤러의 POST 또는 PUT **메서드가 호출될 때마다 로깅**합니다.

<br>

#### 어드바이스 정의 - 응답 로그 기록  

![AfterReturning](https://github.com/hbkuk/now-back-end/assets/109803585/70bec584-7090-47ab-a511-979234a88b5f)

**`controllerPointCut()` 또는 `exceptionHandlerCut()` 포인트컷에 의해 선택된 메서드들이 실행된 후에 실행**되는 메서드입니다.  

메서드가 정상적으로 종료되고, 메서드의 반환값인 **`ResponseEntity<?> response` 객체를 활용하여 응답 로그를 생성하고 로깅**합니다.  

#### 로깅
실제로 실행된다면 아래와 같이 출력됩니다.  

![로깅](https://github.com/hbkuk/now-back-end/assets/109803585/af44cb0b-5a81-48d2-b0a9-5e1c2972844b)

<br>

#### 전체 코드
```
package com.now.common.logging;

import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.Signature;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

import java.util.Arrays;

/**
 * 로깅 관련 기능을 수행하는 Aspect
 *
 * 컨트롤러의 메서드 호출 및 응답 로그 기록
 */
@Aspect
@Component
@Slf4j
public class LoggingAspect {

    @Pointcut("@annotation(org.springframework.web.bind.annotation.PostMapping)")
    private void postMapping() {
    }

    @Pointcut("@annotation(org.springframework.web.bind.annotation.PutMapping)")
    private void putMapping() {
    }

    @Pointcut("execution(* com.now.core..presentation.*Controller.*(..))")
    private void controllerPointCut() {
    }

    @Pointcut("@annotation(org.springframework.web.bind.annotation.ExceptionHandler)")
    private void exceptionHandlerCut() {
    }

    /**
     * 컨트롤러의 POST 또는 PUT 메서드 호출 시 요청 로그를 기록
     *
     * @param joinPoint Aspect가 적용된 메서드의 조인 포인트
     */
    @Before("postMapping() || putMapping()")
    public void requestLog(final JoinPoint joinPoint) {
        Signature signature = joinPoint.getSignature();
        log.info("[ REQUEST ] Controller - {}, Method - {}, Arguments - {}",
                joinPoint.getTarget().getClass().getSimpleName(),
                signature.getName(),
                Arrays.toString(joinPoint.getArgs()));
    }

    /**
     * 컨트롤러의 메서드 호출 또는 예외 핸들러 메서드 실행 후 응답 로그 기록
     *
     * @param joinPoint Aspect가 적용된 메서드의 조인 포인트
     * @param response  응답 객체
     */
    @AfterReturning(value = "controllerPointCut() || exceptionHandlerCut()", returning = "response")
    public void responseLog(final JoinPoint joinPoint, final ResponseEntity<?> response) {
        Signature signature = joinPoint.getSignature();
        log.info("[ RESPONSE ] Controller - {}, Method - {}, returnBody - {}",
                joinPoint.getTarget().getClass().getSimpleName(),
                signature.getName(),
                response.getBody());
    }
}

```

<br>  

### 마무리

이상으로, 공통으로 등장하는 로깅 코드인 횡단 관심과 사용자의 요청에 따라 실제로 수행되는 핵심 로직인 핵심 관심을 완벽하게 분리해봤습니다.  

앞으로도 핵심 관심과 횡단 관심을 분리할 수 있는 상황이 발생한다면, 위와 같은 방식으로 분리해보고자 합니다.  

긴 글 읽어주셔서 감사합니다.


</div>