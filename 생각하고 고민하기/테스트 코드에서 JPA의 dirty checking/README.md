<div class=markdown-body>

모든 코드는 [깃허브](https://github.com/hbkuk/blod-code/tree/main/jpa/dirty-checking)에 있습니다.

## 테스트 코드에서의 JPA의 dirty checking

`Spring Data Jpa`를 사용하면서, 테스트 코드 실행 시 `update` 쿼리가 실행되지 않는 상황이 있었습니다.

결론적으로, `dirty checking` 기능이 제대로 동작하지 않는 상황에 대해서, 해결했던 내용을 기록했습니다. 

### MemberService와 테스트 코드

`JpaRepository<>` 상속받는 `MemberRepository` 클래스를 선언하고,   
이를 협력 객체로 두는 `MemberService` 클래스를 만들어서 `Spring Bean`으로 등록했습니다.

이 후 `MemberService` 레이어에 대한 테스트 코드를 작성하고자 했습니다.

이때, 테스트 환경은 아래와 같이 구성해 주었습니다.

```
@DisplayName("회원 서비스 레이어 테스트")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Sql(value = "/clean.sql", executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
public class MemberServiceTest {

    MemberService memberService;

    @Autowired
    MemberRepository memberRepository;

    @BeforeEach
    void 사전_객체_생성() {
        memberService = new MemberService(memberRepository);
    }
}

```
- `@SpringBootTest`
  - Spring Boot 구동 환경
- `@Sql`
  - 테스트 메서드 간 데이터 베이스 초기화 작업

<br>

테스트 환경을 구성했으니,   
회원 생성 및 조회와 관련된 테스트 코드를 작성했고 **회원 수정과 관련된 테스트 코드를 아래와 같이 작성**해 보았는데요.   

```
@Test
@DisplayName("회원을 수정한다.")
void 회원_수정() {
    // given
    MemberRequest 스미스_회원_생성_요청 = MemberRequest.createOf(스미스.이메일, 스미스.비밀번호, 스미스.나이, MemberType.NORMAL);
    MemberResponse 스미스_회원_정보 = memberService.createMember(스미스_회원_생성_요청);

    // when
    String 변경할_비밀번호 = "New" + 스미스.비밀번호;
    int 변경할_나이 = 스미스.나이 + 10;

    memberService.updateMember(스미스_회원_정보.getId(), MemberRequest.updateOf(변경할_비밀번호, 변경할_나이));

    // then
    Member 회원_조회_정보 = memberRepository.findById(스미스_회원_정보.getId()).get();

    assertThat(회원_조회_정보.getPassword()).isEqualTo(변경할_비밀번호);
    assertThat(회원_조회_정보.getAge()).isEqualTo(변경할_나이);
}
```

**위 코드와 같이 회원 수정 테스트는 실패했습니다.** 

또한, Hibernate가 실행하는 SQL 쿼리에도 `update` 쿼리만 로깅되지 않았습니다.

음, 테스트 코드는 제대로 잘 작성했는데 ... 도대체 뭐가 문제일까요?

### MemberService 코드

테스트 코드는 문제가 없다고 판단해서, 프로덕션 코드를 다시 한번 살펴보았습니다.

```
@Transactional(readOnly = true)
@Service
public class MemberService {
    private final MemberRepository memberRepository;

    public MemberService(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }

    @Transactional
    public void updateMember(Long id, MemberRequest request) {
        Member member = findById(id);
        member.update(request.toMember());
    }

    private Member findById(Long id) {
        return memberRepository.findById(id).orElseThrow(() -> new NotFoundMemberException(ErrorType.NOT_FOUND_MEMBER));
    }
}
```

엔티티를 수정하려면, **트랜잭션 범위 내에서`dirty-checking` 기능을 기반으로 수정**되는 것으로 알고 있습니다.

흐름은 아래와 같이 정리해볼 수 있을 것 같습니다.

1. 트랜잭션 시작
2. 엔티티 영속성 컨텍스트 가져옴
3. 엔티티 수정
4. 트랜잭션 종료
5. 데이터 베이스 반영(`flush`)

혹시라도, `dirty-checking` 기능에 대해서 잘 모르실 수 있어서, 간단하게 정리해보았습니다.  
링크를 추가했으니, 더 궁금하시다면 참고해 주세요.

### Dirty Checking?

![dirty-checking](https://github.com/hbkuk/blod-code/assets/109803585/0f3dbe52-d755-49f4-93b3-01cf8d8cb7cc)
[참고: [토크ON세미나] JPA 프로그래밍 기본기 다지기 6강 - JPA 내부구조 | T아카데미](https://www.youtube.com/watch?v=PMNSeD25Qko&ab_channel=SKplanetTacademy)

<br>

> JPA에서는 트랜잭션이 끝나는 시점에 변화가 있는 모든 엔티티 객체를 데이터베이스에 자동으로 반영해줍니다.  
> 이때, 변화가 있다의 기준은 최초 조회 상태입니다.
> 
> JPA에서는 엔티티를 조회하면 해당 엔티티의 조회 상태 그대로 스냅샷을 만들어놓습니다.  
>그리고 트랜잭션이 끝나는 시점에는 이 스냅샷과 비교해서 다른점이 있다면 Update Query를 데이터베이스로 전달합니다.
> 
> [dirty-checking 참고 - 이동욱님 블로그](https://jojoldu.tistory.com/415)

<br> 

다시 본론으로 돌아와서,  

(왜 테스트가 실패하는지 ... `dirty-checking` 기능은 왜 동작하지 않았는지는 뒤에서 알아보겠습니다.)

우선, 테스트를 빠르게 성공시키기 위해서 아래와 같이 `save` 메서드를 호출하는 코드를 추가해 보았습니다.

```
@Transactional
public void updateMember(Long id, MemberRequest request) {
    Member member = findById(id);
    member.update(request.toMember());
    
    memberRepository.save(member); // save 호출
}
```

그렇다면, 테스트 코드도 정상적으로 성공하게 됩니다.  

<br>

![update query](https://github.com/hbkuk/blod-code/assets/109803585/d47b8ac6-a42e-48a9-96f0-bd60e29662c3)

심지어, 이전에는 실행되지 않았던 `update` 쿼리도 실행되는 것을 확인했습니다.

이걸로 문제가 해결했다고 할 수 있을까요?  

우선, save 메서드는 왜 성공하는지 알아보는 것이 좋을 것 같습니다.
(또한, 필자는 어떻게든 `dirty-checking` 기능을 어떻게든 활용하고자 했습니다.)

### `SimpleJpaRepository`의 `save` 메서드

그렇다면,`Spring Data JPA`에서 제공하는 `SimpleJpaRepository`의 `save` 메서드는 어떤 일을 하는지 확인해볼까요?
 
### `save` 메서드는 2가지 일을 합니다.

1. 인자로 받은 객체가 데이터베이스에서 가져오지 않은 새로운 객체인가?
   - 새로운 객체일 경우, `insert` 쿼리로 새로운 데이터 저장
2. 인자로 받은 객체가 데이터베이스에서 가져온적 있는 객체인가?
   - 이 경우 `update set 필드=변경되는값, ... where id = ?`와 같은 `update` 쿼리로 기존 데이터 수정

결론적으로, 저장 및 수정하는 상황에서 사용할 수 있고, 수정의 경우 기존 데이터를 업데이트를 합니다.

<br>

그렇다면, `save` 메서드 내부 로직에 따라 데이터를 수정하는 경우 `save` 메서드를 호출하면 되는 것 아닌가? 라고 생각할 수 있을 것 같습니다.

이 부분은, 자료를 찾아본 것은 아니지만, 간단하게 필자의 생각을 적어보려고 합니다. 

- 엔티티에서 수정된 필드만 체크해서 업데이트하는 방법이 더 좋은 방법이지 않을까?
- 컬렉션을 사용할 때 처럼, 하나의 값을 가져와서 값을 수정하고, 따로 `update` 메서드를 호출하는가?

(이러한 이유로 `dirty-checking` 기능이 존재한다고 생각합니다. 즉, 지향하는 방법? 일수도 ...)

---

따라서, `save` 메서드를 호출하지 않고, 데이터를 수정할 수 있게 `dirty-checking` 이 되지 않는 이유를 찾아서 수정해야합니다. 

~~오랜 삽질 끝에 ... 찾았습니다.~~

### Spring Bean이 아닌, 직접 객체 생성

![잘못된 부분](https://github.com/hbkuk/blod-code/assets/109803585/e4007747-613b-4036-ba8b-8845ce27e518)

바로, `MemberService` 객체를 `Spring Bean`으로 주입받아서 사용한 것이 아닌, **직접 객체를 생성했었습니다.**

따라서, `Spring`의 `ApplicationContext`에 의해서 관리되지 않으며, `Spring Bean` 라이프사이클 관리 및 `AOP`를 적용받지 않기 때문에, 
dirty checking이 진행되지 않았었습니다.


</div>