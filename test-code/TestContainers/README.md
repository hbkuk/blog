<div class=markdown-body>

##  들어가며

테스트 환경을 어떻게 가져갈지 고민하다 보면 결국 이런 질문으로 귀결되는 것 같습니다.

“운영 환경이랑 최대한 비슷하게 테스트를 돌리고 싶은데, 속도/비용/복잡도는 어디까지 감수할 수 있을까?”

저는 지금 회사 프로젝트에 당장 `Testcontainers`를 도입한 건 아니고요,
“언젠가 팀에 도입한다면 어떻게 설계하는 게 깔끔할까?”를 미리 고민해보고자 합니다.

이 포스팅에서는 다음 내용을 다룹니다.
- 여러 테스트 환경 옵션 중에서 왜 `Testcontainers`를 선택했는지  
- `Testcontainers`를 어떤 방식으로 적용할지 (프로필 / 상속 / 어노테이션 / Tag / Spring Boot 3.1+)
- `Testcontainers` 위에서 초기 데이터 세팅 전략 + 테스트 후 클린업 전략을 어떻게 생각해봤는지
- 특히 `@Transactional` 테스트의 함정 (Lazy 로딩, Dirty Checking) 을 어떻게 볼지

“정답”을 말한다기보다는,
저처럼 도입 전에 미리 실험해보고 싶은 분들이 생각할 포인트 목록 정도로 봐주시면 좋겠습니다.

## 본문

### 지금 테스트 환경에서 느끼는 답답함 정리

먼저, “왜 굳이 `Testcontainers`까지 써볼까?”를 정리해봤습니다.

2-1-1. 환경 불일치 문제  
일반적으로 이런 구조 많이 쓰잖아요.
- 운영: MySQL, Redis, ...
- 테스트: H2 / in-memory DB, Mockito 기반의 Stub …

이렇게 가다 보면:
- H2에서는 통과하는 쿼리가 MySQL에선 락/인덱스/타입 차이로 문제를 일으키고,
- CI는 초록불인데, 배포 후에만 이상하게 깨지는 케이스가 발생하고,

즉, 테스트는 있는데 “테스트를 신뢰할 수 없는 상태”가 되어버리는 거죠.

2-1-2. 제가 세운 기준 4가지  
그래서 개인적으로 실험해보면서, 도입 기준을 네 가지로 잡았습니다.
- 신뢰도
  - 운영과 최대한 비슷한 DB/외부 서비스를 쓰고 싶은가?
- 속도 / 비용
  - PR마다 돌릴 거면 어느 정도까지 허용 가능한 시간인가?
- 작성/유지보수 난이도 (DX)
  - 테스트 하나 추가할 때 얼마나 많은 걸 알아야 하나?
- 유연성
  - 테스트마다 다른 컨테이너 조합을 쓰고 싶을 때 대응이 쉬운가?

아래 옵션들을 이 네 가지 축으로 비교해 보면서,
“실제 팀에 도입한다면 뭘 고를 것 같나?”를 가정해본 셈입니다.


2-2. 테스트 환경 옵션들 간단 비교

2-2-1. 별도 테스트 인프라 구축 (MySQL)
- 장점
  - 운영과 거의 동일한 환경
  - 모든 개발자가 같은 인프라 공유 → 환경 편차 감소.
- 단점
  - 인프라 관리·비용 부담, 모니터링/보안까지 생각해야 함.
  - 로컬/CI에서 항상 그 인프라에 의존 → 장애 시 영향이 큼.

“팀 차원에서 장기적으로 깔끔하게 운영한다”는 느낌은 있는데,
개인적으로 실험해보기엔 너무 무겁다고 느꼈습니다.

2-2-2. dev 환경 인프라를 로컬 테스트에서 사용
•	장점
•	별도 인프라 구축 없이 dev DB/S3를 그대로 재사용.
•	단점
•	테스트가 dev 데이터와 얽혀서 데이터 무결성 문제 위험.
•	네트워크 비용 문제 그대로.
•	dev 환경을 테스트가 더럽힐 수 있고, 다른 팀에 민폐 될 수 있음.

개인 PoC 관점에서도 그렇고,
“테스트 환경은 웬만하면 다른 환경과 깔끔하게 격리하자”는 생각이 강해서
현실적인 선택지는 아니라고 봤습니다.  ￼

2-2-3. 각자 로컬에 Docker(MySQL, Local S3 등) 띄우기
•	장점
•	네트워크 지연 없이 빠르게 테스트 가능.
•	스키마/데이터 깨부수면서 마음껏 실험 가능.
•	단점
•	개발자별 설치·버전·설정 편차.
•	신규 입사자 온보딩이 환경 세팅 지옥이 될 수 있음.

“지금 혼자 PoC 해보는 상황”에서는 꽤 나쁘지 않지만,
“팀에 공식 패턴으로 도입한다”라고 생각하면 아쉬운 지점이 많습니다.

2-2-4. Embedded 솔루션 (H2, Embedded Redis 등)
•	장점
•	외부 의존성이 줄어서 CI/로컬 세팅이 단순해짐.
•	단점
•	DB/브로커 구현 차이로 인한 불일치 문제. ￼

이건 이미 잘 알고 있는 단점이라,
“지금 겪는 스트레스를 해결해보자”는 취지와는 거리가 멀었습니다.

2-2-5. Testcontainers 사용 (이번 글의 주인공)
•	장점
•	실제 Docker 이미지를 그대로 사용 → 운영과 매우 유사한 환경. ￼
•	JUnit 5와 자연스럽게 통합되어 컨테이너 라이프사이클을 자동으로 관리. ￼
•	DB, 메시지 브로커, 검색엔진, 클라우드 서비스 등 다양한 모듈 제공.  ￼
•	단점
•	잘못 설계하면 테스트 속도가 심각하게 느려질 수 있음. ￼

“운영과 최대한 비슷하게 테스트 돌려보고 싶다”는 욕심을 만족시키면서,
PoC로도 충분히 손대볼 수 있는 수준이라 Testcontainers를 메인 후보로 잡고 설계 실험을 해보자는 결론을 냈습니다.

⸻

2-3. Testcontainers 간단 정리

공식 설명을 한 줄로 줄이면:

Testcontainers는 테스트 코드에서 Docker 컨테이너를 쉽게 띄우고 정리할 수 있게 도와주는 라이브러리다.
JUnit과 통합되어 테스트 전후에 컨테이너 라이프사이클을 자동으로 관리해 준다.  ￼

JUnit 5와 함께 쓸 때 핵심은 두 개입니다.  ￼

@Testcontainers
class ExampleTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");
}

	•	@Testcontainers
	•	JUnit 5 확장을 붙여주고, @Container 필드를 찾아서 라이프사이클을 관리합니다.
	•	@Container
	•	이 필드가 컨테이너임을 표시하고, 테스트 시작/종료에 맞춰 start()/stop()을 호출해 줍니다.
	•	static 필드
	•	클래스 단위로 컨테이너를 공유 (shared container).
	•	인스턴스 필드
	•	테스트 메서드마다 컨테이너를 새로 띄우고 내림 (restarted container). ￼

이 기본 개념 위에:
•	“컨테이너를 어디에 정의할지”
•	“여러 테스트에서 어떻게 재사용할지”
•	“Spring Boot 설정은 어디에 숨길지”

를 설계하는 게 이번 글의 나머지 주제입니다.

⸻

2-4. 적용 방식 설계: 상속 vs 어노테이션 vs Tag vs Spring Boot 3.1+

실제로 설계해보면서 고민했던 패턴은 대략 네 가지였습니다.
1.	테스트 클래스에 직접 @Testcontainers + @Container
2.	AbstractIntegrationTest 상속
3.	커스텀 어노테이션 + @Tag
4.	Spring Boot 3.1+의 @ServiceConnection 활용

2-4-1. 테스트 클래스에 직접 선언

@Testcontainers
@SpringBootTest
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");
}

	•	장점
	•	가장 직관적. PoC용으로 시작하기 좋음.
	•	단점
	•	여러 테스트가 늘어나면 설정이 중복되고,
“우리 서비스의 표준 컨테이너 조합”이 코드에 흩어짐.

→ 개인적으로는 “처음 만져볼 때” 가장 적합한 패턴이었습니다.

2-4-2. AbstractIntegrationTest 상속 + Singleton 컨테이너
공통 테스트 베이스 클래스를 하나 두고, 모든 통합 테스트가 상속하는 패턴입니다.
Testcontainers 공식 가이드에서도 JUnit 5와 함께 Singleton 컨테이너 패턴을 별도로 소개하고 있습니다.  ￼

@Testcontainers
@SpringBootTest
public abstract class AbstractIntegrationTest {

    @Container
    protected static final PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");

    // Spring Boot 3.0대라면 @DynamicPropertySource,
    // 3.1+라면 @ServiceConnection으로 대체 가능 (아래에서 다시 언급)
}

class UserRepositoryTest extends AbstractIntegrationTest {
// 비즈니스 테스트 코드만
}

	•	장점
	•	Testcontainers 설정과 Spring 연동이 한 곳에 모인다.
	•	모든 통합 테스트가 같은 컨테이너/설정을 사용 → 일관성↑
	•	단점
	•	이미 다른 부모 클래스를 상속 중인 테스트에 붙이기 어렵다.
	•	테스트마다 DB 버전/옵션을 바꾸고 싶을 땐 유연성이 떨어진다.

실 프로젝트에 도입한다고 가정하면,
**“디폴트 통합 테스트 베이스”**로 제일 먼저 떠오르는 패턴이었습니다.

2-4-3. 커스텀 어노테이션 + Tag
상속 대신, 어노테이션으로 의미를 표현하는 방식도 가능합니다.

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@SpringBootTest
@Testcontainers
@Tag("integration") // 혹은 "TestContainers"
public @interface IntegrationTest {
}

@IntegrationTest
class UserRepositoryTest {
// 인프라 디테일은 숨겨지고, 비즈니스 테스트만 보이게 됨
}

이렇게 하면:
•	테스트 작성자는 @IntegrationTest 하나만 기억하면 되고,
•	빌드 도구(Gradle/Maven)에서는 @Tag("integration")으로
test / integrationTest 태스크를 분리할 수 있습니다.  ￼

여기에 더 나가서, JUnit 5 Extension을 직접 만들어서
•	@Tag("TestContainers")가 붙은 테스트에서만 컨테이너를 띄우는 로직

같은 걸 짤 수도 있습니다. (이건 나중에 별도 글에서 다뤄도 재밌을 것 같더라고요.)

2-4-4. Spring Boot 3.1+ @ServiceConnection
Spring Boot 3.1부터는 @ServiceConnection 덕분에 Testcontainers 연동이 더 단순해졌습니다. ￼

@SpringBootTest
@Testcontainers
class UserRepositoryTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16");
}

이렇게 하면 원래 써야 했던 @DynamicPropertySource 코드가 필요 없습니다. ￼

또는 설정 클래스로 분리해서 재사용할 수도 있습니다. ￼

@TestConfiguration
class TestContainerConfig {

    @Bean
    @ServiceConnection
    PostgreSQLContainer<?> postgres() {
        return new PostgreSQLContainer<>("postgres:16");
    }
}

@SpringBootTest
@Import(TestContainerConfig.class)
class UserRepositoryTest {
// ...
}

실제로 도입한다고 가정하면,
Spring Boot 3.1+ 환경에서는 @ServiceConnection을 기본으로 가져가는 게 자연스럽겠다는 느낌을 받았습니다.

⸻

2-5. 초기 데이터 세팅 전략 (간단 버전)

컨테이너를 띄웠다고 끝이 아니고,
“그 안에 어떤 데이터 상태를 만들 건가?”도 같이 고민해야 합니다.

저는 우선 개인 PoC 단계라 크게 이렇게만 나눴습니다.
1.	스키마
•	DDL 스크립트로 테이블 생성
•	경우에 따라서는 프로젝트에서 사용하는 SQL 스크립트를 그대로 재사용
2.	레퍼런스 데이터
•	코드값, 템플릿 종류 등 “거의 고정”으로 쓰이는 값들
•	별도 SQL 파일로 넣거나, 자바 코드에서 한번 insert
3.	시나리오 데이터
•	특정 테스트 케이스에서만 필요한 숙소/객실/요금/예약 등

스키마/레퍼런스 데이터는 컨테이너 뜰 때 한 번만 세팅하고,
테스트 별로 달라지는 건 팩토리/빌더 + fixture SQL로 섞어가는 방향이 현실적이라고 느꼈습니다.

(아직 실 프로젝트가 아니라 깊게 파고들진 않았고,
“너무 테스트가 fixture SQL에만 의존하지 않게 하자” 정도의 가이드라인만 잡아둔 상태입니다.)

⸻

2-6. 테스트 후 데이터 클린업 전략

+ @Transactional 테스트의 함정 (Lazy 로딩 / 더티체킹)
  개인적으로 여기서 제일 고민이 많았습니다.

“컨테이너는 재사용하고 싶다”
→ 매번 새 컨테이너를 띄우면 너무 느려질 테니까요. ￼

그러면 테스트 간 데이터 격리는 다음 중 하나로 해결해야 합니다.
•	테스트에 @Transactional을 붙이고 롤백하기
•	각 테스트 후에 테이블을 TRUNCATE/DELETE 하기
•	아예 매 테스트마다 스키마를 다시 잡기 (비용 큼)

2-6-1. @Transactional 롤백 전략의 장단점
스프링 테스트에서 흔히 쓰는 방법이죠:

@SpringBootTest
@Transactional
class UserServiceTest {
// ...
}

	•	장점
	•	테스트 끝나면 자동 롤백 → 데이터 정리 고민이 거의 필요 없음.
	•	쿼리/조회/수정 흐름을 빠르게 실험해보기 좋음.
	•	단점 (여기가 핵심)

(1) Lazy 로딩이 “테스트에서만 잘 되는” 문제

@Transaction이 테스트 메서드에 붙어 있으면:
•	테스트 전체가 하나의 트랜잭션 + 영속성 컨텍스트 안에서 돌아가고,
•	세션이 열려 있으니 order.getMember().getName() 같은 Lazy 로딩도 잘 됩니다.

하지만 실제 운영 코드에서는:
•	트랜잭션 경계가 서비스 메서드 단위거나,
•	컨트롤러/뷰 렌더링 시점에서는 이미 트랜잭션이 끝났을 수도 있습니다.

그래서 실제 런타임에서는 LazyInitializationException이 터지는 코드가,
테스트에선 멀쩡히 통과하는 왜곡이 생길 수 있습니다.

(2) 더티체킹/영속성 컨텍스트 캐시 때문에 생기는 착시

또 하나의 함정은,
테스트 안에서 “같은 트랜잭션 안에서 바로 다시 조회”할 때입니다.

order.changeStatus(COMPLETED);
// flush 안 했는데도..

Order found = orderRepository.findById(order.getId()).get();

assertThat(found.getStatus()).isEqualTo(COMPLETED);

위 코드는 사실상 DB에 다시 조회한다기보다,
1차 캐시(영속성 컨텍스트)에서 다시 꺼내오는 것에 가깝습니다.
•	테스트에서는 “어? 더티체킹 잘 되네?”라고 느끼지만,
•	실제 운영 코드에서는 트랜잭션이 나뉘어 있거나,
다른 트랜잭션/스레드에서 조회할 수 있기 때문에
동일하게 동작하지 않을 수 있습니다.

특히 테스트에서:
•	flush/clear를 안 했는데도 값이 잘 보이는 경우,
•	@Transactional 덕분에 같은 영속성 컨텍스트를 계속 쓰고 있어서
“캐시된 값”을 보고 있는 것일 뿐인 경우가 많습니다.

결국,

@Transactional 통합 테스트는
DB 상태라기보다는 **“한 트랜잭션 안에서의 JPA 동작”**을 검증하기에 가깝다.

는 점을 항상 염두에 둬야 한다는 걸 느꼈습니다.

2-6-2. TRUNCATE 기반 클린업 전략
그래서 Testcontainers + 실제 DB 환경에서는
**“컨테이너/스키마는 재사용하고, 데이터만 TRUNCATE로 비운다”**는 전략도 같이 고려해봤습니다.
•	컨테이너는 Singleton 패턴으로 한 번만 띄우고, ￼
•	각 테스트(or 각 클래스) 끝날 때:
•	비즈니스 테이블들만 TRUNCATE TABLE ... 실행
•	코드값/레퍼런스 데이터 테이블은 그대로 둠

이렇게 하면:
•	테스트는 실제 DB 커밋/쿼리/락까지 포함해 검증할 수 있고,
•	테스트 사이의 데이터 간섭은 막으면서도,
•	컨테이너를 매번 다시 띄우지 않아서 속도도 어느 정도 유지할 수 있습니다.  ￼

물론:
•	FK 제약 때문에 TRUNCATE 순서/대상 관리,
•	auto increment 초기화 여부 등 고려할 게 많긴 합니다.

그래도 “JPA 영속성 컨텍스트 캐시/트랜잭션 경계를 실제 운영과 비슷하게 가져가고 싶다”면,
몇몇 중요한 통합 테스트들은 @Transactional 없이,
TRUNCATE 기반으로 격리하는 게 낫다고 느꼈습니다.

2-6-3. 개인적인 결론 (PoC 단계 기준)
아직 실제 팀에 도입한 건 아니고,
개인 PoC를 해본 결과만 놓고 요약하면:
•	빠른 실험 / 로직 스케치
•	@Transactional 통합 테스트도 충분히 유용하다.
•	단, Lazy 로딩/더티체킹이 “테스트에서만 되는 것”이 아닌지 항상 의식해야 한다.
•	운영과 최대한 비슷한 흐름을 보고 싶은 통합 테스트
•	@Transactional은 일부러 빼고,
컨테이너 + 실제 커밋 + TRUNCATE 기반 정리로 가져가는 게 더 낫다고 느꼈다.

실제 팀에 도입하게 된다면,
•	“대부분의 통합 테스트는 @IntegrationTest + Singleton 컨테이너 + TRUNCATE 패턴”
•	“JPA 동작을 실험하는 테스트는 @Transactional로 별도 묶기”

정도로 라인을 나누면 좋겠다는 생각이 들었습니다.

⸻

3. 마치며

이 글은 **“실제 팀에 이미 도입한 후기”가 아니라,
“도입 전에 미리 부딪혀본 개인 PoC 기록”**에 가깝습니다.

그래도 직접 손을 대보면서 몇 가지는 확실히 느꼈습니다.
•	Testcontainers는 **“운영과 비슷한 환경에서 테스트하고 싶다”**는 욕심을 현실로 만들어주는 도구고, ￼
•	그 위에서 어떻게 적용(상속/어노테이션/Tag) + 데이터 세팅 + 클린업을 설계하느냐에 따라
•	테스트 신뢰도
•	실행 속도
•	팀원 경험(DX)
•	유연성이 크게 달라진다는 것.

특히,
•	@Transactional 통합 테스트가 Lazy 로딩/더티체킹 문제를 숨길 수 있다는 점,
•	Singleton 컨테이너 + TRUNCATE 전략이 현실적인 타협점이 될 수 있다는 점은
실제 도입 설계할 때 꼭 다시 떠올릴 것 같아요.

앞으로는:
•	Redis, 메시지 브로커, 외부 API(WireMock 등)까지 Testcontainers로 엮어보는 실험, ￼
•	“태그 기반(TestContainers, slow, e2e 등)”으로 어떤 테스트를 언제 돌릴지 전략 세우기

같은 것들도 한 번씩 PoC 해볼 생각입니다.

혹시 비슷하게 “도입 전 연습”을 해보셨거나,
이미 팀에서 다른 패턴으로 Testcontainers를 쓰고 계시다면,
•	어떤 기준으로 선택하셨는지,
•	@Transactional / 데이터 클린업은 어떻게 가져가셨는지

경험을 공유해 주셔도 정말 재미있을 것 같아요 🙂

</div>