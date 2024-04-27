<div class=markdown-body>

# 대량 쿠폰 발급 시 `Bulk Insert`로 처리 시간 70% 단축

쿠폰 발급과 관련된 프로덕션 코드를 작성하면서,   
향후 서비스 규모가 커짐에 따라 쿠폰을 발급하는 대상 회원 수가 **100명, 1,000명, 혹은 10,000명이 된다면 성능 이슈는 발생하지 않을까?** 라는 고민을 하게 되었습니다.

결과적으로 쿠폰의 발급 방식을 `Single Insert`에서 `Bulk Insert`으로 변경했더니, 아래 그래프와 같이 쿠폰 발급 처리 시간이 **약 70% 단축되는 결과를 확인**할 수 있었습니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/0bca266b-f557-4255-a202-a4f8e807bd84)

해당 포스팅에서는 **70%라는 시간 단축하기까지의 과정을 소개**합니다.  

해당 글에서 사용되었던 모든 코드는 [gitHub](https://github.com/hbkuk/blod-code/tree/main/jpa/bulk-insert)에서 확인하실 수 있습니다.  
아래 서버 환경은 참고해주시면 좋을 것 같습니다.

- Spring Boot: 2.7.1
- Spring Data JPA
- MySQL 8.0(테스트 환경)

## 쿠폰을 등록하고 발급하는 과정

우선 해당 프로젝트에서, 쿠폰이 어떠한 흐름으로 발급되는지 짚고 넘어가면 좋을 것 같습니다.    
**다수의 회원에게 쿠폰을 발급하는 과정을 시퀀스 다이어그램**으로 표현해 보았습니다.  

![쿠폰 발급 시퀀스 다이어그램](https://github.com/hbkuk/blod-code/assets/109803585/520ff364-8e5f-4215-a110-c27a7f6d1463)

부연 설명을 추가해보겠습니다.  

1. 관리자는 쿠폰을 발급하기 위해서 **쿠폰을 등록해야 한다.(이미 등록된 쿠폰으로 발급할 수 있다.)**
2. 쿠폰을 등록할 때, **발급할 수량을 설정**한다.
3. 쿠폰이 등록되면 관리자는 **회원(회원들)에게 쿠폰을 발급**한다.

여기까지 충분히 이해하셨을 것이라고 생각하고,  
다음으로 쿠폰 발급 정보를 저장하는 **프로덕션 코드를 살펴보겠습니다.**

## `saveAll()` 메서드로 대량의 쿠폰 발급하기

처음으로 고려했던 방법은 `JpaRepository`의 구현체인 `SimpleJpaRepository`에서 제공하는 `saveAll()`메서드를 사용하는 것이었습니다.  

- `saveAll()` 메서드

![saveAll 메서드](https://github.com/hbkuk/blod-code/assets/109803585/50f043a4-390a-4b0b-b79d-90373062faf6)    

이 메서드를 활용한 쿠폰을 발급하는 프로덕션 코드입니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/bf3a94b1-4eef-477c-8538-739d6f9252dc)

**위 코드로 대량의 쿠폰을 발급할 경우, 어떤 쿼리가 실행될까요?**  

...

그전에, 실행되는 쿼리를 확인하기 위해서 아래와 같이 애플리케이션 설정했습니다.

```
// application.yml

logging:
  level:
    org.hibernate.SQL: debug
```

관리자가 **100명의 회원에게 쿠폰을 발급하는 테스트 코드**입니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/5974596b-d2be-4db6-b12b-bc2c435228fa)

그렇다면, 이제 테스트 코드를 실행시켜서 실행되는 쿼리를 확인해보겠습니다.

...

총 **100개의 insert 쿼리가 실행**되었습니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/e4075e76-a0af-4a3b-b181-54fa16d9e5ed)

메서드 명(`saveAll`)만 보면 마치 `Bulk Insert`방식으로 insert 쿼리가 실행될 것으로 예상되지만,   
실제로는 여러개의 `Single Insert` 로 실행되는 것을 확인할 수 있습니다.

<small>* Single Insert 예) `INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);` </small>  
<small>* Bulk Insert 예) `INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...), (value1, value2, ...),...`</small>  


그렇다면, 왜 `Single Insert` 쿼리가 실행되는지 코드를 분석해보겠습니다.

`Spring Data JPA`에 익숙하신 분이라면, 이미 알고 계신 내용일 것이라고 생각되는데요.  
모르시는 분들이 있을 수 있으니, 간단하게 짚고 넘어가면 좋을 것 같습니다.  

```
@Repository
@Transactional(readOnly = true)
public class SimpleJpaRepository<T, ID> implements JpaRepositoryImplementation<T, ID> {
	
	private final EntityManager em;

	@Transactional
	@Override
	public <S extends T> List<S> saveAll(Iterable<S> entities) {
		Assert.notNull(entities, "Entities must not be null");

		List<S> result = new ArrayList<>();
		for (S entity : entities) {
			result.add(save(entity));  // N개의 Entity를 save
		}
		return result;
	}

	@Transactional
	@Override
	public <S extends T> S save(S entity) {
		Assert.notNull(entity, "Entity must not be null");

		if (entityInformation.isNew(entity)) {
			em.persist(entity);
			return entity;
		} else {
			return em.merge(entity);
		}
	}
}
```

위 `saveAll()` 메서드의 내부 코드를 확인해보면, `List`를 순회하면서 내부적으로 `save()` 메서드를 호출하고 있습니다.    
따라서, `save()` 메서드를 100번 실행시키는 것과 100개의 `Entity`로 `saveAll()` 메서드를 1번 실행시키는 것은 동일하다고 볼 수 있습니다.

그렇다면 `Bulk Insert`  방식으로 쿠폰이 발급 처리될 수 있도록, 다른 방법을 찾아보겠습니다.

### `Hibernate`에서 제공하는 Batch 설정 활용해보기

`Hibernate`는 기본적으로 일괄 처리를 활성화하지 않는다고 합니다.  
[Hibernate 공식문서](https://docs.jboss.org/hibernate/orm/5.2/userguide/html_single/Hibernate_User_Guide.html#batch)를 확인해보니 활성화하기 위해서 아래와 같이 추가적인 설정이 필요하다고 합니다.  

> `hibernate.jdbc.batch_size`  
> 드라이버에게 배치 실행을 요청하기 전에 Hibernate가 함께 배치할 명령문의 최대 수를 제어합니다.   
> 0 또는 음수는 이 기능을 비활성화합니다.

`application.yml` 파일에 아래와 같이 적용해보겠습니다.

```
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 100
```
설정을 완료했으니, `Bulk Insert` 방식으로 실행되는지 확인하기 위해서,  
다시 100개의 쿠폰을 발급하는 테스트 코드를 실행시켜보겠습니다.

그전에,  
`Coupon` Entity는 `IssuedCoupon` Entity의 부모 Entity 이므로 영속성 전이 옵션(`Cascade`)을 통해 영속화 되도록 수정해보겠습니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/b5aa8abd-4ad4-478b-9b75-a6b2a6735091)

그렇다면, 이전 쿠폰 서비스 메서드에서도 `saveAll` 메서드를 삭제하면 되겠죠?

![image](https://github.com/hbkuk/blod-code/assets/109803585/e1be4511-4141-40c2-a6bc-304080c8b1c5)

혹시라도, 삭제한 의도를 모르시는 분들을 위해 `PERSIST` 옵션에 대해서 아래 간단하게 작성해보겠습니다.

> ### PERSIST  
> 이는 엔티티를 영속화할 때 연관된 엔티티도 함께 영속화하는 옵션입니다.  

```
Post post = new Post();
Comment comment = new Comment();
post.addComment(comment);
entityManger.persist(post); // post, comment 둘 다 영속화
``` 
더 자세한 내용을 알아보고 싶은 분이 계시다면 [JPA Cascade는 무엇이고 언제 사용해야 할까?](https://tecoble.techcourse.co.kr/post/2023-08-14-JPA-Cascade/)을 참고하시면 좋을 것 같습니다.

이 옵션을 활용해서, `Coupon` Entity의 `issueCoupon()` 메서드는 발급할 쿠폰을 모두 추가합니다.  
그렇다면, JPA의 `dirty checking`으로 인해 트랜잭션이 커밋하는 시점에 insert 쿼리가 실행됩니다.

```
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Coupon {

    // ...
    
    @OneToMany(mappedBy = "coupon", cascade = CascadeType.PERSIST, orphanRemoval = true, fetch = FetchType.LAZY)
    private final List<IssuedCoupon> issuedCoupons = new ArrayList<>();

    public void issueCoupon(List<IssuedCoupon> issuedCoupons) {
        checkRemainingIssueCoupon(issuedCoupons);
        checkIssuableStatus();
    
        this.issuedCoupons.addAll(issuedCoupons); // 
        
        // ...
    }
}
```

자 다시 본론으로 돌아와서, 테스트 결과를 확인해보겠습니다.  

...


이번에도 100개의 insert 쿼리가 출력되었습니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/e4075e76-a0af-4a3b-b181-54fa16d9e5ed)

`Hibernate`의 공식문서를 확인해서 Batch 설정을 제대로 했는데 왜 `Single insert` 쿼리가 실행 될까요?  
확인해보니, 아래와 같이 자동 생성 전략을 `IDENTITY`으로 설정했을 경우, Batch 처리가 불가능하다고 합니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/50128cf5-3ac9-44b4-8177-1d1b6fadedb9)

왜 불가능한지, 여러 문서들을 찾아보고 아래와 같이 정리해보았습니다. 

> `Hibernate`는 기본적으로 트랜잭션이 커밋된 후에 SQL 문을 실행하도록 지연시킵니다.  
> 이를 `"Transaction write-behind"`라고 합니다.
> 
> `Hibernate`는 엔티티를 1차 캐시에 저장하고, 모든 SQL 문은 쓰기 지연 SQL 저장소에 저장합니다.  
> **(단, 1차 캐시에 저장할 경우, Entity의 PK는 반드시 할당되어야 한다.)**  
> 
> 하지만, 기본 키의 자동 생성 방식을 `IDENTITY` 전략을 사용하는 경우 데이터베이스에 INSERT 쿼리를 보내기 전까지 기본 키 값을 알 수 없습니다.  
> 이러한 이유로 IDENTITY 전략을 사용하면 Hibernate가 일괄 처리를 수행할 수 없습니다.

더 궁금하시는 분들은 [Why does Hibernate disable INSERT batching when using an IDENTITY identifier generator](https://stackoverflow.com/questions/27697810/why-does-hibernate-disable-insert-batching-when-using-an-identity-identifier-gen)을 참고하시면 좋을 것 같습니다.  

추가적으로 `IDENTITY` 전략을 사용할 경우,  
**데이터베이스로부터 기본 키를 어느 시점에 할당받는지?** 내부적으로 궁금하시는 분들은 [JPA saveAll이 Bulk INSERT 되지 않았던 이유](https://imksh.com/113)을 참고하면 좋을 것 같습니다.    

## 기본 키의 자동 생성 방식을 `UUID`로 변경하기

![image](https://github.com/hbkuk/blod-code/assets/109803585/2a15de35-0616-4053-aa64-419ccf71620a)

기본 키의 자동 생성 방식을 UUID 기반으로 생성되도록 수정했습니다.    

> ### UUID?  
> UUID는 16진수로 구성된 128비트의 값입니다.
> 
> ### UUID는 안전한 값인가?  
> 랜덤으로 생성된 UUID가 충돌을 일으킬 확률은 10억분의 1 확률로 매우 낮기 때문에 상당히 안전한 값이라고 볼 수 있습니다.

그렇다면, 다시 테스트 코드를 실행해서 `Bulk Insert` 쿼리로 실행되는지 확인해보겠습니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/e4075e76-a0af-4a3b-b181-54fa16d9e5ed)

네? 무슨일이죠?   
이번에도 `Single insert` 쿼리가 실행되었습니다.  

...

[MySQL 공식문서](https://dev.mysql.com/doc/connectors/en/connector-j-connp-props-performance-extensions.html)를 확인해보니,   
`Bulk Insert` 쿼리로 실행되게 하려면, URL에 `rewriteBatchedStatements=true` 파라미터를 추가해야 한다고 기술되어 있습니다.    

추가적으로, 필요한 설정도 같이 해주겠습니다.

```
// application.yml

spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/test?rewriteBatchedStatements=true&profileSQL=true&logger=Slf4JLogger&maxQuerySizeToLog=999999
```

- `profileSQL=true` : Driver 에서 전송하는 쿼리 출력
- `logger=Slf4JLogger` : Driver 에서 쿼리 출력시 사용할 Logger 설정
- `maxQuerySizeToLog=999999` : 출력할 쿼리 길이 설정

그렇다면 테스트 코드를 다시 실행해보고, Batch 처리가 되는지 확인해보겠습니다.

```
2024-04-24 20:39:45.745 DEBUG 12420 --- [           main] org.hibernate.SQL                        : 
    insert 
    into
        issued_coupon
        (coupon_id, expired_at, issued_at, member_email, status, coupon_code) 
    values
        (?, ?, ?, ?, ?, ?)
2024-04-24 20:39:45.745 DEBUG 12420 --- [           main] org.hibernate.SQL                        : 
    insert 
    into
        issued_coupon
        (coupon_id, expired_at, issued_at, member_email, status, coupon_code) 
    values
        (?, ?, ?, ?, ?, ?)
2024-04-24 20:39:45.745 DEBUG 12420 --- [           main] org.hibernate.SQL                        : 
    insert 
    into
        issued_coupon
        (coupon_id, expired_at, issued_at, member_email, status, coupon_code) 
    values
        (?, ?, ?, ?, ?, ?)
2024-04-24 20:39:45.765  INFO 12420 --- [           main] MySQL                                    : [QUERY] insert into issued_coupon (coupon_id, expired_at, issued_at, member_email, status, coupon_code) values (1, '2024-05-24 20:39:45.702775', '2024-04-24 20:39:45.702775', 'd7af7714-d628-4e85-9e0c-f91ea9b72fd8@yahoo.com', 'ACTIVE', x'b84cef43c2ce48a192d402c024865448') [Created on: Wed Apr 24 20:39:45 KST 2024, duration: 2, connection-id: 1494, statement-id: 0, resultset-id: 0,	at com.zaxxer.hikari.pool.ProxyStatement.executeBatch(ProxyStatement.java:127)]
```
마지막에 출력된 로그를 보면 알 수 있듯이, **`Batch(Bulk Insert)`** 방식으로 실행된 것을 확인할 수 있습니다.

![image](https://github.com/hbkuk/blod-code/assets/109803585/5c233ba5-7778-46e2-8c62-bd1cfaf78d78)

또한, 로그를 분석해보면 몇가지 사실을 확인해볼 수 있습니다.  

### Hibernate는 쿼리가 재작성되는 모른다.

어쩌면 당연한 이야기일 수 도 있겠지만,  
`Hibernate`는 배치 설정 여부와 관계없이 `Single insert` 쿼리를 출력합니다.    
따라서, `Hibernate`는 **Drvier가 하나의 쿼리로 재작성해서 한방 쿼리로 전송하는 것을 모른다는 것입니다.**  

그렇다면 이제 정리를 해볼까요?

## 정리

`MySQL`을 사용할 경우 `Bulk Insert` 쿼리를 실행하도록 하기 위해서는 아래와 같은 설정이 필요합니다.  

- `Entity`의 기본 키 자동 생성 방식을 `IDENTITY` 아닌 다른 방식 사용 
- 애플리케이션 설정이 필요

   ![image](https://github.com/hbkuk/blod-code/assets/109803585/acdc048a-7a90-425b-a190-7cb6649ce2c7)


## 부록: `Hibernate`와 Data Base 간의 I/O 시간을 확인하는 방법

보통 테스트 실행 시간을 측정할 때, 아래와 같은 방법을 주로 사용하는 것으로 알고 있습니다.

```
@Test
public void testCode() {
  long startTime = System.currentTimeMillis();

  // 실행 시간을 측정할 코드 블록
  // 예를 들어, 여기에는 테스트하려는 코드가 들어갑니다.

  long endTime = System.currentTimeMillis();
  long elapsedTime = endTime - startTime;

  System.out.println("실행 시간: " + elapsedTime + "밀리초");
}
```

개인적으로 테스트 코드에 영향을 주지않으면서, 정확한 시간을 측정하는 방법을 사용하는 것이 좋다고 생각합니다.  
따라서, 기존 테스트 코드에 영향을 주지않으면서, 시간을 측정하는 방법을 소개해드립니다.  

아래는 간단한 애플리케이션 설정으로 로깅되는 정보입니다.  

![image](https://github.com/hbkuk/blod-code/assets/109803585/7a9c9de1-a0b4-4ef4-8273-b402481c4f95)

아래 설정 정보를 참고해 주세요.  

```
spring:
  jpa:
    properties:
      hibernate:
        generate_statistics: true

logging:
  level:
    org.hibernate.stat: debug
```
### 참고 문서
- [MySQL 환경의 스프링부트에 하이버네이트 배치 설정 해보기](https://techblog.woowahan.com/2695/)
- [JPA Cascade는 무엇이고 언제 사용해야 할까?](https://tecoble.techcourse.co.kr/post/2023-08-14-JPA-Cascade/)

</div>