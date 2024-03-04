## 테스트 격리

현재 `ATDD, 클린 코드 with Spring 8기`에 참가해서, 미션을 진행 중이다.

E2E(API) 테스트 기반의 인수 테스트를 작성해야 하기 때문에, **'데이터베이스와의 격리를 어떠한 방법으로 할 것인가?'** 를 고민을 해봐야 했다.

하지만, 나는 요구사항을 분석하고 인수 테스트를 작성하는 프로세스를 익히는 데만 급급한 나머지  비교적 간단한 `@DirtiesContext` 를 사용했다.

나도 테스트 실행속도가 너무 느려서 답답했는데, 리뷰어님께서 마지막 단계에서 아래와 같이 조언을 해주셨다. 

![리뷰 내용](https://github.com/next-step/atdd-subway-map/assets/109803585/4e7f9e09-c956-4577-8a3c-e607361b18f3)

따라서, 공부한 내용을 이번 기회에 제대로 정리해보고자 한다.  

<br>

### 테스트 격리가 왜 필요할까?

우선, 격리가 왜 필요한지부터 생각해보자.

가령, 아래 두 테스트는 독립적으로 진행되어야 하고 테스트 간에 간섭이 절대 발생하면 안 된다.

![격리 이유 2](https://github.com/next-step/atdd-subway-map/assets/109803585/1307c68a-2a7b-4057-8932-86ce06a51f39)

쉽게 풀어서 쓰자면, 각각의 테스트 메서드가 실행될 때 데이터베이스에는 아무것도 없는 상태로 만들어서 진행되어야 한다는 것이다.

이제, `'어떠한 방법이 있을까?'` 라는 생각을 가지고, 적절한 테스트 격리 방법을 찾아봐야 한다.

## 테스트 격리 종류  

내가 찾은 것은 아래 3가지 방법이다. (더 좋은 방법이 있을 수도... ?)

### `@Transitional`  
흔히, 프로덕션 코드에서 사용하는 방식과는 달리 테스트 메서드가 종료될 때 트랜잭션이 `roll back` 되어, 테스트 간에 데이터 베이스 상태가 독립적으로 유지되도록 보장한다고 한다.  

```
@DisplayName("지하철 노선 관련 기능")
@Transactional
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
public class StationLineAcceptanceTest { ... }
```  

하지만, webEnvironment 속성값이 위와 같이 `WebEnvironment.DEFINED_PORT` 혹은 `WebEnvironment.RANDOM_PORT` 이면,   
roll back 되지 않는다.  

**Why?** `@Transitional` 어노테이션을 붙인 Thread와 `Spring Boot`가 구동되는 Thread가 서로 다르므로, roll back 시킬 수 없다고 한다.  

<br>

### `@DirtiesContext` 
`@SpringBootTest`를 통한 테스트 수행에서는 `ApplicationContext`를 띄어 진행한다.  
이때 Spring은 다른 테스트 메서드에서 재사용할 수 있도록, Context를 캐싱한다.  그렇기 때문에 테스트 메서드들은 하나의 Context를 사용하게 된다. 

따라서, `@DirtiesContext`은 고의로 Bean을 오염시켜 caching 조건에 충족되지 않게 한다. 고로, 테스트 메서드가 실행될 때 마다 Context를 새로 띄우는 것이다.
하지만, 위에서 언급했듯이 `ApplicationContext`를 새로 띄우는 것은 비용이 큰 작업이다.  

항상 좋지 않을까? 라는 고민을 해봐야한다. (이 부분은 다음에 기회가 된다면 더 찾아보자.)  

<br>

### `@Sql`
테스트가 실행될 때마다 테이블들을 truncate 시키는 쿼리를 수행하게 한다. 인수 테스트에서 가장 잘 사용되는 테스트 격리 방법이지 않을까 싶다.  

아래는 필자가 사용했던 방식이다. 단점으로는, 테이블이 추가될 때 마다 쿼리를 추가해야 한다.
  
```
// src > main > resources > clean.sql

-- 외래 키 제약 조건 비활성화
SET REFERENTIAL_INTEGRITY FALSE;

-- H2는 TRUNCATE TABLE을 실행하더라도 IDENTITY가 기본값으로 재설정 필요
TRUNCATE TABLE station RESTART IDENTITY;
TRUNCATE TABLE station_line RESTART IDENTITY;
TRUNCATE TABLE station_section RESTART IDENTITY;

-- 외래 키 제약 조건 활성화
SET REFERENTIAL_INTEGRITY TRUE;
```  
  
```
// ...Test.java

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT)
@Retention(RetentionPolicy.RUNTIME)
@Sql(value = "/clean.sql", executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
public class ...Test {}
```  

끝으로 .. 테스트 격리 방법을 고민하는, 모든 분들에게 부족하지만 도움이 되셨으면 좋겠다.