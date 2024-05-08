<div class=markdown-body>

# 강결합된 구조를 이벤트 기반 구조로 변경하기(with. 트랜잭션 분리)

쿠폰(`Coupon`) 발급 시 해당 회원에게 알림이(`Notification`) 발송되어야 하는 요구사항으로 인해 **기존 프로덕션 코드가 수정되어야 했습니다.**    
<small>* 알림: 서비스 내 알림, 메일, SNS 알림 등을 의미합니다.</small>  

해당 요구사항을 파악 후 기존 쿠폰 서비스 객체에 알림 서비스 객체를 추가하는 방향을 고려했습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/05b55d59-1c3c-40d2-a42a-e3bc796019a5)  

그렇다면, 쿠폰 발급 시 알림이 발송되는 흐름은 다음과 같습니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/fe3ca8ee-9325-4303-92e6-e7faa73d61e5)

하나의 트랜잭션으로 진행되다보니, 다음과 같은 문제점을 발견했습니다.  

1. 보조 업무인 **알림 발송이 실패할 경우**, 핵심 업무인 **쿠폰 발급이 실패할 수 있다.**   
    - <small>핵심 업무(Core Business): 쿠폰을 발급하는 로직</small>
   - <small>보조 업무(Auxiliary Business): 쿠폰이 발급되었다는 알림을 발송하는 로직</small>
2. 알림 발송이 지연될 경우, **롱 트랜잭션(`Long Transaction`)으로 진행되어 트랜잭션 경합이 발생할 수 있다.**

이러한 문제점을 해결하기 위해서, 강결합된 구조를 약결합된 구조로 변경해야만 했습니다.    
결론적으로는 약결합된 구조로 변경하기 위해서 `Spirng Event`를 활용했습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/8f091f13-caea-4f2c-89fe-117bff2f6f38)

해당 포스팅에서는 여러가지 시도 끝에 **약결합된 구조로 변경하기까지의 과정을 소개합니다.**

## 기존 쿠폰을 발급하는 프로덕션 코드

알림 발송 로직이 추가되기 전, 쿠폰을 발급하는 프로덕션 코드에 대해서 살펴보겠습니다.

![image](https://github.com/hbkuk/shop/assets/109803585/fc26c75c-92cb-4697-8034-f38e0f6d574d)

알림 발송 로직을 추가하기 위해서,  
기존 쿠폰을 발급하는 서비스 메서드에서 **알림 서비스의 알림을 발송 메서드를 호출하는 방향**을 고려했습니다.   

![강하게 결합된 서비스 코드](https://github.com/hbkuk/shop/assets/109803585/d088acec-4dff-4a67-852f-9b9936c9539a)

테스트 코드를 작성해서 쿠폰 발급 시 알림이 발송되는지 확인해볼까요?  
성공, 실패 케이스 모두 작성해보았습니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/d2f36327-33d4-4ce1-a146-bfdcbbf9a8b7)

두 테스트 코드는 모두 성공했으나, 다음과 같은 문제점을 발견할 수 있었습니다.  

1. 보조 업무인 **알림 발송의 실패로 인해**, 핵심 업무인 **쿠폰 발급이 실패하는 상황이 발생**할 수 있다.  
2. 알림 발송이 지연될 경우, **롱 트랜잭션(`Long Transaction`)으로 진행되어 트랜잭션 경합이 발생**할 수 있다.

두 문제를 해결하기에 앞서, 어떠한 문제인지 조금 더 자세히 살펴보겠습니다.  

### 보조 업무가 실패할 경우, 핵심 업무가 실패하는 상황

아래 사진은 정상적으로 쿠폰 발급이 진행되는 상황입니다.    

![image](https://github.com/hbkuk/shop/assets/109803585/fb614301-3ff7-4048-88d0-d9be31c229eb)

반대로, 정상적으로 쿠폰 발급이 진행되지 않는 상황은 어떠한 상황일까요?      

**쿠폰의 수량이 부족**하거나 **발급할 수 없는 삭제, 발급 중단 상태**일 경우를 예로 들수 있습니다.  
그렇다면, 알림 또한 발송되지 않도록 처리해야합니다.    

우선 쿠폰을 발급하다가 실패하는 경우를 확인해보겠습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/6c638b82-b3f3-4e2b-b227-c0475b7338c2)

쿠폰이 정상적으로 발급되었으나 알림이 발송이 실패하는 상황을 확인해보겠습니다.        

![image](https://github.com/hbkuk/shop/assets/109803585/de0b8845-e94f-42dc-b947-38947aace326)

위처럼 알림 발송이 실패한 경우, 쿠폰 발급 또한 실패했다고 처리하는 것이 좋은 방향일까요?    
**알림 발송만 재시도하도록 처리하는게 좋은 방향이지 않을까요?**    

다른 문제도 상세하게 확인해보겠습니다.  

### 롱 트랜잭션(`Long Transaction`)으로 진행되어 트랜잭션 경합 발생

다음과 같은 상황을 가정해보았습니다.

![image](https://github.com/hbkuk/shop/assets/109803585/4ad25315-f571-4352-92f9-9268a11d08fb)

쿠폰 발급은 비교적 빠르게 처리되었지만, **알림 발송은 네트워크 지연으로 인해 많은 시간이 소요**되었다면 어떻게 될까요?  
만약 쿠폰을 발급하는 과정에서 테이블 전체에 `Lock`을 걸었다면요?  

다른 트랜잭션은 해당 트랜잭션이 종료(`commit`)될 때까지 대기하게되는 상황이 발생하게 되는데요.  
이는 서비스의 성능 저하로 이어지게 될 것으로 예상됩니다.  

이는 과연 좋은 설계라고 할 수 있을까요?  
두 문제를 모두 해결할 수 있는 방법은 무엇일까요?      

우선 두 문제 모두 하나의 트랜잭션으로 진행되는 것에서 발생되는 문제이므로,  
트랜잭션을 분리할 수 있는 방법 중 시도해볼 만한 방법은 **전파 속성일 것으로 예상됩니다.**

## 트랜잭션 전파 속성(Transaction propagation) 활용

전파 속성을 활용해서 기존 트랜잭션을 분리하는 방향으로 진행해보겠습니다.    

`Spring`에서 다음과 같이 총 7가지의 전파 속성을 제공하고 있습니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/da77a3bd-b2e0-4de0-a972-fcdc78bb8207)
<small>출처: [[Spring] 스프링의 트랜잭션 전파 속성(Transaction propagation) 완벽하게 이해하기](https://mangkyu.tistory.com/269)</small>

7가지의 전파 속성 중 트랜잭션이 **항상 새로 생성되는 것은 `REQUIRES_NEW`, `NESTED`** 입니다.   
그렇다면 트랜잭션이 분리된다는 의미이기도 하니, 기존 코드에 전파 속성을 추가해볼까요?  

### REQUIRES_NEW: 항상 새로운 트랜잭션 생성

전파 속성 `REQUIRES_NEW`을 추가해서,   
핵심 업무인 **쿠폰 발급을 부모 트랜잭션으로 진행**되도록 하고, 보조 업무인 **알림 발송을 자식 트랜잭션으로 진행**되도록 해보겠습니다.  

우선 정상적으로 쿠폰이 발급되고 알림이 발송되는 상황입니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/75caae53-4ce3-4a64-9198-0fbb573bcc76)

그렇다면 정상적으로 쿠폰이 발급되지 않는 상황을 살펴보겠습니다.    
두 가지 상황으로 나누어볼 수 있을 것 같습니다.
- 부모 트랜잭션에서 예외가 발생하는 상황
- 자식 트랜잭션에서 예외가 발생하는 상황

부모 트랜잭션에서 예외가 발생하는 상황은 다음과 같습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/103114b4-f9c3-4f47-b8d9-b146894c3364)

이런...!  
쿠폰이 발급되지 않았는데, 알림이 발송되는 상황이 발생합니다.  

결론적으로는 해당 전파 속성으로는 문제를 해결하지 못하는 것으로 정리할 수 있겠는데요.  
이대로 끝내기는 아쉬워서, 자식 트랜잭션에서 예외가 발생하는 상황까지 살펴보겠습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/09ad1949-5edf-4c63-8e74-0952d7bf2c48)

네? 왜 부모 트랜잭션까지 `roll-back` 된 것일까요?      
`REQUIRES_NEW` 전파 속성이 적용되지 않은 것일까요?      

**`REQUIRES_NEW` 전파 속성은 부모 트랜잭션과 자식 트랜잭션이 개별적으로 진행**되는 것으로 알고있는데요.   
하지만 **자식 트랜잭션에서 예외가 발생하니 부모 트랜잭션까지 `roll-back`** 되었습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/93e1e950-3329-49e5-9fc5-57dc0dc0b225)

잘 생각해보면 트랜잭션이 분리되어 있는 것이지, `Thread`가 분리되어서 독립적으로 실행되는 것이 아니었습니다.  

다시 정리해보자면, **자식 트랜잭션에서 예외가 발생했고 해당 예외를 잡아서 적절한 처리를 하지 않자 부모 트랜잭션까지 전파**된 것입니다.    

다른 전파 속성으로 시도해볼까요?  

### NESTED: 중첩(자식) 트랜잭션 생성

`NESTED` 전파 속성은 독립적인 트랜잭션을 생성하는 `REQUIRES_NEW`와는 다르게 **중첩(자식) 트랜잭션을 생성**합니다.  
해당 중첩 트랜잭션은 **부모 트랜잭션의 영향을 받지만**, 중첩 트랜잭션이 **부모 트랜잭션에 영향을 주지 않습니다.**  

![image](https://github.com/hbkuk/shop/assets/109803585/c6f57ed5-29b5-4beb-a6df-64a1d876eb53)

그렇다면 다음과 같이 진행되는 것으로 정리해볼 수 있을 것 같습니다.  

1. 쿠폰 발급이 실패하는 경우, 알림도 발송되지 않는다.
2. 알림 발송이 실패하는 경우, 쿠폰은 정상적으로 발급된다.

아주 좋은 방법을 찾은 것 같습니다.    
그렇다면, `NESTED` 전파 속성을 통해 **두 가지 문제 중 첫 번째 문제는 해결 가능한 것으로 정리**하면 되겠네요.  

- [X] 보조 업무인 알림 발송의 실패로 인해, 핵심 업무인 쿠폰 발급이 실패하지 않아야 한다.  
- [ ] 핵심 업무인 쿠폰 발급과 보조 업무인 알림 발송은 서로 다른 트랜잭션으로 실행되어야 한다.

하지만, [공식문서](https://docs.spring.io/spring-framework/docs/4.3.4.RELEASE/javadoc-api/index.html?org/springframework/orm/hibernate5/HibernateTransactionManager.html)를 확인해보면 `Hibernate`는 중첩된 트랜잭션을 지원하지 않는다고 합니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/523cf843-4f44-4578-8cc7-a4ee0f8b5733)
출처: [https://docs.spring.io/spring-framework/docs/4.3.4.RELEASE/javadoc-api/index.html?org/springframework/orm/hibernate5/HibernateTransactionManager.html](https://docs.spring.io/spring-framework/docs/4.3.4.RELEASE/javadoc-api/index.html?org/springframework/orm/hibernate5/HibernateTransactionManager.html)

그렇다면, 트랜잭션의 전파 속성으로는 두 문제 모두 해결할 수 없다고 결론을 내리겠습니다.  

다른 방법은 무엇이 있을까요?  

## Spring Event: ApplicationEventPublisher

`Spring Event`는 스프링 프레임워크를 사용할 때 Bean 간 데이터를 주고받는 방식 중 하나입니다.  
간단하게 설명하자면 Bean 간 `Event`를 발행(Publish)하고 `Event`를 수신 또는 구독하여 소비(Listen/Subscribe)합니다.  

우선 용어를 명확하게 정리하고 넘어가면 좋을 것 같습니다.  

- `Event(이벤트)`
  - 빈(Bean) 간에 전달할 데이터를 담고 있는 `POJO(Plain Old Java Object)`
  - 주로 어떤 상황이나 조건에 대한 정보 저장
- `Publisher(발행자)`
  - 이벤트를 발행하는 Bean
- `Listener(수신자)`
  - 특정 이벤트를 처리하는 Bean

![image](https://github.com/hbkuk/shop/assets/109803585/7337e5de-6e4c-4cd1-a488-f2b180d8dd0c)

우선, 이벤트를 발행하기 위해서 **이벤트로 사용할 객체를 정의**해야 합니다.  

### 이벤트 객체 정의
```
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class NotificationEvent {

    private List<String> memberEmails;

    private String adminEmail;

    private NotificationType notificationType;

    public static NotificationEvent of(List<String> memberEmails, String adminEmail, NotificationType notificationType) {
        return new NotificationEvent(memberEmails, adminEmail, notificationType);
    }
}
```

### 이벤트 발행을 위한 클래스 정의

이벤트를 발행하기 위한 클래스 정의해야 합니다.  

알림 이벤트를 포함해서 **향후 다양한 이벤트를 발행할 수 있도록 공통 클래스를 정의**했습니다.  
아래 `publish` 메서드를 확인해보면, `Object` 데이터 타입을 가진 인자를 전달해서 이벤트를 발행할 수 있습니다.  

```
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class Event {

    private static ApplicationEventPublisher applicationEventPublisher;

    static void setApplicationEventPublisher(final ApplicationEventPublisher applicationEventPublisher) {
        Event.applicationEventPublisher = applicationEventPublisher;
    }

    public static void publish(final Object event) {
        if (applicationEventPublisher != null) {
            applicationEventPublisher.publishEvent(event);
        }
    }
}
```

```
@Configuration
@RequiredArgsConstructor
public class EventConfig {

    private final ApplicationContext applicationContext;

    @Bean
    public InitializingBean eventsInitializer() {
        return () -> Event.setApplicationEventPublisher(applicationContext);
    }
}

```

### 이벤트 수신 후 처리하기 위한 클래스 정의

발행한 이벤트를 수신 후 처리하기 위한 클래스 정의해야 합니다.  

```
@Component
@RequiredArgsConstructor
public class NotificationEventHandler {

    private final NotificationService notificationService;

    @EventListener
    public void onNotificationEvent(NotificationEvent event) {
        notificationService.send(event.getMemberEmails(), event.getAdminEmail(), event.getNotificationType());
    }
}

```

### 이벤트를 발행하는 프로덕션 코드

기존 쿠폰을 발급하는 코드에서 알림 이벤트를 발행하는 로직은 다음과 같이 구성될 수 있습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/a4176228-2c5d-4cc6-99c8-d8f9c5937ae3)

테스트 코드를 통해 확인해볼까요?  

![image](https://github.com/hbkuk/shop/assets/109803585/095cab4c-1e9a-4369-9669-5cb2fa4d0f7c)

기능이 정상적으로 구현되었음을 확인했습니다.   
아래 흐름도 같이 확인해주시면 좋을 것 같습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/8f357aed-c9ce-41fd-af25-c64ee282061c)

하지만 여전히 두가지 문제를 해결하지 못했습니다.

- [ ] 보조 업무인 알림 발송의 실패로 인해, 핵심 업무인 쿠폰 발급이 실패하지 않아야 한다.
- [ ] 핵심 업무인 쿠폰 발급과 보조 업무인 알림 발송은 서로 다른 트랜잭션으로 실행되어야 한다.

위 흐름도를 보면, 하나의 트랜잭션 안에서 동기적으로 동작하는 것으로 확인할 수 있습니다.     
비동기적으로 동작하게 한다면, 두 문제를 해결할 수 있을 것으로 예상됩니다.  

### Spring Event

기본적으로 `Spring Event`는 동기적으로 동작합니다.  
즉, 이벤트가 발행되면 모든 `Listener`가 이벤트 처리를 완료할 때까지 `Thread`가 차단된 후 진행되는 것을 의미합니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/7cd3d9bd-da75-421e-875e-bc84604a57ac)
<small>출처: https://medium.com/@cizek.jy/spring-events-make-your-code-more-flexible-946951ba8e9f</small>  

그렇다면 비동기적으로 동작하게 변경해보겠습니다.  

### Async 

동기적으로 동작하는 `Spring Event`를 비동기적으로 동작하도록 설정하기 위해서 다음과 같은 설정이 필요합니다.

- `@EnableAsync` 어노테이션 추가  
   ![image](https://github.com/hbkuk/shop/assets/109803585/2f3600a8-0aaf-4700-ad77-a163a814f736)

- 비동기적으로 동작해야 하는 `Listener`에 `@Async` 어노테이션 추가  
   ![image](https://github.com/hbkuk/shop/assets/109803585/6c806d33-68d3-4976-8e5e-d824a8df7d3e)

그렇다면 다음과 같이 비동기적으로 동작합니다.    

![image](https://github.com/hbkuk/shop/assets/109803585/7d7a8af8-b140-4385-9c89-c888735ae4fe)
<small>출처: https://medium.com/@cizek.jy/spring-events-make-your-code-more-flexible-946951ba8e9f</small>  

비동기 설정까지 했으니, 두가지 문제를 해결할 수 있다고 정리할 수 있습니다.   

- [X] 보조 업무인 알림 발송의 실패로 인해, 핵심 업무인 쿠폰 발급이 실패하지 않아야 한다.
- [X] 핵심 업무인 쿠폰 발급과 보조 업무인 알림 발송은 서로 다른 트랜잭션으로 실행되어야 한다.

하지만 다른 문제를 발견할 수 있는데요.

![image](https://github.com/hbkuk/shop/assets/109803585/256f2f47-999c-4522-9f9b-1fb505cb58e3)

쿠폰 발급 중 예외가 발생하여 트랜잭션이 `roll-back` 되었음에도 알림이 전송되는 문제가 있습니다.  
즉, 핵심 업무가 실패했지만 보조 업무는 성공하는 상황입니다.  

이는 비동기적으로 실행되면서 트랜잭션이 분리되어 발생하는 현상입니다.  
이 문제를 해결하기 위해서는 특정 트랜잭션이 정상적으로 종료될 때까지 이벤트 처리를 지연시키면 될 것으로 예상됩니다.

그런 방법이 있을까요?  

## @TransactionalEventListener

`Spring`은 특정 트랜잭션 결과가 나올 때까지 이벤트 처리를 지연시킬 수 있는 방법을 제공하고 있습니다.    
적용하는 방법은 `@EventListener` 어노테이션 대신 `@TransactionalEventListener(phase = <phase>)` 어노테이션을 사용하면 됩니다.  

`phase` 속성은 아래 내용을 참고해주세요.  

![image](https://github.com/hbkuk/shop/assets/109803585/3383cf3a-d2ba-49b2-94bf-1591a28cfca7)  
<small>출처: https://medium.com/@cizek.jy/spring-events-make-your-code-more-flexible-946951ba8e9f</small>

`phase` 속성 값은 4가지이며, 일반적으로 `AFTER_COMMIT` 이 적용하기 적합한 경우가 많다고 합니다.  

- `BEFORE_COMMIT`(트랜잭션 commit 되기전)
- `AFTER_COMMIT`(트랜잭션이 성공했을 때 실행)
- `AFTER_ROLLBACK`(트랜잭션 롤백시 실행)
- `AFTER_COMPLETION`(트랜잭션 완료시 실행(`AFTER_COMMIT+AFTER_ROLLBACK`))

현재 상황에서 적합한 속성 값은 `AFTER_COMMIT` 이므로 다음과 같이 적용해보겠습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/d9b321cd-9fbb-4fbc-b3ae-f98cfe4035e6)

테스트 코드를 실행해보겠습니다.    

![image](https://github.com/hbkuk/shop/assets/109803585/2df00933-e33c-4a53-b2e8-7b403eda5046)

네? 테스트는 실패했습니다.  
왜 실패할까요?

![image](https://github.com/hbkuk/shop/assets/109803585/a4d0b6a4-2166-4443-89b8-9dadb9f3fdb0)

위 흐름을 살펴보면 하나의 `Thread`에서 트랜잭션이 종료 후, 새로운 트랜잭션이 다시 시작되었습니다.    
하지만 기존 트랜잭션이 종료될 때, 이미 데이터베이스 커넥션을 반납했다는 의미이기도 합니다.  

따라서, 새로운 트랜잭션에서 작업한 내용은 데이터베이스에 반영이 되지 않습니다.   

해당 내용은 `@TransactionalEventListener` 어노테이션 상단 주석에서도 언급되고 있으니, 궁금하신 분들은 확인해보면 좋을 것 같습니다.    
![image](https://github.com/hbkuk/shop/assets/109803585/9af669a3-f9f3-4690-803f-a85d9bd7535d)

그렇다면 어떻게 해결하는 것이 좋을까요?

새로운 커넥션을 사용하도록 수정해주면 될 것을 예상됩니다.  
따라서, 이벤트 리스너를 별도의 `Thread`에서 진행하도록  `@Async` 어노테이션을 추가해주는 방법을 선택했습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/16d46cda-0b1c-45b9-aac1-2d3971d0052c)


### 마무리

지금까지 여러가지 시도 끝에 **약결합된 구조로 변경하기까지의 과정을 소개해드렸습니다.  
많은 분들에게 제 경험이 도움이 되었기를 바랍니다. :)

---
### 참고 

- [Spring Event](https://www.nextree.io/spring-event/)
- [Spring events — make your code more flexible](https://medium.com/@cizek.jy/spring-events-make-your-code-more-flexible-946951ba8e9f)
- [Transaction REQUIRES_NEW 옵션 Rollback 이슈!](https://velog.io/@meong/Transaction-REQUIRESNEW-%EC%98%B5%EC%85%98-%EC%82%AC%EC%9A%A9-%EC%8B%9C-Rollback-%EC%B2%98%EB%A6%AC)
- [[Spring] Transactional REQUIRES_NEW 옵션에서 예외 및 Rollback](https://devoong2.tistory.com/entry/Spring-Transactional-REQUIRESNEW-%EC%98%B5%EC%85%98%EC%97%90%EC%84%9C%EC%9D%98-%EC%98%88%EC%99%B8-%EB%B0%8F-Rollback)
- [[Spring] 스프링의 트랜잭션 전파 속성(Transaction propagation) 완벽하게 이해하기](https://mangkyu.tistory.com/269)
- [이벤트 기반, 서비스간 강결합 문제 해결하기 - ApplicationEventPublisher](https://velog.io/@znftm97/%EC%9D%B4%EB%B2%A4%ED%8A%B8-%EA%B8%B0%EB%B0%98-%EC%84%9C%EB%B9%84%EC%8A%A4%EA%B0%84-%EA%B0%95%EA%B2%B0%ED%95%A9-%EB%AC%B8%EC%A0%9C-%ED%95%B4%EA%B2%B0%ED%95%98%EA%B8%B0-ApplicationEventPublisher)
- [스프링 이벤트를 활용해 로직간 강결합을 해결하는 방법](https://velog.io/@eastperson/%EC%8A%A4%ED%94%84%EB%A7%81-%EC%9D%B4%EB%B2%A4%ED%8A%B8%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%B4-%EB%A1%9C%EC%A7%81%EA%B0%84-%EA%B0%95%EA%B2%B0%ED%95%A9%EC%9D%84-%ED%95%B4%EA%B2%B0%ED%95%98%EB%8A%94-%EB%B0%A9%EB%B2%95)
</div>