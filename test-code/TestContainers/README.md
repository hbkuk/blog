<div class=markdown-body>

# `Testcontainers`가 왜 필요했을까?

### 1. 들어가며

현재 팀에서는 저를 포함한 팀원들이 각 애플리케이션 안에 단위 테스트와 통합 테스트를 꾸준히 작성하고 있습니다.  
다만 이 테스트들이 하나의 개발 환경 데이터베이스에 의존해 동작하고 있다는 점이 문제였습니다.

여기서 말하는 “개발 환경”은 운영과 분리된, 개발자들이 기능을 만들고 수정하면서 수시로 확인해보는 환경입니다.  

현재 우리 팀에서는 애플리케이션 환경을 아래와 같이 나누어 사용하고 있습니다.

- **개발 환경**: 개발자들이 기능을 만들고, 수정하고, 테스트해보는 공간  
- **운영 환경**: 실제 사용자가 접속하는 서비스 환경


테스트 코드는 가능한 한 **항상 동일한 초기 상태에서**, 서로 영향을 주지 않도록 **격리된 환경**에서 돌아가는 게 이상적이라고 생각합니다.  
이 원칙을 지키지 못하면 아래와 같은 문제가 발생할 수 있습니다.

- **개발 환경 데이터베이스에 저장된 데이터에 의존**하고,
- 다른 팀원이 테스트 실행 중 디버깅 포인트를 걸고 오래 보고 있으면
  다른 팀원은 테스트를 돌렸다가 **데이터베이스 커넥션을 잡지 못해 실패**하는 경우가 생기고,
- 테스트를 여러 번 돌리다 보면 **개발 환경 데이터가 오염되는 일**도 발생합니다.

어느 순간부터는,

> “테스트 코드와 개발 환경이 서로 영향을 주고받으면서  
>  깔끔하게 분리되지 못한 상태”

가 되어 있더라고요.

이 글은 그런 상황에서 **왜 Testcontainers를 꺼내 들게 되었는지**,  
그리고 어떻게 테스트 환경을 어떻게 구성했는지에 대한 기록입니다.

> 참고: 이 글은 “이미 팀 전체에 도입 완료한 후기”가 아니라,  
> **도입 전에 혼자 설계/실험한 내용**을 정리한 글입니다.

### 2. 본문

#### 2-1. 개발 환경 DB를 공유하는 테스트

테스트를 실행할 때 사용하는 데이터베이스는 모두 개발 환경 데이터베이스였습니다.  
그러다 보니 시간이 지날수록, 개발 환경 DB는 점점 “공용 테스트 + 개발용 DB”   역할을 동시에 떠안게 되었습니다.

물론 편한 점도 있습니다.

개발 환경 DB에는 이미 운영과 비슷한 데이터가 어느 정도 쌓여 있어서  
“어느 지역의 특정 숙소” 같은 현실적인 시나리오를 바로 테스트해 볼 수 있고,  
실제 비즈니스 데이터에 가까운 값들로 검증할 수 있다는 장점이 있죠.

하지만, 그만큼 분명한 단점도 함께 따라왔습니다.

#### 2-2. 디버깅 한 번 잡으면, 다른 팀원의 테스트가 영향을 받는다

실제로 있었던 상황입니다.

- A 개발자가 개발 환경 DB에 붙는 테스트를 돌리다가  
  **브레이크 포인트를 걸고 디버깅** 중
- 같은 시간에 B 개발자가 다른 테스트를 돌렸는데  
  **커넥션을 못 잡아서 타임아웃**이 발생하거나,  
  응답이 이상하게 느려지는 상황이 생깁니다.

여러 팀원이 **같은 개발 환경 DB를 실시간으로 공유**하다 보니,  
디버깅이나 테스트가 다른 팀원의 테스트 결과에 영향을 주는 구조가 되어 있었어요.

#### 2-3. 테스트가 개발 환경 데이터를 망가뜨리는 문제

또 이런 문제도 있습니다.

- 어떤 테스트는 개발 환경 DB에 **INSERT/UPDATE/DELETE**를 하고
- 롤백 없이 그대로 끝나기도 하고,
- 그러다 보니 QA나 기능 개발에 쓰던 개발 환경 데이터가  
  테스트를 여러 번 돌리면서 같이 섞여버리기도 합니다.

“테스트 한 번 돌렸는데, 왜 개발 환경 데이터가 이상해졌지…?”  
라는 말을 듣기 시작하면, 테스트를 추가하는 것도 점점 부담스러워집니다.

#### 2-4. 개발 환경 데이터에 묵시적으로 기대는 테스트들

또 다른 하나는 **보이지 않는 의존성**이었습니다.

- 어떤 테스트는 “id = 5인 숙소가 개발 환경 DB에 이미 존재한다”는 걸  
  **암묵적으로 기대**하고 돌아갑니다.
- 누가 개발 환경 데이터를 정리하거나, 마이그레이션을 한 번 돌리면  
  갑자기 테스트가 깨져버리기도 하고,
- 반대로 테스트를 고쳐야 할 때도  
  “개발 환경 데이터를 건드리기 부담스러워서” 손을 못 대는 상황이 생깁니다.

요약하면,

> 테스트를 돌리면 개발 환경이 불안해지고,  
> 개발 환경을 손대면 테스트가 불안해지는  
> **서로 강하게 얽혀 있는 구조**

였어요.  
이걸 한 번 끊어보고 싶었습니다.

---

### 3. 그래서 나온 결론: “테스트 전용 DB를 코드로 띄우자”

여러 가지 선택지를 놓고 고민해봤습니다.

- 개발 환경 DB 그대로 계속 쓰기 (현상 유지)  
- 개발자마다 로컬 Docker MySQL을 띄워서 사용하는 방식  
- 클라우드에 테스트 전용 DB 인프라를 따로 구축하는 방식  
- **Testcontainers로 테스트 전용 DB를 테스트 코드에서 직접 띄우는 방식**

속도, 인프라 복잡도, 비용 등을 비교해 봤지만,  
결국 “**테스트와 개발 환경을 깔끔하게 분리**”하려면  
마지막 옵션으로 가야겠다는 결론이 났습니다.

그래서 Testcontainers를 도입해서:

- 테스트 시에만 **컨테이너 기반 MySQL**을 띄우고
- 테스트마다 **DB를 깨끗하게 비우고**
- Fixture/SQL로 **재현하고 싶은 시나리오만 명시적으로 세팅**하는 방향으로 시작했습니다.

---

### 4. MySQL Testcontainers 기본 설정

먼저 MySQL 컨테이너를 한 군데에서 관리하기 위한 홀더 클래스를 하나 둡니다.

```java
public class MySQLTestContainerHolder {

    public static final MySQLContainer<?> MYSQL =
        new MySQLContainer<>("mysql:8.0")
            .withUsername("test")
            .withPassword("test")
            .withDatabaseName("example_test");
}
```

그리고 이 컨테이너 정보를 **Spring 설정으로 연결**하는 Config를 하나 더 만듭니다.

```java
@Configuration
@Testcontainers
public class TestcontainersConfig {

    private static final MySQLContainer<?> MYSQL = MySQLTestContainerHolder.MYSQL;

    static {
        MYSQL.start();
    }

    @DynamicPropertySource
    static void overrideProps(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", MYSQL::getJdbcUrl);
        registry.add("spring.datasource.username", MYSQL::getUsername);
        registry.add("spring.datasource.password", MYSQL::getPassword);
        registry.add("spring.datasource.driver-class-name", () -> "com.mysql.cj.jdbc.Driver");
    }
}
```

여기까지가 **“컨테이너를 띄우고, Spring Datasource를 Testcontainers 쪽으로 돌리는”** 기본 설정입니다.

---

### 5. `@TestcontainersEnvironment` 어노테이션으로 한 줄에 묶기

#### 5-1. 목표했던 테스트 클래스 모습

최종적으로는 테스트 클래스를 이렇게 쓰고 싶었습니다.

```java
@TestcontainersEnvironment
class UserRepositoryTest {

    @Autowired
    UserRepository userRepository;

    @Test
    void 사용자_조회가_정상동작한다() {
        // given / when / then ...
    }
}
```

- “이 테스트는 Testcontainers 환경에서 돌아간다”는 걸  
  **어노테이션 한 줄로 표현**하고 싶었고,
- 데이터 클린업, 초기 데이터 세팅, 프로필 활성화 같은 것들은  
  전부 어노테이션 내부로 숨기고 싶었습니다.

그래서 `@TestcontainersEnvironment`를 아래와 같이 정의했습니다.

#### 5-2. `@TestcontainersEnvironment` 정의

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@ActiveProfiles(value = {"testcontainers"}, inheritProfiles = false) // testcontainers 전용 프로파일
@Testcontainers // Testcontainers 라이프사이클 관리
@Import(TestcontainersConfig.class) // MySQL 컨테이너 설정 + DynamicPropertySource
@ExtendWith(TestDataCleanUpExtension.class) // 매 테스트마다 DB 정리
@ExtendWith(TestDataSetUpExtension.class) // 공통 테스트 데이터 설정
@Sql(
    scripts = {"/sql/init-metadata.sql"},
    executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD
) // 코드값/메타데이터 초기화
public @interface TestcontainersEnvironment {
}
```

각 어노테이션이 맡는 역할은 대략 이런 느낌입니다.

- `@ActiveProfiles("testcontainers")`  
  → 테스트에서만 사용할 별도의 Spring 설정이 있다면, 이 프로파일을 통해 분리
- `@Testcontainers`  
  → JUnit 5와 Testcontainers 통합, 컨테이너 라이프사이클 관리
- `@Import(TestcontainersConfig.class)`  
  → 앞에서 만든 MySQL 컨테이너 설정 + `@DynamicPropertySource` 주입
- `@ExtendWith(TestDataCleanUpExtension.class)`  
  → 각 테스트 전에 `DELETE FROM ...`을 수행해 DB 초기화
- `@Sql("/sql/init-data.sql")`  
  → 공통 코드 테이블/메타데이터를 미리 세팅하는 SQL 실행

이제 테스트 쪽에서는 정말로 다음과 같이 쓸 수 있습니다.

```java
@TestcontainersEnvironment
class SomeServiceTest {
    // ...
}
```

이 한 줄만 붙이면, Testcontainers 기반의 테스트 환경이 한 번에 적용되도록 만들 수 있습니다.


### 6. `@Transactional`을 없애고 나서 ..

원래 우리 팀 테스트 코드에는 테스트 메서드마다 `@Transactional`이 붙어 있는 경우가 많았습니다.

- 테스트가 끝나면 자동으로 롤백되기 때문에  
  DB가 더러워지지 않는다는 장점이 있었지만,
- Testcontainers + DB 클린업 전략으로 바꾸면서  
  이 `@Transactional`을 과감하게 제거해 봤습니다.

그랬더니 운영 환경에서는 충분히 발생할 수 있는 문제들이 테스트에서도 발견할 수 있겠더라고요.

1. **Lazy Loading 이슈를 테스트에서 바로 확인 가능**
   - 기존에는 테스트 전체가 하나의 큰 트랜잭션 안에서 돌아가다 보니, 
     영속성 컨텍스트가 끝까지 열려 있어서 `LazyInitializationException` 이 잘 보이지 않았습니다.
   - 하지만 실제 운영 환경에서는 서비스/리포지토리 계층의 트랜잭션 경계가 더 좁고, 
     컨트롤러나 뷰 렌더링 시점에는 이미 트랜잭션이 끝난 상태일 수 있습니다.
   - 테스트에서 메서드 단위로 트랜잭션이 끊기도록 바꾸자, 
     “운영 환경이라면 발생했을 법한” 지연 로딩 관련 버그들을 미리 확인할 수 있게 되었습니다.

2. **영속성 컨텍스트/더티 체킹 동작을 실제와 더 가깝게 검증**
   - 하나의 큰 트랜잭션 안에서만 테스트를 돌리면, 
     엔티티가 계속 영속 상태로 유지되기 때문에 더티 체킹이나 플러시 타이밍을 실제와 다르게 느끼게 됩니다.
   - `@Transactional`을 제거하고, 
     실제 코드에 선언된 서비스/리포지토리 단위 트랜잭션 경계에 의존하도록 바꾸면 
     “어디에서 플러시가 일어나는지”, “언제 엔티티가 detach 되는지”를 테스트에서 더 정확하게 볼 수 있습니다.

3. **트랜잭션 경계 밖에서의 호출 실수를 조기에 발견**
   - 예를 들어, 특정 도메인 로직은 반드시 `@Transactional`이 걸린 서비스/도메인 서비스 안에서만 호출되어야 하는데,
     테스트에서 트랜잭션이 전체를 감싸고 있으면 이런 실수가 잘 드러나지 않습니다.
   - 테스트 메서드 수준의 `@Transactional`을 제거하자, 
     “운영 환경에서라면 실패했을 호출”들이 테스트에서도 예외를 던지기 시작했고, 
     트랜잭션 경계를 다시 점검할 수 있는 계기가 되었습니다.

정리하자면, 테스트 메서드에 `@Transactional`을 거는 방식은  
테스트 데이터 롤백이라는 장점이 있는 대신,  
운영 환경과 다른 트랜잭션 경계를 만들면서 여러 문제를 가릴 수 있습니다.

이번에 Testcontainers + DB 클린업 전략으로 전환하면서 `@Transactional`을 걷어낸 덕분에,  
트랜잭션/지연 로딩/영속성 컨텍스트와 관련된 버그들을 운영 환경에서가 아니라 **테스트 단계에서 미리 발견할 수 있게 된 것**이 가장 큰 수확이었습니다.

### 7. 마치며

정리해보면, Testcontainers를 도입해 보고 싶었던 이유는

> “요즘 유행이라 한 번 써보고 싶어서”가 아니라,  
> “테스트 코드와 개발 환경을 서로 독립적인 공간으로 분리하고 싶어서”였습니다.

- 한 사람이 개발 환경 DB에서 디버깅한다고 해서  
  다른 사람 테스트가 영향을 받지 않았으면 좋겠고,
- 개발 환경 데이터를 함부로 건드리기 어려워서  
  테스트를 고치거나 추가하는 게 부담스럽지 않았으면 좋고,
- “테스트가 있어서 안심된다”는 말을  
  조금 더 자신 있게 할 수 있었으면 좋겠습니다.

그 과정에서

- MySQL Testcontainers 설정을 만들고,  
- 커스텀 어노테이션 `@TestcontainersEnvironment`로  
  테스트 환경 설정을 한 줄로 감쌀 수 있게 했고,
- 개발 환경 DB에 있던 대표 시나리오를  
  Fixture 코드로 재현하는 구조까지 만들어 봤습니다.

이 글은 팀에 도입하기 전 정리해 둔 기록에 가깝고,  
앞으로는

- CI 환경에서 Testcontainers를 어떻게 운영할지,  
- MySQL 외에 Redis, 메시지 큐 같은 인프라도 Testcontainers로 함께 관리할지,

같은 부분들을 더 고민해보면서,  
추가로 정리해 볼 수 있을 것 같습니다.

</div>
