## 테스트를 위해 정의했던 Public 메서드


### 고유 식별자 생성을 데이터베이스에 위임했을 때, Stubbing

`Mockito` 라이브러리를 활용해서 `Service` 레이어에 대한 테스트 코드를 작성하면서, 협력 객체인 `Repository` 레이어에 대한 Stubbing을 진행했다.  
실제 데이터베이스에서 저장된 후 반환되는 것이 아니기 때문에, 실제 저장되어 있던 것처럼 구성을 해야한다.

이때, `Entity` 클래스에는 아래와 같이 고유 식별자를 의미하는 필드가 존재하기 마련이다.  

따라서, 고유 식별자 생성을 데이터베이스에 위임하는 것으로 `id`와 같이 고유 식별자를 인자로 받는 생성자는 열어두지 않는 것이 맞다고 생각한다.

```
// Category.java

@Entity
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    
    public Category(String name) {
        this.name = name;
    }
}
```

### 필자가 Stubbing 했던 방법

게시글 서비스(`PostService`) 레이어에서 게시글을 저장하는 비즈니스 로직이 다음과 같은 프로세스라고 가정해보자.

1. 게시글을 작성한 사용자 번호에 해당하는 사용자를 데이터베이스에서 조회(`MemberRepository`)
2. 게시글에 설정된 카테고리 번호에 해당하는 카테고리를 데이터베이스에서 조회(`CategoryRepository`)
3. 게시글 저장(`PostRepository`)

3가지 협력 객체 중 `Stubbing` 해야하는 객체는 1번과 2번에서 사용된 `Repository` 객체이다.

그렇다면, 테스트 코드에서 사전에 아래와 같이 `Stubbing` 하면된다.

```
// ServiceMockTest.java

@BeforeEach
void 사전_스텁_설정() {
    Long 사용자_번호 = 1L;
    Long 카테고리_번호 = 1L;

    Member 사용자 = new Member("홍길동", "gildong@test.com");
    Category 카테고리 = new Poat("DAILY");
    
    사용자.updateId(사용자_번호);
    카테고리.updateId(카테고리_번호);

    when(memberRepository.findById(사용자_번호)).thenReturn(Optional.of(사용자));
    when(categoryRepository.findById(카테고리_번호)).thenReturn(Optional.of(카테고리));
}
```

위처럼 `id`를 인자로 받는 생성자를 따로 열어주지 않았으니, Entity 객체에 `updateId` 메서드를 정의해줘야 한다.

```
@Entity
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
   
    private String name;
    
    public Post updateId(Long id) {
        this.id = id;
        return this;
    }
}
```

테스트를 위한 `public` 메서드를 만들면서, Stubbing 했었고 굉장히 찝찝했었다.

리뷰어님께 이에 대해서 의견을 부탁드렸고, `ReflectionTestUtils`을 추천해주셨다.  

<br>


> 제 생각을 말씀드리면, Test 만을 위해 public 메소드를 만드는 것은 최대한 지양해야 된다고 생각합니다.  
> 특히나 JPA 같이 ID 라는 식별자를 중요하게 다루는 시스템에 ID 를 수정해도 될 것 같은 메소드를 열어두는 것 좋지 않다고 생각해요 😅

<br>

따라서, 테스트만을 위해 public 메서드를 만들지 않으면서 어떻게 Stubbing할 수 있을까? 라는 고민을 하고 있다면 아래와 같이 사용하면 된다.

```
@BeforeEach
void 사전_스텁_설정() {
    Long 사용자_번호 = 1L;
    Long 카테고리_번호 = 1L;

    Member 사용자 = new Member("홍길동", "gildong@test.com");
    Category 카테고리 = new Poat("DAILY");
    
    ReflectionTestUtils.setField(사용자, "id", 사용자_번호);
    ReflectionTestUtils.setField(카테고리, "id", 카테고리_번호);
    
    사용자.updateId(사용자_번호);
    카테고리.updateId(카테고리_번호);

    when(memberRepository.findById(사용자_번호)).thenReturn(Optional.of(사용자));
    when(categoryRepository.findById(카테고리_번호)).thenReturn(Optional.of(카테고리));
}
```