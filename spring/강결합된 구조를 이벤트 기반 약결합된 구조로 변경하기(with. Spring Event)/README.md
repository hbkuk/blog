<div class=markdown-body>

# 강결합된 구조를 이벤트 기반 구조로 변경하기(with. 트랜잭션 분리)

쿠폰(`Coupon`) 발급 시 해당 회원에게 알림이(`Notification`) 발송되어야 하는 요구사항으로 인해 기존 프로덕션 코드가 수정되어야 했습니다.    

해당 요구사항을 파악 후 기존 쿠폰 서비스 객체에 알림 서비스 객체를 추가하는 방향을 고려했습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/05b55d59-1c3c-40d2-a42a-e3bc796019a5)  

그렇다면, 쿠폰 발급 시 알림이 발송되는 흐름은 다음과 같습니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/fe3ca8ee-9325-4303-92e6-e7faa73d61e5)

하나의 트랜잭션으로 진행되다보니, 다음과 같은 문제점을 발견했습니다.  

1. 보조 업무인 알림 발송이 실패할 경우, **핵심 업무인 쿠폰 발급이 실패할 수 있다.**   
2. 알림 발송이 지연될 경우, 롱 트랜잭션(`Long Transaction`)으로 진행되어 트랜잭션 경합이 발생할 수 있다.

이러한 문제점을 해결하기 위해서, 강결합된 구조를 약결합된 구조로 변경해야만 했습니다.    
결론적으로는 약결합된 구조로 변경하기 위해서 `Spirng Event`를 활용했습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/8f091f13-caea-4f2c-89fe-117bff2f6f38)

해당 포스팅에서는 **`Spirng Event` 활용해서 약결합된 구조로 변경하기까지의 과정을 소개합니다.**

## 기존 쿠폰을 발급하는 프로덕션 코드

알림 발송 요구사항이 추가되기 전, 쿠폰을 발급하는 프로덕션 코드에 대해서 살펴보겠습니다.       
<small>* 알림: 서비스 내 알림함, 메일, SNS 알림 등을 의미합니다.</small>  

![image](https://github.com/hbkuk/shop/assets/109803585/fc26c75c-92cb-4697-8034-f38e0f6d574d)

현재 코드에서 쿠폰 발급 시 회원에게 알림을 발송해야한다는 요구사항이 추가되었으며,  
기존 쿠폰 서비스 객체에 알림 서비스 객체를 추가하는 방향을 고려했습니다.  

![강하게 결합된 서비스 코드](https://github.com/hbkuk/shop/assets/109803585/d088acec-4dff-4a67-852f-9b9936c9539a)

알림 서비스 객체를 추가했으니, 테스트 코드를 작성해서 확인해보았습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/d2f36327-33d4-4ce1-a146-bfdcbbf9a8b7)

테스트 코드는 모두 성공했으나, 다음과 같은 문제점을 발견할 수 있었습니다.  

1. 보조 업무인 알림 발송의 실패로 인해, 핵심 업무인 쿠폰 발급이 실패하는 상황이 발생할 수 있다.  
2. 알림 발송이 지연될 경우, 롱 트랜잭션(`Long Transaction`)으로 진행되어 트랜잭션 경합이 발생할 수 있다.

<small>핵심 업무(Core Business): 쿠폰을 발급하는 로직</small>  
<small>보조 업무(Auxiliary Business): 쿠폰이 발급되었다는 알림을 발송하는 로직</small>

발견한 문제에 대해서 자세히 살펴보겠습니다.  

### 보조 업무가 실패할 경우, 핵심 업무가 실패하는 상황

정상적으로 쿠폰 발급이 진행되는 상황은 다음과 같습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/fb614301-3ff7-4048-88d0-d9be31c229eb)

반대로, 쿠폰 발급이 정상적으로 진행되지 않는 상황은 어떤 상황이 있을까요?    

쿠폰의 수량이 부족하거나 해당 쿠폰이 발급할 수 없는 상태일 경우를 예로 들수 있습니다.    
그렇다면, 쿠폰이 정상적으로 발급되지 않은 경우 알림도 발송되지 않아야합니다.

![image](https://github.com/hbkuk/shop/assets/109803585/6c638b82-b3f3-4e2b-b227-c0475b7338c2)

하지만, 쿠폰이 정상적으로 발급되었으나 알림이 발송이 실패하는 상황은 어떻게 되어야할까요?  

![image](https://github.com/hbkuk/shop/assets/109803585/de0b8845-e94f-42dc-b947-38947aace326)

위처럼 알림 발송이 실패한 경우, 쿠폰 발급 또한 실패했다고 처리하는 것이 좋은 방향일까요?  

이와 같은 문제점이 발견되었습니다. 그렇다면 다른 문제점도 확인해보겠습니다.  

### 롱 트랜잭션(`Long Transaction`)으로 진행되어 트랜잭션 경합 발생

![image](https://github.com/hbkuk/shop/assets/109803585/4ad25315-f571-4352-92f9-9268a11d08fb)

극단적인 상황을 가정해보았습니다.  

쿠폰 발급은 비교적 빠르게 처리되었지만, 갑작스런 네트워크 지연으로 인해 알림 발송에서 많은 시간이 소요되었다면 어떻게 될까요?  
만약 쿠폰을 발급하는 과정에서 테이블 전체에 `Lock`을 걸었다면요?  

다른 트랜잭션은 해당 트랜잭션이 종료(commit)될 때까지 대기하는 상황이 발생하게 되는데요.  
이는 서비스의 성능 저하로 이어지게 됩니다.  

과연 좋은 설계일까요?

두가지 문제점을 해결할 수 있는 여러가지 방법 중 가장 간단한 것부터 확인해보겠습니다.

## 트랜잭션 전파 속성(Transaction propagation)을 활용해보기

하나의 트랜잭션을 분리하는 것이 우선이니, 전파 속성을 활용해서 기존 트랜잭션을 분리하는 방향으로 진행해보겠습니다.  

`Spring`에서 다음과 같이 총 7가지의 전파 속성을 제공하고 있습니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/da77a3bd-b2e0-4de0-a972-fcdc78bb8207)
<small>참고: [[Spring] 스프링의 트랜잭션 전파 속성(Transaction propagation) 완벽하게 이해하기](https://mangkyu.tistory.com/269)</small>

7가지의 전파 속성 중 트랜잭션이 항상 새로 생성되는 것은 `REQUIRES_NEW`, `NESTED` 입니다.  

### REQUIRES_NEW: 항상 새로운 트랜잭션 생성

우선 전파 속성 `REQUIRES_NEW`을 활용해서,  
핵심 업무인 쿠폰 발급을 부모 트랜잭션으로 진행되도록 하고, 보조 업무인 알림 발송을 자식 트랜잭션으로 진행되도록 해보겠습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/75caae53-4ce3-4a64-9198-0fbb573bcc76)

부모 트랜잭션에서 예외가 발생하는 상황과 자식 트랜잭션에서 예외가 발생하는 상황을 살펴볼까요?  

부모 트랜잭션에서 예외가 발생하는 상황은 다음과 같습니다.  
![image](https://github.com/hbkuk/shop/assets/109803585/103114b4-f9c3-4f47-b8d9-b146894c3364)

확인해보니 쿠폰이 발급되지 않았는데, 알림이 발송되는 상황이 발생합니다.

결론적으로는 해당 전파 속성으로는 문제를 해결하지 못하는 것으로 정리할 수 있겠는데요.     
이대로 끝내기는 아쉬워서, 자식 트랜잭션에서 예외가 발생하는 상황까지 살펴보겠습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/09ad1949-5edf-4c63-8e74-0952d7bf2c48)

음? 왜 부모 트랜잭션까지 `roll-back` 된 것일까요?    
`REQUIRES_NEW` 전파 속성이 적용되지 않은 것일까요?    

`REQUIRES_NEW` 전파 속성에서 부모 트랜잭션과 자식 트랜잭션은 분리되어 진행되는 것으로 알고있는데요. 

자식 트랜잭션에서 예외가 발생하니, 부모 트랜잭션까지 `roll-back` 되었습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/93e1e950-3329-49e5-9fc5-57dc0dc0b225)

...

확인해보니 트랜잭션이 분리되어 있는 것이지, `Thread`가 분리되어서 독립적으로 실행되는 것이 아니었습니다.      
다시 정리해보자면, 자식 트랜잭션에서 예외가 발생했고 해당 예외를 잡아서 적절한 처리를 하지 않자 부모 트랜잭션까지 전파된 것입니다.    

### NESTED: 중첩(자식) 트랜잭션 생성

`NESTED` 전파 속성은 독립적인 트랜잭션을 생성하는 `REQUIRES_NEW`와는 다르게 중첩(자식) 트랜잭션을 생성합니다.  
해당 중첩 트랜잭션은 부모 트랜잭션의 영향을 받지만, 중첩 트랜잭션이 부모 트랜잭션에 영향을 주지 않습니다.  

좋은 방법을 찾은 것 같습니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/c6f57ed5-29b5-4beb-a6df-64a1d876eb53)

그렇다면, 이 방법으로 해결 가능한 것으로 정리하면 될 것 같습니다.

1. 쿠폰 발급이 실패하는 경우, 알림도 발송되지 않는다.
2. 알림 발송이 실패하는 경우, 쿠폰은 정상적으로 발급된다.

하지만, [공식문서](https://docs.spring.io/spring-framework/docs/4.3.4.RELEASE/javadoc-api/index.html?org/springframework/orm/hibernate5/HibernateTransactionManager.html)를 확인해보면 Hibernate는 중첩된 트랜잭션을 지원하지 않는다고 합니다.   

![image](https://github.com/hbkuk/shop/assets/109803585/523cf843-4f44-4578-8cc7-a4ee0f8b5733)
참고: [https://docs.spring.io/spring-framework/docs/4.3.4.RELEASE/javadoc-api/index.html?org/springframework/orm/hibernate5/HibernateTransactionManager.html](https://docs.spring.io/spring-framework/docs/4.3.4.RELEASE/javadoc-api/index.html?org/springframework/orm/hibernate5/HibernateTransactionManager.html)

그렇다면, 트랜잭션의 전파 속성으로는 이 문제를 해결할 수 없다는 것으로 결론을 내리겠습니다.     

다른 방법은 무엇이 있을까요?  

## Spring Event: ApplicationEventPublisher

`Spring Event`는 스프링 프레임워크를 사용할 때 빈(Bean)간 데이터를 주고받는 방식 중 하나입니다.  
`Event`를 발행(Publish)하고 `Event`를 수신 또는 구독하여 소비(Listen/Subscribe)하는 기능을 제공합니다.

우선, 용어를 명확하게 정리하고 넘어가면 좋을 것 같습니다.  

- `Event(이벤트)`
  - 빈(Bean) 간에 전달할 데이터를 담고 있는 `POJO(Plain Old Java Object)`
  - 주로 어떤 상황이나 조건에 대한 정보 저장
- `Publisher(발행자)`
  - 이벤트를 발행하는 Bean
- `Listener(수신자)`
  - 특정 이벤트를 처리하는 Bean

![image](https://github.com/hbkuk/shop/assets/109803585/7337e5de-6e4c-4cd1-a488-f2b180d8dd0c)

### 발행할 이벤트

이벤트를 발행하기 위해서 이벤트로 사용할 객체를 정의해야 합니다.  
이벤트를 발행할 때는, `ApplicationContext`의 `publishEvent` 메서드를 이용하여 `Object` 혹은 `ApplicationEvent`의 데이터 타입을 가진 인자를 전달할 수 있습니다.

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

### 이벤트 수신/소비


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

![image](https://github.com/hbkuk/shop/assets/109803585/a4176228-2c5d-4cc6-99c8-d8f9c5937ae3)

기본적으로 `Spring Event`는 동기적으로 동작합니다.  
즉, 이벤트가 발행되면 모든 `Listener`가 이벤트 처리를 완료할 때까지 `Thread`가 차단된 후 진행됩니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/7cd3d9bd-da75-421e-875e-bc84604a57ac)
<small>참고: https://medium.com/@cizek.jy/spring-events-make-your-code-more-flexible-946951ba8e9f</small>  

그렇다면 롱 트랜잭션으로 진행된다는 의미입니다.     
현재 해결해야하는 것은, 쿠폰 발급과 알림 발송의 트랜잭션을 분리해야 합니다.

어떻게 하면 될까요?

### Async 

동기적으로 동작하는 `Spring Event`를 비동기적으로 동작하도록 설정하기 위해서 다음과 같은 설정이 필요합니다.

1. `@EnableAsync` 어노테이션 추가  
   ![image](https://github.com/hbkuk/shop/assets/109803585/2f3600a8-0aaf-4700-ad77-a163a814f736)

2. 비동기적으로 동작해야 하는 `Listener`에 `@Async` 어노테이션 추가  
   ![image](https://github.com/hbkuk/shop/assets/109803585/6c806d33-68d3-4976-8e5e-d824a8df7d3e)

그렇다면 아래와 같이 실행되는 것을 확인할 수 있습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/7d7a8af8-b140-4385-9c89-c888735ae4fe)


### 트랜잭션이 분리되어야 하는 

현재 코드의 문제점은 다음과 같이 정리해볼 수 있다.
핵심 업무가 실패할 경우 보조 업무도 실패해야한다.

그니깐, 핵심 업무가 완벽하게 성공하고 .. 즉, 트랜잭션이 정상적으로 커밋된 이후에 실행되어야만 하는데.. 그렇지 않다.
핵심 업무가 성공하든, 실패하든 비동기적으로 보조 업무가 실행된다.  

![image](https://github.com/hbkuk/shop/assets/109803585/c00cdbfd-89aa-4732-ae1a-91d95361383f)

이러한 문제점 또한.. 해결하기 위해 다른 방법을 찾아야한다.

## 트랜잭션 바인딩 리스너

Spring 에서는 특정 트랜잭션 결과가 나올 때까지 이벤트 처리를 지연시킬 수 있다.
@EventListener 어노테이션 대신 @TransactionalEventListener(phase = <phase>) 어노테이션을 사용하면 된다.

![image](https://github.com/hbkuk/shop/assets/109803585/e30fabe3-01dc-429a-9504-a090e5fe0efa)

phase는 트리거 되는 특정 트랜잭션의 결과이다.
선택할 수 있는 4단계를 살펴보자.

- BEFORE_COMMIT
- AFTER_COMMIT
- AFTER_ROLLBACK
- AFTER_COMPLETION

![image](https://github.com/hbkuk/shop/assets/109803585/d9b321cd-9fbb-4fbc-b3ae-f98cfe4035e6)

### 하지만.. 여기서도 문제가 ...

테스트 코드를 실행해보았습니다.  

![image](https://github.com/hbkuk/shop/assets/109803585/2df00933-e33c-4a53-b2e8-7b403eda5046)

실패했습니다.

왜 실패할까요?

우선 현재 하나의 Thread에서 모든 로직이 실행되는 것을 이해하신다면 충분히 납득할만한 결과라고 생각합니다.
현재 하나의 커넥션만 사용하고 있습니다. 

![image](https://github.com/hbkuk/shop/assets/109803585/a4d0b6a4-2166-4443-89b8-9dadb9f3fdb0)

만약, A 트랜잭션이 종료 후, B 트랜잭션이 시작되는데요.

A 트랜잭션이 종료된다는 말은, 커넥션을 사용 후 종료되었다는 말입니다.  

이에 트랜잭션이 커밋된 이후, B 트랜잭션이 커밋을 동작하지 않는다는 것을 의미합니다.

이 부분은 주석 부분에도 언급되고 있으니, 확인해보면 좋을 것 같습니다.  
![image](https://github.com/hbkuk/shop/assets/109803585/9af669a3-f9f3-4690-803f-a85d9bd7535d)

요약하자면, 이전의 이벤트를 publish 하는 코드에서 트랜잭션이 이미 커밋 되었기 때문에 AFTER_COMMIT 이후에 새로운 트랜잭션을 수행하면 해당 데이터소스 상에서는 트랜잭션을 커밋하지 않는다는 것이다. 따라서 @Transactional 어노테이션을 적용한 코드에서 PROPAGATION_REQUIRES_NEW 옵션을 지정하지 않는다면 (매번 새로운 트랜잭션을 열어서 로직을 처리하라는 의미) 이벤트 리스너에서 트랜잭션에 의존한 로직을 실행했을 경우 이 트랜잭션은 커밋되지 않는다.


그렇다면 어떻게 해결하는 것이 좋을까요?

1. 위 문제를 해결하는 첫 번째 방법으로는 AFTER_COMMIT 이후에 동일한 데이터소스를 사용하지 않는 방법이 있다. 이를 위해서는 이벤트 리스너를 별도의 스레드에서 실행하는 방법이 있다. 바로 @Async 어노테이션을 추가하는 방법이다.
2. @TransactionalEventListener 어노테이션에 추가로 @Transactional(propagation = Propagation.REQUIRES_NEW) 을 붙여주는 방법이다. 이렇게 하면 이벤트 리스너의 로직 안에서 실행되는 @Transactional 로직을 위한 새로운 트랜잭션이 이전의 트랜잭션과 구분되어 새롭게 시작한다. (Propagation.REQUIRES_NEW가 이를 알려줌) 따라서 이벤트를 발생시킨 트랜잭션과는 별도의 분리된 트랜잭션 안에서 이벤트 리스너 로직이 실행된다.

이상 끝!!

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