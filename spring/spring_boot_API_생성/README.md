<div class="markdown-body">  

###### 해당 글은 [2) 스프링부트로 웹 서비스 출시하기 - 2. SpringBoot & JPA로 간단 API 만들기](https://jojoldu.tistory.com/251?category=635883)을 참고해서 작성했습니다.  


## 도메인 코드  

<p align="center">
  <img src="https://user-images.githubusercontent.com/109803585/235952854-7e65c5d0-113a-474b-8ebb-e3aee1650627.PNG" alt="text" width="number" />
</p>  

- `Posts 클래스` : 실제 DB 테이블과 매칭될 클래스이며, **Entity 클래스**라고 함.

```
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Getter
@Entity
public class Posts extends BaseTimeEntity {
	
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;
	
	@Column(length = 500, nullable = false)
	private String title;
	
	@Column(columnDefinition = "TEXT", nullable = false)
	private String content;
	
	private String author;
	
	@Builder
	public Posts( String title, String content, String author) {
		this.title = title;
		this.content = content;
		this.author = author;
	}
}
```  
<br>  

### JPA 제공 어노테이션  

- `@Entity`
    - 테이블과 링크될 클래스(해당 Posts클래스는 `posts table` 으로 자동적으로 네이밍)
- `@id`
    - 테이블의 PK필드
- `@GeneratedValue`
    - PK의 생성 규칙
    - 기본값은 AUTO 이나, 스프링 부트 2.xx에선 위와 같이 추가해야 auto_increment 속성이 추가됨
- `@Column`
    - 테이블의 칼럼, 위 코드와 같이 변경이 필요한 경우에만 선언
    - 예를들어, 데이터 타입이 String인 경우 VARCHAR(255)으로 기본 설정됨  

### Lombok 제공 어노테이션  

- `@NoArgsConstructor`
    - 기본 생성자 자동 추가
        - `access = AccessLevel.PROTECTED` 기본 생성자의 접근 권한을 protected(같은 패키지내에서만 접근)로 제한
            - JPA에서 Entity 클래스를 생성하는 것을 허용하기 위함
- `@Getter`
    - 모든 필드의 getter() 메서드 생성
- `@Builder`
    - 빌더패턴 클래스 생성
        - 생성자 사단에 선언 시 생성자에 포함된 빌드만 빌더에 포함.

###### 빌더 패턴을 써야하는 이유?
- 생성자의 파라미터를 여러개 받을 경우를 생각해보자.
    - `Posts posts = new Posts( "제목1", "내용1", "글쓴이1", ... );`
- 파라미터의 순서를 무시하는 경우를 생각해보자.
    - `Posts posts = new Posts( "글쓴이1", "제목1", "내용1", ... );`
- 위 문제가 되는 경우와 아래 빌더패턴으로 구현한 경우를 비교해보자.
    - 어느 필드에 어떤 값을 넣어야 할지 명확하게 알 수 있다.  

```
Posts posts = Posts.builder()
                    .title("제목1")
                    .content("내용1")
                    .writer("글쓴이1")
                    ...
                    .builder();
```
<br>
- PostsRepository 인터페이스  

```
public interface PostsRepository extends JpaRepository<Posts, Long>{	
}
```
흔히 알고 있는 DAO(Data Access Object) 클래스(데이터베이스에 접근해서 작업을 하는 부분만을 소유한 클래스)와 동일하며,  
JPA 에서는 `JpaRepository<Entity 클래스, PK타입>을 상속`한 인터페이스로 생성한다.  
이를 통해 기본적인 CRUD 메서드를 사용할 수 있다. 또한, `@Repository`를 추가할 필요가 없음.  

<br>  

## 테스트 코드  
Spring Boot 프로젝트에서 `JUnit 5`를 사용하기 위한사전 설정 
- JUnit 4 제외 : build.gradle 설정파일에 dependencies에서 **spring-boot-starter-test** 를 찾고 다음과 같이 수정한다.
```
testCompile('org.springframework.boot:spring-boot-starter-test') {
    exclude module: 'junit'
}
```

- JUnit 5 추가 : dependencies에 다음과 같이 JUnit 5 의존성을 추가한다.  

```
testImplementation('org.junit.jupiter:junit-jupiter-api:5.2.0')
testCompile('org.junit.jupiter:junit-jupiter-params:5.2.0')
testRuntime('org.junit.jupiter:junit-jupiter-engine:5.2.0')
```  
<br>
- PostsRepositoryTest 클래스  

```
@ExtendWith(SpringExtension.class)
@SpringBootTest
public class PostsRepositoryTest {

	@Autowired
	PostsRepository postsRepository;
	
	@AfterEach
	public void cleanup() {
		postsRepository.deleteAll();
	}
	
	@Test
	public void 게시글저장_불러오기() {
		// given
		postsRepository.save(Posts.builder()
						.title("테스트 게시글")
						.content("테스트 본문")
						.author("test@test.com")
						.build());
		
		// when
		List<Posts> postsList = postsRepository.findAll();
		
		// then
		Posts posts = postsList.get(0);
		assertThat(posts.getTitle()).isEqualTo("테스트 게시글");
		assertThat(posts.getContent()).isEqualTo("테스트 본문");
	}
```  
위와 같이 3개 문단으로 나눈다.
- `given`
    - 테스트 기반 환경 구축
- `when`
    - 테스트 하고자 하는 코드 선언
- `then`
    - 테스트 검증  
<br>
> 테스트에 적용한 어노테이션
- `@SpringBootTest`
    - 스프링 어플리케이션 컨텍스트를 로드하는 어노테이션으로, 운영 환경에 가장 가까운 환경을 애뮬레이션
- `@AfterEach`
    - 각각의 테스트 메서드가 끝날때 마다 실행되는 메서드를 의미


<br>  

### Controller와 DTO 클래스 구현
  
```
@RestController
@AllArgsConstructor
public class WebRestController {
	
	private PostsRepository postsRepository;
	
	@GetMapping("/hello")
	public String hello() {
		return "HelloWorld";
	}
	
	@PostMapping("/posts")
	public void savePosts(@RequestBody PostsSaveRequestDto dto) {
		postsRepository.save(dto.toEntity());
	}
}
```
postsRepository 필드에 `@Autowired` 어노테이션이 없다.  
스프링프레임워크에서는 Bean을 주입받는 방법은 다음과 같이 있다.  
- `@Autowired`
- setter() 메서드
- 생성자  

이 중 권장하는 방식은 **생성자로 주입받는 방법**이다.  
위 코드에서는 클래스 위에 선언된 `@AllArgsConstructor` 어노테이션으로 인해, 모든 필드를 인자값으로 하는 생성자가 생성되었다.  

이를 통해 의존성 관계가 변경될 때마다 수정하는 번거로움이 해결된다.  
<br>
DTO 클래스의 코드는 다음과 같다.  

```
@Getter
@Setter
@NoArgsConstructor
public class PostsSaveRequestDto {

	private String title;
	private String content;
	private String author;
	
	public Posts toEntity() {
		return Posts.builder()
				.title(title)
				.content(content)
				.author(author)
				.build();
	}
}
```  
위 코드를 보면서 기억하자.  
Controller에서 `@RequestBody` 어노테이션을 통해 외부에서 데이터를 받는 경우에는 기본 생성자와 setter() 메서드를 통해서만 값이 할당된다.  

**따라서, setter() 메서드가 허용됨을...**  

또한, 위 DTO 클래스는 앞서 생성한 Entity 클래스와 거의 유사한 형태이다.  
테이블과 매핑되는 <u>**Entity 클래스를 Request / Response 하기 위한 클래스로 사용해서는 안된다.**</u>  
  
Entity 클래스가 변경되면 의존관계를 가지고 있는 클래스가 변경되기 때문이다.  
  
DTO는 View를 위한 클래스이므로, 빈번한 변경이 요구된다.  
결론적으로, Entity 클래스와 DTO 클래스는 분리해서 사용하자.  
<br>

### 반복적인 칼럼인 생성시간과 수정시간
  
보통 **Entity 클래스에는 해당 데이터의 생성시간과 수정시간**을 포함시킨다.  
언제 만들어졌는지, 언제 수정되었는지를 확인하기 위해서이다.  
모든 Entity에 공통으로 들어가는 데이터라서.. 이 문제를 해결해보자.  


SpringDataJpa 버전에서는 LocalDate와 LocalDateTime을 DB에 저장할 떄 제대로 전환이 안되는 이슈가 있다.  

이 문제를 SpringDataJpa의 코어 모듈인 Hibernate core 5.2.10부터는 해결되었기 때문에, 다음과 같이 코드를 추가해보자.  

```
buildscript {
    ...
    dependencies {
        ...
        //추가
        classpath "io.spring.gradle:dependency-management-plugin:1.0.4.RELEASE" 
    }
}

apply plugin: 'java'
apply plugin: 'eclipse'
apply plugin: 'org.springframework.boot'

....

//Spring Boot Overriding
ext['hibernate.version'] = '5.2.11.Final' //추가

dependencies {
...
}
``` 

<br>  

### BaseTimeEntity 생성  

```
package com.hbk.webservice.domain;

@Getter
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public class BaseTimeEntity {
	
	@CreatedDate
	private LocalDateTime createDate;
	
	@LastModifiedDate
	private LocalDateTime modifiedDate;
}
```  
위 BaseTimeEntity 클래스는 모든 Entity들의 상위(부모) 클래스가 되어 createDate와 modifiedDate를 관리하는 역할을 한다.  
### BaseTimeEntity 클래스에 사용된 어노테이션  

- `@MappedSuperClass`
    - Entity 클래스에서 이를 해당 어노테이션이 있는 클래스를 상속할 경우 선언된 필드를 테이블의 칼럼으로 인식
        - 위 코드에서는 `createDate, modifiedDate` 필드
- `@EntityListeners(AuditingEntityListener.class)`
    - BaseTimeEntity 클래스에 Auditing 기능 포함
        - 엔티티의 변화를 감지하여 엔티티와 매핑된 테이블의 데이터를 조작
        - Spring Data JPA에서 제공하는 이벤트 리스너로, 엔티티의 영속,수정 이벤트를 감지하는 역할
- `@CreatedDate`
    - 엔티티가 생성됨을 감지하고 그 시점을 `createDate` 필드에 기록
- `@LastModifiedDate`
    - 엔티티가 수정됨을 감지하고 그 시점을 `modifiedDate` 필드에 기록  
<br>  

Entity 클래스가 BaseTimeEntity를 상속받도록 변경한다.
```
public class Posts extends BaseTimeEntity {
    ...
}
```  
<br>
마지막으로, JPA Auditing 어노테이션들을 모두 활성화 시킬수 있도록 Application 클래스에 활성화 어노테이션 추가한다.

```
@EnableJpaAuditing // JPA Auditing 활성화
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```  
</div>